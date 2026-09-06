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


# ---- run-record wiring (added; logic above is unchanged) --------------------
import os  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402


def _rows(path):
    try:
        return sum(1 for _ in runrecord.read_jsonl(path))
    except (OSError, ValueError):
        return None


def _status_by_rows(path):
    n = _rows(path)
    return ("ok" if n else "empty"), {"rows": n}, ""

def main(argv):
    if len(argv) != 3:
        print("Usage: items.py <items.jsonl> <validated_items.jsonl>", file=sys.stderr)
        return 1

    def body():
        try:
            validate(argv[1], argv[2])
        except SystemExit as exc:
            return "void", {}, f"refused (exit {exc.code}): mixed arms, nothing written"
        return _status_by_rows(argv[2])
    return runrecord.run("b4/items.py", argv[1:], None, [argv[1]], argv[2], body)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
