#!/usr/bin/env python3
"""B1.5 report.py — report.md from the real and permuted summaries.

Sections, in order, no others:
  1. Counts and the case set actually present.
  2. The D sweep table.
  3. The L sweep table.
  4. Stability overlaps.
  5. REAL vs PERMUTED, side by side, same table shape.
  6. NULLS TRIGGERED — the reference spec's N1..N5, each with its number.

The permuted result is a SECOND OUTPUT, not a gate: neither result is ever
suppressed. If the permuted summary is missing the report is not written and
the run is recorded with status void.

Every threshold below is a [CHOICE]: it is printed in section 6 beside the
number it was compared against, so a reader can move it.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402

N1_RESYNC_FLOOR = 0.9   # [CHOICE] N1 fires if resync_rate >= this at EVERY (D, L, model)
N2_SEP_FLOOR = 1.0      # [CHOICE] N2 fires if sep_rate_high_ent >= this at D_max for every (L, model)
N3_JACCARD_FLOOR = 0.5  # [CHOICE] N3 fires if any adjacent-D Jaccard < this


def split(rows):
    return [r for r in rows if "jaccard" not in r], [r for r in rows if "jaccard" in r]


def pooled(summaries, field, D=None, L=None):
    grp = [s for s in summaries if (D is None or s["D"] == D) and (L is None or s["L"] == L)]
    n = sum(s["count"] for s in grp)
    return {
        "count": n,
        "mean_div_D": sum(s["mean_div_D"] * s["count"] for s in grp) / n if n else None,
        "resync_rate": sum(s["resync_rate"] * s["count"] for s in grp) / n if n else None,
        "top_decile_count": sum(s["top_decile_count"] for s in grp),
    }


def fmt(x):
    return "--" if x is None else (f"{x:.4f}" if isinstance(x, float) else str(x))


def sweep_table(fh, summaries, axis, values):
    fh.write(f"| {axis} | rows | mean div_D | resync rate | top-decile positions |\n|---|---|---|---|---|\n")
    for v in values:
        p = pooled(summaries, None, **{axis: v})
        fh.write(f"| {v} | {p['count']} | {fmt(p['mean_div_D'])} | {fmt(p['resync_rate'])} | {p['top_decile_count']} |\n")
    fh.write("\n")


def stability_table(fh, real_st, perm_st=None):
    head = "| model | fixed | pair | jaccard |" + (" permuted jaccard |" if perm_st is not None else "")
    fh.write(head + "\n|---|---|---|---|" + ("---|" if perm_st is not None else "") + "\n")
    perm_index = {}
    for st in perm_st or []:
        perm_index[(st["model_id"], st.get("L"), st.get("D"), tuple(st.get("D_pair") or st.get("L_pair")))] = st["jaccard"]
    for st in real_st:
        pair = st.get("D_pair") or st.get("L_pair")
        fixed = f"L={st['L']}" if "D_pair" in st else f"D={st['D']}"
        line = f"| {st['model_id']} | {fixed} | {'D' if 'D_pair' in st else 'L'} {pair} | {fmt(st['jaccard'])} |"
        if perm_st is not None:
            line += f" {fmt(perm_index.get((st['model_id'], st.get('L'), st.get('D'), tuple(pair))))} |"
        fh.write(line + "\n")
    fh.write("\n")


def adjacent_d_jaccards(stability):
    return [st["jaccard"] for st in stability if "D_pair" in st]


def nulls(real_sum, real_st, perm_st):
    """Return a list of (code, fired, number_text, description)."""
    out = []
    min_resync = min((s["resync_rate"] for s in real_sum), default=None)
    out.append(("N1", min_resync is not None and min_resync >= N1_RESYNC_FLOOR,
                f"min resync_rate over the sweep = {fmt(min_resync)} (fires at >= {N1_RESYNC_FLOOR})",
                "separations land only on wording: high resync at all D"))
    D_max = max((s["D"] for s in real_sum), default=None)
    at_max = [s for s in real_sum if s["D"] == D_max]
    min_sep_high = min((s["sep_rate_high_ent"] for s in at_max), default=None)
    sep_all = pooled(at_max, None)["resync_rate"]
    sep_all = None if sep_all is None else 1.0 - sep_all
    out.append(("N2", min_sep_high is not None and min_sep_high >= N2_SEP_FLOOR,
                f"min sep_rate_high_ent at D={D_max} = {fmt(min_sep_high)} against sep_rate_all = {fmt(sep_all)} (fires at >= {N2_SEP_FLOOR})",
                "every high-entropy position separates: entropy alone is the measure"))
    dj = adjacent_d_jaccards(real_st)
    lj = [st["jaccard"] for st in real_st if "L_pair" in st]
    out.append(("N3", bool(dj) and min(dj) < N3_JACCARD_FLOOR,
                f"min adjacent-D Jaccard = {fmt(min(dj) if dj else None)}, min adjacent-L Jaccard = {fmt(min(lj) if lj else None)} (fires at D < {N3_JACCARD_FLOOR}); N sweep: NOT EVALUATED, selection is Stage B upstream of separations.jsonl",
                "results depend on D or on N: instrument-dependence finding"))
    pj = adjacent_d_jaccards(perm_st)
    real_mean = sum(dj) / len(dj) if dj else None
    perm_mean = sum(pj) / len(pj) if pj else None
    out.append(("N4", real_mean is not None and perm_mean is not None and perm_mean >= real_mean,
                f"mean adjacent-D Jaccard real = {fmt(real_mean)}, permuted = {fmt(perm_mean)} (fires if permuted >= real)",
                "permuted run clusters as well as the real run: method artifact"))
    out.append(("N5", None,
                "NOT EVALUATED: entropy_basis lives in base.jsonl (counted in the b1_score.py run record); k sensitivity needs a second base pass at another k",
                "top-k truncation changes the entropy ordering"))
    return out


def write_report(path, real_sum, real_st, perm_sum, perm_st):
    cases = sorted({c for s in real_sum for c in s["case_ids"]})
    models = sorted({s["model_id"] for s in real_sum})
    D_vals = sorted({s["D"] for s in real_sum})
    L_vals = sorted({s["L"] for s in real_sum})
    base_rows = pooled(real_sum, None, D=D_vals[0], L=L_vals[0])["count"] if real_sum else 0
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# B1 runner-up trace — separation report\n\n## 1. Counts and case set\n\n")
        fh.write(f"Cases present: {len(cases)} — {', '.join(cases) if cases else '(none)'}\n\n")
        fh.write(f"Models present: {len(models)} — {', '.join(models) if models else '(none)'}\n\n")
        fh.write(f"Separation rows per (D, L): {base_rows}. D swept over {D_vals}. L swept over {L_vals}.\n\n")
        fh.write("No sampling frame is claimed; the case set is what was supplied.\n\n")
        fh.write("## 2. D sweep\n\n")
        sweep_table(fh, real_sum, "D", D_vals)
        fh.write("## 3. L sweep\n\n")
        sweep_table(fh, real_sum, "L", L_vals)
        fh.write("## 4. Stability overlaps\n\nJaccard overlap of top-decile div_D position sets between adjacent sweep values.\n\n")
        stability_table(fh, real_st)
        fh.write("## 5. Real vs permuted\n\n| D | L | model | real mean div | perm mean div | real resync | perm resync | real top-decile | perm top-decile |\n|---|---|---|---|---|---|---|---|---|\n")
        pindex = {(s["D"], s["L"], s["model_id"]): s for s in perm_sum}
        for s in real_sum:
            p = pindex.get((s["D"], s["L"], s["model_id"]), {})
            fh.write(f"| {s['D']} | {s['L']} | {s['model_id']} | {fmt(s['mean_div_D'])} | {fmt(p.get('mean_div_D'))} | "
                     f"{fmt(s['resync_rate'])} | {fmt(p.get('resync_rate'))} | {s['top_decile_count']} | {fmt(p.get('top_decile_count'))} |\n")
        fh.write("\nStability, real beside permuted:\n\n")
        stability_table(fh, real_st, perm_st)
        fh.write("## 6. Nulls triggered\n\nReference spec N1–N5. Each line carries the number it was decided on; thresholds are declared choices.\n\n")
        for code, fired, number, desc in nulls(real_sum, real_st, perm_st):
            state = "NOT EVALUATED" if fired is None else ("FIRED" if fired else "not fired")
            fh.write(f"- **{code}** {state} — {desc}. {number}\n")
        fh.write("\n")


def report(real_path, perm_path, out_path):
    if not os.path.isfile(perm_path):
        return "void", {}, f"permuted summary missing: {os.path.basename(perm_path)}; report not written"
    real_sum, real_st = split([r for _, r in runrecord.read_jsonl(real_path, "summary.jsonl")])
    perm_sum, perm_st = split([r for _, r in runrecord.read_jsonl(perm_path, "summary_permuted.jsonl")])
    write_report(out_path, real_sum, real_st, perm_sum, perm_st)
    fired = [c for c, f, _, _ in nulls(real_sum, real_st, perm_st) if f]
    counts = {"real_summary_rows": len(real_sum), "perm_summary_rows": len(perm_sum), "nulls_fired": len(fired)}
    return ("ok" if real_sum else "empty"), counts, ("fired: " + ",".join(fired)) if fired else ""


def main(argv):
    if len(argv) != 4:
        print("usage: b1_report.py summary.jsonl summary_permuted.jsonl report.md", file=sys.stderr)
        return 1
    return runrecord.run("b1_report.py", argv[1:], None, [argv[1], argv[2]], argv[3],
                         lambda: report(argv[1], argv[2], argv[3]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
