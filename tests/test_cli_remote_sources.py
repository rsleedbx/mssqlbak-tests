from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import ClassVar

import pytest
from typer.testing import CliRunner

from mssqlbak._cli import app

_FIXTURE_DIR = Path(__file__).parent / "fixtures_2022"
_COMPRESSED = _FIXTURE_DIR / "typecoverage_full_compressed.bak"


class _RangeHandler(BaseHTTPRequestHandler):
    payload: ClassVar[bytes]

    def do_GET(self) -> None:  # noqa: N802
        data = type(self).payload
        range_header = self.headers.get("Range")
        if range_header:
            start_s, end_s = range_header.removeprefix("bytes=").split("-", 1)
            start = int(start_s)
            end = int(end_s)
            chunk = data[start : end + 1]
            self.send_response(206)
            self.send_header("Content-Length", str(len(chunk)))
            self.send_header("Content-Range", f"bytes {start}-{end}/{len(data)}")
            self.end_headers()
            self.wfile.write(chunk)
            return
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        return


@pytest.fixture
def compressed_http_url():
    if not _COMPRESSED.exists():
        pytest.skip(f"missing compressed fixture: {_COMPRESSED}")
    handler = type(
        "CompressedRangeHandler", (_RangeHandler,), {"payload": _COMPRESSED.read_bytes()}
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host = server.server_address[0]
    port = server.server_address[1]
    try:
        yield f"http://{host}:{port}/{_COMPRESSED.name}"
    finally:
        server.shutdown()
        server.server_close()


def test_cli_info_accepts_http_bak(compressed_http_url: str) -> None:
    result = CliRunner().invoke(app, ["info", compressed_http_url])

    assert result.exit_code == 0, result.output
    assert "Database" in result.output
    assert "TypeCoverage" in result.output


def test_cli_inspect_accepts_http_bak(compressed_http_url: str) -> None:
    result = CliRunner().invoke(app, ["inspect", compressed_http_url])

    assert result.exit_code == 0, result.output
    assert "objects:" in result.output
    assert "table extractability:" in result.output
