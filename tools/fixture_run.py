#!/usr/bin/env python3
"""Run fixture generators with forgedb credentials pre-loaded.

Resolves ``FIXTURE_DBA_PASSWORD`` from the forgedb keyring (via the forgedb2
venv) and ``FIXTURE_CONTAINER`` from the conn blob, then invokes the target
generator.  Use this instead of hand-exporting secrets on every run::

    python -m tools.fixture_run make_fixture
    python -m tools.fixture_run compressionmatrix
    python -m tools.fixture_run layout
    python -m tools.fixture_run layout --compressed
    python -m tools.fixture_run catalog --engine 2022
    python -m tools.fixture_run version-matrix --engine 2022
    python -m tools.fixture_run aborted-xact

Override discovery with ``FIXTURE_SERVER_NAME`` (forgedb blob stem, e.g.
``robert-lee-mssql-local-1779207800``) or ``FIXTURE_CONTAINER`` (podman name).

Print shell exports only (for manual ``source``)::

    eval "$(python -m tools.fixture_run env)"
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MSSQL_IMAGE_MATCH = "mssql/server"
FORGEDB_SCOPE = "forgedb"


def _forgedb_python() -> Path:
    override = os.environ.get("FORGEDB_PYTHON")
    if override:
        return Path(override)
    candidates = [
        Path.home() / "github" / "forgedb2" / ".venv" / "bin" / "python",
        REPO_ROOT.parent / "forgedb2" / ".venv" / "bin" / "python",
    ]
    for path in candidates:
        if path.is_file():
            return path
    raise RuntimeError(
        "forgedb venv python not found; set FORGEDB_PYTHON to the forgedb2 "
        ".venv/bin/python path (keyring credentials live there)"
    )


def _secrets_dir(scope: str = FORGEDB_SCOPE) -> Path:
    home = Path(os.environ.get("FORGEDB_HOME", Path.home() / ".forgedb2"))
    return home / "secrets" / scope


def _running_mssql_containers() -> list[str]:
    proc = subprocess.run(
        ["podman", "ps", "--format", "{{.Names}}\t{{.Image}}"],
        text=True,
        capture_output=True,
        check=True,
    )
    return [
        line.split("\t", 1)[0] for line in proc.stdout.splitlines() if MSSQL_IMAGE_MATCH in line
    ]


def _blob_for_container(container: str, scope: str = FORGEDB_SCOPE) -> dict | None:
    for path in sorted(_secrets_dir(scope).glob("*.json")):
        if path.name.endswith(".meta.json"):
            continue
        try:
            blob = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if blob.get("podman_container") == container:
            return blob
    return None


def discover_server_name() -> str:
    """Return forgedb blob stem for the target SQL Server instance.

    When multiple SQL Server containers are running and ``FIXTURE_SERVER_NAME``
    is not set, the function tries to narrow down the choice using the version
    year embedded in ``FIXTURE_DIR`` (e.g. ``tests/fixtures_2022`` → ``2022``).
    This lets ``--fixture-dir tests/fixtures_2022`` automatically select
    ``robert-lee-mssql-2022-*`` without requiring an explicit ``--server``.
    """
    import re as _re

    if name := os.environ.get("FIXTURE_SERVER_NAME"):
        return name
    containers = _running_mssql_containers()
    if not containers:
        raise RuntimeError(
            "no running SQL Server container; provision with forgedb "
            "setup_sqlserver_podman or set FIXTURE_SERVER_NAME"
        )
    if len(containers) > 1:
        # Try to narrow by the SQL Server version year extracted from FIXTURE_DIR.
        fixture_dir = os.environ.get("FIXTURE_DIR", "")
        year_m = _re.search(r"(\d{4})", Path(fixture_dir).name)
        if year_m:
            year = year_m.group(1)
            matched = [c for c in containers if year in c]
            if len(matched) == 1:
                containers = matched
            elif len(matched) > 1:
                raise RuntimeError(
                    f"FIXTURE_DIR year {year!r} matches multiple containers {matched}; "
                    "set --server explicitly"
                )
            else:
                raise RuntimeError(
                    f"FIXTURE_DIR year {year!r} matches no running container "
                    f"(running: {containers}); set --server explicitly"
                )
        else:
            raise RuntimeError(
                f"multiple SQL Server containers {containers}; add a version year to "
                "--fixture-dir (e.g. tests/fixtures_2022) or set --server explicitly"
            )
    container = containers[0]
    blob = _blob_for_container(container)
    if blob and blob.get("server_name"):
        return str(blob["server_name"])
    if blob and blob.get("instance_id"):
        return str(blob["instance_id"])
    return Path(container).name  # last resort; password lookup may still work


def discover_container(server_name: str) -> str:
    if override := os.environ.get("FIXTURE_CONTAINER"):
        return override
    blob_path = _secrets_dir() / f"{server_name}.json"
    if blob_path.is_file():
        blob = json.loads(blob_path.read_text())
        if container := blob.get("podman_container"):
            return str(container)
    containers = _running_mssql_containers()
    if len(containers) == 1:
        return containers[0]
    raise RuntimeError(f"cannot resolve container for {server_name!r}; set FIXTURE_CONTAINER")


def dba_password(server_name: str, scope: str = FORGEDB_SCOPE) -> str:
    py = _forgedb_python()
    script = (
        "from forgedb.core.credentials import get_credentials_service\n"
        f"pw = get_credentials_service().get({scope!r}, {server_name!r}, 'dba')\n"
        "if not pw:\n"
        "    raise SystemExit('dba password not found in forgedb credentials store')\n"
        "print(pw)\n"
    )
    proc = subprocess.run(
        [str(py), "-c", script],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip() or "credential lookup failed"
        raise RuntimeError(msg)
    return proc.stdout.strip()


def _lima_podman_sock() -> str | None:
    """Return the unix socket path for the active Lima podman VM, if discoverable."""
    lima_home = Path.home() / ".lima"
    if not lima_home.is_dir():
        return None
    # Prefer the VM that is set as the default podman connection.
    try:
        import subprocess as _sp

        r = _sp.run(
            ["podman", "system", "connection", "list", "--format", "{{.Name}}\t{{.Default}}"],
            capture_output=True,
            text=True,
        )
        default_name = next(
            (line.split("\t")[0] for line in r.stdout.splitlines() if "\ttrue" in line),
            None,
        )
    except Exception:
        default_name = None

    # Walk lima VMs and look for a podman.sock whose parent dir name matches.
    for vm_dir in sorted(lima_home.iterdir()):
        sock = vm_dir / "sock" / "podman.sock"
        if sock.exists():
            if default_name and default_name in vm_dir.name:
                return str(sock)
            # Fall back to the first one we find.
            return str(sock)
    return None


def bootstrap_fixture_env() -> tuple[str, str]:
    """Set FIXTURE_* env vars; return (server_name, container)."""
    # Set CONTAINER_HOST first so all subsequent podman calls (including
    # discover_server_name → _running_mssql_containers) bypass the SSH tunnel.
    if "CONTAINER_HOST" not in os.environ:
        sock = _lima_podman_sock()
        if sock:
            os.environ["CONTAINER_HOST"] = f"unix://{sock}"
    server = discover_server_name()
    container = discover_container(server)
    password = dba_password(server)
    os.environ.setdefault("FIXTURE_DBA_USER", "sa")
    os.environ["FIXTURE_DBA_PASSWORD"] = password
    os.environ["FIXTURE_CONTAINER"] = container
    os.environ.setdefault("FIXTURE_SERVER_NAME", server)
    return server, container


def _print_env_exports() -> int:
    server, container = bootstrap_fixture_env()
    user = os.environ["FIXTURE_DBA_USER"]
    password = os.environ["FIXTURE_DBA_PASSWORD"]

    # shell-safe single-quoted exports
    def q(s: str) -> str:
        return "'" + s.replace("'", "'\"'\"'") + "'"

    print(f"export FIXTURE_SERVER_NAME={q(server)}")
    print(f"export FIXTURE_CONTAINER={q(container)}")
    print(f"export FIXTURE_DBA_USER={q(user)}")
    print(f"export FIXTURE_DBA_PASSWORD={q(password)}")
    return 0


def _run_make_fixture() -> int:
    from tools.make_fixture import main

    return main()


def _run_compressionmatrix() -> int:
    from tools.compressionmatrix import main

    return main()


def _run_layout(compressed: bool) -> int:
    from tools.make_layout_fixture import main as layout_main

    sys.argv = ["make_layout_fixture", *(["--compressed"] if compressed else [])]
    return layout_main()


def _run_catalog(engine: str, compressed: bool) -> int:
    from tools.make_catalog_fixture import main as catalog_main

    sys.argv = ["make_catalog_fixture", "--engine", engine]
    if compressed:
        sys.argv.append("--compressed")
    return catalog_main()


def _run_version_matrix(engines: list[str] | None, v1_inspect: bool) -> int:
    from tools.make_version_matrix import ENGINES, main as matrix_main

    chosen = engines or list(ENGINES)
    sys.argv = ["make_version_matrix"]
    for eng in chosen:
        sys.argv.extend(["--engine", eng])
    if v1_inspect:
        sys.argv.append("--v1-inspect")
    return matrix_main()


def _run_aborted_xact() -> int:
    from tools.make_aborted_xact_fixture import main

    return main()


def _run_stripe() -> int:
    from tools.make_stripe_fixture import main

    return main()


def _run_unicode_codepage() -> int:
    from tools.make_unicode_codepage_fixture import main

    return main()


def _run_columnstore() -> int:
    from tools.columnstore_minimal import main

    return main()


def _run_computedmatrix() -> int:
    from tools.computedmatrix import main

    return main()


def _run_constraintmatrix() -> int:
    from tools.constraintmatrix import main

    return main()


def _run_xmlmatrix() -> int:
    from tools.xmlmatrix import main

    return main()


def _run_boundary() -> int:
    from tools.make_boundary_fixture import main

    return main()


def _run_dirty() -> int:
    from tools.make_dirty_fixture import main

    return main()


def _run_dirty_v4(*, force: bool = False) -> int:
    from tools.make_dirty_v4_fixture import main

    sys.argv = ["make_dirty_v4_fixture", *(["--force"] if force else [])]
    return main()


def _run_dirty_cci(*, force: bool = False) -> int:
    from tools.make_dirty_cci_fixture import main

    sys.argv = ["make_dirty_cci_fixture", *(["--force"] if force else [])]
    return main()


def _run_incremental() -> int:
    from tools.make_incremental_fixture import main

    return main()


def _run_lob_preamble() -> int:
    from tools.make_lob_preamble_fixture import main

    return main()


def _run_tabletype(rows: int = 4) -> int:
    from tools.make_tabletype_fixture import main

    sys.argv = ["make_tabletype_fixture", "--rows", str(rows)]
    return main()


def _run_heap_scale(rows: int = 1_000) -> int:
    from tools.make_heap_scale_fixture import main

    sys.argv = ["make_heap_scale_fixture", "--rows", str(rows)]
    return main()


def _run_ndf(*, force: bool = False) -> int:
    from tools.make_ndf_fixture import main

    sys.argv = ["make_ndf_fixture", *(["--force"] if force else [])]
    return main()


def _run_feature(*, force: bool = False) -> int:
    from tools.make_feature_fixture import main

    sys.argv = ["make_feature_fixture", *(["--force"] if force else [])]
    return main()


def _run_archive_null(*, force: bool = False) -> int:
    from tools.make_archive_null_fixture import main

    sys.argv = ["make_archive_null_fixture", *(["--force"] if force else [])]
    return main()


def _run_archive_columnstore_partition(*, force: bool = False) -> int:
    from tools.make_archive_columnstore_partition_fixture import main

    sys.argv = ["make_archive_columnstore_partition_fixture", *(["--force"] if force else [])]
    return main()


def _run_archive_columnstore_types(*, force: bool = False) -> int:
    from tools.make_archive_columnstore_types_fixture import main

    sys.argv = ["make_archive_columnstore_types_fixture", *(["--force"] if force else [])]
    return main()


def _run_pfor_columnstore(*, force: bool = False) -> int:
    from tools.make_pfor_columnstore_fixture import main

    sys.argv = ["make_pfor_columnstore_fixture", *(["--force"] if force else [])]
    return main()


def _run_archive_single_chunk(*, force: bool = False) -> int:
    from tools.make_archive_single_chunk_fixture import main

    sys.argv = ["make_archive_single_chunk_fixture", *(["--force"] if force else [])]
    return main()


def _run_archive_columnstore_types_random(*, force: bool = False) -> int:
    from tools.make_archive_columnstore_types_fixture import main

    sys.argv = [
        "make_archive_columnstore_types_fixture",
        "--random",
        *(["--force"] if force else []),
    ]
    return main()


def _run_pfor_columnstore_random(*, force: bool = False) -> int:
    from tools.make_pfor_columnstore_fixture import main

    sys.argv = ["make_pfor_columnstore_fixture", "--random", *(["--force"] if force else [])]
    return main()


def _run_archive_single_chunk_random(*, force: bool = False) -> int:
    from tools.make_archive_single_chunk_fixture import main

    sys.argv = ["make_archive_single_chunk_fixture", "--random", *(["--force"] if force else [])]
    return main()


def _run_v11_probe(*, force: bool = False) -> int:
    from tools.make_v11_probe import main

    sys.argv = ["make_v11_probe", *(["--force"] if force else [])]
    return main()


def _run_g44_probe() -> int:
    from tools.make_g44_probe import main

    return main()


def _run_v13_probe(*, force: bool = False) -> int:
    from tools.make_v13_probe import main

    sys.argv = ["make_v13_probe", *(["--force"] if force else [])]
    return main()


def _run_temporal_hidden(*, force: bool = False) -> int:
    from tools.make_temporal_hidden_fixture import main

    sys.argv = ["make_temporal_hidden_fixture", *(["--force"] if force else [])]
    return main()


def _run_pagecomp_anchor(*, force: bool = False) -> int:
    from tools.make_pagecomp_anchor_fixture import main

    sys.argv = ["make_pagecomp_anchor_fixture", *(["--force"] if force else [])]
    return main()


def _run_pagecomp_long_prefix(*, force: bool = False) -> int:
    from tools.make_pagecomp_long_prefix_fixture import main

    sys.argv = ["make_pagecomp_long_prefix_fixture", *(["--force"] if force else [])]
    return main()


def _run_v13_hidden_probe(*, force: bool = False) -> int:
    from tools.make_v13_hidden_probe import main

    sys.argv = ["make_v13_hidden_probe", *(["--force"] if force else [])]
    return main()


def _run_phase0_probe() -> int:
    from tools.make_phase0_probe import main

    sys.argv = ["make_phase0_probe"]
    return main()


def _run_capture_verifier_sidecar(
    *,
    force: bool = False,
    bak: list[str] | None = None,
    all_: bool = False,
    keep: bool = False,
    fresh: bool = False,
) -> int:
    from tools.capture_verifier_sidecar import main

    argv: list[str] = []
    if force:
        argv.append("--force")
    if all_:
        argv.append("--all")
    if keep:
        argv.append("--keep")
    if fresh:
        argv.append("--fresh")
    for b in bak or []:
        argv += ["--bak", b]
    return main(argv)


def _run_xml_heap(*, force: bool = False) -> int:
    from tools.make_xml_heap_fixture import main

    sys.argv = ["make_xml_heap_fixture", *(["--force"] if force else [])]
    return main()


def _run_sparse(*, force: bool = False) -> int:
    from tools.make_sparse_fixture import main

    sys.argv = ["make_sparse_fixture", *(["--force"] if force else [])]
    return main()


def _run_forwarded_records(*, force: bool = False) -> int:
    from tools.make_forwarded_records_fixture import main

    sys.argv = ["make_forwarded_records_fixture", *(["--force"] if force else [])]
    return main()


def _run_ghost_records(*, force: bool = False) -> int:
    from tools.make_ghost_records_fixture import main

    sys.argv = ["make_ghost_records_fixture", *(["--force"] if force else [])]
    return main()


def _run_multi_rowgroup(*, force: bool = False) -> int:
    from tools.make_multi_rowgroup_fixture import main

    sys.argv = ["make_multi_rowgroup_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_string_dict_regression(*, force: bool = False) -> int:
    from tools.make_cci_string_dict_regression_fixture import main

    sys.argv = [
        "make_cci_string_dict_regression_fixture",
        *(["--force"] if force else []),
    ]
    return main()


def _run_max_row_width(*, force: bool = False) -> int:
    from tools.make_max_row_width_fixture import main

    sys.argv = ["make_max_row_width_fixture", *(["--force"] if force else [])]
    return main()


def _run_surrogate_pairs(*, force: bool = False) -> int:
    from tools.make_surrogate_pairs_fixture import main

    sys.argv = ["make_surrogate_pairs_fixture", *(["--force"] if force else [])]
    return main()


def _run_high_slot_density(*, force: bool = False) -> int:
    from tools.make_high_slot_density_fixture import main

    sys.argv = ["make_high_slot_density_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_switch(*, force: bool = False) -> int:
    from tools.make_cci_switch_fixture import main

    sys.argv = ["make_cci_switch_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_reorganize(*, force: bool = False) -> int:
    from tools.make_cci_reorganize_fixture import main

    sys.argv = ["make_cci_reorganize_fixture", *(["--force"] if force else [])]
    return main()


def _run_covering_index(*, force: bool = False) -> int:
    from tools.make_covering_index_fixture import main

    sys.argv = ["make_covering_index_fixture", *(["--force"] if force else [])]
    return main()


def _run_sql_variant_extract(*, force: bool = False) -> int:
    from tools.make_sql_variant_extract_fixture import main

    sys.argv = ["make_sql_variant_extract_fixture", *(["--force"] if force else [])]
    return main()


def _run_filtered_ncci(*, force: bool = False) -> int:
    from tools.make_filtered_ncci_fixture import main

    sys.argv = ["make_filtered_ncci_fixture", *(["--force"] if force else [])]
    return main()


def _run_ncci_heap(*, force: bool = False) -> int:
    from tools.make_ncci_heap_fixture import main

    sys.argv = ["make_ncci_heap_fixture", *(["--force"] if force else [])]
    return main()


def _run_identity_coverage(*, force: bool = False) -> int:
    from tools.make_identity_coverage_fixture import main

    sys.argv = ["make_identity_coverage_fixture", *(["--force"] if force else [])]
    return main()


def _run_extended_properties(*, force: bool = False) -> int:
    from tools.make_extended_properties_fixture import main

    sys.argv = ["make_extended_properties_fixture", *(["--force"] if force else [])]
    return main()


def _run_rowversion_extract(*, force: bool = False) -> int:
    from tools.make_rowversion_extract_fixture import main

    sys.argv = ["make_rowversion_extract_fixture", *(["--force"] if force else [])]
    return main()


def _run_hierarchyid_extract(*, force: bool = False) -> int:
    from tools.make_hierarchyid_extract_fixture import main

    sys.argv = ["make_hierarchyid_extract_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_computed(*, force: bool = False) -> int:
    from tools.make_cci_computed_fixture import main

    sys.argv = ["make_cci_computed_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_btree_nci(*, force: bool = False) -> int:
    from tools.make_cci_btree_nci_fixture import main

    sys.argv = ["make_cci_btree_nci_fixture", *(["--force"] if force else [])]
    return main()


def _run_ordered_cci(*, force: bool = False) -> int:
    from tools.make_ordered_cci_fixture import main

    sys.argv = ["make_ordered_cci_fixture", *(["--force"] if force else [])]
    return main()


def _run_backup_blocksize(*, force: bool = False) -> int:
    from tools.make_backup_blocksize_fixture import main

    sys.argv = ["make_backup_blocksize_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_string_minmax(*, force: bool = False) -> int:
    from tools.make_cci_string_minmax_fixture import main

    sys.argv = ["make_cci_string_minmax_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_enc5_largepool(*, force: bool = False) -> int:
    from tools.make_cci_enc5_largepool_fixture import main

    sys.argv = ["make_cci_enc5_largepool_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_enc5_largepool_matrix(*, force: bool = False) -> int:
    from tools.make_cci_enc5_largepool_matrix_fixture import main

    sys.argv = ["make_cci_enc5_largepool_matrix_fixture", *(["--force"] if force else [])]
    return main()


def _run_xml_index(*, force: bool = False) -> int:
    from tools.make_xml_index_fixture import main

    sys.argv = ["make_xml_index_fixture", *(["--force"] if force else [])]
    return main()


def _run_spatial_index(*, force: bool = False) -> int:
    from tools.make_spatial_index_fixture import main

    sys.argv = ["make_spatial_index_fixture", *(["--force"] if force else [])]
    return main()


def _run_alias_types(*, force: bool = False) -> int:
    from tools.make_alias_types_fixture import main

    sys.argv = ["make_alias_types_fixture", *(["--force"] if force else [])]
    return main()


def _run_typed_xml(*, force: bool = False) -> int:
    from tools.make_typed_xml_fixture import main

    sys.argv = ["make_typed_xml_fixture", *(["--force"] if force else [])]
    return main()


def _run_spatial_edge(*, force: bool = False) -> int:
    from tools.make_spatial_edge_fixture import main

    sys.argv = ["make_spatial_edge_fixture", *(["--force"] if force else [])]
    return main()


def _run_float_extreme(*, force: bool = False) -> int:
    from tools.make_float_extreme_fixture import main

    sys.argv = ["make_float_extreme_fixture", *(["--force"] if force else [])]
    return main()


def _run_rowstore_lob_image(*, force: bool = False) -> int:
    from tools.make_rowstore_lob_image_fixture import main

    sys.argv = ["make_rowstore_lob_image_fixture", *(["--force"] if force else [])]
    return main()


def _run_rowstore_lob_markup(*, force: bool = False) -> int:
    from tools.make_rowstore_lob_markup_fixture import main

    sys.argv = ["make_rowstore_lob_markup_fixture", *(["--force"] if force else [])]
    return main()


def _run_rowstore_hash_pii(*, force: bool = False) -> int:
    from tools.make_rowstore_hash_pii_fixture import main

    sys.argv = ["make_rowstore_hash_pii_fixture", *(["--force"] if force else [])]
    return main()


def _run_xtp_rich(*, force: bool = False) -> int:
    from tools.make_xtp_rich_fixture import main

    return main(force=force)


def _run_xtp_checkpoint(*, force: bool = False) -> int:
    from tools.make_xtp_checkpoint_fixture import main

    return main(force=force)


def _run_realworld_numeric_digest(*, force: bool = False) -> int:
    from tools.make_realworld_numeric_digest_fixture import main

    sys.argv = ["make_realworld_numeric_digest_fixture", *(["--force"] if force else [])]
    return main()


def _run_corrupt_metadata_confidence(*, force: bool = False) -> int:
    from tools.make_corrupt_metadata_confidence_fixture import main

    sys.argv = ["make_corrupt_metadata_confidence_fixture", *(["--force"] if force else [])]
    return main()


def _run_nvarchar_max_u21(*, force: bool = False) -> int:
    from tools.make_nvarchar_max_u21_fixture import main

    sys.argv = ["make_nvarchar_max_u21_fixture", *(["--force"] if force else [])]
    return main()


def _run_compressed_nvarchar(*, force: bool = False) -> int:
    from tools.make_compressed_nvarchar_fixture import main

    sys.argv = ["make_compressed_nvarchar_fixture", *(["--force"] if force else [])]
    return main()


def _run_torn_page(*, force: bool = False) -> int:
    from tools.make_torn_page_fixture import main

    return main(force=force)


def _run_xtp_simple(*, force: bool = False) -> int:
    from tools.make_xtp_simple_fixture import main

    return main(force=force)


def _run_xtp_probe(*, force: bool = False) -> int:
    from tools.make_xtp_probe_fixture import main

    return main(force=force)


def _run_vector(*, force: bool = False) -> int:
    from tools.make_vector_fixture import main

    sys.argv = ["make_vector_fixture", *(["--force"] if force else [])]
    return main()


def _run_native_json(*, force: bool = False) -> int:
    from tools.make_native_json_fixture import main

    sys.argv = ["make_native_json_fixture", *(["--force"] if force else [])]
    return main()


def _run_utf8_collation(*, force: bool = False) -> int:
    from tools.make_utf8_collation_fixture import main

    sys.argv = ["make_utf8_collation_fixture", *(["--force"] if force else [])]
    return main()


def _run_tabletype_cci_large(*, force: bool = False) -> int:
    from tools.make_tabletype_cci_large_fixture import main

    sys.argv = ["make_tabletype_cci_large_fixture", *(["--force"] if force else [])]
    return main()


def _run_delta_rowgroup(*, force: bool = False) -> int:
    from tools.make_delta_rowgroup_fixture import main

    sys.argv = ["make_delta_rowgroup_fixture", *(["--force"] if force else [])]
    return main()


def _run_boundary_datetime(*, force: bool = False) -> int:
    from tools.make_boundary_datetime_fixture import main

    sys.argv = ["make_boundary_datetime_fixture", *(["--force"] if force else [])]
    return main()


def _run_enc_bak(*, force: bool = False) -> int:
    from tools.make_enc_bak_fixture import main

    sys.argv = ["make_enc_bak_fixture", *(["--force"] if force else [])]
    return main()


def _run_tde(*, force: bool = False) -> int:
    from tools.make_tde_fixture import main

    sys.argv = ["make_tde_fixture", *(["--force"] if force else [])]
    return main()


def _run_tde_page(*, force: bool = False) -> int:
    from tools.make_tde_page_fixture import main

    sys.argv = ["make_tde_page_fixture", *(["--force"] if force else [])]
    return main()


def _run_mixed_collation(*, force: bool = False) -> int:
    from tools.make_mixed_collation_fixture import main

    sys.argv = ["make_mixed_collation_fixture", *(["--force"] if force else [])]
    return main()


def _run_ncci_types(*, force: bool = False) -> int:
    from tools.make_ncci_types_fixture import main

    sys.argv = ["make_ncci_types_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_lob(*, force: bool = False) -> int:
    from tools.make_cci_lob_fixture import main

    sys.argv = ["make_cci_lob_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_types_large(*, force: bool = False) -> int:
    from tools.make_cci_types_large_fixture import main

    sys.argv = ["make_cci_types_large_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_extended(*, force: bool = False) -> int:
    from tools.make_cci_extended_fixture import main

    sys.argv = ["make_cci_extended_fixture", *(["--force"] if force else [])]
    return main()


def _run_row_boundary(*, force: bool = False) -> int:
    from tools.make_rowboundary_fixture import main

    sys.argv = ["make_rowboundary_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_varbinary_micro(*, force: bool = False) -> int:
    from tools.make_cci_varbinary_micro_fixture import main

    sys.argv = ["make_cci_varbinary_micro_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_binary_varbinary_compare(*, force: bool = False) -> int:
    from tools.make_cci_binary_varbinary_compare_fixture import main

    sys.argv = ["make_cci_binary_varbinary_compare_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_varbinary_probe(*, force: bool = False) -> int:
    from tools.make_cci_varbinary_probe_fixture import main

    sys.argv = ["make_cci_varbinary_probe_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_bitpack_probe_int(*, force: bool = False) -> int:
    from tools.make_cci_bitpack_probe_fixture import main

    sys.argv = ["make_cci_bitpack_probe_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_bitpack_probe_bigint(*, force: bool = False) -> int:
    from tools.make_cci_bitpack_probe_bigint_fixture import main

    sys.argv = ["make_cci_bitpack_probe_bigint_fixture", *(["--force"] if force else [])]
    return main()


def _run_cci_bitpack_probe_highbase(*, force: bool = False) -> int:
    from tools.make_cci_bitpack_probe_highbase_fixture import main

    sys.argv = ["make_cci_bitpack_probe_highbase_fixture", *(["--force"] if force else [])]
    return main()


def _run_rebak_realworld(
    source: str | None,
    scan_dir: str | None,
    out_dir: str | None,
    *,
    force: bool = False,
) -> int:
    from tools.make_realworld_rebak_fixture import main

    argv: list[str] = []
    if source:
        argv += ["--source", source]
    elif scan_dir:
        argv += ["--scan-dir", scan_dir]
    if out_dir:
        argv += ["--out-dir", out_dir]
    if force:
        argv.append("--force")
    sys.argv = ["rebak-realworld", *argv]
    return main()


def _run_register_bak(
    bak: str, db_name: str, keep: bool, out: str | None, cells_only: bool = False
) -> int:
    from tools.register_bak import main as register_main

    extra: list[str] = []
    if db_name:
        extra += ["--db-name", db_name]
    if keep:
        extra.append("--keep")
    if out:
        extra += ["--out", out]
    if cells_only:
        extra.append("--cells-only")
    sys.argv = ["register_bak", bak, *extra]
    return register_main()


def _run_register_all(fixture_dir: str, force: bool, keep: bool, cells_only: bool = False) -> int:
    from tools.register_bak import register_all

    return register_all(
        Path(fixture_dir),
        skip_existing=not force,
        keep=keep,
        cells_only=cells_only,
    )


_COMMANDS = {
    "make_fixture": _run_make_fixture,
    "tabletype": lambda: _run_tabletype(rows=4),
    "compressionmatrix": _run_compressionmatrix,
    "columnstore": _run_columnstore,
    "computedmatrix": _run_computedmatrix,
    "constraintmatrix": _run_constraintmatrix,
    "xmlmatrix": _run_xmlmatrix,
    "boundary": _run_boundary,
    "dirty": _run_dirty,
    "dirty-v4": _run_dirty_v4,
    "dirty-cci": _run_dirty_cci,
    "incremental": _run_incremental,
    "lob-preamble": _run_lob_preamble,
    "aborted-xact": _run_aborted_xact,
    "stripe": _run_stripe,
    "unicode-codepage": _run_unicode_codepage,
    "layout": lambda: _run_layout(compressed=False),
    "heap-scale": lambda: _run_heap_scale(rows=1_000),
    # Gap-3: secondary filegroup (all versions)
    "ndf": _run_ndf,
    # Gap-2+4: long_text + memory_oltp + existing feature tables (SS2022 only)
    "feature": _run_feature,
    # Gap-5: ARCHIVE CCI null encoding — unpartitioned (SS2019 preferred)
    "archive-null": _run_archive_null,
    # Gap-5: ARCHIVE CCI null encoding — partitioned, 4 REBUILD scenarios
    "archive-columnstore-partition": _run_archive_columnstore_partition,
    # Gap I-1: all dictionary-encoded types under COLUMNSTORE_ARCHIVE
    "archive-columnstore-types": _run_archive_columnstore_types,
    # Gap I-1 random-order variant
    "archive-columnstore-types-random": _run_archive_columnstore_types_random,
    # PFOR exercise: integer segments engineered to emit Patched-FOR exceptions
    "pfor-columnstore": _run_pfor_columnstore,
    # PFOR random-order variant
    "pfor-columnstore-random": _run_pfor_columnstore_random,
    # TODO-F1: single-chunk enc=5 blob (small ARCHIVE CHAR(10) table)
    "archive-single-chunk": _run_archive_single_chunk,
    # TODO-F1 random-order variant
    "archive-single-chunk-random": _run_archive_single_chunk_random,
    # Gap-10: heap + xml/LOB regression guard (all SS2016+ versions)
    "xml-heap": _run_xml_heap,
    # Gap D-1: sparse columns + column set (all versions)
    "sparse": _run_sparse,
    # Gap H-1: forwarded records on heap (all versions)
    "forwarded-records": _run_forwarded_records,
    # Gap H-2: ghost (deleted) records on heap (all versions)
    "ghost-records": _run_ghost_records,
    # Gap C-3: multiple small CCI compressed rowgroups (all versions)
    "multi-rowgroup": _run_multi_rowgroup,
    # Regression: bounded VARCHAR CCI string dictionaries (TPC-BB item/reviews)
    "cci-string-dict-regression": _run_cci_string_dict_regression,
    # Gap H-3: max-row-width (single row per page, CHAR(8000)) (all versions)
    "max-row-width": _run_max_row_width,
    # Gap G-2: surrogate pairs in nvarchar (all versions)
    "surrogate-pairs": _run_surrogate_pairs,
    # Gap H-4: high slot density (TINYINT, 100k rows) (all versions)
    "high-slot-density": _run_high_slot_density,
    # Gap C-9: CCI PARTITION SWITCH — metadata-only switch reassigns rowgroup ownership
    "cci-switch": _run_cci_switch,
    # Gap C-10: CCI REORGANIZE + deleted-row bitmap — verifies delete-bitmap handling
    "cci-reorganize": _run_cci_reorganize,
    # Gap E-1: nonclustered covering index (INCLUDE columns) — NC leaf record format
    "covering-index": _run_covering_index,
    # Gap D-2: sql_variant value extraction — per-value type header parsing
    "sql-variant-extract": _run_sql_variant_extract,
    # Gap C-4: filtered NCCI (WHERE clause) — row count must equal base table, not filtered subset
    "filtered-ncci": _run_filtered_ncci,
    # Gap C-5: NCCI on heap — RID-locator column must not corrupt data column extraction
    "ncci-heap": _run_ncci_heap,
    # identity-coverage: all 6 SQL Server IDENTITY-capable types (tinyint→bigint, decimal, numeric)
    "identity-coverage": _run_identity_coverage,
    # extended-properties: MS_Description + arbitrary named props at schema/table/column level
    "extended-properties": _run_extended_properties,
    # Gap D-3: rowversion column extraction — 8-byte big-endian bytes, monotonically increasing
    "rowversion-extract": _run_rowversion_extract,
    # Gap D-4: hierarchyid column extraction — raw varbinary bytes, correct length
    "hierarchyid-extract": _run_hierarchyid_extract,
    # Gap C-11: non-persisted computed columns in CCI — absent from segments, must not crash
    "cci-computed": _run_cci_computed,
    # Gap C-12: CCI + B-tree NC indexes on same table — NC index pages must not contaminate CCI read
    "cci-btree-nci": _run_cci_btree_nci,
    # Gap C-7: ordered CCI (SS2022+ ORDER clause) — same segment format, metadata accuracy
    "ordered-cci": _run_ordered_cci,
    # Gap A-5: non-default BLOCKSIZE backup — auto-detection in _detect_block_size
    "backup-blocksize": _run_backup_blocksize,
    # Gap C-8: CCI string/binary min-max segment metadata (SS2022+) — NULL-minmax path
    "cci-string-minmax": _run_cci_string_minmax,
    "cci-enc5-largepool": _run_cci_enc5_largepool,
    "cci-enc5-largepool-matrix": _run_cci_enc5_largepool_matrix,
    # Gap E-3: XML index internal node table — recover_schema must skip IT-type objects
    "xml-index": _run_xml_index,
    # Gap E-4: spatial index internal tessellation table — same as E-3
    "spatial-index": _run_spatial_index,
    # Cell gap: user-defined alias scalar types (Flag/NameStyle over bit)
    "alias-types": _run_alias_types,
    # Cell gap: XML schema collection typed XML values
    "typed-xml": _run_typed_xml,
    # Cell gap: geometry/geography edge values with exact WKT output
    "spatial-edge": _run_spatial_edge,
    # Cell gap: rowstore float/real extreme values
    "float-extreme": _run_float_extreme,
    # Cell gap: rowstore image/varbinary(max)/varchar(max)/nvarchar(max)
    "rowstore-lob-image": _run_rowstore_lob_image,
    # Real-world regression: rowstore HTML/JSON/Unicode markup LOB payloads
    "rowstore-lob-markup": _run_rowstore_lob_markup,
    # Real-world regression: binary/hash PII-shaped rowstore cells
    "rowstore-hash-pii": _run_rowstore_hash_pii,
    # Real-world regression: richer memory-optimized XTP schemas
    "xtp-rich": _run_xtp_rich,
    # Large compressed XTP fixture that flushes checkpoint DATA chunks (straddle-row RE)
    "xtp-checkpoint": _run_xtp_checkpoint,
    # Real-world regression: taxi/rate/cost numeric digest cells
    "realworld-numeric-digest": _run_realworld_numeric_digest,
    # Confidence-only corrupt metadata fixture
    "corrupt-metadata-confidence": _run_corrupt_metadata_confidence,
    # Regression: nvarchar(max) values whose first UTF-16LE byte is 0x21
    "nvarchar-max-u21": _run_nvarchar_max_u21,
    # Regression: ROW-compressed nvarchar SCSU vs UTF-16LE heuristic
    "compressed-nvarchar": _run_compressed_nvarchar,
    # Regression: PAGE_VERIFY TORN_PAGE_DETECTION sector-bit restoration
    "torn-page": _run_torn_page,
    # Reverse-engineering: XTP (Hekaton) in-memory OLTP checkpoint format
    "xtp-simple": _run_xtp_simple,
    "xtp-probe": _run_xtp_probe,
    # Gap D-5: VECTOR column type (SS2025 only) — unknown binary header must not crash
    "vector": _run_vector,
    # Gap D-6: native JSON column type (SS2025 only) — UTF-8 bytes, not UCS-2 nvarchar
    "native-json": _run_native_json,
    # Gap G-1: UTF-8 collation varchar (SS2019+ only; exclude from _ALL_VERSIONS_SUITE)
    "utf8-collation": _run_utf8_collation,
    # Gap K-1: CCI with 1,200 rows — real segment encoding (all versions)
    "tabletype-cci-large": _run_tabletype_cci_large,
    # Gap C-1: CCI open delta store — compressed segment + uncompressed delta rows
    "delta-rowgroup": _run_delta_rowgroup,
    # Gap F-1: TDE detect-and-fail — encrypted backup raises EncryptedBackupError
    "enc-bak": _run_enc_bak,
    "tde": _run_tde,
    # TDE page-level — database TDE, no backup-level encryption; decryptable with cert
    "tde-page": _run_tde_page,
    # Gap K-2: datetime/bit/decimal boundary values in enc=4 CCI segments
    "boundary-datetime": _run_boundary_datetime,
    # Gap G-3: per-column collation override — Latin1/Greek/Hebrew/UTF-8 in one table
    "mixed-collation": _run_mixed_collation,
    # Gap K-5: NCCI type coverage — 19 types × 1,203 rows, each with an NCCI on val
    "ncci-types": _run_ncci_types,
    # Gap C-6: CCI LOB types — VARCHAR(MAX), NVARCHAR(MAX), VARBINARY(MAX)
    "cci-lob": _run_cci_lob,
    # Gap K-3: one-table-per-type CCI (1,200 rows each) — char/varbinary/bit/binary/uuid
    "cci-types-large": _run_cci_types_large,
    # Extended CCI bug-trigger tables — int/varchar50/char10_varied/binary4/nvarchar50_sparse
    "cci-extended": _run_cci_extended,
    # Row-size + LOB-page boundary: rb_overflow (±2 of 8060), rb_lob (±2 of 8096), rb_page_fill
    "row-boundary": _run_row_boundary,
    # F1: VARBINARY(16) micro fixture — 7 hand-chosen rows to inspect Format C pool/index
    "cci-varbinary-micro": _run_cci_varbinary_micro,
    # F4: BINARY(8) + VARBINARY(8) side-by-side comparison in same row group
    "cci-binary-varbinary-compare": _run_cci_binary_varbinary_compare,
    # F2+F3+F5: maxwidth/narrowmax/small-rowgroup probes for item_size and pool boundary
    "cci-varbinary-probe": _run_cci_varbinary_probe,
    # Enc=2 integer bit-pack probes: INT, BIGINT, and high-base variants
    "cci-bitpack-probe-int": _run_cci_bitpack_probe_int,
    "cci-bitpack-probe-bigint": _run_cci_bitpack_probe_bigint,
    "cci-bitpack-probe-highbase": _run_cci_bitpack_probe_highbase,
    # A1: columnstore segment metadata verifier sidecars (DBCC PAGE alternative)
    "capture-verifier-sidecar": _run_capture_verifier_sidecar,
    # Part I: Phase 0 gate — ORDER BY NEWID() shuffle verification
    "phase0-probe": _run_phase0_probe,
    # Part IV: V11 IAM secondary-filegroup probe — DBCC PAGE sidecar
    "v11-probe": _run_v11_probe,
    # Part V: G44 binary dictionary probe — DBCC CSINDEX sidecar
    "g44-probe": _run_g44_probe,
    # Part VI: V13 hidden temporal period columns probe — syscolpars DBCC PAGE
    "v13-probe": _run_v13_probe,
    # Part VI: V13 is_hidden fixture — temporal tables with/without HIDDEN keyword
    "temporal-hidden": _run_temporal_hidden,
    "pagecomp-anchor": _run_pagecomp_anchor,
    # PAGE-compression extended plen (0x80 <len>) regression probe
    "pagecomp-long-prefix": _run_pagecomp_long_prefix,
    # Part VI: V13 is_hidden probe — XOR syscolpars.status to find is_hidden bit
    "v13-hidden-probe": _run_v13_hidden_probe,
}

# Fixtures included in every all-versions run.
# Excludes:
# Every command that is compatible with at least one supported SQL Server version is
# listed here.  Scripts that require a newer engine call skip_if_server_older_than()
# and exit 0 silently when the target version does not qualify — so the runner never
# sees an error for a version-gated skip.
#   catalog — version-specific name, handled by the version-matrix command.
_ALL_VERSIONS_SUITE = [
    "make_fixture",
    "tabletype",
    "compressionmatrix",
    "columnstore",
    "computedmatrix",
    "constraintmatrix",
    "xmlmatrix",
    "boundary",
    "incremental",
    "lob-preamble",
    "aborted-xact",
    "stripe",
    "unicode-codepage",
    "layout",
    "dirty",
    "heap-scale",
    "pagecomp-anchor",  # PAGE-compression CI anchor/dictionary decode (WWI *_Archive pattern)
    "pagecomp-long-prefix",  # PAGE-compression extended plen (0x80 <len>) — prefix ≥ 128 bytes
    "ndf",  # Gap-3: secondary filegroup; all SS versions
    "xml-heap",  # Gap-10: heap xml/LOB regression guard; SS2016+
    "archive-columnstore-partition",  # Gap-5 supplement: partitioned CCI REBUILD scenarios
    "archive-columnstore-types",  # Gap I-1: VARCHAR/NCHAR/BINARY/VARBINARY/UUID under ARCHIVE
    "archive-columnstore-types-random",  # Part II: random-order variant of Gap I-1
    "sparse",  # Gap D-1: sparse columns + column set (sparse vector record)
    "forwarded-records",  # Gap H-1: forwarded records on heap (stub + overflow page)
    "ghost-records",  # Gap H-2: ghost (deleted) records on heap (status bit)
    "multi-rowgroup",  # Gap C-3: multiple small CCI compressed rowgroups
    "cci-string-dict-regression",  # Regression: bounded VARCHAR CCI string dictionaries
    "max-row-width",  # Gap H-3: max-row-width (single row per page)
    "surrogate-pairs",  # Gap G-2: surrogate pairs in nvarchar
    "high-slot-density",  # Gap H-4: high slot density (many tiny rows per page)
    "cci-switch",  # Gap C-9: CCI PARTITION SWITCH
    "cci-reorganize",  # Gap C-10: CCI REORGANIZE + deleted-row bitmap
    "covering-index",  # Gap E-1: nonclustered covering index with INCLUDE columns
    "sql-variant-extract",  # Gap D-2: sql_variant per-value type extraction
    "tabletype-cci-large",  # Gap K-1: CCI 1,200-row row group (real segment encoding)
    "delta-rowgroup",  # Gap C-1: CCI open delta store (compressed + uncompressed rows)
    "enc-bak",  # backup-level WITH ENCRYPTION decryption fixtures (AES_128 / AES_256)
    "tde",  # TDE-encrypted backup (backup-level + database-level chained decryption)
    "tde-page",  # page-level TDE (database-encrypted pages, backup-level not encrypted)
    "boundary-datetime",  # Gap K-2: datetime/bit/decimal boundary values in enc=4 CCI segments
    "mixed-collation",  # Gap G-3: per-column collation override — Latin1/Greek/Hebrew/UTF-8
    "ncci-types",  # Gap K-5: NCCI type coverage — 19 types × 1,203 rows
    "cci-lob",  # Gap C-6: CCI LOB types — VARCHAR(MAX), NVARCHAR(MAX), VARBINARY(MAX)
    "cci-types-large",  # Gap K-3: one-table-per-type CCI — char/varbinary/bit/binary/uuid
    "cci-extended",  # Extended bug-trigger — int/varchar50/char10_varied/binary4/nvarchar50_sparse
    "row-boundary",  # Row-size + LOB-page boundary: 8060 overflow, 8096 LOB-page, slot-array
    "cci-varbinary-micro",  # F1: VARBINARY(16) micro (7 rows) — Format C pool/index manual probe
    "cci-binary-varbinary-compare",  # F4: BINARY(8)+VARBINARY(8) side-by-side, 1,200 rows
    "cci-varbinary-probe",  # F2+F3+F5: maxwidth/narrowmax/small-rowgroup enc probes
    "cci-bitpack-probe-int",  # enc=2 INT bit-pack probe; single row group, FOR base 0
    "cci-bitpack-probe-bigint",  # enc=2 BIGINT bit-pack probe; multi-rowgroup high-base
    "cci-bitpack-probe-highbase",  # enc=2 INT bit-pack probe; high-base single row group
    "pfor-columnstore",  # PFOR exercise: outlier INT segments, plain + ARCHIVE
    "pfor-columnstore-random",  # Part II: random-order variant of PFOR
    "archive-single-chunk",  # TODO-F1: single-chunk enc=5 blob (small ARCHIVE CHAR(10))
    "archive-single-chunk-random",  # Part II: random-order variant of TODO-F1
    "filtered-ncci",  # Gap C-4: filtered NCCI (WHERE clause) — all base rows must be returned
    "ncci-heap",  # Gap C-5: NCCI on heap — RID-locator column isolation
    "identity-coverage",  # all 6 IDENTITY-capable types: tinyint, smallint, int, bigint, decimal, numeric
    "extended-properties",  # MS_Description + arbitrary named extended properties at schema/table/column level
    "rowversion-extract",  # Gap D-3: rowversion/timestamp — 8-byte big-endian bytes
    "hierarchyid-extract",  # Gap D-4: hierarchyid — raw bytes, correct length
    "cci-computed",  # Gap C-11: non-persisted computed columns in CCI — absent from segments
    "cci-btree-nci",  # Gap C-12: CCI + B-tree NC indexes on same table
    "backup-blocksize",  # Gap A-5: non-default BLOCKSIZE (4096) — auto-detected by reader
    "cci-string-minmax",  # Gap C-8: CCI VARCHAR/NVARCHAR with NULL min-max metadata
    "cci-enc5-largepool",  # regular-CCI enc=5 CHAR >64 KiB pool — archive false-positive guard
    "cci-enc5-largepool-matrix",  # enc=5 Format D boundary/cardinality evidence tables
    "xml-index",  # Gap E-3: XML index IT-type node tables skipped by recover_schema
    "spatial-index",  # Gap E-4: spatial index IT-type tessellation tables skipped
    "alias-types",  # Cell gap: user-defined alias scalar types
    "typed-xml",  # Cell gap: XML schema collection typed XML values
    "spatial-edge",  # Cell gap: exact geometry/geography WKT values
    "float-extreme",  # Cell gap: rowstore float/real extreme values
    "rowstore-lob-image",  # Cell gap: rowstore image and max-type LOB payloads
    "rowstore-lob-markup",  # Real-world regression: markup/JSON/Unicode rowstore LOBs
    "rowstore-hash-pii",  # Real-world regression: binary/hash PII-shaped cells
    "realworld-numeric-digest",  # Real-world regression: taxi/rate/cost numeric digest cells
    "nvarchar-max-u21",  # Regression: nvarchar(max) first UTF-16LE byte == 0x21
    "compressed-nvarchar",  # Regression: ROW-compressed nvarchar SCSU vs UTF-16LE
    "torn-page",  # Regression: PAGE_VERIFY TORN_PAGE_DETECTION sector-bit restoration
    "xtp-simple",  # Gap-4: In-Memory OLTP (XTP) — fixed + variable tables; SS2014+ (all versions)
    "xtp-probe",  # Gap-4: XTP canary-value probe — 5 tables with bit-distinctive values
    "xtp-rich",  # Real-world regression: richer XTP fixed/varlen schemas and indexes
    "xtp-checkpoint",  # large compressed XTP checkpoint DATA straddle probe
    "dirty-cci",  # dirty CCI: compressed rowgroup + delta store dirty-backup coverage
    "dirty-v4",  # dirty v4: committed delete/update v4 (mssql_python + fkr__seed)
    "archive-null",  # Gap ARCHIVE+NULL: DATA_COMPRESSION=COLUMNSTORE_ARCHIVE (SS2012+, all versions)
    "utf8-collation",  # Gap G-1: UTF-8 collation varchar; self-skips on SS<2019
    "temporal-hidden",  # temporal HIDDEN period columns; SS2016+ (all tested versions)
    "feature",  # full feature-coverage db; self-skips on SS<2022 (ledger tables)
    "ordered-cci",  # Gap C-7: ordered CCI ORDER clause; self-skips on SS<2022
    "native-json",  # Gap D-6: native JSON column type; self-skips on SS<2025
    "vector",  # Gap D-5: VECTOR column type; self-skips on SS<2025
]


_ALL_VERSIONS_EXPECTED_SKIPS: dict[tuple[str, str], str] = {
    (
        "2019",
        "xtp-simple",
    ): "SQL Server 2019 local container crashes during XTP fixture generation",
    (
        "2019",
        "xtp-probe",
    ): "SQL Server 2019 local container crashes during XTP fixture generation",
    (
        "2019",
        "xtp-rich",
    ): "SQL Server 2019 local container crashes during XTP fixture generation",
    (
        "2019",
        "xtp-checkpoint",
    ): "SQL Server 2019 local container crashes during XTP fixture generation",
}


def _all_versions_expected_skip_reason(version: str, cmd: str) -> str | None:
    return _ALL_VERSIONS_EXPECTED_SKIPS.get((version, cmd))


def _running_containers() -> set[str]:
    """Return the set of currently running Podman container names."""
    try:
        r = subprocess.run(
            ["podman", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
        )
        return set(r.stdout.splitlines())
    except Exception:
        return set()


def _discover_version_instances() -> dict[str, str]:
    """Return {ss_version: server_name} for every *running* sqlserver container
    that has a matching forgedb blob in the secrets dir.

    Blobs whose container is stopped or missing are skipped with a warning so
    they don't cause cascading failures in the all-versions loop.
    """
    import re

    running = _running_containers()
    result: dict[str, str] = {}
    for path in sorted(_secrets_dir().glob("*.json")):
        if path.name.endswith(".meta.json"):
            continue
        try:
            blob = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        container = blob.get("podman_container", "")
        m = re.search(r"-mssql-(\d{4})-", container)
        if not m:
            continue
        if container not in running:
            print(
                f"  (skip SS{m.group(1)}: container {container!r} is not running)",
                file=sys.stderr,
            )
            continue
        version = m.group(1)
        server_name = blob.get("server_name") or blob.get("instance_id") or path.stem
        result[version] = server_name
    return result


def _run_all_versions(
    versions: list[str] | None,
    fixture_base: Path,
    suite: list[str],
    cmd_extra: dict[str, list[str]] | None = None,
) -> int:
    """Run *suite* against every discovered SQL Server version.

    Each (version, fixture) pair runs in a fresh subprocess so that module-level
    OUT_PATH constants in the make_*.py scripts are re-evaluated with the correct
    FIXTURE_DIR env var for that version.

    *cmd_extra* is an optional mapping from command name to extra CLI args that
    are appended after the command name in the subprocess call, e.g.::

        {"heap-scale": ["--rows", "50000"]}
    """
    cmd_extra = cmd_extra or {}
    instances = _discover_version_instances()
    if versions:
        instances = {v: s for v, s in instances.items() if v in versions}
    if not instances:
        print("No SQL Server instances found in forgedb blobs.", file=sys.stderr)
        return 1

    errors: list[str] = []
    for version in sorted(instances):
        server_name = instances[version]
        fixture_dir = fixture_base / f"fixtures_{version}"
        fixture_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n==> SS{version}  server={server_name}", file=sys.stderr)
        print(f"    output → {fixture_dir}", file=sys.stderr)
        for cmd in suite:
            skip_reason = _all_versions_expected_skip_reason(version, cmd)
            if skip_reason:
                print(
                    f"    xfail/skip SS{version}/{cmd}: {skip_reason}",
                    file=sys.stderr,
                )
                continue
            print(f"    running {cmd} ...", file=sys.stderr)
            extra = cmd_extra.get(cmd, [])
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "tools.fixture_run",
                    "--fixture-dir",
                    str(fixture_dir),
                    "--server",
                    server_name,
                    cmd,
                    *extra,
                ],
            )
            if result.returncode != 0:
                errors.append(f"SS{version}/{cmd}")
                print(f"    FAILED (exit {result.returncode})", file=sys.stderr)

    if errors:
        print(f"\nFailed: {', '.join(errors)}", file=sys.stderr)
        return 1

    # Collect ground-truth stats for every .bak that was just generated.
    for version in sorted(instances):
        server_name = instances[version]
        fixture_dir = fixture_base / f"fixtures_{version}"
        print(f"\n==> SS{version}  collecting stats (register-all) …", file=sys.stderr)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.fixture_run",
                "--fixture-dir",
                str(fixture_dir),
                "--server",
                server_name,
                "register-all",
            ],
        )

    print("\nall-versions complete.", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run mssqlbak fixture generators with forgedb credentials"
    )
    # Global options — apply to every subcommand.
    parser.add_argument(
        "--fixture-dir",
        default=None,
        metavar="DIR",
        help="override output directory for generated .bak files (sets FIXTURE_DIR env var)",
    )
    parser.add_argument(
        "--server",
        default=None,
        metavar="SERVER_NAME",
        help="forgedb blob stem to target (overrides FIXTURE_SERVER_NAME; required when "
        "multiple SQL Server containers are running)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("env", help="print shell export statements (use with eval)")

    sub.add_parser("make_fixture", help="typecoverage_full.bak")
    tt_p = sub.add_parser(
        "tabletype", help="tabletypecoverage_full.bak + tabletypecoverage_diff.bak"
    )
    tt_p.add_argument(
        "--rows",
        type=int,
        default=4,
        metavar="N",
        help=(
            "total rows per table (default: 4). "
            "The 4 type-coverage rows are always included; extra rows use only "
            "the id column (all type columns NULL) for IAM-scale testing."
        ),
    )
    sub.add_parser("compressionmatrix", help="compressioncoverage_full.bak")
    sub.add_parser("columnstore", help="columnstore_minimal.bak")
    sub.add_parser("computedmatrix", help="computedcoverage_full.bak")
    sub.add_parser("constraintmatrix", help="constraintcoverage_full.bak")
    sub.add_parser("xmlmatrix", help="xmlcoverage_full.bak")
    sub.add_parser("boundary", help="boundarycoverage_full.bak")
    sub.add_parser("dirty", help="dirtycoverage_*.bak (30+ files)")
    dirty_v4_p = sub.add_parser(
        "dirty-v4",
        help="dirtycoverage_committed_{delete,update}_v4.bak (mssql_python + fkr__seed; guaranteed cds/rp>0)",
    )
    dirty_v4_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    dirty_cci_p = sub.add_parser(
        "dirty-cci",
        help="dirtycoverage_cci_{delete,update}.bak (CCI compressed rowgroup + delta store dirty backup)",
    )
    dirty_cci_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    sub.add_parser("incremental", help="incrementalcoverage_full.bak + diff_01..06.bak")
    sub.add_parser("lob-preamble", help="cs_lob_preamble.bak")
    sub.add_parser("aborted-xact", help="dirtycoverage_aborted_xact.bak")
    sub.add_parser("stripe", help="striped_full_{1,2}.bak + striped_single.bak")
    sub.add_parser("unicode-codepage", help="unicode_codepage_coverage.bak (G55 probe)")
    ndf_p = sub.add_parser(
        "ndf",
        help="ndfcoverage_full.bak — secondary NDF filegroup tables (Gap 3)",
    )
    ndf_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    feat_p = sub.add_parser(
        "feature",
        help=(
            "featurecoverage_full.bak — temporal, COMPRESS, UTF-8, NCCI, "
            "ledger, graph, long_text (Gap 2), memory_oltp (Gap 4); SS2022 only"
        ),
    )
    feat_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    an_p = sub.add_parser(
        "archive-null",
        help="archivenull_full.bak — unpartitioned CCI with ARCHIVE compression, known NULLs (Gap 5)",
    )
    an_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    ap_p = sub.add_parser(
        "archive-columnstore-partition",
        help=(
            "archive_columnstore_partition_full.bak — partitioned CCI, 4 REBUILD scenarios "
            "(single / all / mixed / roundtrip ARCHIVE+COLUMNSTORE) for Gap 5; all versions"
        ),
    )
    ap_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    act_p = sub.add_parser(
        "archive-columnstore-types",
        help=(
            "archive_columnstore_types_full.bak — Gap I-1: all dictionary-encoded types "
            "(CHAR/VARCHAR/NCHAR/NVARCHAR/BINARY/VARBINARY/UUID) under COLUMNSTORE_ARCHIVE; "
            "first fixture using the new SqlDialect/EngineAdapter architecture; all versions"
        ),
    )
    act_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    actr_p = sub.add_parser(
        "archive-columnstore-types-random",
        help=(
            "archive_columnstore_types_random_full.bak — Part II: random-order variant of "
            "archive-columnstore-types (INSERT ORDER BY NEWID()); all versions"
        ),
    )
    actr_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    pf_p = sub.add_parser(
        "pfor-columnstore",
        help=(
            "pfor_columnstore_full.bak — INT columnstore segments engineered to emit "
            "PFOR exceptions (sparse / deep / compulsory / dense outliers), plain vs "
            "ARCHIVE; for exercising the bit-pack exception-walk path"
        ),
    )
    pf_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    pfr_p = sub.add_parser(
        "pfor-columnstore-random",
        help=(
            "pfor_columnstore_random_full.bak — Part II: random-order variant of "
            "pfor-columnstore (INSERT ORDER BY NEWID()); all versions"
        ),
    )
    pfr_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    asc_p = sub.add_parser(
        "archive-single-chunk",
        help=(
            "archive_single_chunk_full.bak — TODO-F1: small ARCHIVE CHAR(10) table "
            "(~5000 rows) whose enc=5 blob fits in a single 64KB chunk; all versions"
        ),
    )
    asc_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    ascr_p = sub.add_parser(
        "archive-single-chunk-random",
        help=(
            "archive_single_chunk_random_full.bak — Part II: random-order variant of "
            "archive-single-chunk (INSERT ORDER BY NEWID()); all versions"
        ),
    )
    ascr_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    xh_p = sub.add_parser(
        "xml-heap",
        help="xmlheap_full.bak — heap + xml/varchar(MAX)/varbinary(MAX) LOBs (Gap 10 guard)",
    )
    xh_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    sp_p = sub.add_parser(
        "sparse",
        help=(
            "sparse_full.bak — sparse columns + XML COLUMN_SET; "
            "10,000 rows with varying sparsity patterns (Gap D-1)"
        ),
    )
    sp_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    fwd_p = sub.add_parser(
        "forwarded-records",
        help=(
            "forwarded_records_full.bak — heap with forwarding stubs; "
            "1,000 rows where odd IDs are forwarded to overflow pages (Gap H-1)"
        ),
    )
    fwd_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    ghost_p = sub.add_parser(
        "ghost-records",
        help=(
            "ghost_records_full.bak — heap with ghost (deleted) records; "
            "800 live rows + 200 ghost records frozen via TF 661 (Gap H-2)"
        ),
    )
    ghost_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    mrg_p = sub.add_parser(
        "multi-rowgroup",
        help=(
            "multi_rowgroup_full.bak — CCI with 3 compressed rowgroups: "
            "1,200 + 600 + 300 rows (total 2,100); exercises segment-index "
            "multi-rowgroup iteration (Gap C-3)"
        ),
    )
    mrg_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    csdr_p = sub.add_parser(
        "cci-string-dict-regression",
        help=(
            "cci_string_dict_regression_full.bak — bounded VARCHAR CCI table "
            "with item/review-like dictionary strings across two compressed "
            "rowgroups; guards TPC-BB i_item_desc/pr_review_content regressions"
        ),
    )
    csdr_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    mrw_p = sub.add_parser(
        "max-row-width",
        help=(
            "max_row_width_full.bak — 5 rows of CHAR(8,000) (one slot per page); "
            "exercises slot-array edge cases with slot_count=1 (Gap H-3)"
        ),
    )
    mrw_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    sgp_p = sub.add_parser(
        "surrogate-pairs",
        help=(
            "surrogate_pairs_full.bak — nvarchar with surrogate-pair code points "
            "(𠀀, 😀, 🇬🇧) + ASCII control + NULL; verifies UTF-16 surrogate handling (Gap G-2)"
        ),
    )
    sgp_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    hsd_p = sub.add_parser(
        "high-slot-density",
        help=(
            "high_slot_density_full.bak — 100,000 TINYINT rows (many slots per page); "
            "exercises slot-array iteration at high density (Gap H-4)"
        ),
    )
    hsd_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    ccsw_p = sub.add_parser(
        "cci-switch",
        help=(
            "cci_switch_full.bak — CCI PARTITION SWITCH: 1,200 rows from src → dst; "
            "verifies catalog-based rowgroup ownership after metadata-only switch (Gap C-9)"
        ),
    )
    ccsw_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    ccre_p = sub.add_parser(
        "cci-reorganize",
        help=(
            "cci_reorganize_full.bak — CCI with 200 rows deleted: one table without "
            "REORGANIZE (delete bitmap in effect), one with REORGANIZE (compacted); "
            "verifies correct live-row count in both cases (Gap C-10)"
        ),
    )
    ccre_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    covi_p = sub.add_parser(
        "covering-index",
        help=(
            "covering_index_full.bak — 1,000-row table with NC index INCLUDE (name, amount); "
            "verifies base-table extraction is not disrupted by covering NC index (Gap E-1)"
        ),
    )
    covi_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    svar_p = sub.add_parser(
        "sql-variant-extract",
        help=(
            "sql_variant_extract_full.bak — 6-row table with mixed sql_variant values "
            "(INT, DECIMAL, NVARCHAR, BIGINT, DATETIME2, NULL); "
            "verifies per-value type header parsing (Gap D-2)"
        ),
    )
    svar_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    fncci_p = sub.add_parser(
        "filtered-ncci",
        help=(
            "filtered_ncci_full.bak — 1,000-row clustered + heap tables each with a "
            "filtered NCCI (WHERE active=1 covers only 500 rows); verifies base-table "
            "row count is not clamped to the NCCI filter (Gap C-4)"
        ),
    )
    fncci_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    nhp_p = sub.add_parser(
        "ncci-heap",
        help=(
            "ncci_heap_full.bak — 1,200-row heap with NCCI on (id, val); "
            "RID-locator column must not contaminate data-column extraction (Gap C-5)"
        ),
    )
    nhp_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    ic_p = sub.add_parser(
        "identity-coverage",
        help=(
            "identity_coverage_full.bak — 6 tables covering all SQL Server IDENTITY-capable types "
            "(tinyint, smallint, int, bigint, decimal(9,0), numeric(9,0)); "
            "seed and increment must decode correctly for every xtype"
        ),
    )
    ic_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    ep_p = sub.add_parser(
        "extended-properties",
        help=(
            "extended_properties_full.bak — MS_Description and arbitrary-named extended "
            "properties at schema, table, and column levels; tests recover_extended_properties "
            "and rendering in DDL / pg / delta sinks"
        ),
    )
    ep_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    rv_p = sub.add_parser(
        "rowversion-extract",
        help=(
            "rowversion_extract_full.bak — 100-row table with rowversion column; "
            "values must be 8-byte bytes objects, distinct and monotonically increasing (Gap D-3)"
        ),
    )
    rv_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    hid_p = sub.add_parser(
        "hierarchyid-extract",
        help=(
            "hierarchyid_extract_full.bak — 6-row org table with known hierarchyid "
            "paths (/,/1/,/2/,/1/1/,/1/2/,/1/1/1/); raw bytes must be non-empty and "
            "persisted path column must match (Gap D-4)"
        ),
    )
    hid_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    ccmp_p = sub.add_parser(
        "cci-computed",
        help=(
            "cci_computed_full.bak — 1,200-row CCI table with persisted + non-persisted "
            "computed columns; non-persisted column absent from segments must not crash (Gap C-11)"
        ),
    )
    ccmp_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    cbn_p = sub.add_parser(
        "cci-btree-nci",
        help=(
            "cci_btree_nci_full.bak — 1,200-row CCI table with two B-tree NC indexes; "
            "NC index pages must not be decoded as CCI segments (Gap C-12)"
        ),
    )
    cbn_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    ordc_p = sub.add_parser(
        "ordered-cci",
        help=(
            "ordered_cci_full.bak — 1,200-row ordered CCI (ORDER clause, SS2022+) vs "
            "regular CCI; segment min/max metadata must decode correctly (Gap C-7)"
        ),
    )
    ordc_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    bbsz_p = sub.add_parser(
        "backup-blocksize",
        help=(
            "backup_blocksize_full.bak — 100-row table backed up with BLOCKSIZE=4096; "
            "_detect_block_size() must auto-detect the non-default block size (Gap A-5)"
        ),
    )
    bbsz_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    ccsm_p = sub.add_parser(
        "cci-string-minmax",
        help=(
            "cci_string_minmax_full.bak — 1,200-row CCI with VARCHAR/NVARCHAR columns; "
            "120 NULL rows exercise the NULL-minmax path in SS2022+ segment metadata (Gap C-8)"
        ),
    )
    ccsm_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    cclp_p = sub.add_parser(
        "cci-enc5-largepool",
        help=(
            "cci_enc5_largepool_full.bak — regular CCI with high-cardinality CHAR(13)/CHAR(10) "
            "columns (>64 KiB enc=5 pool) + sparse NULLs; guards the ARCHIVE-probe false positive "
            "that misrouted regular CCI CHAR segments to all-NULL"
        ),
    )
    cclp_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    cclpm_p = sub.add_parser(
        "cci-enc5-largepool-matrix",
        help=(
            "cci_enc5_largepool_matrix_full.bak — regular CCI enc=5 CHAR/VARCHAR evidence "
            "matrix across 32K/64K/80K row boundaries, cardinality, and effective string width"
        ),
    )
    cclpm_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    xidx_p = sub.add_parser(
        "xml-index",
        help=(
            "xml_index_full.bak — 100-row XML table with PRIMARY + secondary XML index; "
            "internal IT-type node tables must be skipped by recover_schema (Gap E-3)"
        ),
    )
    xidx_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    sidx_p = sub.add_parser(
        "spatial-index",
        help=(
            "spatial_index_full.bak — 200-row geometry table with GEOMETRY_GRID spatial index; "
            "internal IT-type tessellation tables must be skipped by recover_schema (Gap E-4)"
        ),
    )
    sidx_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    alias_p = sub.add_parser(
        "alias-types",
        help=(
            "alias_types_full.bak — scalar user-defined alias types such as Flag and "
            "NameStyle over bit; cell canonicalization must use the base system type"
        ),
    )
    alias_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    txml_p = sub.add_parser(
        "typed-xml",
        help=(
            "typed_xml_full.bak — XML schema collection typed XML rows; verifies "
            "typed binary XML cell decoding and digest stability"
        ),
    )
    txml_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    sedge_p = sub.add_parser(
        "spatial-edge",
        help=(
            "spatial_edge_full.bak — geometry/geography edge values with exact WKT "
            "expectations, including multipolygon, full globe, and NULL"
        ),
    )
    sedge_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    fext_p = sub.add_parser(
        "float-extreme",
        help=(
            "float_extreme_full.bak — rowstore FLOAT/REAL maximum, minimum, "
            "zero, and fractional values for canonical text coverage"
        ),
    )
    fext_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    lobimg_p = sub.add_parser(
        "rowstore-lob-image",
        help=(
            "rowstore_lob_image_full.bak — rowstore image, varbinary(max), "
            "varchar(max), and nvarchar(max) cells with fixed hashes"
        ),
    )
    lobimg_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    lobmarkup_p = sub.add_parser(
        "rowstore-lob-markup",
        help=(
            "rowstore_lob_markup_full.bak — rowstore varchar(max), nvarchar(max), "
            "and JSON-like markup LOB cells modelled after real-world Body/Text/SearchDetails failures"
        ),
    )
    lobmarkup_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    hashpii_p = sub.add_parser(
        "rowstore-hash-pii",
        help=(
            "rowstore_hash_pii_full.bak — binary/hash PII-shaped cells: "
            "BINARY(32), VARBINARY(16), VARBINARY(MAX), HASHBYTES, sparse NULLs"
        ),
    )
    hashpii_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    numeric_p = sub.add_parser(
        "realworld-numeric-digest",
        help=(
            "realworld_numeric_digest_full.bak — rowstore/NCCI/CCI float, decimal, "
            "money, bit, and key-like numeric cells modelled after taxi/rate/cost failures"
        ),
    )
    numeric_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    corrupt_meta_p = sub.add_parser(
        "corrupt-metadata-confidence",
        help=(
            "corrupt_metadata_confidence_full.bak — deterministic malformed backup "
            "for confidence catalog-consistency failure coverage"
        ),
    )
    corrupt_meta_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    nvu21_p = sub.add_parser(
        "nvarchar-max-u21",
        help=(
            "nvarchar_max_u21_full.bak — nvarchar(max) values whose first "
            "UTF-16LE byte is 0x21 (Cyrillic С, CJK 無, Devanagari ड, etc.); "
            "regression fixture for the inline 0x21-prefix strip bug"
        ),
    )
    nvu21_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    cnv_p = sub.add_parser(
        "compressed-nvarchar",
        help=(
            "compressed_nvarchar_full.bak — ROW-compressed nvarchar(200) table with "
            "ASCII, Cyrillic, Greek, CJK, mixed, and NULL values; regression fixture "
            "for the _is_utf16le_not_scsu SCSU/UTF-16LE decode heuristic"
        ),
    )
    cnv_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    tp_p = sub.add_parser(
        "torn-page",
        help=(
            "torn_page_full.bak — PAGE_VERIFY TORN_PAGE_DETECTION database; "
            "regression fixture for restore_torn_page sector-bit reversal "
            "(pre-fix: dropped 9,303 rows from CreditBackup100.bak)"
        ),
    )
    tp_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    xtp_p = sub.add_parser(
        "xtp-simple",
        help=(
            "xtp_simple_full.bak — minimal XTP (Hekaton/In-Memory OLTP) fixture "
            "for reverse-engineering the checkpoint data format; "
            "xtp_fixed (INT/BIGINT/TINYINT) + xtp_var (INT/NVARCHAR NULL)"
        ),
    )
    xtp_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    xtp_probe_p = sub.add_parser(
        "xtp-probe",
        help=(
            "xtp_probe_full.bak — canary-value XTP probe fixture for "
            "format reverse-engineering; 5 memory-optimized tables with "
            "bit-distinctive values to pinpoint column byte positions"
        ),
    )
    xtp_probe_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    xtp_rich_p = sub.add_parser(
        "xtp-rich",
        help=(
            "xtp_rich_full.bak — richer XTP fixture with fixed/varlen memory-optimized "
            "tables and secondary nonclustered indexes"
        ),
    )
    xtp_rich_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    xtp_ckpt_p = sub.add_parser(
        "xtp-checkpoint",
        help=(
            "xtp_checkpoint_straddle_full.bak — LARGE compressed memory-optimized "
            "fixture (100k variable-width rows + CHECKPOINT) that flushes XTP "
            "checkpoint DATA chunks and induces boundary-straddle rows"
        ),
    )
    xtp_ckpt_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    vec_p = sub.add_parser(
        "vector",
        help=(
            "vector_full.bak — 10-row table with VECTOR(3) column (SS2025 only); "
            "unknown binary header must not crash (Gap D-5)"
        ),
    )
    vec_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    njson_p = sub.add_parser(
        "native-json",
        help=(
            "native_json_full.bak — 10-row table with native JSON column (SS2025 only); "
            "UTF-8 bytes must not be decoded as UCS-2 nvarchar (Gap D-6)"
        ),
    )
    njson_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    utf8_p = sub.add_parser(
        "utf8-collation",
        help=(
            "utf8_collation_full.bak — VARCHAR with Latin1_General_100_CI_AS_SC_UTF8 "
            "collation; 7 rows incl. CJK, emoji, Euro (Gap G-1; SS2019+ only)"
        ),
    )
    utf8_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    cci_large_p = sub.add_parser(
        "tabletype-cci-large",
        help=(
            "tabletype_cci_large_full.bak — tt_column (CCI) with 1,200 rows; "
            "4 structural rows + 1,196 NULL fillers force real segment encoding "
            "for all 25 CCI-compatible types (Gap K-1)"
        ),
    )
    cci_large_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    delta_rg_p = sub.add_parser(
        "delta-rowgroup",
        help=(
            "delta_rowgroup_full.bak — cs_mixed (100 compressed + 50 open delta) and "
            "cs_delta_only (30 rows, no compressed segment); exercises "
            "_read_columnstore_delta_rows (Gap C-1)"
        ),
    )
    delta_rg_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    enc_bak_p = sub.add_parser(
        "enc-bak",
        help=(
            "enc_bak_plain.bak + enc_bak_aes128_full.bak + enc_bak_aes256_full.bak + "
            "enc_bak_aes256_compressed.bak + enc_bak_cert.pfx — "
            "backup-level WITH ENCRYPTION fixtures (known-plaintext pair) for "
            "the mssqlbak/backupenc/ decryption feature"
        ),
    )
    enc_bak_p.add_argument("--force", action="store_true", help="overwrite existing files")

    tde_p = sub.add_parser(
        "tde",
        help=(
            "tde_full.bak + tde_full_compressed.bak + tde_full_cert.pfx — "
            "double-encrypted fixtures (TDE + WITH ENCRYPTION); same cert both layers"
        ),
    )
    tde_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    tde_page_p = sub.add_parser(
        "tde-page",
        help=(
            "tde_page_full.bak + tde_page_plain.bak + tde_page_cert.pfx — "
            "database-level TDE backup (AES_128, no backup-level encryption); "
            "used by the Phase 0 spike and TDE page decryption integration tests"
        ),
    )
    tde_page_p.add_argument("--force", action="store_true", help="overwrite existing files")

    bdt_p = sub.add_parser(
        "boundary-datetime",
        help=(
            "boundarycoverage_datetime_full.bak — 9 tables (bit, decimal(9,4), decimal(18,4), "
            "date, datetime, datetime2(3), time(3), smalldatetime, datetimeoffset(3)); "
            "1 200 rows each to force enc=4 CCI segments; tests min/max/sec_min/sec_max (Gap K-2)"
        ),
    )
    bdt_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    mc_p = sub.add_parser(
        "mixed-collation",
        help=(
            "mixed_collation_full.bak — one table with Latin1_General (CP1252), "
            "Greek (CP1253), Hebrew (CP1255), and UTF-8 varchar columns; "
            "3 rows (ASCII, non-ASCII, NULL); exercises per-column collation decode (Gap G-3)"
        ),
    )
    mc_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    ncci_types_p = sub.add_parser(
        "ncci-types",
        help=(
            "ncci_types_full.bak — 19 rowstore tables each with a NONCLUSTERED COLUMNSTORE "
            "INDEX on the value column; 1,203 rows per table covering bigint, smallint, "
            "tinyint, bit, float, real, money, smallmoney, date, datetime2, time, "
            "datetimeoffset, char, nchar, varchar, nvarchar, binary, varbinary, "
            "uniqueidentifier (Gap K-5)"
        ),
    )
    ncci_types_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    cci_lob_p = sub.add_parser(
        "cci-lob",
        help=(
            "cci_lob_full.bak — three CCI tables with VARCHAR(MAX), NVARCHAR(MAX), "
            "VARBINARY(MAX) columns; 1,200 rows each; varint-encoded dictionary entries "
            "covering short, medium, and long values (Gap C-6)"
        ),
    )
    cci_lob_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    cci_tl_p = sub.add_parser(
        "cci-types-large",
        help=(
            "cci_types_large_full.bak — five focused CCI tables (1,200 rows each): "
            "CHAR(20), VARBINARY(16), BIT, BINARY(16), UNIQUEIDENTIFIER; "
            "varied non-null fillers stress multi-entry dictionaries (Gap K-3)"
        ),
    )
    cci_tl_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    cci_ext_p = sub.add_parser(
        "cci-extended",
        help=(
            "cci_extended_full.bak — five bug-trigger CCI tables (1,200 rows each): "
            "INT (K3B on enc=2?), VARCHAR(50) (K3B new type?), CHAR(10) 26+ values (K3A width-independent?), "
            "BINARY(4) (E3B width-independent?), NVARCHAR(50) sparse-NULL (K3B masks E3C?)"
        ),
    )
    cci_ext_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    rb_p = sub.add_parser(
        "row-boundary",
        help=(
            "rowboundary_full.bak — row-size + LOB-page boundary coverage: "
            "rb_overflow (in-row vs ROW_OVERFLOW at ±2 of 8060 bytes, Bug B-3), "
            "rb_lob (single- vs two-LOB-page at ±2 of 8096 bytes), "
            "rb_page_fill (3 full data pages of CHAR(100) rows)"
        ),
    )
    rb_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    vbm_p = sub.add_parser(
        "cci-varbinary-micro",
        help=(
            "cci_varbinary_micro_full.bak — F1 diagnostic: 7 hand-chosen VARBINARY(16) rows "
            "to make the Format C pool/index manually inspectable (M1/M2/M3). "
            "Three tables: cci_varbinary_micro (7 rows), cci_varbinary_micro_nullonly "
            "(1 non-null + 20 NULLs), cci_varbinary_micro_1byte (20 one-byte values)."
        ),
    )
    vbm_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    bvc_p = sub.add_parser(
        "cci-binary-varbinary-compare",
        help=(
            "cci_binary_varbinary_compare_full.bak — F4 diagnostic: BINARY(8) and "
            "VARBINARY(8) in the same row group with identical values (1,200 rows). "
            "Side-by-side blob comparison resolves M1 and M2."
        ),
    )
    bvc_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    vbp_p = sub.add_parser(
        "cci-varbinary-probe",
        help=(
            "cci_varbinary_probe_full.bak — F2+F3+F5 probes: "
            "cci_varbinary_maxwidth (all 16-byte values, F2), "
            "cci_varbinary_narrowmax (VARBINARY(4), F3), "
            "cci_varbinary_small_rowgroup (128 rows no NULLs, F5)."
        ),
    )
    vbp_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    cbp_int_p = sub.add_parser(
        "cci-bitpack-probe-int",
        help=(
            "cci_bitpack_probe_full.bak — enc=2 INT bit-pack probe: "
            "single compressed row group, FOR base 0, 200k rows."
        ),
    )
    cbp_int_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    cbp_bigint_p = sub.add_parser(
        "cci-bitpack-probe-bigint",
        help=(
            "cci_bitpack_probe_bigint_full.bak — enc=2 BIGINT bit-pack probe: "
            "multi-rowgroup high-base layout, 2.2M rows."
        ),
    )
    cbp_bigint_p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    cbp_highbase_p = sub.add_parser(
        "cci-bitpack-probe-highbase",
        help=(
            "cci_bitpack_probe_highbase_full.bak — enc=2 INT bit-pack probe: "
            "high-base single compressed row group, 200k rows."
        ),
    )
    cbp_highbase_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    cvs_p = sub.add_parser(
        "capture-verifier-sidecar",
        help=(
            "A1 verifier: capture sys.column_store_segments metadata for ARCHIVE "
            "CCI fixtures → *.segments.json sidecars for enc=1/enc=5 bug investigation"
        ),
    )
    cvs_p.add_argument("--force", action="store_true", help="overwrite existing .segments.json")
    cvs_p.add_argument(
        "--bak",
        action="append",
        default=[],
        metavar="PATH",
        help="capture this .bak (repeatable; relative to fixture dir or absolute)",
    )
    cvs_p.add_argument(
        "--all",
        action="store_true",
        help="capture every *.bak in the fixture dir (non-columnstore fixtures skipped)",
    )
    cvs_p.add_argument(
        "--keep",
        action="store_true",
        help="keep databases this run restores (default: drop after capture)",
    )
    cvs_p.add_argument(
        "--fresh",
        action="store_true",
        help="drop and re-restore even if the DB exists (fixes a broken RESTORING DB)",
    )

    sub.add_parser(
        "phase0-probe",
        help=(
            "Part I Phase 0 gate: verify ORDER BY NEWID() shuffles inserts "
            "and changes the columnstore encoder's segment layout. "
            "Results written to <fixture-dir>/phase0_probe_results.txt"
        ),
    )

    v11_p = sub.add_parser(
        "v11-probe",
        help=(
            "Part IV V11: DBCC PAGE capture for IAM secondary-filegroup tables "
            "(primary_tbl vs secondary_tbl in ndfcoverage_full.bak). "
            "Results written to <fixture-dir>/V11_probe_results.txt"
        ),
    )
    v11_p.add_argument("--force", action="store_true", help="overwrite existing results")

    sub.add_parser(
        "g44-probe",
        help=(
            "Part V G44: DBCC CSINDEX capture for columnstore binary-dictionary "
            "(version-4 hash format) in cs_lob_preamble2.bak. "
            "Results written to <fixture-dir>/G44_csindex_output.txt"
        ),
    )

    v13_p = sub.add_parser(
        "v13-probe",
        help=(
            "Part VI V13: DBCC PAGE syscolpars capture to identify is_hidden / "
            "generated_always_type status bits for hidden temporal period columns "
            "(WideWorldImporters-Standard.bak). "
            "Results written to <fixture-dir>/V13_probe_results.txt"
        ),
    )
    v13_p.add_argument("--force", action="store_true", help="overwrite existing results")

    th_p = sub.add_parser(
        "temporal-hidden",
        help=(
            "Part VI V13 is_hidden: generate temporal_hidden_full.bak — two temporal "
            "tables differing only in the HIDDEN keyword on their period columns; "
            "prerequisite for v13-hidden-probe"
        ),
    )
    th_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    pca_p = sub.add_parser(
        "pagecomp-anchor",
        help=(
            "pagecomp_anchor_full.bak — PAGE-compression CI anchor/dictionary "
            "decode fixture: clustered PAGE-compressed table whose constant "
            "columns collapse into the page anchor (_CD_ZERO rows), mirroring "
            "WWI *_Archive; all versions"
        ),
    )
    pca_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    pclp_p = sub.add_parser(
        "pagecomp-long-prefix",
        help=(
            "pagecomp_long_prefix_full.bak — PAGE-compressed NVARCHAR fixture "
            "with a >=128-byte shared prefix, exercising the extended 0x80 <len> "
            "prefix-length form; all versions"
        ),
    )
    pclp_p.add_argument("--force", action="store_true", help="overwrite existing .bak")

    v13h_p = sub.add_parser(
        "v13-hidden-probe",
        help=(
            "Part VI V13 is_hidden: restore temporal_hidden_full.bak and XOR "
            "syscolpars.status of HIDDEN vs non-HIDDEN period columns to identify "
            "the is_hidden bit mask. "
            "Results written to <fixture-dir>/V13_hidden_probe_results.txt"
        ),
    )
    v13h_p.add_argument("--force", action="store_true", help="overwrite existing results")

    heap_p = sub.add_parser(
        "heap-scale",
        help="heapcoverage_large.bak — clustered + heap pair for IAM traversal testing",
    )
    heap_p.add_argument(
        "--rows",
        type=int,
        default=1_000,
        metavar="N",
        help=(
            "rows per table (default: 1000 in all-versions suite). "
            "Use --rows 50000 or more to reproduce the IAM traversal bug."
        ),
    )

    rr_p = sub.add_parser(
        "rebak-realworld",
        help=(
            "restore a real-world .bak on the current SQL Server and re-backup "
            "in the server's native format (e.g. NYCTaxi_Sample_2017.bak)"
        ),
    )
    rr_src = rr_p.add_mutually_exclusive_group(required=True)
    rr_src.add_argument(
        "--source",
        metavar="BAK",
        help="path to a specific source .bak file",
    )
    rr_src.add_argument(
        "--scan-dir",
        metavar="DIR",
        help=(
            "scan a directory for candidate .bak files (skips files whose name "
            "already ends with a standard year: 2017/2019/2022/2025)"
        ),
    )
    rr_p.add_argument(
        "--out-dir",
        default=None,
        metavar="DIR",
        help="output directory (default: same dir as source / scan-dir)",
    )
    rr_p.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing outputs; also rebak standard-year sources",
    )

    reg_p = sub.add_parser(
        "register-bak",
        help="restore a .bak fixture to SQL Server and write ground-truth .stats.json",
    )
    reg_p.add_argument("bak", help="path to the .bak file")
    reg_p.add_argument("--db-name", default="", help="database name override")
    reg_p.add_argument(
        "--keep", action="store_true", help="don't drop the DB after collecting stats"
    )
    reg_p.add_argument("--out", default=None, help="output .stats.json path override")
    reg_p.add_argument(
        "--cells-only",
        action="store_true",
        help="capture only the .cells/ sidecar; leave .stats.json untouched",
    )

    all_p = sub.add_parser(
        "register-all",
        help="register every .bak in tests/fixtures/ that has no .stats.json (or .cells/) yet",
    )
    all_p.add_argument(
        "--fixture-dir",
        dest="reg_fixture_dir",
        default=None,
        help="directory to scan for .bak files (overrides global --fixture-dir)",
    )
    all_p.add_argument(
        "--force",
        action="store_true",
        help="re-register even if .stats.json / .cells/ already exists",
    )
    all_p.add_argument("--keep", action="store_true", help="don't drop DBs after collecting stats")
    all_p.add_argument(
        "--cells-only",
        action="store_true",
        help=(
            "capture only the .cells/ sidecar for fixtures that already have "
            ".stats.json but no .cells/; skips stats collection (no churn)"
        ),
    )

    ho_p = sub.add_parser(
        "register-headeronly-all",
        help=(
            "capture <bak>.bak.headeronly.json LSN sidecars for every .bak that "
            "does not have one yet (uses RESTORE HEADERONLY only, no full restore)"
        ),
    )
    ho_p.add_argument(
        "--fixture-dir",
        dest="ho_fixture_dir",
        default=None,
        help="directory to scan (overrides global --fixture-dir)",
    )
    ho_p.add_argument(
        "--force",
        action="store_true",
        help="re-capture even if .headeronly.json already exists",
    )

    meta_p = sub.add_parser(
        "register-metadata-all",
        help=(
            "capture <bak>.metadata.json sidecars (constraints, indexes, modules, "
            "security, statistics, plan guides, Query Store) for every .bak that "
            "does not have one yet (requires a full restore per fixture)"
        ),
    )
    meta_p.add_argument(
        "--fixture-dir",
        dest="meta_fixture_dir",
        default=None,
        help="directory to scan (overrides global --fixture-dir)",
    )
    meta_p.add_argument(
        "--force",
        action="store_true",
        help="re-capture even if .metadata.json already exists",
    )

    layout_p = sub.add_parser("layout", help="layoutcoverage_full.bak")
    layout_p.add_argument("--compressed", action="store_true")

    catalog_p = sub.add_parser("catalog", help="catalog_ss{engine}.bak")
    catalog_p.add_argument("--engine", required=True, choices=("2012", "2016", "2019", "2022"))
    catalog_p.add_argument("--compressed", action="store_true")

    matrix_p = sub.add_parser("version-matrix", help="all catalog_ss*.bak fixtures")
    matrix_p.add_argument("--engine", action="append", choices=("2012", "2016", "2019", "2022"))
    matrix_p.add_argument("--v1-inspect", action="store_true")

    av_p = sub.add_parser(
        "all-versions",
        help="run fixture suite against every discovered SQL Server version "
        f"(default suite: {_ALL_VERSIONS_SUITE}); outputs to "
        "tests/fixtures_YEAR/ per version",
    )
    av_p.add_argument(
        "--version",
        action="append",
        dest="versions",
        metavar="YEAR",
        help="limit to specific SQL Server version(s) (e.g. --version 2017 --version 2019); "
        "default: all discovered instances",
    )
    av_p.add_argument(
        "--suite",
        action="append",
        dest="suite",
        metavar="CMD",
        choices=sorted(_COMMANDS),
        help="fixture command(s) to run per version (repeatable; default: all commands "
        "in _ALL_VERSIONS_SUITE). Choices are listed alphabetically.",
    )
    av_p.add_argument(
        "--suite-all",
        action="store_true",
        dest="suite_all",
        help="run the complete _ALL_VERSIONS_SUITE (all commands included in the "
        "cross-version default; useful after adding new fixtures to regenerate "
        "everything without specifying each command individually)",
    )
    av_p.add_argument(
        "--base-dir",
        default="tests",
        help="parent directory for per-version fixture dirs (default: tests/)",
    )
    av_p.add_argument(
        "--heap-scale-rows",
        type=int,
        default=1_000,
        metavar="N",
        help=(
            "rows per table for the heap-scale command "
            "(default: 1000). Use 50000 to trigger the IAM traversal bug."
        ),
    )
    av_p.add_argument(
        "--tabletype-rows",
        type=int,
        default=4,
        metavar="N",
        help=(
            "total rows per table for the tabletype command (default: 4). "
            "Extra rows beyond 4 use only the id column for IAM-scale testing."
        ),
    )

    args = parser.parse_args(argv)

    # Apply global --fixture-dir before anything else so make_*.py modules
    # pick up FIXTURE_DIR when they are imported and evaluate OUT_PATH.
    # Relative paths are resolved from the repo root (parent of tools/), not from
    # CWD, so the command works correctly regardless of which directory the user
    # runs it from (e.g. from inside tests/fixtures_realworld/).
    # For register-all, the subparser uses dest="reg_fixture_dir" to avoid
    # argparse clobbering the global --fixture-dir value with the subparser default.
    _raw_fdir = (
        args.fixture_dir
        or getattr(args, "reg_fixture_dir", None)
        or getattr(args, "ho_fixture_dir", None)
        or getattr(args, "meta_fixture_dir", None)
    )
    if _raw_fdir and args.command != "all-versions":
        _fdir = Path(_raw_fdir)
        if not _fdir.is_absolute():
            _fdir = Path(__file__).resolve().parent.parent / _fdir
        os.environ["FIXTURE_DIR"] = str(_fdir.resolve())

    # Apply global --server.  Clear any stale FIXTURE_CONTAINER so that
    # bootstrap_fixture_env() re-resolves the container from the blob for this
    # server instead of reusing one cached from a prior run in the same process.
    if args.server:
        os.environ["FIXTURE_SERVER_NAME"] = args.server
        os.environ.pop("FIXTURE_CONTAINER", None)
        os.environ.pop("FIXTURE_DBA_PASSWORD", None)

    if args.command == "env":
        return _print_env_exports()

    if args.command == "all-versions":
        cmd_extra: dict[str, list[str]] = {}
        if args.heap_scale_rows != 1_000:
            cmd_extra["heap-scale"] = ["--rows", str(args.heap_scale_rows)]
        if args.tabletype_rows != 4:
            cmd_extra["tabletype"] = ["--rows", str(args.tabletype_rows)]
        # --suite-all overrides any explicit --suite list; falls back to
        # _ALL_VERSIONS_SUITE when neither flag is given.
        if args.suite_all:
            resolved_suite: list[str] = list(_ALL_VERSIONS_SUITE)
        else:
            resolved_suite = args.suite or list(_ALL_VERSIONS_SUITE)
        return _run_all_versions(
            versions=args.versions,
            fixture_base=Path(args.base_dir),
            suite=resolved_suite,
            cmd_extra=cmd_extra,
        )

    server, container = bootstrap_fixture_env()
    print(f"==> fixture target: server={server} container={container}", file=sys.stderr)

    if args.command == "layout":
        return _run_layout(args.compressed)
    if args.command == "tabletype":
        return _run_tabletype(rows=args.rows)
    if args.command == "heap-scale":
        return _run_heap_scale(rows=args.rows)
    if args.command == "ndf":
        return _run_ndf(force=getattr(args, "force", False))
    if args.command == "feature":
        return _run_feature(force=getattr(args, "force", False))
    if args.command == "archive-null":
        return _run_archive_null(force=getattr(args, "force", False))
    if args.command == "archive-columnstore-partition":
        return _run_archive_columnstore_partition(force=getattr(args, "force", False))
    if args.command == "archive-columnstore-types":
        return _run_archive_columnstore_types(force=getattr(args, "force", False))
    if args.command == "archive-columnstore-types-random":
        return _run_archive_columnstore_types_random(force=getattr(args, "force", False))
    if args.command == "pfor-columnstore":
        return _run_pfor_columnstore(force=getattr(args, "force", False))
    if args.command == "pfor-columnstore-random":
        return _run_pfor_columnstore_random(force=getattr(args, "force", False))
    if args.command == "archive-single-chunk":
        return _run_archive_single_chunk(force=getattr(args, "force", False))
    if args.command == "archive-single-chunk-random":
        return _run_archive_single_chunk_random(force=getattr(args, "force", False))
    if args.command == "capture-verifier-sidecar":
        return _run_capture_verifier_sidecar(
            force=getattr(args, "force", False),
            bak=getattr(args, "bak", []),
            all_=getattr(args, "all", False),
            keep=getattr(args, "keep", False),
            fresh=getattr(args, "fresh", False),
        )
    if args.command == "xml-heap":
        return _run_xml_heap(force=getattr(args, "force", False))
    if args.command == "sparse":
        return _run_sparse(force=getattr(args, "force", False))
    if args.command == "forwarded-records":
        return _run_forwarded_records(force=getattr(args, "force", False))
    if args.command == "ghost-records":
        return _run_ghost_records(force=getattr(args, "force", False))
    if args.command == "multi-rowgroup":
        return _run_multi_rowgroup(force=getattr(args, "force", False))
    if args.command == "cci-string-dict-regression":
        return _run_cci_string_dict_regression(force=getattr(args, "force", False))
    if args.command == "max-row-width":
        return _run_max_row_width(force=getattr(args, "force", False))
    if args.command == "surrogate-pairs":
        return _run_surrogate_pairs(force=getattr(args, "force", False))
    if args.command == "high-slot-density":
        return _run_high_slot_density(force=getattr(args, "force", False))
    if args.command == "cci-switch":
        return _run_cci_switch(force=getattr(args, "force", False))
    if args.command == "cci-reorganize":
        return _run_cci_reorganize(force=getattr(args, "force", False))
    if args.command == "covering-index":
        return _run_covering_index(force=getattr(args, "force", False))
    if args.command == "sql-variant-extract":
        return _run_sql_variant_extract(force=getattr(args, "force", False))
    if args.command == "filtered-ncci":
        return _run_filtered_ncci(force=getattr(args, "force", False))
    if args.command == "ncci-heap":
        return _run_ncci_heap(force=getattr(args, "force", False))
    if args.command == "identity-coverage":
        return _run_identity_coverage(force=getattr(args, "force", False))
    if args.command == "extended-properties":
        return _run_extended_properties(force=getattr(args, "force", False))
    if args.command == "rowversion-extract":
        return _run_rowversion_extract(force=getattr(args, "force", False))
    if args.command == "hierarchyid-extract":
        return _run_hierarchyid_extract(force=getattr(args, "force", False))
    if args.command == "cci-computed":
        return _run_cci_computed(force=getattr(args, "force", False))
    if args.command == "cci-btree-nci":
        return _run_cci_btree_nci(force=getattr(args, "force", False))
    if args.command == "ordered-cci":
        return _run_ordered_cci(force=getattr(args, "force", False))
    if args.command == "backup-blocksize":
        return _run_backup_blocksize(force=getattr(args, "force", False))
    if args.command == "cci-string-minmax":
        return _run_cci_string_minmax(force=getattr(args, "force", False))
    if args.command == "cci-enc5-largepool":
        return _run_cci_enc5_largepool(force=getattr(args, "force", False))
    if args.command == "cci-enc5-largepool-matrix":
        return _run_cci_enc5_largepool_matrix(force=getattr(args, "force", False))
    if args.command == "xml-index":
        return _run_xml_index(force=getattr(args, "force", False))
    if args.command == "spatial-index":
        return _run_spatial_index(force=getattr(args, "force", False))
    if args.command == "alias-types":
        return _run_alias_types(force=getattr(args, "force", False))
    if args.command == "typed-xml":
        return _run_typed_xml(force=getattr(args, "force", False))
    if args.command == "spatial-edge":
        return _run_spatial_edge(force=getattr(args, "force", False))
    if args.command == "float-extreme":
        return _run_float_extreme(force=getattr(args, "force", False))
    if args.command == "rowstore-lob-image":
        return _run_rowstore_lob_image(force=getattr(args, "force", False))
    if args.command == "rowstore-lob-markup":
        return _run_rowstore_lob_markup(force=getattr(args, "force", False))
    if args.command == "rowstore-hash-pii":
        return _run_rowstore_hash_pii(force=getattr(args, "force", False))
    if args.command == "realworld-numeric-digest":
        return _run_realworld_numeric_digest(force=getattr(args, "force", False))
    if args.command == "corrupt-metadata-confidence":
        return _run_corrupt_metadata_confidence(force=getattr(args, "force", False))
    if args.command == "nvarchar-max-u21":
        return _run_nvarchar_max_u21(force=getattr(args, "force", False))
    if args.command == "compressed-nvarchar":
        return _run_compressed_nvarchar(force=getattr(args, "force", False))
    if args.command == "torn-page":
        return _run_torn_page(force=getattr(args, "force", False))
    if args.command == "xtp-simple":
        return _run_xtp_simple(force=getattr(args, "force", False))
    if args.command == "xtp-probe":
        return _run_xtp_probe(force=getattr(args, "force", False))
    if args.command == "xtp-rich":
        return _run_xtp_rich(force=getattr(args, "force", False))
    if args.command == "xtp-checkpoint":
        return _run_xtp_checkpoint(force=getattr(args, "force", False))

    if args.command == "vector":
        return _run_vector(force=getattr(args, "force", False))
    if args.command == "native-json":
        return _run_native_json(force=getattr(args, "force", False))
    if args.command == "utf8-collation":
        return _run_utf8_collation(force=getattr(args, "force", False))
    if args.command == "tabletype-cci-large":
        return _run_tabletype_cci_large(force=getattr(args, "force", False))
    if args.command == "delta-rowgroup":
        return _run_delta_rowgroup(force=getattr(args, "force", False))
    if args.command == "enc-bak":
        return _run_enc_bak(force=getattr(args, "force", False))
    if args.command == "tde":
        return _run_tde(force=getattr(args, "force", False))
    if args.command == "boundary-datetime":
        return _run_boundary_datetime(force=getattr(args, "force", False))
    if args.command == "mixed-collation":
        return _run_mixed_collation(force=getattr(args, "force", False))
    if args.command == "ncci-types":
        return _run_ncci_types(force=getattr(args, "force", False))
    if args.command == "cci-lob":
        return _run_cci_lob(force=getattr(args, "force", False))
    if args.command == "cci-types-large":
        return _run_cci_types_large(force=getattr(args, "force", False))
    if args.command == "cci-extended":
        return _run_cci_extended(force=getattr(args, "force", False))
    if args.command == "row-boundary":
        return _run_row_boundary(force=getattr(args, "force", False))
    if args.command == "cci-varbinary-micro":
        return _run_cci_varbinary_micro(force=getattr(args, "force", False))
    if args.command == "cci-binary-varbinary-compare":
        return _run_cci_binary_varbinary_compare(force=getattr(args, "force", False))
    if args.command == "cci-varbinary-probe":
        return _run_cci_varbinary_probe(force=getattr(args, "force", False))
    if args.command == "cci-bitpack-probe-int":
        return _run_cci_bitpack_probe_int(force=getattr(args, "force", False))
    if args.command == "cci-bitpack-probe-bigint":
        return _run_cci_bitpack_probe_bigint(force=getattr(args, "force", False))
    if args.command == "cci-bitpack-probe-highbase":
        return _run_cci_bitpack_probe_highbase(force=getattr(args, "force", False))
    if args.command == "catalog":
        return _run_catalog(args.engine, args.compressed)
    if args.command == "version-matrix":
        return _run_version_matrix(args.engine, args.v1_inspect)
    if args.command == "rebak-realworld":
        return _run_rebak_realworld(
            source=getattr(args, "source", None),
            scan_dir=getattr(args, "scan_dir", None),
            out_dir=getattr(args, "out_dir", None),
            force=args.force,
        )
    if args.command == "register-bak":
        return _run_register_bak(
            args.bak,
            args.db_name,
            args.keep,
            args.out,
            cells_only=getattr(args, "cells_only", False),
        )
    if args.command == "register-all":
        # FIXTURE_DIR was already resolved and set in the env block above; use it.
        # Fall back to the subparser's --fixture-dir, then the 2022 default.
        fixture_dir = (
            os.environ.get("FIXTURE_DIR")
            or getattr(args, "reg_fixture_dir", None)
            or "tests/fixtures_2022"
        )
        return _run_register_all(
            fixture_dir,
            args.force,
            args.keep,
            cells_only=getattr(args, "cells_only", False),
        )
    if args.command == "register-headeronly-all":
        from tools.register_bak import register_headeronly_all
        fixture_dir = (
            os.environ.get("FIXTURE_DIR")
            or getattr(args, "ho_fixture_dir", None)
            or "tests/fixtures_2022"
        )
        return register_headeronly_all(
            Path(fixture_dir),
            skip_existing=not args.force,
        )
    if args.command == "register-metadata-all":
        from tools.register_bak import register_metadata_all
        fixture_dir = (
            os.environ.get("FIXTURE_DIR")
            or getattr(args, "meta_fixture_dir", None)
            or "tests/fixtures_2022"
        )
        return register_metadata_all(
            Path(fixture_dir),
            skip_existing=not getattr(args, "force", False),
        )

    if args.command == "v11-probe":
        return _run_v11_probe(force=getattr(args, "force", False))
    if args.command == "g44-probe":
        return _run_g44_probe()
    if args.command == "v13-probe":
        return _run_v13_probe(force=getattr(args, "force", False))
    if args.command == "temporal-hidden":
        return _run_temporal_hidden(force=getattr(args, "force", False))
    if args.command == "pagecomp-anchor":
        return _run_pagecomp_anchor(force=getattr(args, "force", False))
    if args.command == "pagecomp-long-prefix":
        return _run_pagecomp_long_prefix(force=getattr(args, "force", False))
    if args.command == "v13-hidden-probe":
        return _run_v13_hidden_probe(force=getattr(args, "force", False))
    if args.command == "dirty-v4":
        return _run_dirty_v4(force=getattr(args, "force", False))
    if args.command == "dirty-cci":
        return _run_dirty_cci(force=getattr(args, "force", False))
    if args.command == "tde-page":
        return _run_tde_page(force=getattr(args, "force", False))
    runner = _COMMANDS[args.command]
    return runner()


if __name__ == "__main__":
    sys.exit(main())
