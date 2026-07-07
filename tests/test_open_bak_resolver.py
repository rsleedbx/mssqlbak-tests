from __future__ import annotations

from pathlib import Path

import pytest


def test_parse_bak_uri_recognizes_local_path() -> None:
    from mssqlbak.readers import parse_bak_uri

    parsed = parse_bak_uri("tests/fixtures_2022/typecoverage_full.bak")
    assert parsed.scheme == "file"
    assert parsed.path == "tests/fixtures_2022/typecoverage_full.bak"


def test_open_bak_routes_file_to_local_reader(tmp_path: Path) -> None:
    from mssqlbak.bak_io import LocalBakReader
    from mssqlbak.readers import open_bak

    bak = tmp_path / "local.bak"
    bak.write_bytes(b"local backup bytes")
    reader = open_bak(str(bak))
    try:
        assert isinstance(reader, LocalBakReader)
        assert reader.read_at(0, 5) == b"local"
    finally:
        reader.close()


def test_open_bak_routes_s3(monkeypatch: pytest.MonkeyPatch) -> None:
    from mssqlbak import readers

    seen: dict[str, object] = {}

    class FakeS3:
        def __init__(self, bucket: str, key: str, *, region: str | None = None) -> None:
            seen.update(bucket=bucket, key=key, region=region)

    monkeypatch.setattr(readers, "S3BakReader", FakeS3)

    assert readers.open_bak("s3://my-bucket/path/to/db.bak", region="us-west-2") is not None
    assert seen == {"bucket": "my-bucket", "key": "path/to/db.bak", "region": "us-west-2"}


def test_open_bak_routes_gcs(monkeypatch: pytest.MonkeyPatch) -> None:
    from mssqlbak import readers

    seen: dict[str, object] = {}

    class FakeGCS:
        def __init__(self, bucket: str, blob_name: str) -> None:
            seen.update(bucket=bucket, blob_name=blob_name)

    monkeypatch.setattr(readers, "GCSBakReader", FakeGCS)

    assert readers.open_bak("gs://my-bucket/path/to/db.bak") is not None
    assert seen == {"bucket": "my-bucket", "blob_name": "path/to/db.bak"}


def test_open_bak_routes_http(monkeypatch: pytest.MonkeyPatch) -> None:
    from mssqlbak import readers

    seen: dict[str, object] = {}

    class FakeHTTP:
        def __init__(self, url: str, **kwargs: object) -> None:
            seen.update(url=url, kwargs=kwargs)

    monkeypatch.setattr(readers, "HTTPBakReader", FakeHTTP)

    assert readers.open_bak("github://owner/repo/db.bak", token="tok") is not None
    assert seen == {"url": "github://owner/repo/db.bak", "kwargs": {"token": "tok"}}


def test_open_bak_rejects_unknown_scheme() -> None:
    from mssqlbak.readers import open_bak

    with pytest.raises(ValueError, match="Unsupported .bak URI scheme"):
        open_bak("ftp://example.com/db.bak")
