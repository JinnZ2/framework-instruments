#!/usr/bin/env python3
"""B2.2 order.py — counterbalance condition order across readers.

assignment.jsonl: reader_id, order [conditions], seed.

Readers are filled in blocks of four from a Williams Latin square (every
condition once in every position, and every condition follows every other
condition exactly once across the block, so first-order carry-over is
balanced too). A remainder below four gets a seeded permutation each; the
shortfall is the number of such readers and is written to the run record
notes, since those readers are not balanced against anyone.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402

CONDITIONS = ("A", "B", "C", "D")
WILLIAMS = (("A", "B", "D", "C"), ("B", "C", "A", "D"), ("C", "D", "B", "A"), ("D", "A", "C", "B"))


def assignments(reader_count, seed):
    rng = random.Random(seed)
    rows = []
    for r in range(reader_count):
        if r < (reader_count // 4) * 4:
            order = list(WILLIAMS[r % 4])
        else:
            order = list(CONDITIONS)
            rng.shuffle(order)
        rows.append({"reader_id": f"R{r + 1:03d}", "order": order, "seed": seed})
    return rows


def order(reader_count, seed, out_path):
    if reader_count < 0:
        raise ValueError("reader_count must be >= 0")
    rows = assignments(reader_count, seed)
    runrecord.write_jsonl(out_path, rows)
    square = (reader_count // 4) * 4
    shortfall = reader_count - square
    counts = {"readers": reader_count, "latin_square_readers": square, "seeded_readers": shortfall}
    notes = f"shortfall={shortfall}: readers beyond the last full block of 4 carry a seeded permutation, not a balanced position"
    return ("ok" if rows else "empty"), counts, notes if shortfall else ""


def main(argv):
    if len(argv) != 4:
        print("usage: b2_order.py reader_count seed assignment.jsonl", file=sys.stderr)
        return 1
    seed = int(argv[2])
    return runrecord.run("b2_order.py", argv[1:], seed, [], argv[3],
                         lambda: order(int(argv[1]), seed, argv[3]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
