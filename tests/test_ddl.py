# tests/test_ddl.py
from __future__ import annotations
import dataclasses
import pytest
import mssqlbak.types as t
from mssqlbak.catalog import (
    CatalogObjects, Column, Constraint, ForeignKey, Index, Schema, Table,
    INDEX_CLUSTERED, INDEX_NONCLUSTERED,
)
from mssqlbak.ddl import col_sql_type, emit_create_index, emit_create_table, emit_schema


def _col(type_id: int, max_length: int = 0, precision: int = 0, scale: int = 0,
         user_type_id: int = 0) -> Column:
    return Column(
        name="x", colid=1, type_id=type_id, max_length=max_length,
        precision=precision, scale=scale, nullable=True, leaf_offset=-1,
        is_variable=False, user_type_id=user_type_id,
    )


@pytest.mark.parametrize("col, expected", [
    (_col(t.INT),                           "INT"),
    (_col(t.BIGINT),                        "BIGINT"),
    (_col(t.SMALLINT),                      "SMALLINT"),
    (_col(t.TINYINT),                       "TINYINT"),
    (_col(t.BIT),                           "BIT"),
    (_col(t.MONEY),                         "MONEY"),
    (_col(t.SMALLMONEY),                    "SMALLMONEY"),
    (_col(t.REAL),                          "REAL"),
    (_col(t.FLOAT),                         "FLOAT"),
    (_col(t.DATE),                          "DATE"),
    (_col(t.SMALLDATETIME),                 "SMALLDATETIME"),
    (_col(t.DATETIME),                      "DATETIME"),
    (_col(t.DATETIME2, scale=7),            "DATETIME2(7)"),
    (_col(t.DATETIMEOFFSET, scale=3),       "DATETIMEOFFSET(3)"),
    (_col(t.TIME, scale=0),                 "TIME(0)"),
    (_col(t.UNIQUEIDENTIFIER),              "UNIQUEIDENTIFIER"),
    (_col(t.ROWVERSION),                    "ROWVERSION"),
    (_col(t.DECIMAL, precision=10, scale=2), "DECIMAL(10,2)"),
    (_col(t.NUMERIC, precision=18, scale=4), "NUMERIC(18,4)"),
    (_col(t.CHAR, max_length=10),           "CHAR(10)"),
    (_col(t.VARCHAR, max_length=50),        "VARCHAR(50)"),
    (_col(t.VARCHAR, max_length=-1),        "VARCHAR(MAX)"),
    (_col(t.NCHAR, max_length=20),          "NCHAR(10)"),
    (_col(t.NVARCHAR, max_length=200),      "NVARCHAR(100)"),
    (_col(t.NVARCHAR, max_length=-1),       "NVARCHAR(MAX)"),
    (_col(t.BINARY, max_length=16),         "BINARY(16)"),
    (_col(t.VARBINARY, max_length=100),     "VARBINARY(100)"),
    (_col(t.VARBINARY, max_length=-1),      "VARBINARY(MAX)"),
    (_col(t.IMAGE),                         "IMAGE"),
    (_col(t.TEXT),                          "TEXT"),
    (_col(t.NTEXT),                         "NTEXT"),
    (_col(t.XML),                           "XML"),
    (_col(t.SQL_VARIANT),                   "SQL_VARIANT"),
    (_col(t.NATIVE_JSON),                   "JSON"),
    (_col(t.CLR_UDT, user_type_id=t.UT_HIERARCHYID), "HIERARCHYID"),
    (_col(t.CLR_UDT, user_type_id=t.UT_GEOMETRY),    "GEOMETRY"),
    (_col(t.CLR_UDT, user_type_id=t.UT_GEOGRAPHY),   "GEOGRAPHY"),
])
def test_col_sql_type(col: Column, expected: str) -> None:
    assert col_sql_type(col) == expected


def _make_table(name: str, cols: list[Column], schema: str = "dbo") -> Table:
    return Table(name=name, object_id=1, schema=schema, columns=cols)


def _make_col(name: str, type_id: int, **kw) -> Column:
    return Column(
        name=name, colid=kw.get("colid", 1), type_id=type_id,
        max_length=kw.get("max_length", 0), precision=kw.get("precision", 0),
        scale=kw.get("scale", 0), nullable=kw.get("nullable", True),
        leaf_offset=kw.get("leaf_offset", -1), is_variable=False,
        identity_seed=kw.get("identity_seed"), identity_increment=kw.get("identity_increment"),
    )


def test_emit_create_table_simple() -> None:
    cols = [
        _make_col("id", t.INT, colid=1, nullable=False, identity_seed=1, identity_increment=1),
        _make_col("name", t.NVARCHAR, colid=2, max_length=200, nullable=True),
    ]
    tbl = _make_table("Person", cols)
    pk = Index(object_id=1, index_id=1, index_type=INDEX_CLUSTERED,
               name="PK_Person", is_primary_key=True, is_unique=True,
               is_unique_constraint=False, key_columns=[1])
    sql = emit_create_table(tbl, [pk], [], [], {}, {})
    assert "CREATE TABLE [dbo].[Person]" in sql
    assert "[id] INT IDENTITY(1,1) NOT NULL" in sql
    assert "[name] NVARCHAR(100) NULL" in sql
    assert "CONSTRAINT [PK_Person] PRIMARY KEY CLUSTERED ([id] ASC)" in sql


def test_emit_create_table_check_and_default() -> None:
    cols = [
        _make_col("id", t.INT, colid=1, nullable=False),
        _make_col("code", t.INT, colid=2, nullable=False),
        _make_col("label", t.VARCHAR, colid=3, max_length=50, nullable=True),
    ]
    tbl = _make_table("T", cols)
    ck = Constraint(object_id=10, parent_object_id=1, type_code="C",
                    kind="check", name="ck_code", definition="([code]>(0))")
    df = Constraint(object_id=11, parent_object_id=1, type_code="D",
                    kind="default", name="df_label", definition="('n/a')")
    cols[2] = dataclasses.replace(cols[2], default_object_id=11)
    tbl = _make_table("T", cols)
    sql = emit_create_table(tbl, [], [ck, df], [], {}, {})
    assert "CONSTRAINT [ck_code] CHECK ([code]>(0))" in sql
    assert "CONSTRAINT [df_label] DEFAULT ('n/a') FOR [label]" in sql


def test_emit_create_table_foreign_key() -> None:
    cols = [
        _make_col("id", t.INT, colid=1, nullable=False),
        _make_col("ref_id", t.INT, colid=2, nullable=True),
    ]
    tbl = _make_table("Child", cols)
    fk = ForeignKey(constraint_id=20, name="fk_ref", parent_object_id=1,
                    child_col_ids=[2], ref_object_id=99, ref_col_ids=[1])
    ref_cols = [_make_col("id", t.INT, colid=1)]
    obj_to_table = {99: Table(name="Parent", object_id=99, schema="dbo", columns=ref_cols)}
    sql = emit_create_table(tbl, [], [], [fk], {1: 1, 2: 2}, obj_to_table)
    assert "CONSTRAINT [fk_ref] FOREIGN KEY ([ref_id]) REFERENCES [dbo].[Parent] ([id])" in sql


def test_emit_create_index() -> None:
    cols = [
        _make_col("id", t.INT, colid=1),
        _make_col("code", t.INT, colid=2),
    ]
    tbl = _make_table("T", cols)
    nci = Index(object_id=1, index_id=2, index_type=INDEX_NONCLUSTERED,
                name="ix_code", is_primary_key=False, is_unique=False,
                is_unique_constraint=False, key_columns=[2])
    sql = emit_create_index(nci, tbl, {1: 1, 2: 2})
    assert "CREATE NONCLUSTERED INDEX [ix_code] ON [dbo].[T] ([code] ASC)" in sql


def test_emit_schema_contains_create_table() -> None:
    cols = [_make_col("id", t.INT, nullable=False, identity_seed=1, identity_increment=1)]
    tbl = _make_table("Foo", cols)
    schema = Schema(tables=[tbl])
    catalog = CatalogObjects()
    sql = emit_schema(schema, catalog, [], {})
    assert "CREATE TABLE [dbo].[Foo]" in sql
