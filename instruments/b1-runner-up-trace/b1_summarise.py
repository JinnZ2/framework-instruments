#!/usr/bin/env python3
"""B1.4 summarise.py — aggregate separations.jsonl (real or permuted).

Per (D, L, model_id): count, mean div_D, resync rate, top-decile count.
Stability: Jaccard overlap of top-decile position sets for adjacent D and L.
"""

import json
import sys
from collections import defaultdict


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def summarise(in_path, out_path):
    rows = []
    with open(in_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))

    # Group by (D, L, model_id)
    groups = defaultdict(list)
    for r in rows:
        groups[(r["D"], r["L"], r["model_id"])].append(r)

    summaries = []
    for key in sorted(groups.keys()):
        D, L, model_id = key
        grp = groups[key]
        divs = [r["div_D"] for r in grp]
        resyncs = [r["resync_D"] for r in grp]
        mean_div = sum(divs) / len(divs) if divs else 0.0
        resync_rate = sum(resyncs) / len(resyncs) if resyncs else 0.0

        # Top decile of div_D
        sorted_div = sorted(grp, key=lambda r: r["div_D"], reverse=True)
        cutoff = max(1, len(sorted_div) // 10)
        top_decile = {r["i"] for r in sorted_div[:cutoff]}

        summaries.append({
            "D": D, "L": L, "model_id": model_id,
            "count": len(grp), "mean_div_D": mean_div,
            "resync_rate": resync_rate, "top_decile_count": len(top_decile),
            "top_decile_positions": sorted(top_decile),
            "case_ids": sorted({r["case_id"] for r in grp}),
        })

    # Stability: adjacent D and L overlaps
    stability = []
    # Adjacent D
    D_vals = sorted({s["D"] for s in summaries})
    L_vals = sorted({s["L"] for s in summaries})
    models = sorted({s["model_id"] for s in summaries})

    for model_id in models:
        for L in L_vals:
            for i in range(len(D_vals) - 1):
                d1, d2 = D_vals[i], D_vals[i + 1]
                s1 = next((s for s in summaries if s["D"] == d1 and s["L"] == L and s["model_id"] == model_id), None)
                s2 = next((s for s in summaries if s["D"] == d2 and s["L"] == L and s["model_id"] == model_id), None)
                if s1 and s2:
                    overlap = jaccard(set(s1["top_decile_positions"]), set(s2["top_decile_positions"]))
                    stability.append({
                        "model_id": model_id, "L": L,
                        "D_pair": [d1, d2], "type": "D_adjacent",
                        "jaccard": overlap,
                    })
        for D in D_vals:
            for i in range(len(L_vals) - 1):
                l1, l2 = L_vals[i], L_vals[i + 1]
                s1 = next((s for s in summaries if s["D"] == D and s["L"] == l1 and s["model_id"] == model_id), None)
                s2 = next((s for s in summaries if s["D"] == D and s["L"] == l2 and s["model_id"] == model_id), None)
                if s1 and s2:
                    overlap = jaccard(set(s1["top_decile_positions"]), set(s2["top_decile_positions"]))
                    stability.append({
                        "model_id": model_id, "D": D,
                        "L_pair": [l1, l2], "type": "L_adjacent",
                        "jaccard": overlap,
                    })

    with open(out_path, "w", encoding="utf-8") as fh:
        for s in summaries:
            fh.write(json.dumps({"type": "summary", **s}, ensure_ascii=False) + "\n")
        for st in stability:
            fh.write(json.dumps({"type": "stability", **st}, ensure_ascii=False) + "\n")

    print(f"Summarised {len(summaries)} groups, {len(stability)} stability entries")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: summarise.py <separations.jsonl> <summary.jsonl>", file=sys.stderr)
        sys.exit(1)
    summarise(sys.argv[1], sys.argv[2])
