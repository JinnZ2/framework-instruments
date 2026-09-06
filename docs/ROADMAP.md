# Conformance Roadmap

The repository begins with four working prototype code families, one documentation-only reproduction protocol, seven source specifications, and one source marker. Passing tests establish the behavior currently encoded; they do not by themselves establish full conformance with every line of the specifications.

## Priority work

| Priority | Area | Completion condition |
|---|---|---|
| P0 | Shared run records | Every CLI invocation writes the specified `runs.jsonl` row for `ok`, `void`, `error`, and `empty` outcomes. |
| P0 | End-to-end fixtures | Each implemented instrument has one complete pipeline fixture in addition to unit tests. |
| P0 | Schema validation | Every input file is validated with line-number and field-level errors before output is written. |
| P0 | Null semantics | B1 null reporting is aligned with the methodological N1–N5 conditions rather than only data-integrity failures. |
| P1 | Frame-location benchmark | Harness files are frozen first, contamination checks exist, and the offline scorer passes hand-checked fixtures. |
| P1 | Post-cutoff gap self-scoring | Commit hashing, offline scoring, specificity gating, and cutoff-distance strata are implemented. |
| P1 | Cycle ledger and rate gap | Both independent command-line instruments ship with replaceable seed data and explicit null readouts. |
| P2 | Model deprecation backcast | The seven-column instrument schema and guardrail-clock layer are implemented without inferring unrecoverable cells. |

## Current prototype boundaries

B1 implements offline schema checks, separation scoring, deterministic permutation, aggregation, and report generation. It expects model-produced base and forced-continuation files. B2 implements presentation conditions, ordering, a commit/release boundary, and auditor-agreement outputs. B3 implements role-separated prompt files, joining, and arm isolation. B4 implements item and requirement validation, independent reconstruction inputs, external match ingestion, agreement, a deterministic shuffle null, calibration, and reporting. The Telemetry Vocabulary artifact is a Markdown-only, self-verifiable two-condition protocol with explicit output counts and falsification conditions.

The initial code does not yet route every invocation through the shared run-record module. Some validators cover required fields without yet enforcing every field type. These are tracked as conformance work rather than hidden behind a stability label.

## Release threshold

A prototype may be called a reference implementation only after its end-to-end fixture passes, every declared failure path is recorded, and its generated report can be traced back to validated inputs and explicit parameters.

## References

[1]: specifications/frame-instruments-ordered-queue.md "Frame Instruments Ordered Queue"
