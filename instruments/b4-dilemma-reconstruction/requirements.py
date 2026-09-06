#!/usr/bin/env python3
"""B4.3 requirements.py — validate requirements.jsonl.

Schema:
    item_id, reconstructor_id, req_id, requirement_text,
    status, settling_test, layer

status ∈ {true, false, lapsed, partial, unknown, undifferentiated}
A file containing ONLY true/false is rejected (status → void).
settling_test must be non-empty.
Forbidden fields: label, category, interpretation.
"""

import json
import sys

REQUIRED = {
    "item_id",
    "reconstructor_id",
    "req_id",
    "requirement_text",
    "status",
    "settling_test",
    "layer",
}
VALID_STATUS = {
    "true",
    "false",
    "lapsed",
    "partial",
    "unknown",
    "undifferentiated",
}
FORBIDDEN = {"label", "category", "interpretation"}


def validate(req_path, out_path):
    rows = []
    with open(req_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            missing = REQUIRED - set(row.keys())
            if missing:
                raise ValueError(f"Missing fields {missing} in row {row.get('req_id', '?')}")
            extra = set(row.keys()) - REQUIRED
            forbidden = extra & FORBIDDEN
            if forbidden:
                raise ValueError(f"Forbidden fields present: {forbidden}")
            if row["status"] not in VALID_STATUS:
                raise ValueError(f"Invalid status {row['status']!r}")
            st = str(row.get("settling_test", "")).strip()
            if not st:
                raise ValueError("Empty settling_test")
            rows.append(row)

    statuses = {r["status"] for r in rows}
    if statuses.issubset({"true", "false"}):
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {"status": "void", "reason": "Two-state grading was not run"}
                )
                + "\n"
            )
        print("REJECTED: only true/false present → status void", file=sys.stderr)
        return False

    with open(out_path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Validated {len(rows)} requirement rows")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: requirements.py <requirements.jsonl> <validated_requirements.jsonl>",
            file=sys.stderr,
        )
        sys.exit(1)
    ok = validate(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
