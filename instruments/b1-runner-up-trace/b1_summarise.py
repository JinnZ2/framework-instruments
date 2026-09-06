#!/usr/bin/env python3
"""B1.4 summarise.py — aggregate separations.jsonl (real or permuted, identically).

Per (D, L, model_id) one SUMMARY row:
  count, mean_div_D, resync_rate, sep_rate_all,
  high_ent_count, sep_rate_high_ent   (top decile of rows by ent_i; sep = resync_D == 0)
  top_decile_count, top_decile_positions  (positions [case_id, i] among the top
                                           decile of rows by div_D)
  case_ids
STABILITY rows: Jaccard overlap of top-decile position sets for adjacent D
(at fixed L, model) and adjacent L (at fixed D, model). A stability row is
the one carrying "jaccard"; there is no type field.

No branching on which file this is. Unknown row fields (the permuted file's
seed) are ignored, not rejected, so both files run through one path.

NOTE ON L: div_D does not depend on L, so at fixed D the top-decile div set is
the same for every L and adjacent-L Jaccard is 1.0 on any real file by
construction. The L sweep carries information through resync_rate only.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402

NEEDED = ("case_id", "model_id", "i", "branch_rank", "D", "L", "ent_i", "gap_i", "resync_D", "div_D")


def jaccard(a, b):
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def top_decile(rows, key):
    """Rows in the top decile by key, ties broken deterministically."""
    ordered = sorted(rows, key=lambda r: (-r[key], r["case_id"], r["i"], r["branch_rank"]))
    return ordered[:max(1, len(ordered) // 10)]


def summarise_rows(rows):
    for n, r in enumerate(rows, 1):
        for f in NEEDED:
            if f not in r:
                raise ValueError(f"separations.jsonl row {n}: missing field {f}")
    groups = {}
    for r in rows:
        groups.setdefault((r["D"], r["L"], r["model_id"]), []).append(r)
    summaries = []
    for D, L, model_id in sorted(groups):
        grp = groups[(D, L, model_id)]
        n = len(grp)
        high = top_decile(grp, "ent_i")
        top = top_decile(grp, "div_D")
        summaries.append({
            "D": D, "L": L, "model_id": model_id, "count": n,
            "mean_div_D": sum(r["div_D"] for r in grp) / n,
            "resync_rate": sum(r["resync_D"] for r in grp) / n,
            "sep_rate_all": sum(1 for r in grp if r["resync_D"] == 0) / n,
            "high_ent_count": len(high),
            "sep_rate_high_ent": sum(1 for r in high if r["resync_D"] == 0) / len(high),
            "top_decile_count": len({(r["case_id"], r["i"]) for r in top}),
            "top_decile_positions": sorted([c, i] for c, i in {(r["case_id"], r["i"]) for r in top}),
            "case_ids": sorted({r["case_id"] for r in grp}),
        })
    return summaries


def stability_rows(summaries):
    index = {(s["D"], s["L"], s["model_id"]): {tuple(p) for p in s["top_decile_positions"]} for s in summaries}
    D_vals = sorted({s["D"] for s in summaries})
    L_vals = sorted({s["L"] for s in summaries})
    out = []
    for model_id in sorted({s["model_id"] for s in summaries}):
        for L in L_vals:
            for d1, d2 in zip(D_vals, D_vals[1:]):
                if (d1, L, model_id) in index and (d2, L, model_id) in index:
                    out.append({"model_id": model_id, "L": L, "D_pair": [d1, d2],
                                "jaccard": jaccard(index[(d1, L, model_id)], index[(d2, L, model_id)])})
        for D in D_vals:
            for l1, l2 in zip(L_vals, L_vals[1:]):
                if (D, l1, model_id) in index and (D, l2, model_id) in index:
                    out.append({"model_id": model_id, "D": D, "L_pair": [l1, l2],
                                "jaccard": jaccard(index[(D, l1, model_id)], index[(D, l2, model_id)])})
    return out


def summarise(in_path, out_path):
    rows = [r for _, r in runrecord.read_jsonl(in_path, "separations.jsonl")]
    summaries = summarise_rows(rows)
    stability = stability_rows(summaries)
    runrecord.write_jsonl(out_path, summaries + stability)
    counts = {"rows_in": len(rows), "summary_rows": len(summaries), "stability_rows": len(stability)}
    return ("ok" if summaries else "empty"), counts, ""


def main(argv):
    if len(argv) != 3:
        print("usage: b1_summarise.py separations.jsonl summary.jsonl", file=sys.stderr)
        return 1
    return runrecord.run("b1_summarise.py", argv[1:], None, [argv[1]], argv[2],
                         lambda: summarise(argv[1], argv[2]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
