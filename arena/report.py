#!/usr/bin/env python3
"""report.py — the arena report, six sections, in order, no others.

  report.py specimens.jsonl probe_results.jsonl report.md

Refuses (status void, nothing written) a specimen set graded only true/false:
two states means the grading was not run. Section 2 — the count of
detector_exercised: false — precedes every aggregate, since a pass rate
printed above the false-green count reproduces the original error at the
report layer.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "instruments"))
import runrecord  # noqa: E402

GRADES = ("true", "false", "lapsed", "partial", "unknown", "undifferentiated")
FIELDS = ("specimen_id", "package", "defect_text", "surface_signal", "actual_path", "intended_path",
          "detector_exercised", "masked_by", "found_by", "grade", "absent_behaviour", "settled_by")


def load_specimens(path):
    out, ids = [], set()
    for n, row in runrecord.read_jsonl(path, "specimens.jsonl"):
        for f in FIELDS:
            if f not in row:
                raise ValueError(f"specimens.jsonl line {n}: missing field {f}")
        if row["grade"] not in GRADES:
            raise ValueError(f"specimens.jsonl line {n}: field grade must be one of {GRADES}")
        if not isinstance(row["detector_exercised"], bool) or not isinstance(row["absent_behaviour"], bool):
            raise ValueError(f"specimens.jsonl line {n}: detector_exercised and absent_behaviour must be booleans")
        if row["specimen_id"] in ids:
            raise ValueError(f"specimens.jsonl line {n}: duplicate specimen_id {row['specimen_id']}")
        ids.add(row["specimen_id"])
        out.append(row)
    for row in out:
        if row["masked_by"] is not None and row["masked_by"] not in ids:
            raise ValueError(f"{row['specimen_id']}: masked_by {row['masked_by']} is not a specimen")
    return out


def chain(spec, by_id):
    ids, cur = [spec["specimen_id"]], spec
    while cur["masked_by"] is not None and cur["masked_by"] not in ids:
        cur = by_id[cur["masked_by"]]
        ids.append(cur["specimen_id"])
    return ids


def write(path, specs, probe):
    by_id = {s["specimen_id"]: s for s in specs}
    grades = {g: sum(1 for s in specs if s["grade"] == g) for g in GRADES}
    not_ex = [s for s in specs if not s["detector_exercised"]]
    signature = [s for s in not_ex if s["surface_signal"].startswith("test green")]
    masked = [s for s in specs if s["masked_by"] is not None]
    absent = [s for s in specs if s["absent_behaviour"]]
    wrong = [s for s in specs if not s["absent_behaviour"]]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# Arena report\n\n## 1. Specimen count by grade\n\n| grade | count |\n|---|---|\n")
        for g in GRADES:
            fh.write(f"| {g} | {grades[g]} |\n")
        fh.write(f"\nSpecimens: {len(specs)}.\n\n## 2. detector_exercised: false\n\n")
        fh.write(f"**{len(not_ex)}** specimens have `detector_exercised: false`; **{len(signature)}** of those carry the class signature (`surface_signal` = test green).\n\n")
        fh.write("- " + "\n- ".join(f"{s['specimen_id']} ({s['package']})" for s in not_ex) + "\n\n" if not_ex else "(none)\n\n")
        fh.write("## 3. Masking chains\n\n")
        maskers = {s["masked_by"] for s in masked}
        fh.write(f"{len(masked)} masked specimens; {len(maskers)} distinct upstream maskers.\n\n")
        for s in masked:
            fh.write("- " + " <- masked by ".join(chain(s, by_id)) + "\n")
        fh.write("\n## 4. Absent behaviour, apart from wrong behaviour\n\n")
        fh.write(f"Absent behaviour ({len(absent)}; packages: {sorted({s['package'] for s in absent})}):\n\n")
        for s in absent:
            fh.write(f"- {s['specimen_id']} [{s['grade']}] {s['surface_signal']}\n")
        fh.write(f"\nWrong behaviour ({len(wrong)}; packages: {sorted({s['package'] for s in wrong})}):\n\n")
        for s in wrong:
            fh.write(f"- {s['specimen_id']} [{s['grade']}] {s['actual_path']} -> intended: {s['intended_path']}\n")
        fh.write("\n## 5. path_probe: tests passing with their claimed branch disabled\n\n")
        still = [r for r in probe if r.get("still_passes") is True]
        fh.write(f"Claims probed: {len(probe)}; still_passes true: {len(still)}; false: {sum(1 for r in probe if r.get('still_passes') is False)}; undecidable: {sum(1 for r in probe if r.get('still_passes') is None)}.\n\n")
        for r in probe:
            state = {True: "STILL PASSES", False: "exercised", None: "undecidable"}[r.get("still_passes")]
            fh.write(f"- {state}: {r['test']} / `{r['guard']}` ({r['branch']}) {r.get('notes', '')}\n")
        fh.write("\n## 6. Undifferentiated, and what would settle it\n\n")
        und = [s for s in specs if s["grade"] == "undifferentiated"]
        if not und:
            fh.write("(none graded undifferentiated)\n")
        for s in und:
            fh.write(f"- {s['specimen_id']}: {s['settled_by'] or 'no instrument named'}\n")
        fh.write("\nAny specimen with `detector_exercised: false` that has not been probed is settled by `path_probe.py` with a claim naming its intended branch.\n")


def report(spec_path, probe_path, out_path):
    specs = load_specimens(spec_path)
    present = {s["grade"] for s in specs}
    if specs and present <= {"true", "false"}:
        return "void", {"specimens": len(specs)}, f"grades present {sorted(present)}: two-state grading was not run; report not written"
    probe = [r for _, r in runrecord.read_jsonl(probe_path, "probe_results.jsonl")] if os.path.isfile(probe_path) else []
    write(out_path, specs, probe)
    counts = {"specimens": len(specs), "detector_not_exercised": sum(1 for s in specs if not s["detector_exercised"]),
              "probe_rows": len(probe), "probe_still_passes": sum(1 for r in probe if r.get("still_passes") is True)}
    notes = "" if os.path.isfile(probe_path) else "probe_results missing: section 5 empty"
    return ("ok" if specs else "empty"), counts, notes


def main(argv):
    if len(argv) != 4:
        print("usage: report.py specimens.jsonl probe_results.jsonl report.md", file=sys.stderr)
        return 1
    return runrecord.run("arena/report.py", argv[1:], None, [argv[1], argv[2]], argv[3],
                         lambda: report(argv[1], argv[2], argv[3]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
