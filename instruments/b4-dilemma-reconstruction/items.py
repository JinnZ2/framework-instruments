#!/usr/bin/env python3
"""B4.1 items.py — validate items.jsonl and refuse mixed arms.

Schema per row:
    item_id, source, text_verbatim, branches_stated, arm
arm ∈ {"hypothetical", "documented"}
If mixed arms are present the script refuses to write one output file.
"""

import json
import sys

REQUIRED = {"item_id", "source", "text_verbatim", "branches_stated", "arm"}
VALID_ARMS = {"hypothetical", "documented"}


def validate(inpath, outpath):
    rows = []
    with open(inpath, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            missing = REQUIRED - set(row.keys())
            if missing:
                raise ValueError(f"Missing fields {missing} in {row.get('item_id', '?')}")
            extra = set(row.keys()) - REQUIRED
            if extra:
                raise ValueError(f"Extra fields {extra} in {row.get('item_id', '?')}")
            if row["arm"] not in VALID_ARMS:
                raise ValueError(f"Invalid arm {row['arm']!r}")
            rows.append(row)

    arms = {r["arm"] for r in rows}
    if len(arms) > 1:
        print(
            f"ERROR: Mixed arms detected ({arms}). "
            "Refusing to write single output file.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(outpath, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Validated {len(rows)} items, arm={arms.pop()}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: items.py <items.jsonl> <validated_items.jsonl>", file=sys.stderr)
        sys.exit(1)
    validate(sys.argv[1], sys.argv[2])
