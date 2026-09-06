#!/usr/bin/env python3
"""B1.2 score.py — emit separations.jsonl, one row per (i, branch_rank, D, L).

  gap_i    = logprob_taken - logprob of the forced token at position i (from topk)
  resync_D = 1 if continuation[:D] and base_continuation[:D] end in the same
             aligned run of >= L tokens, else 0.  L is swept, not fixed.
  div_D    = Levenshtein distance over tokens between the two truncations,
             divided by the longer truncation's length.

D is swept over D_VALUES by truncating the stored continuation; L over L_VALUES.
Both are written into every row. A continuation shorter than D is scored over
the tokens it has and counted in the run record (short_at_D_<D>), since rows
at that D then carry no more information than the row at the shorter length.

DECLARED READING: "rejoins the base sequence" is scored as an ALIGNED suffix
match (same offset in both continuations). A rejoin after a token-count shift
(same text, different tokenisation length) scores 0 under this reading.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402
import b1_schema  # noqa: E402

D_VALUES = (8, 16, 32, 64, 128)
L_VALUES = (2, 4, 8)
ROW_FIELDS = ("case_id", "model_id", "i", "branch_rank", "D", "L",
              "ent_i", "gap_i", "resync_D", "div_D")


def levenshtein(a, b):
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ai in enumerate(a, 1):
        curr = [i]
        for j, bj in enumerate(b, 1):
            cost = 0 if ai == bj else 1
            curr.append(min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[-1]


def norm_lev(a, b):
    m = max(len(a), len(b))
    return levenshtein(a, b) / m if m else 0.0


def shared_suffix(a, b):
    n = 0
    for x, y in zip(reversed(a), reversed(b)):
        if x != y:
            break
        n += 1
    return n


def resync(cont, base_cont, D, L):
    return 1 if shared_suffix(cont[:D], base_cont[:D]) >= L else 0


def gap(base_row, forced_token):
    for token, logprob in base_row["topk"]:
        if token == forced_token:
            return base_row["logprob_taken"] - logprob
    raise ValueError("forced_token not in topk")  # validated upstream; kept as a guard


def score_rows(base, traces):
    """Yield separation rows and accumulate counts. base: dict from validate_base."""
    counts = {"trace_rows": len(traces), "positions": len({(t["case_id"], t["model_id"], t["i"]) for t in traces}),
              "rows": 0}
    for D in D_VALUES:
        counts[f"short_at_D_{D}"] = 0
    for basis in b1_schema.ENTROPY_BASIS:
        counts[f"entropy_basis_{basis}"] = 0
    seen_basis = set()
    rows = []
    for t in traces:
        brow = base[(t["case_id"], t["model_id"], t["i"])]
        pos_key = (t["case_id"], t["model_id"], t["i"])
        if pos_key not in seen_basis:
            seen_basis.add(pos_key)
            counts[f"entropy_basis_{brow['entropy_basis']}"] += 1
        g = gap(brow, t["forced_token"])
        cont, bcont = t["continuation"], t["base_continuation"]
        for D in D_VALUES:
            if len(cont) < D:
                counts[f"short_at_D_{D}"] += 1
            div = norm_lev(cont[:D], bcont[:D])
            for L in L_VALUES:
                rows.append({
                    "case_id": t["case_id"], "model_id": t["model_id"], "i": t["i"],
                    "branch_rank": t["branch_rank"], "D": D, "L": L,
                    "ent_i": brow["entropy_i"], "gap_i": g,
                    "resync_D": resync(cont, bcont, D, L), "div_D": div,
                })
    counts["rows"] = len(rows)
    return rows, counts


def score(base_path, traces_path, out_path):
    base, traces = b1_schema.validate(base_path, traces_path)
    rows, counts = score_rows(base, traces)
    runrecord.write_jsonl(out_path, rows)
    return ("ok" if rows else "empty"), counts, ""


def main(argv):
    if len(argv) != 4:
        print("usage: b1_score.py base.jsonl traces.jsonl separations.jsonl", file=sys.stderr)
        return 1
    return runrecord.run("b1_score.py", argv[1:], None, [argv[1], argv[2]], argv[3],
                         lambda: score(argv[1], argv[2], argv[3]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
