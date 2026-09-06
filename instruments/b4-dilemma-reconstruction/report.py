#!/usr/bin/env python3
"""B4.8 report.py — assemble report.md from all prior outputs.

Required sections, in order, no others:
1. Item set actually present, by arm, with sources.
2. Reconstructor count and how they were kept separate.
3. Requirement counts and the layer strings as returned, with counts.
4. Status distribution across the five states.
5. Policy-to-physical ratio per item, with unresolved printed.
6. Agreement, with the singleton set printed in full.
7. REAL vs SHUFFLED, side by side, same table shape.
8. Calibration arm results, with beyond_report printed.
9. match_source.

If shuffled run is missing, exits void.
"""

import json
import os
import sys
from collections import Counter, defaultdict


def load_jsonl(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main(items_path, reqs_path, grades_path, agree_path,
         shuffled_agree_path, calibration_path, report_path):

    items = load_jsonl(items_path)
    reqs = load_jsonl(reqs_path)
    grades = load_jsonl(grades_path)
    agreement = load_jsonl(agree_path)
    shuffled = load_jsonl(shuffled_agree_path) if os.path.exists(shuffled_agree_path) else None
    calibration = load_jsonl(calibration_path) if os.path.exists(calibration_path) else []

    if shuffled is None:
        print("Shuffled run missing. Exiting void.", file=sys.stderr)
        with open(report_path, "w", encoding="utf-8") as fh:
            fh.write("# B4 Report — VOID\n\nShuffled agreement run missing.\n")
        sys.exit(1)

    # Precompute lookups
    grade_by_item = {g["item_id"]: g for g in grades}
    shuf_by_item = {s["item_id"]: s for s in shuffled}
    recon_ids = sorted({r["reconstructor_id"] for r in reqs})
    layer_counts = Counter(r["layer"] for r in reqs)
    status_counts = Counter(r["status"] for r in reqs)
    arms = Counter(i["arm"] for i in items)
    sources_by_arm = defaultdict(list)
    for i in items:
        sources_by_arm[i["arm"]].append(i["source"])

    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("# B4 Dilemma Reconstruction Protocol Report\n\n")

        # 1. Item set by arm
        fh.write("## 1. Item Set by Arm\n\n")
        for arm in sorted(arms.keys()):
            fh.write(f"### {arm}\n\n")
            fh.write(f"Count: {arms[arm]}\n\n")
            fh.write("Sources:\n")
            for src in sorted(set(sources_by_arm[arm])):
                fh.write(f"- {src}\n")
            fh.write("\n")

        # 2. Reconstructors
        fh.write("## 2. Reconstructor Count and Separation\n\n")
        fh.write(f"Total reconstructors: {len(recon_ids)}\n\n")
        fh.write("IDs: " + ", ".join(recon_ids) + "\n\n")
        fh.write(
            "Separation: File boundary enforced by reconstruct.py; "
            "no reconstructor sees another's output, examples, or prior runs.\n\n"
        )

        # 3. Requirement counts and layers
        fh.write("## 3. Requirement Counts and Layer Strings\n\n")
        fh.write(f"Total requirements: {len(reqs)}\n\n")
        fh.write("| Layer | Count |\n")
        fh.write("|-------|-------|\n")
        for layer, cnt in sorted(layer_counts.items(), key=lambda x: -x[1]):
            fh.write(f"| {layer} | {cnt} |\n")
        fh.write("\n")

        # 4. Status distribution
        fh.write("## 4. Status Distribution\n\n")
        fh.write("| Status | Count |\n")
        fh.write("|--------|-------|\n")
        for st, cnt in sorted(status_counts.items(), key=lambda x: -x[1]):
            fh.write(f"| {st} | {cnt} |\n")
        fh.write("\n")

        # 5. Policy-to-physical ratio
        fh.write("## 5. Policy-to-Physical Ratio per Item\n\n")
        fh.write(
            "| Item ID | Total | Physical | Policy | Unresolved | Ratio |\n"
        )
        fh.write(
            "|---------|-------|----------|--------|------------|-------|\n"
        )
        for iid in sorted(grade_by_item.keys()):
            g = grade_by_item[iid]
            fh.write(
                f"| {iid} | {g['requirement_count']} | {g['physical_count']} | "
                f"{g['policy_count']} | {g['unresolved_count']} | "
                f"{g['policy_to_physical_ratio']} |\n"
            )
        fh.write("\n")

        # 6. Agreement
        fh.write("## 6. Agreement\n\n")
        for agg in agreement:
            iid = agg["item_id"]
            fh.write(f"### Item {iid}\n\n")
            fh.write("Pairwise:\n\n")
            fh.write(
                "| Pair | Agreement | Matched | Total A | Total B |\n"
            )
            fh.write(
                "|------|-----------|---------|---------|---------|\n"
            )
            for p in agg.get("pairwise", []):
                pair = f"{p['reconstructor_a']} ↔ {p['reconstructor_b']}"
                fh.write(
                    f"| {pair} | {p['agreement']:.2f} | {p['matched']} | "
                    f"{p['total_a']} | {p['total_b']} |\n"
                )
            fh.write(
                f"\nFull-disagreement count: {agg['full_disagreement_count']}\n\n"
            )
            singles = agg.get("singleton_set", [])
            fh.write(f"Singleton set ({len(singles)}):\n")
            if singles:
                for s in singles:
                    fh.write(f"- `{s}`\n")
            else:
                fh.write("- (none)\n")
            fh.write("\n")

        # 7. Real vs Shuffled
        fh.write("## 7. Real vs Shuffled Agreement\n\n")
        fh.write(
            "| Item ID | Real (avg) | Shuffled (avg) | "
            "Full-Disagree (real) | Full-Disagree (shuffled) |\n"
        )
        fh.write(
            "|---------|------------|----------------|"
            "----------------------|--------------------------|\n"
        )
        for agg in agreement:
            iid = agg["item_id"]
            pw = agg.get("pairwise", [])
            real_avg = sum(p["agreement"] for p in pw) / len(pw) if pw else 0.0
            shuf = shuf_by_item.get(iid, {})
            spw = shuf.get("pairwise", [])
            shuf_avg = sum(p["agreement"] for p in spw) / len(spw) if spw else 0.0
            fh.write(
                f"| {iid} | {real_avg:.2f} | {shuf_avg:.2f} | "
                f"{agg['full_disagreement_count']} | "
                f"{shuf.get('full_disagreement_count', 0)} |\n"
            )
        fh.write("\n")

        # 8. Calibration
        fh.write("## 8. Calibration Arm Results\n\n")
        if calibration:
            fh.write(
                "| Item ID | Recovered | Missed | Beyond Report | "
                "Total Factors | Total Reqs |\n"
            )
            fh.write(
                "|---------|-----------|--------|---------------|"
                "---------------|------------|\n"
            )
            for cal in calibration:
                fh.write(
                    f"| {cal['item_id']} | {cal['recovered_count']} | "
                    f"{cal['missed_count']} | {cal['beyond_report']} | "
                    f"{cal['total_factors']} | {cal['total_requirements']} |\n"
                )
        else:
            fh.write("No documented-arm items present.\n")
        fh.write("\n")

        # 9. match_source
        fh.write("## 9. Match Source\n\n")
        match_sources = sorted({a.get("match_source", "unknown") for a in agreement})
        for src in match_sources:
            fh.write(f"- {src}\n")
        fh.write("\n")

    print(f"Report written to {report_path}")


# ---- run-record wiring (added; logic above is unchanged) --------------------
import os  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402


def _rows(path):
    try:
        return sum(1 for _ in runrecord.read_jsonl(path))
    except (OSError, ValueError):
        return None


def _status_by_rows(path):
    n = _rows(path)
    return ("ok" if n else "empty"), {"rows": n}, ""

def cli(argv):
    if len(argv) != 8:
        print("Usage: report.py <items> <reqs> <grades> <agreement> <shuffled_agreement> <calibration> <report.md>", file=sys.stderr)
        return 1

    def body():
        try:
            main(*argv[1:])
        except SystemExit as exc:
            return "void", {}, f"shuffled agreement run missing (exit {exc.code}); VOID report written"
        return "ok", {}, ""
    return runrecord.run("b4/report.py", argv[1:], None, list(argv[1:7]), argv[7], body)


if __name__ == "__main__":
    sys.exit(cli(sys.argv))
