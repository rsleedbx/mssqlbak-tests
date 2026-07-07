#!/usr/bin/env python3
"""Generate ``typed_xml_full.bak`` — XML schema collection typed XML cells."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.cell_canon import canon, column_digest  # noqa: E402
from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    skip_if_exists,
)

DB_NAME = "TypedXmlCells"
TABLE = "typed_xml_docs"

EXPECTED_XML: dict[int, str] = {
    1: '<event id="1" kind="database"><message>create table</message><severity>10</severity></event>',
    2: '<event id="2" kind="resume"><message>candidate profile</message><severity>20</severity></event>',
    3: '<event id="3" kind="store"><message>demographics update</message><severity>30</severity></event>',
    4: '<event id="4" kind="empty"><message>empty element</message><severity>40</severity><empty></empty></event>',
    5: '<event id="5" kind="cr"><message>line1&#x0D;\nline2</message><severity>50</severity><note>cr</note></event>',
    6: '<event id="6" kind="numeric"><message>store</message><severity>60</severity><squareFeet>21000.0</squareFeet></event>',
    7: '<event id="7" kind="entity"><message>entity</message><severity>70</severity><bank>Primary Bank &amp; Reserve</bank></event>',
    8: '<event id="8" kind="typed"><message>typed atoms</message><severity>80</severity><asBoolean>true</asBoolean><asDecimal>3.1400</asDecimal></event>',
}
EXPECTED_SNIPPETS: dict[int, tuple[str, ...]] = {
    1: ('id="1"', "<message>", "<severity>"),
    2: ('id="2"', "<message>", "<severity>"),
    3: ('id="3"', "<message>", "<severity>"),
    4: ('id="4"', "<empty"),
    5: ('id="5"', "line1", "line2"),
    6: ('id="6"', "<squareFeet>21000</squareFeet>"),
    7: ('id="7"', "Primary Bank", "Reserve"),
    8: ('id="8"', "<asBoolean>true</asBoolean>", "<asDecimal>3.14</asDecimal>"),
}
EXPECTED_DIGEST = column_digest(canon(xml, "xml") for xml in EXPECTED_XML.values())
ROW_COUNT = len(EXPECTED_XML)

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "typed_xml_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"

_XSD = """<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <xsd:element name="event">
    <xsd:complexType>
      <xsd:sequence>
        <xsd:element name="message" type="xsd:string" />
        <xsd:element name="severity" type="xsd:int" />
        <xsd:element name="empty" type="xsd:string" minOccurs="0" />
        <xsd:element name="note" type="xsd:string" minOccurs="0" />
        <xsd:element name="squareFeet" type="xsd:decimal" minOccurs="0" />
        <xsd:element name="bank" type="xsd:string" minOccurs="0" />
        <xsd:element name="asBoolean" type="xsd:boolean" minOccurs="0" />
        <xsd:element name="asDecimal" type="xsd:decimal" minOccurs="0" />
      </xsd:sequence>
      <xsd:attribute name="id" type="xsd:int" use="required" />
      <xsd:attribute name="kind" type="xsd:string" use="required" />
    </xsd:complexType>
  </xsd:element>
</xsd:schema>"""


def build_stmts() -> list[str]:
    rows = ",\n    ".join(
        f"({row_id}, CAST({_str_sql(xml)} AS XML(dbo.TypedCellSchema)))"
        for row_id, xml in EXPECTED_XML.items()
    )
    return [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        f"CREATE XML SCHEMA COLLECTION dbo.TypedCellSchema AS {_str_sql(_XSD)}",
        f"""CREATE TABLE dbo.{TABLE} (
    id  INT NOT NULL PRIMARY KEY CLUSTERED,
    doc XML(dbo.TypedCellSchema) NOT NULL
)""",
        f"""INSERT INTO dbo.{TABLE} (id, doc) VALUES
    {rows}""",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]


def _str_sql(value: str) -> str:
    return "N'" + value.replace("'", "''") + "'"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"inserting {ROW_COUNT} typed XML rows")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
