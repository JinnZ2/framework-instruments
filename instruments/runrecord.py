#!/usr/bin/env python3
"""runrecord.py — execution metadata logger.

Every run of every script appends one object to runs.jsonl.
"""

import json
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def record(script, args, seed, input_paths, output_path, status, counts, notes):
    """Append a run record to runs.jsonl in the current directory."""
    args_hash = hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest()[:16]
    inputs = []
    for p in input_paths:
        if os.path.exists(p):
            inputs.append({"name": os.path.basename(p), "sha256": sha256_file(p)})
        else:
            inputs.append({"name": os.path.basename(p), "sha256": None})
    entry = {
        "run_id": hashlib.sha256(
            (script + datetime.now(timezone.utc).isoformat()).encode()
        ).hexdigest()[:16],
        "utc": datetime.now(timezone.utc).isoformat(),
        "script": script,
        "args_hash": args_hash,
        "seed": seed,
        "input_files": inputs,
        "output_file": os.path.basename(output_path) if output_path else None,
        "status": status,
        "counts": counts,
        "notes": notes,
    }
    with open("runs.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    # Manual entry: runrecord.py <script> <args_hash> <seed> <inputs> <output> <status> <counts> <notes>
    if len(sys.argv) < 7:
        print("Usage: runrecord.py <script> <args_hash> <seed> <inputs> <output> <status> [counts] [notes]", file=sys.stderr)
        sys.exit(1)
    record(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3] if sys.argv[3] != "null" else None,
        sys.argv[4].split(",") if sys.argv[4] else [],
        sys.argv[5] if sys.argv[5] != "null" else None,
        sys.argv[6],
        sys.argv[7] if len(sys.argv) > 7 else None,
        sys.argv[8] if len(sys.argv) > 8 else None,
    )
