#!/usr/bin/env python3
"""runrecord.py — the run record, shared by every script in every build.

Every run appends ONE object to runs.jsonl:
  run_id, utc, script, args_hash, seed, input_files (name+sha256),
  output_file, status, counts, notes

status is one of: ok, void, error, empty.

RULE: a run that fails, voids, or returns nothing STILL WRITES ITS RECORD,
through the same code path as a success. Use run() below: it calls the
script body, converts an exception into status "error", records, prints the
one-line summary, and returns the exit code. No script should write its own
record any other way.

Also holds the two JSONL helpers every script needs, so line-numbered
rejection of malformed input is one implementation rather than five.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

STATUSES = ("ok", "void", "error", "empty")
EXIT_CODE = {"ok": 0, "empty": 0, "void": 2, "error": 1}
RUNS_FILE = "runs.jsonl"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def args_hash(args):
    return sha256_text(json.dumps([str(a) for a in args]))[:16]


def read_jsonl(path, name=None):
    """Yield (line_number, row). A line that is not a JSON object is rejected
    with its line number; blank lines are skipped and counted nowhere."""
    label = name or os.path.basename(path)
    with open(path, "r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{label} line {n}: invalid JSON ({exc.msg})")
            if not isinstance(row, dict):
                raise ValueError(f"{label} line {n}: not a JSON object")
            yield n, row


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def record(script, args, seed, input_paths, output_paths, status, counts, notes,
           runs_path=RUNS_FILE):
    """Append one record. output_paths may be a string, a list, or None."""
    if status not in STATUSES:
        raise ValueError(f"status {status!r} not in {STATUSES}")
    inputs = []
    for p in input_paths or []:
        if p is not None and os.path.isfile(p):
            inputs.append({"name": os.path.basename(p), "sha256": sha256_file(p)})
        else:
            inputs.append({"name": os.path.basename(str(p)), "sha256": None})
    if isinstance(output_paths, (list, tuple)):
        output_file = [os.path.basename(p) for p in output_paths]
    else:
        output_file = os.path.basename(output_paths) if output_paths else None
    utc = datetime.now(timezone.utc).isoformat()
    ahash = args_hash(args)
    entry = {
        "run_id": sha256_text(script + utc + ahash)[:16],
        "utc": utc,
        "script": script,
        "args_hash": ahash,
        "seed": seed,
        "input_files": inputs,
        "output_file": output_file,
        "status": status,
        "counts": counts or {},
        "notes": notes or "",
    }
    with open(runs_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def run(script, args, seed, input_paths, output_paths, body, runs_path=RUNS_FILE):
    """Execute body() -> (status, counts, notes); always record; print one line.

    Returns the process exit code (0 ok/empty, 2 void, 1 error). A body that
    raises is recorded as status "error" with the exception text as notes and
    is not re-raised, so the failure row is written by this path and no other.
    """
    try:
        status, counts, notes = body()
        if status not in STATUSES:
            raise ValueError(f"body returned status {status!r}")
    except Exception as exc:  # noqa: BLE001 — every failure becomes a row
        status, counts, notes = "error", {}, f"{type(exc).__name__}: {exc}"
    entry = record(script, args, seed, input_paths, output_paths, status,
                   counts, notes, runs_path=runs_path)
    counts_txt = " ".join(f"{k}={v}" for k, v in sorted((counts or {}).items()))
    print(f"{script} {status} run_id={entry['run_id']} {counts_txt} {notes}".rstrip())
    return EXIT_CODE[status]


def main_exit(code):
    sys.exit(code)
