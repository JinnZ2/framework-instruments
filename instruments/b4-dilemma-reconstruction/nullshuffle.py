#!/usr/bin/env python3
"""B4.6 nullshuffle.py — reassign requirement lists to wrong items.

Preserves row count and the multiset of requirement_text values.
Uses a deterministic derangement with explicit seed.
"""

import json
import sys
import random
from collections import defaultdict


def derangement(ids, rng):
    """Return a shuffled list with no element in its original position."""
    if len(ids) < 2:
        raise ValueError("Need ≥2 items to derange")
    shuffled = ids[:]
    while all(a != b for a, b in zip(ids, shuffled)) is False:
        rng.shuffle(shuffled)
    return shuffled


def shuffle(req_path, seed, out_path):
    rows = []
    with open(req_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))

    by_item = defaultdict(list)
    for r in rows:
        by_item[r["item_id"]].append(r)

    item_ids = list(by_item.keys())
    rng = random.Random(seed)
    shuffled_ids = derangement(item_ids, rng)

    shuffled_rows = []
    for orig_id, new_id in zip(item_ids, shuffled_ids):
        for req in by_item[orig_id]:
            new_req = req.copy()
            new_req["item_id"] = new_id
            shuffled_rows.append(new_req)

    # Verification
    assert len(shuffled_rows) == len(rows), "Row count changed"
    orig_texts = sorted(r["requirement_text"] for r in rows)
    new_texts = sorted(r["requirement_text"] for r in shuffled_rows)
    assert orig_texts == new_texts, "Requirement text multiset changed"

    with open(out_path, "w", encoding="utf-8") as fh:
        for r in shuffled_rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Seed record
    seed_path = out_path.replace(".jsonl", "_seed.json")
    with open(seed_path, "w", encoding="utf-8") as fh:
        json.dump({"seed": seed, "algorithm": "derangement"}, fh, indent=2)
        fh.write("\n")

    print(f"Shuffled {len(rows)} rows across {len(item_ids)} items (seed={seed})")


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
    if len(argv) != 4:
        print("Usage: nullshuffle.py <requirements.jsonl> <seed> <requirements_shuffled.jsonl>", file=sys.stderr)
        return 1
    seed = int(argv[2])

    def body():
        shuffle(argv[1], seed, argv[3])
        return _status_by_rows(argv[3])
    return runrecord.run("b4/nullshuffle.py", argv[1:], seed, [argv[1]], argv[3], body)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
