# framework-instruments

CC0 collection of small, falsifiable measurement instruments. Index only;
detail lives in each instrument's `README.md`, the specifications under
`docs/specifications/`, and the dated audit under `docs/`.

## Read first

- `docs/specifications/frame-instruments-ordered-queue.md` — the work order
  B1–B3 are built to. Its HARD CONSTRAINTS and SHARED RULE bind every script
  in this repository, B4 and the arena included.
- `docs/AUDIT_2026-09-06.md` — what the build did not do that the
  specification said, and what changed. Read before assuming a green suite
  means conformance; the audit's own subject is greens that meant nothing.
- `arena/grading.md` — the five-state grade and the one claim it grades.

## Layout

| path | what it is |
|---|---|
| `instruments/runrecord.py` | The run record. Every script's every run is one row in `runs.jsonl` (cwd), status `ok` / `void` / `error` / `empty`, through `runrecord.run()`. Failure rows come from the same code path as success rows. |
| `instruments/b1-runner-up-trace/` | Offline scoring half of the runner-up trace: schema → score → permute (null) → summarise → report. D and L both swept and written into every row. |
| `instruments/b2-audit-isolation/` | Key-as-artifact under conditions A/B/C/D; commit/release lock as a process boundary; agreement across auditors, never correctness. |
| `instruments/b3-split-authorship/` | Case role and key role that never share context, enforced by file boundary; joins into B2's case schema with drops counted; arms never mixed. |
| `instruments/b4-dilemma-reconstruction/` | Requirement-set reconstruction, agreement, shuffle null, calibration. Delivered logic; only its entry points were wired to the run record. |
| `instruments/unfold/` | Deterministic frame-analysis prompt generator. Preserves the dilemma verbatim and emits legitimate, incomplete, and corrupt verdict paths; model execution remains outside the repository. `unfold_score.py` counts what a retained response contains (verdict, pattern rows by evidence state); `controls/` holds two constructed dilemmas with verdicts declared before any run. Audit: `docs/AUDIT_UNFOLD_2026-09-07.md`. |
| `instruments/coverage_pairs.py` | Coverage as counted `(script, status)` pairs exercised over reachable. Run it; do not store its numbers here. |
| `instruments/test_status_paths.py` | Every script's `empty` and `error` paths through the run record. |
| `arena/` | Specimens of defects that pass every normal signal; `path_probe.py` disables one claimed branch and re-runs the claiming test; `report.py` puts the false-green count before any aggregate. |
| `docs/specifications/` | Source specifications, delivered verbatim, never edited by an audit. |
| `docs/reviews/` | Audits of external reviews of this repository. A review is not landed if it characterises anyone; its hash and every number it states are recorded in a `check_report.py` that recomputes them. |

## Conventions that hold everywhere

- Python 3 standard library only. No network anywhere in any script; model
  calls happen outside and arrive as files.
- Deterministic. Randomness takes an explicit seed argument; the seed is
  written into the output rows and the run record.
- One command, file paths as arguments, one-line summary to stdout, JSONL
  out, nothing written outside the declared output path (plus the
  `runs.jsonl` row).
- No `label`, `category`, `type`, or `interpretation` field in any output
  schema. Row kinds are told apart by structure, or by separate files.
- Nulls are second outputs, never gates. Both print or neither does.
- Absent is not zero: a rate over no pairs is `null`; a missing input hashes
  to `null`; a state that means "not measured" is its own value.
- A fix that turns a test red is a finding, not a test to adjust. A guard
  written as a bare `assert` is not a guard.
- No section characterising any author, operator or contributor, and no
  description of anyone's working style, anywhere. Results only.
- Files stay under about 300 lines; split rather than grow. Every module
  keeps a `main(argv)` that returns the exit code, so tests call it directly.

## Running

```bash
./scripts/test-all.sh          # every suite, then the coverage count
python3 arena/path_probe.py arena/claims.jsonl 7 probe.jsonl
python3 arena/report.py arena/specimens.jsonl probe.jsonl report.md
```

Suites `chdir` into a temporary directory before writing, so `runs.jsonl`
never lands in the tree from a test run. The count of tests and of coverage
pairs is printed by the runner and is not written here, because a stored
count is the kind of number that stops matching its artifact.

## Neighbours

The `Simulators` repository holds the methodology spine these instruments
descend from (`SHAPE_SPEC.md`, `METHOD_SPEC.md`, `AUDIT_CONTRACT.md`) and,
on its branch `claude/frame-instruments-setup-lfcntd`, a second independent
build of the same ordered queue. Neither build is merged into the other.
