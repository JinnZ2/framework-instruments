#!/usr/bin/env python3
"""path_probe.py — which branch produced a test's passing value?

  path_probe.py claims.jsonl SEED probe_results.jsonl

claims.jsonl rows: test (module.Class.method), module (path from the repo
root), guard (source text of an `if` / conditional-expression test in that
module), branch ("if" = the body under the guard, "else" = the other arm).

For each claim, in an order set by SEED: run the test unmutated (baseline),
then rewrite the ONE guard so the claimed branch cannot run (`False` for the
if-body, `True` for the else-body), load the rewritten module in a fresh
subprocess in place of the real one, and run the test again.

  still_passes = true   the test passes with its claimed branch disabled: it
                        is not exercising that branch. A specimen record is
                        attached to the row.
  still_passes = false  the test fails when its branch is disabled: it
                        exercises the branch it claims.
  still_passes = null   not decidable: baseline failed, the guard matched
                        zero or several nodes, or the test did not run.

One question only. Not a mutation-testing framework.
"""

import json
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "instruments"))
import runrecord  # noqa: E402

FIELDS = ("test", "module", "guard", "branch")

BOOTSTRAP = r'''
import ast, io, json, os, sys, types, unittest
cfg = json.loads(sys.argv[1])
sys.path.insert(0, cfg["test_dir"])
sys.path.insert(0, cfg["instruments_dir"])
if cfg["guard"] is not None:
    with open(cfg["module_path"], encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), cfg["module_path"])
    hits = [n for n in ast.walk(tree) if isinstance(n, (ast.If, ast.IfExp))
            and ast.unparse(n.test) == cfg["guard"]]
    if len(hits) != 1:
        print(json.dumps({"guard_matches": len(hits)}))
        sys.exit(3)
    hits[0].test = ast.Constant(value=(cfg["branch"] == "else"))
    ast.fix_missing_locations(tree)
    name = os.path.basename(cfg["module_path"])[:-3]
    mod = types.ModuleType(name)
    mod.__file__ = cfg["module_path"]
    sys.modules[name] = mod
    exec(compile(ast.unparse(tree), cfg["module_path"], "exec"), mod.__dict__)
suite = unittest.defaultTestLoader.loadTestsFromName(cfg["test"])
res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
print(json.dumps({"passed": res.wasSuccessful(), "ran": res.testsRun}))
'''


def find_test_dir(test_module):
    for dirpath, _, files in os.walk(os.path.join(ROOT, "instruments")):
        if test_module + ".py" in files:
            return dirpath
    return None


def run_once(claim, mutate):
    test_dir = find_test_dir(claim["test"].split(".")[0])
    if test_dir is None:
        return {"error": "test module not found"}
    cfg = {"test": claim["test"], "test_dir": test_dir, "instruments_dir": os.path.join(ROOT, "instruments"),
           "module_path": os.path.join(ROOT, claim["module"]),
           "guard": claim["guard"] if mutate else None, "branch": claim["branch"]}
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run([sys.executable, "-c", BOOTSTRAP, json.dumps(cfg)], cwd=tmp,
                              capture_output=True, text=True, timeout=300)
    last = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "{}"
    try:
        return json.loads(last)
    except json.JSONDecodeError:
        return {"error": (proc.stderr or proc.stdout)[-400:]}


def specimen(claim, n):
    return {"specimen_id": f"PROBE-{n:03d}", "package": os.path.dirname(claim["module"]),
            "defect_text": f"{claim['test']} passes with the {claim['branch']} branch of `{claim['guard']}` in {os.path.basename(claim['module'])} disabled.",
            "surface_signal": "test green", "actual_path": "a path other than the claimed branch",
            "intended_path": f"{claim['branch']} branch of `{claim['guard']}`", "detector_exercised": False,
            "masked_by": None, "found_by": "path_probe", "grade": "false", "absent_behaviour": False, "settled_by": None}


def probe(claims_path, seed, out_path):
    claims = []
    for n, row in runrecord.read_jsonl(claims_path, "claims.jsonl"):
        for f in FIELDS:
            if f not in row:
                raise ValueError(f"claims.jsonl line {n}: missing field {f}")
        if row["branch"] not in ("if", "else"):
            raise ValueError(f"claims.jsonl line {n}: field branch must be if or else")
        claims.append(row)
    order = list(range(len(claims)))
    random.Random(seed).shuffle(order)
    rows, n_true, n_void = [], 0, 0
    for k, idx in enumerate(order, 1):
        c = claims[idx]
        base = run_once(c, mutate=False)
        row = dict(c, seed=seed, baseline_passes=bool(base.get("passed")) and base.get("ran", 0) > 0,
                   still_passes=None, guard_matches=None, notes="")
        if not row["baseline_passes"]:
            row["notes"] = "baseline failed or test not run: " + str(base.get("error", base))
        else:
            mut = run_once(c, mutate=True)
            row["guard_matches"] = mut.get("guard_matches", 1 if "passed" in mut else None)
            if "passed" in mut:
                row["still_passes"] = bool(mut["passed"])
            else:
                row["notes"] = "guard matched %s nodes" % mut.get("guard_matches", "?") if "guard_matches" in mut else str(mut.get("error"))
        if row["still_passes"] is True:
            n_true += 1
            row["specimen"] = specimen(c, n_true)
        if row["still_passes"] is None:
            n_void += 1
        rows.append(row)
    runrecord.write_jsonl(out_path, rows)
    counts = {"claims": len(rows), "still_passes_true": n_true,
              "still_passes_false": sum(1 for r in rows if r["still_passes"] is False), "undecidable": n_void}
    return ("ok" if rows else "empty"), counts, ""


def main(argv):
    if len(argv) != 4:
        print("usage: path_probe.py claims.jsonl SEED probe_results.jsonl", file=sys.stderr)
        return 1
    seed = int(argv[2])
    return runrecord.run("arena/path_probe.py", argv[1:], seed, [argv[1]], argv[3],
                         lambda: probe(argv[1], seed, argv[3]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
