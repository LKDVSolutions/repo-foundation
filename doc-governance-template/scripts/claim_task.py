#!/usr/bin/env python3
"""Multi-agent file claim protocol.

Prevents two agents from writing conflicting patches to the same target file.
Uses a FileLock over the full read-modify-write cycle on AGENT_CLAIMS.md.

Usage:
    python scripts/claim_task.py claim <file_path> [--agent-id <id>] [--ttl <seconds>]
    python scripts/claim_task.py release <file_path> [--agent-id <id>]
    python scripts/claim_task.py check <file_path>
    python scripts/claim_task.py cleanup
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from filelock import FileLock, Timeout

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CLAIMS_FILE = REPO_ROOT / "docs" / "history" / "AGENT_CLAIMS.md"
DEFAULT_TTL = 1800  # 30 minutes
LOCK_TIMEOUT = 30

_BLOCK_RE = re.compile(r"```yaml claims\n(.*?)```", re.DOTALL)

CLAIMS_HEADER = """\
---
doc_id: AGENT_CLAIMS
doc_class: active
authority_kind: current_config
title: Agent Claims Registry
primary_audience: agents
task_entry_for: []
system_owner: system-wide
doc_owner: system-wide
updated_by: auto
authoritative_for:
- active agent file reservations
source_inputs:
- scripts/claim_task.py
refresh_policy: auto
verification_level: none
status: active
depends_on: []
---
# Agent Claims Registry

<!-- AUTO-MANAGED by scripts/claim_task.py — do not edit manually -->

```yaml claims
[]
```
"""


class ClaimError(RuntimeError):
    pass


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


class ClaimManager:
    def __init__(self, claims_file: Path = DEFAULT_CLAIMS_FILE) -> None:
        self.claims_file = claims_file
        self.lock_file = claims_file.with_suffix(".lock")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_claims(self) -> list[dict]:
        if not self.claims_file.exists():
            self.claims_file.parent.mkdir(parents=True, exist_ok=True)
            self.claims_file.write_text(CLAIMS_HEADER, encoding="utf-8")
        content = self.claims_file.read_text(encoding="utf-8")
        m = _BLOCK_RE.search(content)
        if not m:
            return []
        return yaml.safe_load(m.group(1)) or []

    def _write_claims(self, claims: list[dict]) -> None:
        if not self.claims_file.exists():
            self.claims_file.parent.mkdir(parents=True, exist_ok=True)
            self.claims_file.write_text(CLAIMS_HEADER, encoding="utf-8")
        content = self.claims_file.read_text(encoding="utf-8")
        block = "```yaml claims\n" + yaml.dump(claims, default_flow_style=False) + "```"
        new_content = _BLOCK_RE.sub(lambda _: block, content)
        count = 1 if new_content != content else 0
        if count == 0:
            new_content = content.rstrip() + "\n\n" + block + "\n"
        self.claims_file.write_text(new_content, encoding="utf-8")

    def _active_claims(self, claims: list[dict]) -> list[dict]:
        now = _now()
        return [c for c in claims if _parse(c["expires_at"]) > now]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def claim(self, file_path: str, agent_id: str, ttl_seconds: int = DEFAULT_TTL) -> None:
        with FileLock(str(self.lock_file), timeout=LOCK_TIMEOUT):
            all_claims = self._read_claims()
            active = self._active_claims(all_claims)
            for c in active:
                if c["file"] == file_path:
                    raise ClaimError(
                        f"File '{file_path}' is already claimed by '{c['agent_id']}' "
                        f"until {c['expires_at']}"
                    )
            now = _now()
            expires = datetime.fromtimestamp(
                now.timestamp() + ttl_seconds, tz=timezone.utc
            )
            active.append(
                {
                    "file": file_path,
                    "agent_id": agent_id,
                    "claimed_at": _iso(now),
                    "expires_at": _iso(expires),
                }
            )
            self._write_claims(active)

    def release(self, file_path: str, agent_id: str) -> None:
        with FileLock(str(self.lock_file), timeout=LOCK_TIMEOUT):
            claims = self._read_claims()
            before = len(claims)
            claims = [
                c for c in claims
                if not (c["file"] == file_path and c["agent_id"] == agent_id)
            ]
            if len(claims) == before:
                print(f"  [WARN] No active claim found for '{file_path}' by '{agent_id}'")
            self._write_claims(claims)

    def check(self, file_path: str) -> dict | None:
        with FileLock(str(self.lock_file), timeout=LOCK_TIMEOUT):
            active = self._active_claims(self._read_claims())
            for c in active:
                if c["file"] == file_path:
                    return c
            return None

    def cleanup(self) -> int:
        with FileLock(str(self.lock_file), timeout=LOCK_TIMEOUT):
            claims = self._read_claims()
            active = self._active_claims(claims)
            removed = len(claims) - len(active)
            self._write_claims(active)
            return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Multi-agent file claim protocol.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_claim = sub.add_parser("claim", help="Claim a file for exclusive editing.")
    p_claim.add_argument("file_path")
    p_claim.add_argument("--agent-id", default="anonymous")
    p_claim.add_argument("--ttl", type=int, default=DEFAULT_TTL)

    p_release = sub.add_parser("release", help="Release a claim.")
    p_release.add_argument("file_path")
    p_release.add_argument("--agent-id", default="anonymous")

    p_check = sub.add_parser("check", help="Check if a file is claimed.")
    p_check.add_argument("file_path")

    sub.add_parser("cleanup", help="Remove expired claims.")

    args = parser.parse_args()
    mgr = ClaimManager()

    if args.command == "claim":
        try:
            mgr.claim(args.file_path, agent_id=args.agent_id, ttl_seconds=args.ttl)
            print(f"  [OK] Claimed '{args.file_path}' for agent '{args.agent_id}'.")
            return 0
        except ClaimError as e:
            print(f"  [FAIL] {e}")
            return 1
        except Timeout:
            print(f"  [FAIL] Lock not acquired after {LOCK_TIMEOUT}s — another process may be hung.")
            return 2

    if args.command == "release":
        try:
            mgr.release(args.file_path, agent_id=args.agent_id)
            print(f"  [OK] Released '{args.file_path}'.")
            return 0
        except Timeout:
            print(f"  [FAIL] Lock not acquired after {LOCK_TIMEOUT}s — another process may be hung.")
            return 2

    if args.command == "check":
        try:
            info = mgr.check(args.file_path)
        except Timeout:
            print(f"  [FAIL] Lock not acquired after {LOCK_TIMEOUT}s — another process may be hung.")
            return 2
        if info:
            print(f"  [CLAIMED] '{args.file_path}' — agent '{info['agent_id']}' until {info['expires_at']}")
            return 1
        print(f"  [FREE] '{args.file_path}' is not claimed.")
        return 0

    if args.command == "cleanup":
        try:
            removed = mgr.cleanup()
            print(f"  [OK] Removed {removed} expired claim(s).")
            return 0
        except Timeout:
            print(f"  [FAIL] Lock not acquired after {LOCK_TIMEOUT}s — another process may be hung.")
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
