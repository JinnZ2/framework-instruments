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


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: nullshuffle.py <requirements.jsonl> <seed> <requirements_shuffled.jsonl>",
            file=sys.stderr,
        )
        sys.exit(1)
    shuffle(sys.argv[1], int(sys.argv[2]), sys.argv[3])
