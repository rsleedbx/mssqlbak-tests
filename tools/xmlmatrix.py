"""XML-coverage matrix — feature-isolating xml documents for binary-XML RE.

SQL Server stores an ``xml`` column as a tokenised binary blob, not text.  Each
row below isolates one XML construct so the on-disk token grammar can be
reverse-engineered and the decoder validated against a known-good document.

The ``expected`` text is what ``CAST(col AS nvarchar(max))`` returns from the
engine (the canonical serialisation), so the parser's ``decode_xml`` output can
be asserted equal to it.  Use ``--dump`` to print the engine's serialisation per
row (requires a live container) when adding cases.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB_NAME = "XmlCoverage"

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))
OUT_PATH = FIXTURE_DIR / "xmlcoverage_full.bak"


@dataclass(frozen=True)
class XmlCase:
    name: str
    doc: str  # the literal inserted into the xml column
    expected: str  # the engine's canonical serialisation (decode_xml must match)


# Each case isolates one construct.  ``doc`` is the inserted literal; ``expected``
# is the engine's canonical serialisation (``CAST(doc AS nvarchar(max))``), which
# the parser's decode_xml must reproduce.  Re-capture with ``--dump`` if changed.
CASES: list[XmlCase] = [
    XmlCase("empty", "<a/>", "<a/>"),
    XmlCase("text", "<a>hello</a>", "<a>hello</a>"),
    XmlCase("attr", '<a b="1"/>', '<a b="1"/>'),
    XmlCase("attr_multi", '<a x="1" y="2">t</a>', '<a x="1" y="2">t</a>'),
    XmlCase("nested", "<a><b/><c/></a>", "<a><b/><c/></a>"),
    XmlCase("nested_text", "<r><a>1</a><a>2</a></r>", "<r><a>1</a><a>2</a></r>"),
    XmlCase("escaping", "<a>x &amp; y &lt; z</a>", "<a>x &amp; y &lt; z</a>"),
    XmlCase("cdata", "<a><![CDATA[x<y&z]]></a>", "<a>x&lt;y&amp;z</a>"),
    XmlCase("comment", "<r><!-- note --><a/></r>", "<r><!-- note --><a/></r>"),
    XmlCase("pi", '<r><?style type="text/xsl"?><a/></r>',
           '<r><?style type="text/xsl"?><a/></r>'),
    XmlCase("ns_default", '<a xmlns="urn:demo"><b/></a>', '<a xmlns="urn:demo"><b/></a>'),
    XmlCase("ns_prefix", '<p:a xmlns:p="urn:demo"><p:b/></p:a>',
           '<p:a xmlns:p="urn:demo"><p:b/></p:a>'),
    # 300-child document whose binary XML encoding exceeds the 8 KB in-row
    # threshold, so SQL Server stores it as a LOB chain.  Verifies that
    # _stitch_lob reassembles all fragments before decode_xml is called.
    # Item content uses a 32-char 'x' prefix ("x" * 32 + str(i)) to pad each
    # element beyond a single page so the LOB chain spans multiple chunks.
    XmlCase(
        "large_lob",
        "<root>" + "".join(f'<item id="{i}">{"x" * 32}{i}</item>' for i in range(1, 301)) + "</root>",
        "<root>" + "".join(f'<item id="{i}">{"x" * 32}{i}</item>' for i in range(1, 301)) + "</root>",
    ),
]


def build_sql() -> str:
    parts = [
        "USE [master];",
        "GO",
        f"IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN "
        f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
        f"DROP DATABASE [{DB_NAME}]; END;",
        "GO",
        f"CREATE DATABASE [{DB_NAME}];",
        "GO",
        f"USE [{DB_NAME}];",
        "GO",
        "CREATE TABLE [xmlcov] (id int NOT NULL PRIMARY KEY CLUSTERED, "
        "name nvarchar(20) NOT NULL, doc xml NULL);",
        "GO",
    ]
    for i, case in enumerate(CASES, start=1):
        literal = case.doc.replace("'", "''")
        parts.append(
            f"INSERT INTO [xmlcov] (id, name, doc) "
            f"VALUES ({i}, N'{case.name}', CAST(N'{literal}' AS xml));"
        )
    parts.append("GO")
    return "\n".join(parts) + "\n"


def _dump_expected() -> int:
    """Print the engine's canonical serialisation for each case (RE aid)."""
    from tools.make_fixture import discover_container, sqlcmd_base
    import os
    import subprocess

    container = discover_container()
    base = sqlcmd_base(os.environ.get("FIXTURE_DBA_USER", "sa"),
                       os.environ["FIXTURE_DBA_PASSWORD"], container)
    q = (f"SET NOCOUNT ON; USE [{DB_NAME}]; "
         "SELECT id, name, CAST(doc AS nvarchar(max)) FROM xmlcov ORDER BY id;")
    cmd = ["podman", "exec", container, *base, "-h", "-1", "-W", "-s", "|", "-Q", q]
    print(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
    return 0


def main() -> int:
    if "--dump" in sys.argv:
        return _dump_expected()
    from tools.make_fixture import generate_fixture

    return generate_fixture(DB_NAME, build_sql(), OUT_PATH)


if __name__ == "__main__":
    sys.exit(main())
