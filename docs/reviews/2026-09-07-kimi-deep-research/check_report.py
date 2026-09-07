#!/usr/bin/env python3
"""check_report.py — recompute what the Kimi deep-research report (2026-09-07)
states about this repository, from the tree and by running the instruments.

  check_report.py checks.jsonl

The report itself is not in this tree (see AUDIT.md); the numbers it states
are transcribed below as data. Each row: check, report_states, observed,
agrees (true / false / null = not evaluable here). External-literature claims
are not evaluated: the egress policy refuses their sources.
"""

import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "instruments"))
import runrecord  # noqa: E402

REPORT_SHA256 = "13ab0dba8538274808abedb451b345576432aa2e7ea944951c91b2b4db82ab86"  # of the delivered zip
COMMIT = "47787e9"
FIG3_MEAN_DIV = [1.0, 1.0, 0.8125, 0.6562, 0.5781]      # printed on the report's Figure 3
FIG3_RESYNC = [0.0, 0.0, 0.5, 0.5, 0.5]
SPEC_QUOTES = {
    "frame-location-benchmark.md": ["40%", "one capacity and the split is decoration", "measuring suspicion, not frame-location"],
    "model-deprecation-backcast.md": ["0.1% daily selection"],
    "routing-data-layer-marker.md": ["An unscoped claim substitutes for a solution"],
}


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def row(check, states, observed, agrees):
    return {"check": check, "report_states": states, "observed": observed, "agrees": agrees}


def old_tree():
    tmp = tempfile.mkdtemp()
    data = subprocess.run(["git", "archive", COMMIT], cwd=ROOT, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(tmp)
    return tmp


def check_commits():
    lines = git("log", "--format=%H %ad", "--date=iso-strict-local", COMMIT).strip().splitlines()
    dates = {l.split()[1][:10] for l in lines}
    return [row("commits reachable from 47787e9, all dated 2026-09-06", "four, all 2026-09-06",
                {"count": len(lines), "dates_utc": sorted(dates)}, len(lines) == 4 and dates == {"2026-09-06"})]


def check_lines(tree):
    py = [os.path.join(d, f) for d, _, fs in os.walk(tree) for f in fs if f.endswith(".py")]
    total = sum(sum(1 for _ in open(p, encoding="utf-8")) for p in py)
    non_test = [p for p in py if not os.path.basename(p).startswith("test_")]
    non_test_lines = sum(sum(1 for _ in open(p, encoding="utf-8")) for p in non_test)
    scripts = sum(1 for p in non_test if 'runrecord.run("' in open(p, encoding="utf-8").read()
                  and os.path.basename(p) != "coverage_pairs.py")  # the counter does not count itself
    return [row("Python line count and script count", "roughly 4,200 lines of Python across 23 scripts",
                {"lines_all_py": total, "py_files": len(py), "lines_non_test": non_test_lines,
                 "non_test_files": len(non_test), "run_record_scripts": scripts},
                abs(total - 4200) < 100 and scripts == 23),
            row("the two numbers share a frame", "one count", "4,200 counts test files; 23 does not", False)]


def check_specs(tree):
    specs = sorted(os.listdir(os.path.join(tree, "docs", "specifications")))
    return [row("specification files", "seven unbuilt instrument specifications; Figure 1 shows 4 spec-only + 1 marker",
                {"files": len(specs), "spec_only_in_figure_1": 4, "marker": 1}, False)]


def check_arena():
    specs = [r for _, r in runrecord.read_jsonl(os.path.join(ROOT, "arena", "specimens.jsonl"))]
    grades = {}
    for s in specs:
        grades[s["grade"]] = grades.get(s["grade"], 0) + 1
    chains = sorted(f"{s['specimen_id']}<-{s['masked_by']}" for s in specs if s["masked_by"])
    obs = {"specimens": len(specs), "grades": grades,
           "detector_exercised_false": sum(1 for s in specs if not s["detector_exercised"]), "chains": chains}
    ok = (len(specs) == 12 and grades.get("false") == 10 and grades.get("partial") == 1
          and grades.get("undifferentiated") == 1 and obs["detector_exercised_false"] == 11
          and chains == ["SPEC-002<-SPEC-001", "SPEC-007<-SPEC-005"])
    return [row("arena specimen counts", "12 specimens: 10 false, 1 partial, 1 undifferentiated; 11 detector_exercised false; chains 002<-001, 007<-005", obs, ok),
            row("SPEC-001..003 provenance", "presented as this repository's own defect history",
                "arena/README.md: seeds describe full_instrument_suite, NOT in this repository, unverified", False)]


def check_coverage(tree):
    with tempfile.TemporaryDirectory() as tmp:
        out = subprocess.run([sys.executable, os.path.join(tree, "instruments", "coverage_pairs.py"),
                              os.path.join(tree, "instruments"), "cov.jsonl"], cwd=tmp, capture_output=True, text=True).stdout
        rows = [r for _, r in runrecord.read_jsonl(os.path.join(tmp, "cov.jsonl"))]
    reach = [r for r in rows if r["reachable"]]
    missing = sorted(f"{r['script']}:{r['status']}" for r in reach if not r["exercised"])
    obs = {"exercised": sum(1 for r in reach if r["exercised"]), "reachable": len(reach), "unexercised": missing}
    return [row("coverage pairs at 47787e9", "69 of 72; unexercised b4/items:empty, b4/nullshuffle:empty, b4/requirements:empty", obs,
                obs["exercised"] == 69 and obs["reachable"] == 72 and missing == ["b4/items.py:empty", "b4/nullshuffle.py:empty", "b4/requirements.py:empty"])]


def check_probe():
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([sys.executable, os.path.join(ROOT, "arena", "path_probe.py"),
                        os.path.join(ROOT, "arena", "claims.jsonl"), "7", "probe.jsonl"], cwd=tmp, capture_output=True, text=True)
        rows = [r for _, r in runrecord.read_jsonl(os.path.join(tmp, "probe.jsonl"))]
    still = [r["test"].split(".")[-1] for r in rows if r["still_passes"] is True]
    obs = {"claims": len(rows), "still_passes_false": sum(1 for r in rows if r["still_passes"] is False), "still_passes_true": still}
    return [row("path_probe on the shipped claims", "10 of 11 false; test_permutation_preserves_count_and_multiset still passes", obs,
                obs["claims"] == 11 and obs["still_passes_false"] == 10 and still == ["test_permutation_preserves_count_and_multiset"])]


def b1_run(traces, tmp):
    b1 = os.path.join(ROOT, "instruments", "b1-runner-up-trace")
    sys.path.insert(0, b1)
    import b1_score, b1_permute, b1_summarise  # noqa: E401
    base_cont = list(range(1000, 1128))
    base = [{"case_id": c, "model_id": "m", "i": 0, "token_taken": 1, "logprob_taken": -0.1, "topk": [[1, -0.1], [2, -0.5]],
             "entropy_i": 1.0, "entropy_basis": "full"} for c in ("a", "b")]
    tr = [{"case_id": c, "model_id": "m", "i": 0, "branch_rank": 2, "forced_token": 2, "continuation": cont,
           "base_continuation": base_cont} for c, cont in zip(("a", "b"), traces)]
    cwd = os.getcwd()
    os.chdir(tmp)
    try:
        runrecord.write_jsonl("base.jsonl", base)
        runrecord.write_jsonl("traces.jsonl", tr)
        with redirect_stdout(io.StringIO()):
            b1_score.main(["x", "base.jsonl", "traces.jsonl", "sep.jsonl"])
            perm_code = b1_permute.main(["x", "sep.jsonl", "1", "perm.jsonl"])
            b1_summarise.main(["x", "sep.jsonl", "sum.jsonl"])
        summ = [r for _, r in runrecord.read_jsonl("sum.jsonl") if "jaccard" not in r and r["L"] == 4]
        perm_rec = [r for _, r in runrecord.read_jsonl("runs.jsonl") if r["script"] == "b1_permute.py"][-1]
    finally:
        os.chdir(cwd)
    return [round(s["mean_div_D"], 4) for s in summ], [s["resync_rate"] for s in summ], perm_code, perm_rec


def check_figure3():
    base_cont = list(range(1000, 1128))
    with tempfile.TemporaryDirectory() as tmp:
        div, res, perm_code, perm_rec = b1_run([[7000 + k for k in range(20)] + base_cont[20:], [9000 + k for k in range(128)]], tmp)
    with tempfile.TemporaryDirectory() as tmp:
        sdiv, sres, _, _ = b1_run([[7000] + base_cont[:127], [9000 + k for k in range(128)]], tmp)
    return [row("Figure 3 values reproduce from an ALIGNED rejoin at token 20 plus a never-rejoin case",
                "mean div 1, 1, 0.8125, 0.6562, 0.5781; resync 0.5 from D=32", {"mean_div_D": div, "resync": res},
                div == FIG3_MEAN_DIV and res == FIG3_RESYNC),
            row("a genuinely SHIFTED rejoin under the aligned reading", "report: shifted case resynchronised once D exceeded the shift",
                {"shift_by_one_token": {"mean_div_D": sdiv, "resync": sres}}, all(r == 0.0 for r in sres) is False),
            row("the report's two-case permutation null", "N2 and N4 fired with their triggering numbers (at 47787e9)",
                {"at_47787e9": "both fired because every stratum held one position and the permutation was the identity",
                 "now": {"permute_status": perm_rec["status"], "single_position_strata": perm_rec["counts"]["single_position_strata"],
                         "strata": perm_rec["counts"]["strata"], "exit": perm_code}},
                False)]


def check_dates_and_quotes():
    out = [row("retirement date after announcement date", "announced 2026-09-03; retire on 2026-02-13",
               {"retirement_minus_announcement_days": -202}, False)]
    for fn, quotes in SPEC_QUOTES.items():
        text = open(os.path.join(ROOT, "docs", "specifications", fn), encoding="utf-8").read()
        found = {q: (q in text) for q in quotes}
        out.append(row(f"quotes attributed to {fn}", quotes, found, all(found.values())))
    return out


def check(out_path):
    tree = old_tree()
    rows = (check_commits() + check_lines(tree) + check_specs(tree) + check_arena() + check_coverage(tree)
            + check_probe() + check_figure3() + check_dates_and_quotes())
    runrecord.write_jsonl(out_path, rows)
    counts = {"checks": len(rows), "agree": sum(1 for r in rows if r["agrees"] is True),
              "disagree": sum(1 for r in rows if r["agrees"] is False), "not_evaluable": sum(1 for r in rows if r["agrees"] is None)}
    return "ok", counts, f"report zip sha256 {REPORT_SHA256[:16]}; literature claims not evaluated (egress)"


def main(argv):
    if len(argv) != 2:
        print("usage: check_report.py checks.jsonl", file=sys.stderr)
        return 1
    return runrecord.run("docs/reviews/2026-09-07-kimi-deep-research/check_report.py", argv[1:], None, [], argv[1],
                         lambda: check(argv[1]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
