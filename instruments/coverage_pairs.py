#!/usr/bin/env python3
"""coverage_pairs.py — coverage as counted (function, status) pairs, never a bare percentage.

  coverage_pairs.py instruments_dir coverage.jsonl

REACHABLE pairs are read from source: every runrecord.run("<script>", ...)
call names a script; the body it runs (a lambda calling a module function, or
a nested `body` function) is walked for `return ("<status>", ...)` literals,
plus "ok"/"empty" when it delegates to `_status_by_rows`, plus "error" always,
since runrecord.run turns any exception into an error row.

EXERCISED pairs are observed: every test module in the tree is run in-process
with runrecord.record wrapped to log (script, status). A pair is exercised iff
a test made that script return that status through the run record.

Output: one row per reachable pair with exercised true/false, one row per
exercised pair that no source walk predicted (a reachable-set gap), and the
two counts on the summary line. A percentage without both counts is not
reported.
"""

import ast
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runrecord  # noqa: E402

STATUSES = set(runrecord.STATUSES)


def _module_functions(tree):
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def _status_literals(fn):
    """Every status literal anywhere in the body function counts as reachable
    (a literal assigned to a variable and returned later is still a path);
    delegation to _status_by_rows adds ok and empty. Over-approximates a
    literal used for something other than a return; that direction only
    lowers the reported coverage, never raises it."""
    found = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Constant) and node.value in STATUSES:
            found.add(node.value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_status_by_rows":
            found.update({"ok", "empty"})
    return found


def _body_function(call, enclosing, module_fns):
    body_arg = call.args[5] if len(call.args) > 5 else None
    if isinstance(body_arg, ast.Lambda) and isinstance(body_arg.body, ast.Call) \
            and isinstance(body_arg.body.func, ast.Name):
        return module_fns.get(body_arg.body.func.id)
    if isinstance(body_arg, ast.Name):
        for node in ast.walk(enclosing):
            if isinstance(node, ast.FunctionDef) and node.name == body_arg.id:
                return node
    return None


def reachable_pairs(root):
    pairs = {}
    for dirpath, _, files in sorted(os.walk(root)):
        for fn in sorted(files):
            if not fn.endswith(".py") or fn.startswith("test_") or fn in ("runrecord.py", "coverage_pairs.py"):
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8") as fh:
                tree = ast.parse(fh.read(), path)
            fns = _module_functions(tree)
            for top in tree.body:
                if not isinstance(top, ast.FunctionDef):
                    continue
                for node in ast.walk(top):
                    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                            and node.func.attr == "run" and node.args
                            and isinstance(node.args[0], ast.Constant)):
                        script = node.args[0].value
                        body = _body_function(node, top, fns)
                        statuses = (_status_literals(body) if body is not None else set()) | {"error"}
                        for st in statuses:
                            pairs[(script, st)] = os.path.relpath(path, root)
    return pairs


def exercised_pairs(root):
    seen = set()
    original = runrecord.record

    def logging_record(script, args, seed, inputs, outputs, status, counts, notes, runs_path=runrecord.RUNS_FILE):
        seen.add((script, status))
        return original(script, args, seed, inputs, outputs, status, counts, notes, runs_path=runs_path)

    runrecord.record = logging_record
    cwd = os.getcwd()
    try:
        for dirpath, _, files in sorted(os.walk(root)):
            tests = sorted(f for f in files if f.startswith("test_") and f.endswith(".py"))
            if not tests:
                continue
            for name in tests:
                sys.path.insert(0, dirpath)
                suite = unittest.defaultTestLoader.loadTestsFromName(name[:-3])
                with tempfile.TemporaryDirectory() as tmp:
                    os.chdir(tmp)
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
                    os.chdir(cwd)
                sys.path.pop(0)
                sys.modules.pop(name[:-3], None)
    finally:
        os.chdir(cwd)
        runrecord.record = original
    return seen


def coverage(root, out_path):
    reachable = reachable_pairs(root)
    exercised = exercised_pairs(root)
    rows = [{"script": s, "status": st, "declared_in": path, "reachable": True, "exercised": (s, st) in exercised}
            for (s, st), path in sorted(reachable.items())]
    unpredicted = sorted(exercised - set(reachable))
    rows += [{"script": s, "status": st, "declared_in": None, "reachable": False, "exercised": True}
             for s, st in unpredicted]
    runrecord.write_jsonl(out_path, rows)
    hit = sum(1 for r in rows if r["reachable"] and r["exercised"])
    missing = [f"{r['script']}:{r['status']}" for r in rows if r["reachable"] and not r["exercised"]]
    counts = {"pairs_reachable": len(reachable), "pairs_exercised": hit, "pairs_unpredicted": len(unpredicted),
              "scripts": len({s for s, _ in reachable})}
    notes = f"exercised {hit} of {len(reachable)} reachable (script, status) pairs"
    if missing:
        notes += "; unexercised: " + ", ".join(missing)
    return ("ok" if reachable else "empty"), counts, notes


def main(argv):
    if len(argv) != 3:
        print("usage: coverage_pairs.py instruments_dir coverage.jsonl", file=sys.stderr)
        return 1
    return runrecord.run("coverage_pairs.py", argv[1:], None, [], argv[2], lambda: coverage(argv[1], argv[2]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
