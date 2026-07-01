#!/usr/bin/env python3
"""Migrate a RunStore JSON file to the current schema version."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from groundseal.lifecycle.migrations import migrate_store_payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate RunStore JSON to current schema")
    parser.add_argument("--input", required=True, type=Path, help="Source runs JSON file")
    parser.add_argument("--output", required=True, type=Path, help="Destination runs JSON file")
    parser.add_argument("--target-version", default="1", help="Target schema version")
    args = parser.parse_args()

    raw = json.loads(args.input.read_text())
    migrated = migrate_store_payload(raw, target_version=args.target_version)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(migrated, indent=2) + "\n")
    print(f"Migrated {len(migrated)} records to schema_version={args.target_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
