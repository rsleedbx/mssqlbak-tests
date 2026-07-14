#!/usr/bin/env python3
"""Generate ``extended_properties_full.bak`` — MS_Description and arbitrary named extended properties.

## Purpose

Exercises ``sys.extended_properties`` (internally ``sysobjvalues``) at three
levels so the reader's ``recover_extended_properties`` can be verified:

  - **Schema-level**: MS_Description on the ``sales`` schema.
  - **Table-level**: MS_Description + one arbitrary-named property (``Owner``)
    on ``dbo.products`` and on ``sales.orders``.
  - **Column-level**: MS_Description + one arbitrary-named property
    (``SensitivityLabel``) on several columns.

## Schema

Two schemas: ``dbo`` and ``sales``.

Tables:
  - ``dbo.products``  — id INT PK, name NVARCHAR(100), price DECIMAL(10,2)
  - ``sales.orders``  — id INT PK, product_id INT, qty INT, ordered_at DATETIME2(0)
  - ``dbo.simple``    — id INT PK  (no extended properties — used to verify absence)

Extended-property inventory (names → values as SQL Server stores them):

  Schema sales:
    MS_Description = "Sales data schema"

  Table dbo.products:
    MS_Description = "Product catalogue"
    Owner          = "commerce-team"

  Table sales.orders:
    MS_Description = "Customer order records"

  Column dbo.products.id:
    MS_Description = "Surrogate primary key"

  Column dbo.products.name:
    MS_Description    = "Display name of the product"
    SensitivityLabel  = "Public"

  Column dbo.products.price:
    MS_Description = "Unit price in USD"

  Column sales.orders.id:
    MS_Description = "Order surrogate key"

  Column sales.orders.product_id:
    MS_Description = "FK to dbo.products.id"

## Exported constants (imported by the coverage test)

  - ``DB_NAME``
  - ``TABLE_PRODUCTS``, ``TABLE_ORDERS``, ``TABLE_SIMPLE``
  - ``EXPECTED_TABLE_PROPS`` — dict[table_name, dict[prop_name, str]]
  - ``EXPECTED_COL_PROPS``   — dict[(table_name, col_name), dict[prop_name, str]]
  - ``EXPECTED_SCHEMA_PROPS`` — dict[schema_name, dict[prop_name, str]]

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run extended-properties
    python -m tools.fixture_run all-versions --suite extended-properties

Direct:
    python -m tools.make_extended_properties_fixture
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    skip_if_exists,
)

DB_NAME = "ExtendedProperties"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "extended_properties_full.bak"

TABLE_PRODUCTS = "products"
TABLE_ORDERS = "orders"
TABLE_SIMPLE = "simple"

# Ground-truth: what the reader should extract after calling recover_extended_properties.
EXPECTED_SCHEMA_PROPS: dict[str, dict[str, str]] = {
    "sales": {"MS_Description": "Sales data schema"},
}

EXPECTED_TABLE_PROPS: dict[str, dict[str, str]] = {
    "dbo.products": {
        "MS_Description": "Product catalogue",
        "Owner": "commerce-team",
    },
    "sales.orders": {
        "MS_Description": "Customer order records",
    },
}

EXPECTED_COL_PROPS: dict[tuple[str, str], dict[str, str]] = {
    ("dbo.products", "id"):         {"MS_Description": "Surrogate primary key"},
    ("dbo.products", "name"):       {"MS_Description": "Display name of the product",
                                     "SensitivityLabel": "Public"},
    ("dbo.products", "price"):      {"MS_Description": "Unit price in USD"},
    ("sales.orders", "id"):         {"MS_Description": "Order surrogate key"},
    ("sales.orders", "product_id"): {"MS_Description": "FK to dbo.products.id"},
}


def _addprop(
    name: str,
    value: str,
    *,
    level0type: str,
    level0name: str,
    level1type: str | None = None,
    level1name: str | None = None,
    level2type: str | None = None,
    level2name: str | None = None,
) -> str:
    """Return a single EXEC sp_addextendedproperty statement."""
    parts = [
        f"EXEC sp_addextendedproperty",
        f"    @name  = N'{name}',",
        f"    @value = N'{value}',",
        f"    @level0type = N'{level0type}', @level0name = N'{level0name}'",
    ]
    if level1type:
        parts.append(f"    ,@level1type = N'{level1type}', @level1name = N'{level1name}'")
    if level2type:
        parts.append(f"    ,@level2type = N'{level2type}', @level2name = N'{level2name}'")
    return "\n".join(parts)


def build_stmts() -> list[str]:
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",

        # ── schemas ─────────────────────────────────────────────────────────
        "CREATE SCHEMA [sales]",

        # ── tables ──────────────────────────────────────────────────────────
        """CREATE TABLE dbo.products (
    id       INT           NOT NULL CONSTRAINT pk_products PRIMARY KEY CLUSTERED,
    name     NVARCHAR(100) NOT NULL,
    price    DECIMAL(10,2) NOT NULL
)""",

        """CREATE TABLE sales.orders (
    id         INT       NOT NULL CONSTRAINT pk_orders PRIMARY KEY CLUSTERED,
    product_id INT       NOT NULL,
    qty        INT       NOT NULL,
    ordered_at DATETIME2(0) NOT NULL
)""",

        """CREATE TABLE dbo.simple (
    id INT NOT NULL CONSTRAINT pk_simple PRIMARY KEY CLUSTERED
)""",

        # ── seed rows ────────────────────────────────────────────────────────
        """INSERT INTO dbo.products (id, name, price) VALUES
    (1, N'Widget Alpha',  9.99),
    (2, N'Gadget Beta',  19.99),
    (3, N'Doohickey Gamma', 4.49)""",

        """INSERT INTO sales.orders (id, product_id, qty, ordered_at) VALUES
    (1, 1, 5, '2024-01-10 09:00:00'),
    (2, 2, 2, '2024-01-11 14:30:00'),
    (3, 1, 1, '2024-01-12 07:45:00')""",

        "INSERT INTO dbo.simple (id) VALUES (1), (2)",

        # ── schema-level extended properties ─────────────────────────────────
        _addprop(
            "MS_Description", "Sales data schema",
            level0type="SCHEMA", level0name="sales",
        ),

        # ── table-level extended properties ──────────────────────────────────
        _addprop(
            "MS_Description", "Product catalogue",
            level0type="SCHEMA", level0name="dbo",
            level1type="TABLE",  level1name="products",
        ),
        _addprop(
            "Owner", "commerce-team",
            level0type="SCHEMA", level0name="dbo",
            level1type="TABLE",  level1name="products",
        ),
        _addprop(
            "MS_Description", "Customer order records",
            level0type="SCHEMA", level0name="sales",
            level1type="TABLE",  level1name="orders",
        ),

        # ── column-level extended properties: dbo.products ───────────────────
        _addprop(
            "MS_Description", "Surrogate primary key",
            level0type="SCHEMA", level0name="dbo",
            level1type="TABLE",  level1name="products",
            level2type="COLUMN", level2name="id",
        ),
        _addprop(
            "MS_Description", "Display name of the product",
            level0type="SCHEMA", level0name="dbo",
            level1type="TABLE",  level1name="products",
            level2type="COLUMN", level2name="name",
        ),
        _addprop(
            "SensitivityLabel", "Public",
            level0type="SCHEMA", level0name="dbo",
            level1type="TABLE",  level1name="products",
            level2type="COLUMN", level2name="name",
        ),
        _addprop(
            "MS_Description", "Unit price in USD",
            level0type="SCHEMA", level0name="dbo",
            level1type="TABLE",  level1name="products",
            level2type="COLUMN", level2name="price",
        ),

        # ── column-level extended properties: sales.orders ───────────────────
        _addprop(
            "MS_Description", "Order surrogate key",
            level0type="SCHEMA", level0name="sales",
            level1type="TABLE",  level1name="orders",
            level2type="COLUMN", level2name="id",
        ),
        _addprop(
            "MS_Description", "FK to dbo.products.id",
            level0type="SCHEMA", level0name="sales",
            level1type="TABLE",  level1name="orders",
            level2type="COLUMN", level2name="product_id",
        ),

        # ── backup ───────────────────────────────────────────────────────────
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print("building extended_properties_full.bak …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
