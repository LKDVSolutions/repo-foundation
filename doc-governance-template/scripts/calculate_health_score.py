#!/usr/bin/env python3
"""Generate a Governance Health Score based on registry state and staleness TTLs."""

import yaml
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"
AGENT_CONFIG_PATH = REPO_ROOT / ".agent_config.yaml"


def _load_warn_thresholds() -> dict:
    defaults = {"runtime_evidence": 7, "current_config": 30}
    if not AGENT_CONFIG_PATH.exists():
        return defaults
    try:
        cfg = yaml.safe_load(AGENT_CONFIG_PATH.read_text(encoding="utf-8"))
        ttl = (cfg or {}).get("governance", {}).get("staleness_ttl", {})
        for kind, thresholds in ttl.items():
            defaults[kind] = int(thresholds.get("warn_days", defaults.get(kind, 30)))
    except Exception:
        pass
    return defaults


def main():
    print("=== calculate_health_score.py ===")
    if not REGISTRY_PATH.exists():
        print("Score: 0/100 (Missing registry)")
        return

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    entries = data.get("entries", [])
    if not entries:
        print("Score: 0/100 (Empty registry)")
        return

    today = date.today()
    warn_thresholds = _load_warn_thresholds()

    total = len(entries)
    active_valid = sum(1 for e in entries if e.get("status") in ("active", "current"))
    explicit_stale = sum(1 for e in entries if e.get("status") == "stale")

    # Count docs stale by TTL (last_verified older than warn threshold)
    ttl_stale = 0
    for entry in entries:
        ak = entry.get("authority_kind")
        if ak not in warn_thresholds:
            continue
        lv = entry.get("last_verified")
        if lv is None:
            ttl_stale += 1
            continue
        try:
            lv_date = lv if isinstance(lv, date) else date.fromisoformat(str(lv))
            if (today - lv_date).days >= warn_thresholds[ak]:
                ttl_stale += 1
        except ValueError:
            ttl_stale += 1

    combined_stale = max(explicit_stale, ttl_stale)
    score = max(0, min(100, int((active_valid / total) * 100 - (combined_stale / total) * 50)))

    print(f"Governance Health Score: {score}/100")
    print(f"Total Docs: {total}")
    print(f"Active/Valid: {active_valid}")
    print(f"Stale (by status field): {explicit_stale}")
    print(f"Stale (by TTL threshold): {ttl_stale}")


if __name__ == "__main__":
    main()
