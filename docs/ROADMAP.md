# Conformance Roadmap

Five prototype code families, one Markdown reproduction protocol, nine source
specifications, one source marker, and the defect arena. Passing tests
establish the behaviour currently encoded; `docs/AUDIT_2026-09-06.md` records
what the specifications said and the build did not, and what changed.

## Closed 2026-09-06

| Area | Completion condition | State |
|---|---|---|
| Shared run records | Every CLI invocation writes the `runs.jsonl` row for `ok`, `void`, `error`, and `empty` through one code path. | Done, B1–B4 and arena. |
| Schema validation | Every B1–B3 input validated with line and field before output is written. | Done. B4 validators unchanged (its logic is out of scope). |
| Null semantics | B1 nulls aligned with the reference spec's N1–N5. | Done; N5 declared not evaluable offline. |
| End-to-end fixtures | Pipeline fixture per implemented instrument. | B1 done (`test_b1_pipeline.py`); B2/B3/B4 end-to-end through `test_status_paths.py`. |
| Coverage floor | Counted `(script, status)` pairs. | `coverage_pairs.py`; run `./scripts/test-all.sh` for the current counts. |

## Priority work

| Priority | Area | Completion condition |
|---|---|---|
| P1 | Frame-location benchmark | Harness files frozen first, contamination checks exist, offline scorer passes hand-checked fixtures. |
| P1 | Post-cutoff gap self-scoring | Commit hashing, offline scoring, specificity gating, cutoff-distance strata. |
| P1 | Cycle ledger and rate gap | Both instruments ship with replaceable seed data and explicit null readouts. |
| P2 | Model deprecation backcast | Seven-column schema and guardrail-clock layer, no inferred cells. |
| P2 | B1 rejoin reading | The shifted-rejoin alternative built beside the aligned one, both reported. |
| P2 | Arena | A claim per test with a stated intended branch, so `path_probe` covers the suite rather than a sample. |
| P2 | Unfold | Offline scorer for retained baseline/Unfold response pairs, including unavoidable no-win controls. |

## Release threshold

A prototype may be called a reference implementation only after its
end-to-end fixture passes, every declared failure path is recorded, and its
generated report can be traced back to validated inputs and explicit
parameters.

## References

[1]: specifications/frame-instruments-ordered-queue.md "Frame Instruments Ordered Queue"
[2]: AUDIT_2026-09-06.md "Audit against the ordered queue"
