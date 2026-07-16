"""Local HTTP server that simulates GitHub release CDN download flow."""

from __future__ import annotations

import errno
import functools
import http.server
import os
import re
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

_CDN_PREFIX = "/_cdn"
_RANGE_RE = re.compile(r"^bytes=(\d+)-(\d*)$")

# macOS exhausts the per-socket send buffer (ENOBUFS) under many concurrent
# per-chunk Range GETs.  Retry the write a bounded number of times with a short
# backoff before giving up on the response (the client retries the Range GET).
_ENOBUFS_MAX_RETRIES = 100
_ENOBUFS_BACKOFF_S = 0.005


class _RangeCDNHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that simulates GitHub release -> CDN download flow.

    Two-stage design mirrors real GitHub HTTPS behaviour:

    * ``GET /<name>.bak`` (no leading ``/_cdn``) → ``302 Location: /_cdn/<name>.bak``
      (mirrors ``github.com/.../releases/download/...`` → ``objects.githubusercontent.com``).

    * ``GET /_cdn/<name>.bak`` → serves the file with ``206 Partial Content`` and
      ``Content-Range`` when the request carries a ``Range: bytes=…`` header.
      Falls back to ``200`` full-body when there is no ``Range`` header, preserving
      the existing spool path as a safety net.

    This causes :class:`~mssqlbak.readers.http.HTTPBakReader` to:
    1. Follow the redirect during ``_probe`` (``_request_range_following_redirects``).
    2. Receive a ``206`` response and parse ``Content-Range`` for the file size.
    3. Set ``_is_range_reader = True`` and issue per-chunk ``Range`` GETs for all
       subsequent ``read_at`` calls → exercises ``LazyPageStore`` + ``warm_file``.
    """

    def log_message(self, *_: object) -> None:  # silence request logs
        pass

    def _safe_write(self, chunk: bytes) -> bool:
        """Write *chunk* to the client, tolerating transient socket errors.

        Returns ``True`` on success.  On ``ENOBUFS`` (macOS send-buffer
        exhaustion under concurrent Range GETs) it retries with a short backoff.
        On a dropped connection (``EPIPE`` / ``ECONNRESET`` / broken pipe) it
        returns ``False`` so the caller aborts the response quietly; the client
        (:class:`~mssqlbak.readers.http.HTTPBakReader`) retries the Range GET.
        """
        for _attempt in range(_ENOBUFS_MAX_RETRIES):
            try:
                self.wfile.write(chunk)
                return True
            except OSError as exc:
                if exc.errno == errno.ENOBUFS:
                    time.sleep(_ENOBUFS_BACKOFF_S)
                    continue
                # EPIPE / ECONNRESET / other: client went away — abort quietly.
                return False
        return False

    def do_GET(self) -> None:  # noqa: N802
        # ── redirect leg: /<name>.bak → /_cdn/<name>.bak ───────────────────
        if not self.path.startswith(_CDN_PREFIX + "/"):
            self.send_response(302)
            self.send_header("Location", _CDN_PREFIX + self.path)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        # ── CDN leg: serve the file, honouring Range if present ─────────────
        # Translate /_cdn/<name> back to <root>/<name> via the parent method.
        # Temporarily strip the prefix so translate_path resolves correctly.
        orig_path = self.path
        self.path = self.path[len(_CDN_PREFIX) :]
        fs_path = self.translate_path(self.path)
        self.path = orig_path  # restore (not strictly needed, but tidy)

        try:
            file_size = os.path.getsize(fs_path)
        except OSError:
            self.send_error(404)
            return

        range_header = self.headers.get("Range", "")
        m = _RANGE_RE.match(range_header.strip())
        if m:
            start = int(m.group(1))
            end = int(m.group(2)) if m.group(2) else file_size - 1
            end = min(end, file_size - 1)
            length = end - start + 1
            if start > end or start >= file_size:
                self.send_error(416, "Range Not Satisfiable")
                return
            self.send_response(206)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            with open(fs_path, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(65536, remaining))
                    if not chunk:
                        break
                    if not self._safe_write(chunk):
                        return
                    remaining -= len(chunk)
        else:
            # No Range header → full 200 response (fallback / spool path).
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            with open(fs_path, "rb") as f:
                while chunk := f.read(65536):
                    if not self._safe_write(chunk):
                        return


class _QuietThreadingHTTPServer(http.server.ThreadingHTTPServer):
    """ThreadingHTTPServer that does not dump a traceback for expected socket errors.

    Under heavy concurrent Range GETs the client may drop a connection or the OS
    may exhaust send buffers (``ENOBUFS``); these surface as ``OSError`` and are
    handled/retried in :meth:`_RangeCDNHandler._safe_write`.  Any that still
    escape are benign, so suppress the noisy stack trace the default
    ``handle_error`` would print.
    """

    def handle_error(self, request: object, client_address: object) -> None:
        exc = sys.exc_info()[1]
        if isinstance(exc, OSError):
            return
        super().handle_error(request, client_address)  # type: ignore[arg-type]


@contextmanager
def _local_http_server(directory: Path) -> Generator[int, None, None]:
    """Spin up a local HTTP server rooted at *directory* and yield its port.

    Uses an ephemeral port (OS chooses) so multiple concurrent runs never
    conflict.  The server runs in a daemon thread and is shut down cleanly
    when the context exits.

    The server uses :class:`_RangeCDNHandler` which simulates GitHub HTTPS:
    a ``302`` redirect hop followed by ``206`` Range responses.  This causes
    :class:`~mssqlbak.readers.http.HTTPBakReader` to set
    ``_is_range_reader = True`` and exercise the ``LazyPageStore`` +
    ``warm_file`` path instead of spooling the whole file.

    Uses :class:`~http.server.ThreadingHTTPServer` (thread-per-connection) so
    concurrent worker processes and many per-chunk Range GETs never serialise.
    """
    handler = functools.partial(_RangeCDNHandler, directory=str(directory))
    with _QuietThreadingHTTPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            yield port
        finally:
            httpd.shutdown()
