#!/usr/bin/env python3
"""B1.5 report.py — assemble report.md from real and permuted summaries.

Required sections, in order, no others:
1. Counts and the case set actually present.
2. The D sweep table.
3. The L sweep table.
4. Stability overlaps.
5. REAL vs PERMUTED, side by side, same table shape.
6. NULLS TRIGGERED.

If permuted summary is missing, exits void.
"""

import json
import os
import sys


def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main(real_summary, perm_summary, nulls_path, report_path):
    if not os.path.exists(perm_summary):
        print("Permuted summary missing. Exiting void.", file=sys.stderr)
        sys.exit(1)

    real = load_jsonl(real_summary)
    perm = load_jsonl(perm_summary)
    nulls = load_jsonl(nulls_path) if os.path.exists(nulls_path) else []

    real_summaries = [r for r in real if r.get("type") == "summary"]
    real_stability = [r for r in real if r.get("type") == "stability"]
    perm_summaries = [r for r in perm if r.get("type") == "summary"]
    perm_stability = [r for r in perm if r.get("type") == "stability"]

    cases = sorted({
        case_id
        for row in real_summaries
        for case_id in row.get("case_ids", [])
    })
    models = sorted({r["model_id"] for r in real_summaries})
    D_vals = sorted({r["D"] for r in real_summaries})
    L_vals = sorted({r["L"] for r in real_summaries})

    # Null counts
    null_counts = {}
    for n in nulls:
        null_counts[n["null_code"]] = null_counts.get(n["null_code"], 0) + 1

    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("# B1 Runner-Up Trace Scoring Report\n\n")

        # 1. Counts and case set
        fh.write("## 1. Counts and Case Set\n\n")
        fh.write(f"Cases: {len(cases)} — {', '.join(cases)}\n\n")
        fh.write(f"Models: {len(models)} — {', '.join(models)}\n\n")
        fh.write(f"Real separations: {len(real_summaries)} summary rows\n\n")

        # 2. D sweep table
        fh.write("## 2. D Sweep Table\n\n")
        fh.write("| D | Count | Mean div_D | Resync Rate | Top-Decile Count |\n")
        fh.write("|---|-------|------------|-------------|------------------|\n")
        for D in D_vals:
            grp = [r for r in real_summaries if r["D"] == D]
            cnt = sum(r["count"] for r in grp)
            mean_div = sum(r["mean_div_D"] * r["count"] for r in grp) / cnt if cnt else 0
            resync = sum(r["resync_rate"] * r["count"] for r in grp) / cnt if cnt else 0
            top_dec = sum(r["top_decile_count"] for r in grp)
            fh.write(f"| {D} | {cnt} | {mean_div:.4f} | {resync:.4f} | {top_dec} |\n")
        fh.write("\n")

        # 3. L sweep table
        fh.write("## 3. L Sweep Table\n\n")
        fh.write("| L | Count | Mean div_D | Resync Rate | Top-Decile Count |\n")
        fh.write("|---|-------|------------|-------------|------------------|\n")
        for L in L_vals:
            grp = [r for r in real_summaries if r["L"] == L]
            cnt = sum(r["count"] for r in grp)
            mean_div = sum(r["mean_div_D"] * r["count"] for r in grp) / cnt if cnt else 0
            resync = sum(r["resync_rate"] * r["count"] for r in grp) / cnt if cnt else 0
            top_dec = sum(r["top_decile_count"] for r in grp)
            fh.write(f"| {L} | {cnt} | {mean_div:.4f} | {resync:.4f} | {top_dec} |\n")
        fh.write("\n")

        # 4. Stability overlaps
        fh.write("## 4. Stability Overlaps\n\n")
        fh.write("| Type | Model | Parameter Pair | Jaccard |\n")
        fh.write("|------|-------|----------------|---------|\n")
        for st in real_stability:
            pair = st.get("D_pair") or st.get("L_pair")
            fh.write(f"| {st['type']} | {st['model_id']} | {pair} | {st['jaccard']:.4f} |\n")
        fh.write("\n")

        # 5. REAL vs PERMUTED
        fh.write("## 5. Real vs Permuted\n\n")
        fh.write("| D | L | Model | Real Mean div | Perm Mean div | Real Resync | Perm Resync |\n")
        fh.write("|---|---|-------|---------------|---------------|-------------|-------------|\n")
        for key in sorted({(r["D"], r["L"], r["model_id"]) for r in real_summaries}):
            D, L, model_id = key
            real_row = next((r for r in real_summaries if (r["D"], r["L"], r["model_id"]) == key), {})
            perm_row = next((r for r in perm_summaries if (r["D"], r["L"], r["model_id"]) == key), {})
            fh.write(f"| {D} | {L} | {model_id} | "
                     f"{real_row.get('mean_div_D', 0):.4f} | "
                     f"{perm_row.get('mean_div_D', 0):.4f} | "
                     f"{real_row.get('resync_rate', 0):.4f} | "
                     f"{perm_row.get('resync_rate', 0):.4f} |\n")
        fh.write("\n")

        # 6. NULLS TRIGGERED
        fh.write("## 6. Nulls Triggered\n\n")
        for code in ["N1", "N2", "N3", "N4", "N5"]:
            fh.write(f"- **{code}**: {null_counts.get(code, 0)}\n")
        fh.write("\n")

    print(f"Report written to {report_path}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: report.py <real_summary> <perm_summary> <nulls.jsonl> <report.md>",
              file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
