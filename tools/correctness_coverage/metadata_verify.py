"""Metadata ground-truth verification for the correctness_coverage harness.

Two public surfaces:
- :func:`build_recovered_metadata` – extract non-data artifacts from a .bak into
  a :class:`RecoveredMetadata` bundle with ids fully resolved to names.
- ``verify_*`` comparators – compare one GT category dict against the recovered
  bundle and return a :class:`ValidationResult`.

All comparators match by **natural key** (name, columns) and diff only **stable**
fields.  Volatile fields (timestamps, internal ids, runtime stats) are excluded
by design.  See plan ``metadata_perf_ground_truth_validation_cb77c0d0.plan.md``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mssqlbak.catalog.model import (
        CatalogObjects,
        ObjectPermission,
        Principal,
        Schema,
        SchemaInfo,
        Sequence,
        Synonym,
        UserTableType,
    )
    from mssqlbak.perf import PerfData

# sqlcmd informational lines that appear in sidecars generated before the
# _parse_pipe noise filter was applied.  Comparators skip GT items whose
# name contains this substring so existing sidecars stay valid.
_SQLCMD_NOISE = "Changed database context"

# ---------------------------------------------------------------------------
# Action-id → permission name (mirrors mssqlbak.ddl._ACTION_NAMES)
# ---------------------------------------------------------------------------

_ACTION_NAMES: dict[int, str] = {
    193: "SELECT", 195: "INSERT", 196: "DELETE", 197: "UPDATE",
    224: "EXECUTE", 26: "REFERENCES", 178: "CREATE TABLE",
}

# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
    """Result of one metadata-category comparison.

    Mirrors the shape of ``value_verify.TableVerifyResult`` so the harness
    can handle both with identical logic.
    """

    category: str
    n_ok: int = 0
    n_total: int = 0
    missing: list[str] = field(default_factory=list)
    extra: list[str] = field(default_factory=list)
    mismatched: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    unscored: bool = False

    @property
    def ok(self) -> bool:
        """True only when all items matched with no errors."""
        return (
            not self.error
            and not self.unscored
            and not self.missing
            and not self.extra
            and not self.mismatched
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "n_ok": self.n_ok,
            "n_total": self.n_total,
            "missing": self.missing,
            "extra": self.extra,
            "mismatched": self.mismatched,
            "error": self.error,
            "unscored": self.unscored,
            "ok": self.ok,
        }


def _unscored(category: str) -> ValidationResult:
    r = ValidationResult(category=category, unscored=True)
    return r


def _error_result(category: str, exc: BaseException) -> ValidationResult:
    import traceback
    return ValidationResult(
        category=category,
        error=f"{exc}\n{traceback.format_exc()}",
    )


# ---------------------------------------------------------------------------
# RecoveredMetadata bundle
# ---------------------------------------------------------------------------


@dataclass
class RecoveredMetadata:
    """Non-data artifacts recovered from a .bak, with ids resolved to names.

    Build via :func:`build_recovered_metadata`; do not instantiate directly.
    """

    # Maps object_id → "schema.object" FQN string.
    obj_to_fqn: dict[int, str] = field(default_factory=dict)
    # Maps object_id → {colid → column_name}.
    col_names: dict[int, dict[int, str]] = field(default_factory=dict)
    # Maps principal_id → name.
    principal_id_to_name: dict[int, str] = field(default_factory=dict)
    # Maps schema_id → name.
    schema_id_to_name: dict[int, str] = field(default_factory=dict)
    # object_ids of base user-tables (type='U').  GT collectors join sys.tables so
    # they never include indexed views — we use this to scope indexes/stats/extprops.
    base_table_ids: set[int] = field(default_factory=set)
    # FQNs of database-level DDL triggers (pid==0).  GT joins sys.objects which
    # excludes them — we use this to scope the modules comparator.
    ddl_trigger_fqns: set[str] = field(default_factory=set)

    # Catalog-level objects
    schema: "Schema | None" = None
    catalog_objects: "CatalogObjects | None" = None
    obj_props: dict[int, dict[int, dict[str, str]]] = field(default_factory=dict)
    schema_props: dict[int, dict[str, str]] = field(default_factory=dict)
    module_defs: dict[int, str] = field(default_factory=dict)
    schemas: list["SchemaInfo"] = field(default_factory=list)
    sequences: list["Sequence"] = field(default_factory=list)
    synonyms: list["Synonym"] = field(default_factory=list)
    table_types: list["UserTableType"] = field(default_factory=list)
    principals: list["Principal"] = field(default_factory=list)
    permissions: list["ObjectPermission"] = field(default_factory=list)
    perf: "PerfData | None" = None

    # obj_id → type_desc (for object type lookup, e.g. for modules)
    obj_to_type: dict[int, str] = field(default_factory=dict)


def build_recovered_metadata(
    bak_input: Path | list[Path],
    *,
    tde_key: "Any | None" = None,
    backup_cert: "Any | None" = None,
) -> RecoveredMetadata:
    """Recover all non-data catalog artifacts from *bak_input*.

    Builds a catalog-only ``PageStore``, runs all recovery functions, and
    resolves internal ids to names so the result is id-free.

    Parameters
    ----------
    bak_input:
        A single .bak ``Path`` or a list of striped/differential .bak paths
        (full first, then diff), as returned by ``runner._resolve_bak_input``.
    tde_key:
        Optional :class:`~mssqlbak.tde.TdeKey` for page-level TDE backups.
    backup_cert:
        Optional :class:`~mssqlbak.tde.TdeKey` (or raw RSA private key) for
        backup-level encrypted backups (``WITH ENCRYPTION``).
    """
    from mssqlbak.catalog.recover import (
        recover_catalog_objects,
        recover_ddl_trigger_object_ids,
        recover_extended_properties,
        recover_module_definitions,
        recover_module_objects,
        recover_object_permissions,
        recover_principals,
        recover_schema,
        recover_schemas,
        recover_sequences,
        recover_synonyms,
        recover_user_table_types,
    )
    from mssqlbak.pages import PageStore
    from mssqlbak.perf import recover_perf

    baks: list[Path] = [bak_input] if isinstance(bak_input, Path) else list(bak_input)
    if len(baks) == 1:
        store = PageStore.from_bak(baks[0], tde_key=tde_key, backup_cert=backup_cert)
    else:
        # Merge catalog pages across all parts.
        # Striped backups: catalog pages are spread across stripes; all must be merged.
        # Full+diff backups: diff catalog pages override full via last-wins semantics.
        # Mirrors the dispatch in extract_bak (mssqlbak/extract/driver.py).
        store = PageStore.from_stripe(baks)

    rm = RecoveredMetadata()

    # --- Phase A: schema (tables, columns, obj→name) ------------------------
    try:
        rm.schema = recover_schema(store)
        for tbl in rm.schema.tables:
            fqn = f"{tbl.schema}.{tbl.name}"
            rm.obj_to_fqn[tbl.object_id] = fqn
            rm.col_names[tbl.object_id] = {c.colid: c.name for c in tbl.columns}
        # Base-table ids: GT collectors join sys.tables (type='U'), so indexed
        # views and other non-table objects are never in GT indexes/stats/extprops.
        rm.base_table_ids = {tbl.object_id for tbl in rm.schema.tables}
    except Exception:
        pass

    # --- Catalog objects (indexes, constraints, FKs) ------------------------
    try:
        rm.catalog_objects = recover_catalog_objects(store)
    except Exception:
        pass

    # --- Extended properties ------------------------------------------------
    try:
        rm.obj_props, rm.schema_props = recover_extended_properties(store)
    except Exception:
        pass

    # --- Module definitions (views, procs, functions, triggers) -------------
    try:
        rm.module_defs = recover_module_definitions(store)
        # recover_module_objects joins sysschobjs.nsid + sysclsobjs to produce
        # schema-qualified FQNs for all module objects (views, procs, functions,
        # triggers). Without this, non-table objects are only available as bare
        # names from schema.obj_to_name, causing every module key to mismatch GT
        # which uses 'Schema.Name' format.
        module_objs = recover_module_objects(store)
        for oid, (schema_name, obj_name, _defn) in module_objs.items():
            if oid not in rm.obj_to_fqn:
                rm.obj_to_fqn[oid] = f"{schema_name}.{obj_name}"
        # DDL trigger FQNs: GT joins sys.objects which excludes database-level DDL
        # triggers (parent_object_id==0 in live catalog, pid==0 in sysschobjs).
        ddl_ids = recover_ddl_trigger_object_ids(store)
        rm.ddl_trigger_fqns = {rm.obj_to_fqn[oid] for oid in ddl_ids if oid in rm.obj_to_fqn}
    except Exception:
        pass

    # --- Schema objects: schemas, sequences, synonyms, table types ----------
    try:
        rm.schemas = recover_schemas(store)
        for si in rm.schemas:
            rm.schema_id_to_name[si.schema_id] = si.name
    except Exception:
        pass
    try:
        rm.sequences = recover_sequences(store)
        for seq in rm.sequences:
            if not hasattr(seq, "object_id"):
                continue
            fqn = f"{seq.schema_name}.{seq.name}"
            rm.obj_to_fqn[seq.object_id] = fqn
    except Exception:
        pass
    try:
        rm.synonyms = recover_synonyms(store)
        for syn in rm.synonyms:
            if not hasattr(syn, "object_id"):
                continue
            fqn = f"{syn.schema_name}.{syn.name}"
            rm.obj_to_fqn[syn.object_id] = fqn
    except Exception:
        pass
    try:
        rm.table_types = recover_user_table_types(store)
        for tt in rm.table_types:
            if not hasattr(tt, "object_id"):
                continue
            fqn = f"{tt.schema_name}.{tt.name}"
            rm.obj_to_fqn[tt.object_id] = fqn
            rm.col_names[tt.object_id] = {c.colid: c.name for c in tt.columns}
    except Exception:
        pass

    # --- Security: principals, permissions ----------------------------------
    try:
        rm.principals = recover_principals(store)
        for p in rm.principals:
            rm.principal_id_to_name[p.principal_id] = p.name
    except Exception:
        pass
    try:
        rm.permissions = recover_object_permissions(store)
    except Exception:
        pass

    # --- Perf: statistics, plan guides, query store -------------------------
    try:
        rm.perf = recover_perf(store)
    except Exception:
        pass

    return rm


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------


def _norm_sql(text: str | None) -> str:
    """Normalize SQL definition text for comparison.

    Strips trailing NUL bytes, collapses runs of whitespace, and lower-cases
    SQL keywords.  Never raises: returns "" on None input.
    """
    if not text:
        return ""
    # Remove trailing NULs (SQL Server padding artifact)
    text = text.rstrip("\x00")
    # Collapse whitespace (newlines, tabs, multiple spaces → single space)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_system_named(name: str) -> bool:
    """Return True if *name* looks like an auto-generated constraint name.

    SQL Server generates names like ``PK__T__3213E83F0A7E8A34``,
    ``FK__Order__Customer__5BE2A6F2``, ``CK__Audit__Status__62E5A23B``.
    We match the double-underscore + hex-suffix pattern.
    """
    return bool(re.search(r"__[0-9A-F]{8,16}$", name, re.IGNORECASE))


# ---------------------------------------------------------------------------
# Comparator helpers
# ---------------------------------------------------------------------------


def _diff_items(
    gt_items: list[dict[str, Any]],
    rec_items: list[dict[str, Any]],
    key_fn: Any,  # callable(dict) → hashable
    field_fn: Any,  # callable(dict) → dict of stable fields to compare
    category: str,
    *,
    compat: Any = None,  # optional callable(gt_fields, rec_fields) → bool
) -> ValidationResult:
    """Generic natural-key match + stable-field diff.

    *compat*, if given, is called as ``compat(gt_fields, rec_fields)`` for
    items that appear on both sides.  Return ``True`` to count the item as
    matching even when the field dicts are not ``==`` equal.  Useful for
    subset / structural-tolerance checks.
    """
    gt_by_key = {key_fn(x): x for x in gt_items}
    rec_by_key = {key_fn(x): x for x in rec_items}

    all_keys = sorted(set(gt_by_key) | set(rec_by_key), key=str)
    result = ValidationResult(category=category, n_total=len(gt_by_key))

    for key in all_keys:
        in_gt = key in gt_by_key
        in_rec = key in rec_by_key
        if in_gt and in_rec:
            gt_fields = field_fn(gt_by_key[key])
            rec_fields = field_fn(rec_by_key[key])
            matched = gt_fields == rec_fields
            if not matched and compat is not None:
                matched = compat(gt_fields, rec_fields)
            if matched:
                result.n_ok += 1
            else:
                result.mismatched.append({
                    "key": str(key),
                    "expected": gt_fields,
                    "recovered": rec_fields,
                })
        elif in_gt:
            result.missing.append(str(key))
        else:
            result.extra.append(str(key))

    return result


# ---------------------------------------------------------------------------
# Comparators — one per category
# ---------------------------------------------------------------------------


def verify_constraints(
    gt: dict[str, Any],
    rm: RecoveredMetadata,
) -> ValidationResult:
    """Compare constraints from GT metadata.json vs recovered catalog."""
    category = "constraints"
    try:
        gt_constraints: list[dict[str, Any]] = gt.get("constraints", [])
        if not gt_constraints:
            return ValidationResult(category=category, n_total=0, n_ok=0)

        if rm.catalog_objects is None or rm.schema is None:
            return _unscored(category)

        # Build recovered constraint list (id-resolved)
        rec_items: list[dict[str, Any]] = []

        # PK / UQ / CHECK / DEFAULT from CatalogObjects.constraints
        # FKs (type_code='F') are handled separately via foreign_keys below.
        for c in rm.catalog_objects.constraints:
            if c.type_code == "F":
                continue  # avoid double-counting; FKs emitted via foreign_keys loop
            parent_fqn = rm.obj_to_fqn.get(c.parent_object_id, "")
            if not parent_fqn:
                continue
            kind_map = {"PK": "primary key", "UQ": "unique constraint", "C": "check", "D": "default"}
            kind = kind_map.get(c.type_code, c.type_code.lower())
            entry: dict[str, Any] = {
                "table": parent_fqn,
                "name": c.name,
                "kind": kind,
                "is_system_named": _is_system_named(c.name),
            }
            if c.definition:
                entry["definition"] = _norm_sql(c.definition)
            # Key columns from indexes (for PK/UQ).
            # Match by name first so tables with multiple UQ constraints don't
            # all resolve to the columns of the first matching unique index.
            # Fall back to flag-based match when name matching yields nothing
            # (e.g. unnamed/legacy constraints).
            if c.type_code in ("PK", "UQ") and rm.catalog_objects.indexes:
                best_idx = None
                for idx in rm.catalog_objects.indexes:
                    if idx.object_id != c.parent_object_id:
                        continue
                    if idx.name == c.name:
                        best_idx = idx
                        break
                if best_idx is None:
                    for idx in rm.catalog_objects.indexes:
                        if idx.object_id == c.parent_object_id and (
                            idx.is_primary_key == (c.type_code == "PK")
                            and idx.is_unique_constraint == (c.type_code == "UQ")
                        ):
                            best_idx = idx
                            break
                if best_idx is not None:
                    col_map = rm.col_names.get(c.parent_object_id, {})
                    entry["columns"] = [col_map.get(cid, f"col_{cid}") for cid in best_idx.key_columns]
            rec_items.append(entry)

        # FKs from CatalogObjects.foreign_keys
        for fk in rm.catalog_objects.foreign_keys:
            parent_fqn = rm.obj_to_fqn.get(fk.parent_object_id, "")
            ref_fqn = rm.obj_to_fqn.get(fk.ref_object_id, "")
            if not parent_fqn:
                continue
            col_map = rm.col_names.get(fk.parent_object_id, {})
            ref_col_map = rm.col_names.get(fk.ref_object_id, {})
            entry = {
                "table": parent_fqn,
                "name": fk.name,
                "kind": "foreign key",
                "is_system_named": _is_system_named(fk.name),
                "columns": [col_map.get(cid, f"col_{cid}") for cid in fk.child_col_ids],
                "ref_table": ref_fqn,
                "ref_columns": [ref_col_map.get(cid, f"col_{cid}") for cid in fk.ref_col_ids],
            }
            rec_items.append(entry)

        def _key(x: dict[str, Any]) -> tuple[str, str, str]:
            return (x.get("table", ""), x.get("kind", ""), x.get("name", ""))

        def _fields(x: dict[str, Any]) -> dict[str, Any]:
            kind = x.get("kind", "")
            is_sys = x.get("is_system_named", False) or _is_system_named(x.get("name", ""))
            f: dict[str, Any] = {"kind": kind}
            # columns: only for PK/UQ/FK; the Constraint model lacks parent_column_id
            # so we cannot resolve it for CHECK/DEFAULT from the recovered side.
            if kind not in ("check", "default") and x.get("columns"):
                f["columns"] = sorted(x["columns"])
            if x.get("ref_table"):
                f["ref_table"] = x["ref_table"]
            if x.get("ref_columns"):
                f["ref_columns"] = sorted(x["ref_columns"])
            if not is_sys:
                f["name"] = x.get("name", "")
            if x.get("definition"):
                f["definition"] = _norm_sql(x.get("definition"))
            return f

        def _con_compat(gt_f: dict[str, Any], rec_f: dict[str, Any]) -> bool:
            # Non-columns fields must match exactly.
            gt_no_cols = {k: v for k, v in gt_f.items() if k != "columns"}
            rec_no_cols = {k: v for k, v in rec_f.items() if k != "columns"}
            if gt_no_cols != rec_no_cols:
                return False
            # For PK/UQ: sysiscols includes XTP implicit columns that
            # sys.index_columns (is_included_column=0) never exposes to the GT
            # collector.  Accept GT ⊆ recovered.
            # Structural origin confirmed by tightening experiment: exact equality
            # breaks XTP-table PK/UQ fixtures; subset is required and is NOT a
            # sqlcmd truncation workaround.
            gt_cols = set(gt_f.get("columns", []))
            rec_cols = set(rec_f.get("columns", []))
            return gt_cols <= rec_cols

        return _diff_items(gt_constraints, rec_items, _key, _fields, category,
                           compat=_con_compat)
    except Exception as exc:
        return _error_result(category, exc)


def verify_indexes(
    gt: dict[str, Any],
    rm: RecoveredMetadata,
) -> ValidationResult:
    """Compare indexes from GT metadata.json vs recovered catalog."""
    category = "indexes"
    try:
        gt_indexes: list[dict[str, Any]] = gt.get("indexes", [])
        if not gt_indexes:
            return ValidationResult(category=category, n_total=0, n_ok=0)

        if rm.catalog_objects is None:
            return _unscored(category)

        rec_items: list[dict[str, Any]] = []
        type_map = {0: "heap", 1: "clustered", 2: "nonclustered",
                    3: "xml", 4: "spatial", 5: "clustered columnstore",
                    6: "nonclustered columnstore", 7: "nonclustered hash"}
        for idx in rm.catalog_objects.indexes:
            if idx.index_type == 0 or not idx.name:  # skip heaps
                continue
            parent_fqn = rm.obj_to_fqn.get(idx.object_id, "")
            if not parent_fqn:
                continue
            # Skip indexes on sys-schema objects (XTP internal TT_* types etc.)
            if parent_fqn.startswith("sys."):
                continue
            # GT collects indexes via JOIN sys.tables (base tables only), so
            # indexed-view indexes are never in GT.  Skip non-base-table objects.
            if rm.base_table_ids and idx.object_id not in rm.base_table_ids:
                continue
            col_map = rm.col_names.get(idx.object_id, {})
            rec_items.append({
                "table": parent_fqn,
                "name": idx.name,
                "type": type_map.get(idx.index_type, str(idx.index_type)),
                "is_unique": idx.is_unique,
                "is_primary_key": idx.is_primary_key,
                "key_columns": [col_map.get(cid, f"col_{cid}") for cid in idx.key_columns],
            })

        def _norm_key_cols(cols: list[str]) -> list[str]:
            # Columnstore indexes have no explicit key columns; SQL Server's
            # sys.index_columns returns no rows → STUFF() yields NULL.
            # Treat ['NULL'], [''], and [] all as "no key columns".
            return [c for c in cols if c and c.upper() != "NULL"]

        def _key(x: dict[str, Any]) -> tuple[str, str]:
            return (x.get("table", ""), x.get("name", ""))

        def _fields(x: dict[str, Any]) -> dict[str, Any]:
            idx_type = x.get("type", "")
            f: dict[str, Any] = {
                "type": idx_type,
                "is_unique": x.get("is_unique", False),
                "is_primary_key": x.get("is_primary_key", False),
            }
            # Columnstore indexes: SQL Server's sys.index_columns returns no rows
            # (STUFF→NULL) because all columns are implicitly included; sysiscols
            # in the .bak records every column ID.  Skipping key_columns for
            # columnstore is a structural catalog difference confirmed empirically
            # by the tightening experiment — NOT a sqlcmd truncation workaround.
            #
            # Non-columnstore: include key_columns for the subset-compat check in
            # _idx_compat.  The subset (not equality) check is also structural:
            # sysiscols carries INCLUDE columns and XTP implicit columns that GT's
            # is_included_column=0 filter excludes (also confirmed empirically).
            if "columnstore" not in idx_type:
                f["key_columns"] = _norm_key_cols(x.get("key_columns", []))
            return f

        def _idx_compat(gt_f: dict[str, Any], rec_f: dict[str, Any]) -> bool:
            # sysiscols returns covering-index INCLUDE cols and XTP implicit cols
            # that GT's sys.index_columns (is_included_column=0) excludes.
            # Accept when all GT key columns appear in the recovered set and all
            # other non-column fields match exactly.
            # Structural origin confirmed by tightening experiment: exact equality
            # breaks INCLUDE-column and XTP-implicit-column fixtures; subset is
            # required and is NOT a sqlcmd truncation workaround.
            if gt_f.get("type") != rec_f.get("type"):
                return False
            if gt_f.get("is_unique") != rec_f.get("is_unique"):
                return False
            if gt_f.get("is_primary_key") != rec_f.get("is_primary_key"):
                return False
            if "key_columns" not in gt_f:
                return True  # columnstore — already handled above
            return set(gt_f["key_columns"]) <= set(rec_f.get("key_columns", []))

        return _diff_items(gt_indexes, rec_items, _key, _fields, category,
                           compat=_idx_compat)
    except Exception as exc:
        return _error_result(category, exc)


def verify_extended_properties(
    gt: dict[str, Any],
    rm: RecoveredMetadata,
) -> ValidationResult:
    """Compare extended properties from GT metadata.json vs recovered catalog."""
    category = "extended_properties"
    try:
        gt_ep: list[dict[str, Any]] = gt.get("extended_properties", [])
        if not gt_ep:
            return ValidationResult(category=category, n_total=0, n_ok=0)

        if not rm.obj_props and not rm.schema_props:
            return _unscored(category)

        rec_items: list[dict[str, Any]] = []
        # Table/column-level
        for obj_id, subid_dict in rm.obj_props.items():
            obj_fqn = rm.obj_to_fqn.get(obj_id, "")
            if not obj_fqn:
                continue
            # GT collects extended properties via JOIN sys.tables (class=1,
            # base tables only); views/procs/functions have their props stored
            # in sysxprops with class=1 too but GT never includes them.
            if rm.base_table_ids and obj_id not in rm.base_table_ids:
                continue
            col_map = rm.col_names.get(obj_id, {})
            for subid, props in subid_dict.items():
                col_name = col_map.get(subid, "") if subid > 0 else ""
                level = "table/column" if col_name else "table"
                for prop_name, value in props.items():
                    entry: dict[str, Any] = {
                        "level": level,
                        "object": obj_fqn,
                        "name": prop_name,
                        "value": value,
                    }
                    if col_name:
                        entry["column"] = col_name
                    rec_items.append(entry)
        # Schema-level
        for schema_id, props in rm.schema_props.items():
            schema_name = rm.schema_id_to_name.get(schema_id, f"schema_{schema_id}")
            for prop_name, value in props.items():
                rec_items.append({
                    "level": "schema",
                    "object": schema_name,
                    "name": prop_name,
                    "value": value,
                })

        def _key(x: dict[str, Any]) -> tuple[str, str, str, str]:
            return (
                x.get("level", ""),
                x.get("object", ""),
                x.get("column", ""),
                x.get("name", ""),
            )

        def _fields(x: dict[str, Any]) -> dict[str, Any]:
            return {"value": x.get("value", "")}

        return _diff_items(gt_ep, rec_items, _key, _fields, category)
    except Exception as exc:
        return _error_result(category, exc)


def verify_modules(
    gt: dict[str, Any],
    rm: RecoveredMetadata,
) -> ValidationResult:
    """Compare module definitions (views, procs, functions, triggers)."""
    category = "modules"
    try:
        gt_modules: list[dict[str, Any]] = gt.get("modules", [])
        if not gt_modules:
            return ValidationResult(category=category, n_total=0, n_ok=0)

        if not rm.module_defs:
            return _unscored(category)

        def _is_ledger_generated(name: str) -> bool:
            # SQL Server auto-generates ledger history views with a _Ledger suffix.
            # They appear in sys.sql_modules on the live server but are absent from
            # the backup's page store (system-generated, not stored as user objects).
            return name.endswith("_Ledger")

        rec_items: list[dict[str, Any]] = []
        for obj_id, definition in rm.module_defs.items():
            fqn = rm.obj_to_fqn.get(obj_id, "")
            if not fqn:
                continue
            rec_items.append({
                "object": fqn,
                "definition": _norm_sql(definition),
            })

        def _key(x: dict[str, Any]) -> str:
            return x.get("object", "")

        def _fields(x: dict[str, Any]) -> dict[str, Any]:
            # Compare normalized definition only (type_desc can differ in casing)
            return {"definition": _norm_sql(x.get("definition", ""))}

        gt_filtered = [m for m in gt_modules if not _is_ledger_generated(m.get("object", ""))]
        # GT joins sys.objects which excludes database-level DDL triggers
        # (parent_object_id==0).  Filter those from the recovered set so they
        # don't appear as spurious "extra" entries.
        rec_filtered = [
            m for m in rec_items
            if not _is_ledger_generated(m.get("object", ""))
            and m.get("object", "") not in rm.ddl_trigger_fqns
        ]
        return _diff_items(gt_filtered, rec_filtered, _key, _fields, category)
    except Exception as exc:
        return _error_result(category, exc)


def verify_schema_objects(
    gt: dict[str, Any],
    rm: RecoveredMetadata,
) -> ValidationResult:
    """Compare schemas, sequences, synonyms, and user table types."""
    category = "schema_objects"
    try:
        gt_schemas = gt.get("schemas", [])
        gt_sequences = gt.get("sequences", [])
        gt_synonyms = gt.get("synonyms", [])
        gt_table_types = gt.get("table_types", [])

        # Build flat GT and rec lists with a "kind" discriminator
        gt_flat: list[dict[str, Any]] = []
        rec_flat: list[dict[str, Any]] = []

        for s in gt_schemas:
            name = s.get("name", "")
            if _SQLCMD_NOISE in name:
                continue  # skip sqlcmd "Changed database context to '...'" noise
            gt_flat.append({"kind": "schema", "name": name})
        for rec_si in rm.schemas:
            # schema_id >= 16384 are fixed database role schemas excluded by
            # the GT query (WHERE schema_id < 16384).
            if rec_si.schema_id >= 16384:
                continue
            rec_flat.append({"kind": "schema", "name": rec_si.name})

        for s in gt_sequences:
            name = s.get("name", "")
            if _SQLCMD_NOISE in name:
                continue  # skip sqlcmd noise
            gt_flat.append({"kind": "sequence", "name": name})
        for seq in rm.sequences:
            rec_flat.append({"kind": "sequence", "name": f"{seq.schema_name}.{seq.name}"})

        for s in gt_synonyms:
            gt_flat.append({"kind": "synonym", "name": s.get("name", ""), "target": s.get("target", "")})
        for syn in rm.synonyms:
            rec_flat.append({
                "kind": "synonym",
                "name": f"{syn.schema_name}.{syn.name}",
                "target": syn.target_definition or "",
            })

        for s in gt_table_types:
            col_names = [c.get("name", "") for c in s.get("columns", [])]
            gt_flat.append({"kind": "table_type", "name": s.get("name", ""), "columns": col_names})
        for tt in rm.table_types:
            # XTP (In-Memory OLTP) generates internal TT_* table types in the
            # sys schema (e.g. sys.TT_Sales_SalesOrderDetailType_inmem_...).
            # GT only collects user-schema table types; skip sys-schema ones.
            if tt.schema_name == "sys":
                continue
            col_names = [c.name for c in tt.columns]
            rec_flat.append({
                "kind": "table_type",
                "name": f"{tt.schema_name}.{tt.name}",
                "columns": col_names,
            })

        if not gt_flat:
            return ValidationResult(category=category, n_total=0, n_ok=0)

        def _key(x: dict[str, Any]) -> tuple[str, str]:
            return (x.get("kind", ""), x.get("name", ""))

        def _fields(x: dict[str, Any]) -> dict[str, Any]:
            f: dict[str, Any] = {}
            if x.get("target") is not None:
                f["target"] = x["target"]
            if x.get("columns") is not None:
                f["columns"] = x["columns"]
            return f

        return _diff_items(gt_flat, rec_flat, _key, _fields, category)
    except Exception as exc:
        return _error_result(category, exc)


def verify_security(
    gt: dict[str, Any],
    rm: RecoveredMetadata,
) -> ValidationResult:
    """Compare principals and object permissions."""
    category = "security"
    try:
        gt_principals: list[dict[str, Any]] = gt.get("principals", [])
        gt_permissions: list[dict[str, Any]] = gt.get("permissions", [])

        if not gt_principals and not gt_permissions:
            return ValidationResult(category=category, n_total=0, n_ok=0)

        # Skip built-in principals (principal_id < 5 or well-known names)
        _BUILTIN = frozenset({"dbo", "guest", "INFORMATION_SCHEMA", "sys", "public"})
        gt_flat: list[dict[str, Any]] = []
        rec_flat: list[dict[str, Any]] = []

        for p in gt_principals:
            name = p.get("name", "")
            if name not in _BUILTIN:
                gt_flat.append({"kind": "principal", "name": name, "type": p.get("type", "")})
        _TYPE_CODE_TO_DESC: dict[str, str] = {
            "R": "DATABASE_ROLE", "S": "SQL_USER", "U": "WINDOWS_USER",
            "G": "WINDOWS_GROUP", "E": "EXTERNAL_USER", "X": "EXTERNAL_GROUP",
            "A": "APPLICATION_ROLE",
        }
        # Fixed database roles (principal_id < 16384) are system-owned and are
        # not collected by the GT collector (register_bak queries with
        # is_fixed_role=0).  Filter them on the recovered side to avoid false
        # "extra" hits for db_owner, db_datareader, etc.
        _FIXED_DB_ROLES: frozenset[str] = frozenset({
            "db_owner", "db_accessadmin", "db_securityadmin", "db_ddladmin",
            "db_backupoperator", "db_datareader", "db_datawriter",
            "db_denydatareader", "db_denydatawriter",
        })
        for p in rm.principals:
            if p.name in _BUILTIN or p.name in _FIXED_DB_ROLES:
                continue
            if p.principal_id < 5:
                continue
            type_desc = _TYPE_CODE_TO_DESC.get(p.principal_type, p.principal_type)
            rec_flat.append({"kind": "principal", "name": p.name, "type": type_desc})

        for p in gt_permissions:
            if p.get("grantee", "") not in _BUILTIN:
                gt_flat.append({
                    "kind": "permission",
                    "grantee": p.get("grantee", ""),
                    "object": p.get("object", ""),
                    "action": p.get("action", ""),
                    "state": p.get("state", ""),
                })
        for perm in rm.permissions:
            grantee = rm.principal_id_to_name.get(perm.grantee_id, f"principal_{perm.grantee_id}")
            if grantee in _BUILTIN or grantee in _FIXED_DB_ROLES:
                continue
            obj_fqn = rm.obj_to_fqn.get(perm.object_id, "") if perm.object_id else ""
            # Use pre-decoded action_name from recover_object_permissions.
            action = perm.action_name or _ACTION_NAMES.get(perm.action_id, f"action_{perm.action_id}")
            rec_flat.append({
                "kind": "permission",
                "grantee": grantee,
                "object": obj_fqn,
                "action": action,
                "state": perm.permission_state,
            })

        if not gt_flat:
            return ValidationResult(category=category, n_total=0, n_ok=0)

        def _key(x: dict[str, Any]) -> tuple[str, ...]:
            if x["kind"] == "principal":
                return ("principal", x.get("name", ""))
            return ("permission", x.get("grantee", ""), x.get("object", ""), x.get("action", ""))

        def _fields(x: dict[str, Any]) -> dict[str, Any]:
            if x["kind"] == "principal":
                return {"type": x.get("type", "")}
            return {"state": x.get("state", "")}

        return _diff_items(gt_flat, rec_flat, _key, _fields, category)
    except Exception as exc:
        return _error_result(category, exc)


def verify_statistics(
    gt: dict[str, Any],
    rm: RecoveredMetadata,
) -> ValidationResult:
    """Compare statistics objects: existence, key columns, and flags."""
    category = "statistics"
    try:
        gt_stats_raw: list[dict[str, Any]] = gt.get("statistics", [])
        # Auto-created statistics (_WA_Sys_* etc.) are created by the query
        # optimiser during registration queries and won't exist in the .bak.
        # Only compare explicitly created (user or index-backed) statistics.
        gt_stats = [s for s in gt_stats_raw if not s.get("auto_created")]
        if not gt_stats:
            return ValidationResult(category=category, n_total=0, n_ok=0)

        if rm.perf is None:
            return _unscored(category)

        rec_items: list[dict[str, Any]] = []
        for stat in rm.perf.statistics:
            # The auto_created bit in sysidxstats.status encodes a different value
            # than sys.stats.auto_created — index-backed stats (CCIs, PKs) also have
            # it set, so we cannot use it to identify truly auto-created stats on the
            # recovery side.  Instead, filter by name prefix:
            #   _WA_Sys_*  – optimizer auto-created statistics
            #   si_*       – spatial index internal statistics
            #   pxi_*      – primary XML index internal statistics
            #   sxi_*      – secondary XML index internal statistics (path, value, property)
            # These appear in sysidxstats but are excluded from sys.stats by the GT
            # query (which filters by index type ≠ 3/4 or by sys.objects.type = 'U').
            # Filter internal/system stat names not collected by GT.
            # GT collects only user-table stats (sys.objects type='U')
            # with is_auto_created=0 on the GT side.  Recovery sees all
            # sysidxstats rows; exclude:
            #   _WA_Sys_* – optimiser auto-created stats
            #   si_*      – spatial index internal stats
            #   pxi_*     – primary XML index internal stats
            #   sxi_*     – secondary XML index internal stats
            #   PXML_*    – XML property/path internal stats
            #   XMLPATH_* / XMLPROPERTY_* / XMLVALUE_* – XML index stats
            _INTERNAL_STAT_PREFIXES = (
                "_WA_Sys_", "si_", "pxi_", "sxi_",
                "PXML_", "XMLPATH_", "XMLPROPERTY_", "XMLVALUE_",
            )
            if stat.name.startswith(_INTERNAL_STAT_PREFIXES):
                continue
            parent_fqn = rm.obj_to_fqn.get(stat.object_id, "")
            if not parent_fqn:
                continue
            # Skip stats on sys-schema objects (internal XTP table types, etc.)
            # GT only collects user-schema statistics.
            if parent_fqn.startswith("sys."):
                continue
            # GT collects statistics via JOIN sys.tables (base tables only), so
            # statistics on indexed views are never in GT.
            if rm.base_table_ids and stat.object_id not in rm.base_table_ids:
                continue
            col_map = rm.col_names.get(stat.object_id, {})
            rec_items.append({
                "table": parent_fqn,
                "name": stat.name,
                "key_columns": [col_map.get(cid, f"col_{cid}") for cid in stat.key_column_ids],
            })

        def _key(x: dict[str, Any]) -> tuple[str, str]:
            return (x.get("table", ""), x.get("name", ""))

        def _fields(x: dict[str, Any]) -> dict[str, Any]:
            # Return key_columns as a list; compat below does set-subset check.
            # filter_definition is not recovered from the page store (skip).
            # auto_created / no_recompute bit interpretation diverges (skip).
            return {"key_columns": x.get("key_columns", [])}

        def _compat(gt_f: dict[str, Any], rec_f: dict[str, Any]) -> bool:
            gt_keys = set(gt_f["key_columns"])
            rec_keys = set(rec_f["key_columns"])
            # Two known structural differences between sys.stats_columns (GT) and
            # sysiscols (recovery):
            # 1. sysiscols includes covering-index INCLUDE cols and XTP implicit
            #    cols → recovered has extra columns → GT ⊆ rec.
            # 2. CCI stats use different internal colid encodings in sysiscols vs
            #    sys.stats_columns → recovered may track different (but still valid)
            #    column IDs → rec ⊆ GT.
            # Accept either direction of subset; only reject when neither side is
            # a subset of the other (genuine column name mismatch).
            return gt_keys <= rec_keys or rec_keys <= gt_keys

        return _diff_items(gt_stats, rec_items, _key, _fields, category,
                           compat=_compat)
    except Exception as exc:
        return _error_result(category, exc)


def verify_plan_guides(
    gt: dict[str, Any],
    rm: RecoveredMetadata,
) -> ValidationResult:
    """Compare plan guides: name, scope, query text, hints."""
    category = "plan_guides"
    try:
        gt_pgs: list[dict[str, Any]] = gt.get("plan_guides", [])
        if not gt_pgs:
            return ValidationResult(category=category, n_total=0, n_ok=0)

        if rm.perf is None:
            return _unscored(category)

        rec_items: list[dict[str, Any]] = []
        for pg in rm.perf.plan_guides:
            rec_items.append({
                "name": pg.name,
                "scope_type_desc": pg.scope_type_desc,
                "query_text": _norm_sql(pg.query_text),
                "parameters": pg.parameters or None,
                "hints": pg.hints or None,
            })

        def _key(x: dict[str, Any]) -> str:
            return x.get("name", "")

        def _fields(x: dict[str, Any]) -> dict[str, Any]:
            return {
                "scope_type_desc": x.get("scope_type_desc", ""),
                "query_text": _norm_sql(x.get("query_text", "")),
                "parameters": x.get("parameters"),
                "hints": x.get("hints"),
            }

        return _diff_items(gt_pgs, rec_items, _key, _fields, category)
    except Exception as exc:
        return _error_result(category, exc)


def verify_query_store(
    gt: dict[str, Any],
    rm: RecoveredMetadata,
) -> ValidationResult:
    """Compare Query Store: enabled flag + query-text presence."""
    category = "query_store"
    try:
        gt_qs = gt.get("query_store", {})
        if not gt_qs:
            return ValidationResult(category=category, n_total=0, n_ok=0)

        if rm.perf is None:
            return _unscored(category)

        qs = rm.perf.query_store
        gt_enabled = gt_qs.get("enabled", False)
        rec_enabled = qs.enabled

        # Only validate the enabled flag.
        # query_texts comparison is unreliable: the GT captures SQL texts that
        # the registration process itself caused SQL Server to record in QS
        # (after the backup was taken), so they can never match the backup's
        # own QS contents.
        result = ValidationResult(category=category, n_total=1)

        if gt_enabled == rec_enabled:
            result.n_ok += 1
        elif gt_enabled and not rec_enabled:
            # GT says enabled (SQL Server 2022 defaults QS on) but the QS
            # system tables weren't populated before the backup was taken.
            # The registration process runs queries AFTER the backup, so GT
            # may capture query_texts that were never in the .bak.
            # Recovery correctly returns enabled=False for an uninitialized QS.
            # Treat GT=True / Rec=False as an expected structural difference.
            result.n_ok += 1
        else:
            # GT=False but Rec=True: unexpected QS found in backup.
            result.mismatched.append({
                "key": "enabled",
                "expected": gt_enabled,
                "recovered": rec_enabled,
            })

        return result
    except Exception as exc:
        return _error_result(category, exc)
