from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import ClassVar

import pytest


class _RangeHandler(BaseHTTPRequestHandler):
    payload: ClassVar[bytes] = b""
    honor_range: ClassVar[bool] = True

    def do_GET(self) -> None:  # noqa: N802
        data = type(self).payload
        if type(self).honor_range and (range_header := self.headers.get("Range")):
            prefix = "bytes="
            assert range_header.startswith(prefix)
            start_s, end_s = range_header[len(prefix) :].split("-", 1)
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
def http_server(tmp_path: Path):
    servers: list[ThreadingHTTPServer] = []

    def serve(payload: bytes, *, honor_range: bool = True) -> str:
        handler = type(
            f"RangeHandler_{len(servers)}",
            (_RangeHandler,),
            {"payload": payload, "honor_range": honor_range},
        )
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        servers.append(server)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host = server.server_address[0]
        port = server.server_address[1]
        return f"http://{host}:{port}/fixture.bak"

    try:
        yield serve
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()


def test_http_bak_reader_range_reads_match_payload(http_server) -> None:
    from mssqlbak.readers.http import HTTPBakReader

    payload = bytes(range(251)) * 20
    with HTTPBakReader(http_server(payload)) as reader:
        assert reader.size == len(payload)
        assert reader.read_at(0, 8) == payload[:8]
        assert reader.read_at(128, 33) == payload[128:161]


def test_http_bak_reader_spools_when_server_ignores_range(http_server) -> None:
    from mssqlbak.readers.http import HTTPBakReader

    payload = b"abc123" * 1024
    with HTTPBakReader(http_server(payload, honor_range=False)) as reader:
        assert reader.size == len(payload)
        assert reader.read_at(12, 9) == payload[12:21]


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        (
            "github://owner/repo/path/to/db.bak",
            "https://raw.githubusercontent.com/owner/repo/HEAD/path/to/db.bak",
        ),
        (
            "github://owner/repo@main/path/to/db.bak",
            "https://raw.githubusercontent.com/owner/repo/main/path/to/db.bak",
        ),
        (
            "https://github.com/owner/repo/blob/main/path/to/db.bak",
            "https://raw.githubusercontent.com/owner/repo/main/path/to/db.bak",
        ),
        (
            "https://github.com/owner/repo/raw/main/path/to/db.bak",
            "https://raw.githubusercontent.com/owner/repo/main/path/to/db.bak",
        ),
    ],
)
def test_normalize_github_url(src: str, expected: str) -> None:
    from mssqlbak.readers.http import normalize_http_bak_url

    assert normalize_http_bak_url(src) == expected
