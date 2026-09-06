#!/usr/bin/env python3
"""B1.3 permute.py — shuffle position index assignments.

Preserves row count and the multiset of (ent_i, gap_i, resync_D, div_D).
"""

import json
import random
import sys


def permute(in_path, seed, out_path):
    rows = []
    with open(in_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))

    # Group by original i, shuffle the group labels
    by_i = {}
    for r in rows:
        by_i.setdefault(r["i"], []).append(r)

    indices = sorted(by_i.keys())
    rng = random.Random(seed)
    shuffled_indices = indices[:]
    while any(a == b for a, b in zip(indices, shuffled_indices)):
        rng.shuffle(shuffled_indices)

    # Map: old i → new i
    i_map = dict(zip(indices, shuffled_indices))

    # Rebuild rows with shuffled i
    new_rows = []
    for old_i, group in by_i.items():
        new_i = i_map[old_i]
        for r in group:
            new_r = r.copy()
            new_r["i"] = new_i
            new_rows.append(new_r)

    # Verify multiset preservation
    orig_tuples = sorted((r["ent_i"], r["gap_i"], r["resync_D"], r["div_D"]) for r in rows)
    new_tuples = sorted((r["ent_i"], r["gap_i"], r["resync_D"], r["div_D"]) for r in new_rows)
    assert orig_tuples == new_tuples, "Multiset changed during permutation"

    with open(out_path, "w", encoding="utf-8") as fh:
        for r in new_rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Permuted {len(rows)} rows (seed={seed})")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: permute.py <separations.jsonl> <seed> <out.jsonl>", file=sys.stderr)
        sys.exit(1)
    permute(sys.argv[1], int(sys.argv[2]), sys.argv[3])
