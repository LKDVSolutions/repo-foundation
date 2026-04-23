#!/usr/bin/env python3
"""Check that active/generated docs in the registry have required metadata fields."""

import sys
import yaml
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"
AGENT_CONFIG_PATH = REPO_ROOT / ".agent_config.yaml"

# Sentinel values injected by auto_fix.py — must not pass the metadata gate.
_SENTINEL_PREFIXES = ("FIXME",)


def _load_staleness_config() -> dict:
    """Load per-authority_kind TTL thresholds from .agent_config.yaml.

    Returns a dict keyed by authority_kind, each value having warn_days and fail_days.
    Falls back to safe defaults if the config file is missing or malformed.
    """
    defaults = {
        "runtime_evidence": {"warn_days": 7, "fail_days": 30},
        "current_config": {"warn_days": 30, "fail_days": 90},
    }
    if not AGENT_CONFIG_PATH.exists():
        return defaults
    try:
        cfg = yaml.safe_load(AGENT_CONFIG_PATH.read_text(encoding="utf-8"))
        ttl = (cfg or {}).get("governance", {}).get("staleness_ttl", {})
        for kind, thresholds in ttl.items():
            defaults[kind] = {
                "warn_days": int(thresholds.get("warn_days", defaults.get(kind, {}).get("warn_days", 7))),
                "fail_days": int(thresholds.get("fail_days", defaults.get(kind, {}).get("fail_days", 30))),
            }
    except Exception:
        pass
    return defaults


def _detect_cycle(start: str, graph: dict[str, list[str]]) -> bool:
    """Return True if start has a cycle in the directed graph."""
    visited: set[str] = set()
    current = start
    while current:
        if current in visited:
            return True
        visited.add(current)
        neighbors = graph.get(current, [])
        current = neighbors[0] if neighbors else None
    return False


def check_metadata():
    """Run all metadata checks. Returns (passed, warnings, failures)."""
    passed = 0
    warnings = 0
    failures = 0

    if not REGISTRY_PATH.exists():
        print(f"[FAIL] Registry file not found: {REGISTRY_PATH.relative_to(REPO_ROOT)}")
        return passed, warnings, failures + 1

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"[FAIL] YAML parse error: {e}")
            return passed, warnings, failures + 1

    entries = data.get("entries", [])
    if not entries:
        print("[FAIL] No entries found in registry")
        return passed, warnings, failures + 1

    staleness_config = _load_staleness_config()
    today = date.today()

    # --- Check 1: active/generated entries have required metadata fields ---
    governed_classes = {"active", "generated"}
    required_metadata = [
        "authority_kind",
        "system_owner",
        "doc_owner",
        "updated_by",
        "authoritative_for",
        "refresh_policy",
    ]

    meta_failures = []
    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        doc_class = entry.get("doc_class")
        if doc_class not in governed_classes:
            continue
        for field_name in required_metadata:
            if field_name not in entry or entry[field_name] is None:
                meta_failures.append(
                    f"'{doc_id}' (doc_class={doc_class}) missing required metadata field: '{field_name}'"
                )

    if meta_failures:
        for msg in meta_failures:
            print(f"[FAIL] {msg}")
            failures += 1
    else:
        count = sum(1 for e in entries if e.get("doc_class") in governed_classes)
        print(f"[PASS] All {count} active/generated entries have required metadata fields")
        passed += 1

    # --- Check 2: sentinel title values must not pass ---
    sentinel_failures = []
    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        title = entry.get("title") or ""
        if any(title.startswith(prefix) for prefix in _SENTINEL_PREFIXES):
            sentinel_failures.append(
                f"'{doc_id}' has a sentinel title '{title}' — replace with a real title before merging"
            )

    if sentinel_failures:
        for msg in sentinel_failures:
            print(f"[FAIL] {msg}")
            failures += 1
    else:
        print("[PASS] No sentinel title values found")
        passed += 1

    # --- Check 3: current_config and runtime_evidence entries have source_inputs and verification_level ---
    config_kinds = {"current_config", "runtime_evidence"}
    all_doc_ids = {e.get("doc_id") for e in entries if e.get("doc_id")}
    source_failures = []

    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        ak = entry.get("authority_kind")
        if ak not in config_kinds:
            continue
        source_inputs = entry.get("source_inputs")
        if not source_inputs:
            source_failures.append(
                f"'{doc_id}' (authority_kind={ak}) has null/empty source_inputs"
            )
        else:
            # Validate that path-like source_inputs exist on disk or as doc_ids in the registry
            for src in source_inputs:
                src_str = str(src)
                is_path = "/" in src_str or "." in src_str.rsplit("/", 1)[-1]
                if is_path:
                    if not (REPO_ROOT / src_str).exists():
                        source_failures.append(
                            f"'{doc_id}' source_inputs path '{src_str}' does not exist on disk"
                        )
                else:
                    if src_str not in all_doc_ids:
                        source_failures.append(
                            f"'{doc_id}' source_inputs doc_id '{src_str}' not found in registry"
                        )
        verification_level = entry.get("verification_level")
        if verification_level is None:
            source_failures.append(
                f"'{doc_id}' (authority_kind={ak}) has null verification_level"
            )

    if source_failures:
        for msg in source_failures:
            print(f"[FAIL] {msg}")
            failures += 1
    else:
        count = sum(1 for e in entries if e.get("authority_kind") in config_kinds)
        print(
            f"[PASS] All {count} current_config/runtime_evidence entries have "
            f"source_inputs and verification_level"
        )
        passed += 1

    # --- Check 4: staleness TTL enforcement for governed authority_kinds ---
    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        ak = entry.get("authority_kind")
        if ak not in staleness_config:
            continue

        thresholds = staleness_config[ak]
        warn_days = thresholds["warn_days"]
        fail_days = thresholds["fail_days"]

        last_verified_raw = entry.get("last_verified")
        if last_verified_raw is None:
            print(
                f"[WARN] '{doc_id}' (authority_kind={ak}) has null last_verified "
                f"— no verification date on record"
            )
            warnings += 1
            continue

        try:
            last_verified = (
                last_verified_raw
                if isinstance(last_verified_raw, date)
                else date.fromisoformat(str(last_verified_raw))
            )
        except ValueError:
            print(f"[WARN] '{doc_id}' last_verified '{last_verified_raw}' is not a valid date")
            warnings += 1
            continue

        age_days = (today - last_verified).days

        if age_days >= fail_days:
            print(
                f"[FAIL] '{doc_id}' (authority_kind={ak}) last verified {age_days}d ago "
                f"(>{fail_days}d threshold) — re-verify and update last_verified"
            )
            failures += 1
        elif age_days >= warn_days:
            print(
                f"[WARN] '{doc_id}' (authority_kind={ak}) last verified {age_days}d ago "
                f"(>{warn_days}d advisory threshold)"
            )
            warnings += 1
        else:
            print(f"[PASS] '{doc_id}' (authority_kind={ak}) last_verified: {last_verified} ({age_days}d ago)")
            passed += 1

    # --- Check 5: superseded_by references exist and no cycles ---
    entry_dict = {e.get("doc_id"): e for e in entries if e.get("doc_id")}
    supersession_failures = []
    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        superseded_by = entry.get("superseded_by")
        if superseded_by:
            if superseded_by not in all_doc_ids:
                supersession_failures.append(
                    f"'{doc_id}' superseded_by='{superseded_by}' but that doc_id does not exist in registry"
                )
            else:
                visited: set[str] = {doc_id}
                current = superseded_by
                while current:
                    if current in visited:
                        supersession_failures.append(
                            f"Cycle detected in superseded_by starting at '{doc_id}'"
                        )
                        break
                    visited.add(current)
                    curr_entry = entry_dict.get(current)
                    current = curr_entry.get("superseded_by") if curr_entry else None

    if supersession_failures:
        for msg in supersession_failures:
            print(f"[FAIL] {msg}")
            failures += 1
    else:
        count = sum(1 for e in entries if e.get("superseded_by"))
        if count == 0:
            print("[PASS] No superseded_by references to check")
        else:
            print(f"[PASS] All {count} superseded_by references resolve to existing doc_ids")
        passed += 1

    # --- Check 6: depends_on cycle detection ---
    depends_graph: dict[str, list[str]] = {}
    for entry in entries:
        doc_id = entry.get("doc_id")
        deps = entry.get("depends_on") or []
        if doc_id and isinstance(deps, list):
            depends_graph[doc_id] = deps

    def _reachable_includes_start(start: str) -> bool:
        """Return True if following depends_on from start can reach start again (cycle)."""
        visited: set[str] = set()
        queue = list(depends_graph.get(start, []))
        while queue:
            node = queue.pop()
            if node == start:
                return True
            if node in visited:
                continue
            visited.add(node)
            queue.extend(depends_graph.get(node, []))
        return False

    depends_cycle_failures = []
    for doc_id in depends_graph:
        if _reachable_includes_start(doc_id):
            depends_cycle_failures.append(f"Cycle detected in depends_on graph involving '{doc_id}'")

    if depends_cycle_failures:
        for msg in set(depends_cycle_failures):  # deduplicate
            print(f"[FAIL] {msg}")
            failures += 1
    else:
        print("[PASS] No cycles detected in depends_on graph")
        passed += 1

    return passed, warnings, failures


def main():
    print("=== check_doc_metadata.py ===")
    passed, warnings, failures = check_metadata()
    print(f"\nResult: {passed} passed, {warnings} warnings, {failures} failures")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
