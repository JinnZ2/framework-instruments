#!/usr/bin/env python3
"""B1.3 permute.py — the permutation null for separations.jsonl.

Shuffles WHICH position index carries which (ent_i, gap_i, resync_D, div_D)
tuple. Row count and every other field are preserved. Every output row carries
the seed.

STRATUM: the shuffle runs independently inside each (case_id, model_id,
branch_rank, D) stratum, with one mapping over positions applied to every L
row in that stratum. So:
  - per-(D, L, model) counts, mean div_D and resync rate are UNCHANGED by
    construction (the null does not touch them);
  - the association between a position and its tuple is broken separately at
    each D, so cross-D stability of a position set (the structure the sweep
    reads) is what the null can remove;
  - div_D stays consistent across L for one (position, D), as in the real file.
A single global relabelling of i would leave every summary in this pipeline
identical to the real one and the null could never fire; that is why the
stratum is per D. The cost: on the permuted file ent_i is no longer constant
across D for one position. That file is a null, not a claim.

A stratum with one position cannot be permuted and stays as it is; the count
of such strata is in the run record. If EVERY stratum has one position the
permutation is the identity and the "null" is the real file under another
name: the run is refused (status void, nothing written), so the report
downstream goes void instead of printing a real-vs-permuted comparison of a
file against itself.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402

TUPLE = ("ent_i", "gap_i", "resync_D", "div_D")


def permute_rows(rows, seed):
    rng = random.Random(seed)
    strata = {}
    for r in rows:
        strata.setdefault((r["case_id"], r["model_id"], r["branch_rank"], r["D"]), []).append(r)
    out = []
    single = 0
    for key in sorted(strata):
        grp = strata[key]
        positions = sorted({r["i"] for r in grp})
        if len(positions) < 2:
            single += 1
        target = positions[:]
        rng.shuffle(target)
        i_map = dict(zip(positions, target))  # old i -> the i whose tuples it receives
        by_pos_L = {(r["i"], r["L"]): r for r in grp}
        for r in grp:
            src = by_pos_L[(i_map[r["i"]], r["L"])]
            new = dict(r)
            for f in TUPLE:
                new[f] = src[f]
            new["seed"] = seed
            out.append(new)
    return out, single


def check_multiset(rows, out):
    a = sorted(tuple(r[f] for f in TUPLE) for r in rows)
    b = sorted(tuple(r[f] for f in TUPLE) for r in out)
    if a != b or len(rows) != len(out):
        raise ValueError("permutation changed the tuple multiset or the row count")


def permute(in_path, seed, out_path):
    rows = [r for _, r in runrecord.read_jsonl(in_path, "separations.jsonl")]
    out, single = permute_rows(rows, seed)
    check_multiset(rows, out)
    strata = len({(r["case_id"], r["model_id"], r["branch_rank"], r["D"]) for r in rows})
    counts = {"rows": len(out), "strata": strata, "single_position_strata": single}
    if rows and single == strata:
        return "void", counts, "every stratum holds one position: the permutation is the identity; no null written"
    runrecord.write_jsonl(out_path, out)
    return ("ok" if out else "empty"), counts, ""


def main(argv):
    if len(argv) != 4:
        print("usage: b1_permute.py separations.jsonl seed separations_permuted.jsonl", file=sys.stderr)
        return 1
    seed = int(argv[2])
    return runrecord.run("b1_permute.py", argv[1:], seed, [argv[1]], argv[3],
                         lambda: permute(argv[1], seed, argv[3]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
