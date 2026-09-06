#!/usr/bin/env python3
"""B2.2 order.py — counterbalance condition order across readers.

Emits assignment.jsonl (reader_id, order: [conditions]).
Latin square where count allows; otherwise seeded permutation.
"""

import json
import random
import sys

CONDITIONS = ["A", "B", "C", "D"]


def latin_square(n):
    """Generate a Latin square of order 4 for n readers."""
    if n % 4 != 0:
        return None
    assignments = []
    for r in range(n):
        offset = r % 4
        order = CONDITIONS[offset:] + CONDITIONS[:offset]
        assignments.append({"reader_id": f"R{r+1}", "order": order})
    return assignments


def seeded_perm(n, seed):
    rng = random.Random(seed)
    assignments = []
    for r in range(n):
        order = CONDITIONS[:]
        rng.shuffle(order)
        assignments.append({"reader_id": f"R{r+1}", "order": order})
    return assignments


def assign(reader_count, seed, out_path):
    if reader_count % 4 == 0:
        assignments = latin_square(reader_count)
        note = "latin_square"
    else:
        assignments = seeded_perm(reader_count, seed)
        note = f"seeded_perm (shortfall: {reader_count % 4} readers off balance)"

    with open(out_path, "w", encoding="utf-8") as fh:
        for a in assignments:
            fh.write(json.dumps({**a, "note": note}, ensure_ascii=False) + "\n")

    print(f"Assigned {reader_count} readers ({note})")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: order.py <reader_count> <seed> <assignment.jsonl>", file=sys.stderr)
        sys.exit(1)
    assign(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
