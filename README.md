# Framework Instruments

Framework Instruments is a **CC0 collection of small, falsifiable measurement tools** for questions that are usually left implicit: whether a problem is well posed, whether an alternative branch remains separated, whether an answer key is coherent, where work relocates, and what evidence would reverse a reading.

The repository treats an instrument as more than a prompt or argument. An instrument declares its inputs, outputs, comparison arm, null conditions, and failure records so that another party can reproduce or refute the result with their own data.

## Design principles

1. **Nulls are outputs.** A failed, empty, void, or contradictory run remains part of the record.
2. **Parameters are exposed.** Arbitrary choices are swept, logged, or identified as unresolved.
3. **Process boundaries enforce independence.** Commit/release and split-authorship protocols use files and separate invocations rather than instructions alone.
4. **Results are not rankings.** These tools measure separation, agreement, framing, reconstruction, rates, or ledgers. They do not produce capability leaderboards.
5. **Local execution is the default.** Implemented tools use the Python 3 standard library and make no network calls.
6. **Unmeasured cells remain visible.** Missing records are not silently estimated.

## Repository map

| Area | Status | Purpose |
|---|---|---|
| [`B1 — Runner-Up Trace`](instruments/b1-runner-up-trace/) | Prototype, tested | Scores whether forced alternative continuations resynchronize with a base continuation. |
| [`B2 — Audit Isolation`](instruments/b2-audit-isolation/) | Prototype, tested | Separates statement and key exposure across A/B/C/D audit conditions. |
| [`B3 — Split Authorship`](instruments/b3-split-authorship/) | Prototype, tested | Separates case writing from key writing and preserves arm isolation. |
| [`B4 — Dilemma Reconstruction`](instruments/b4-dilemma-reconstruction/) | Prototype, tested | Reconstructs requirement sets independently, computes agreement, runs a shuffle null, and calibrates documented items. |
| [`Arena`](arena/) | Instrument, tested | Defects that pass every normal signal as specimens: five-state grading, `path_probe.py` (which branch produced a green), a six-section report. |
| [`Reviews`](docs/reviews/) | Audit | External reviews of this repository, checked by recomputation rather than read. |
| [`Run record`](instruments/runrecord.py) | Shared | Every script's every run, failures included, as one row in `runs.jsonl`; `coverage_pairs.py` counts the `(script, status)` pairs the tests reach. |
| [`Telemetry Vocabulary`](instruments/telemetry-vocabulary/) | Reproduction protocol | Names and tests a category error in which an exchange-condition request is replaced by ontological status or unsolicited reassurance. |
| [`Unfold`](instruments/unfold/) | Generator, tested | Expands a forced-choice moral dilemma into a structured frame analysis with legitimate, incomplete, and corrupt verdict paths. |
| [`Frame-Location Benchmark`](docs/specifications/frame-location-benchmark.md) | Specification | Scores whether a mis-posed task and its faulty target are identified before answering. |
| [`Post-Cutoff Gap Self-Scoring`](docs/specifications/post-cutoff-gap-self-scoring.md) | Specification | Uses staged commits and dated external records instead of an authored answer key. |
| [`Cycle Ledger and Rate Gap`](docs/specifications/cycle-ledger-and-rate-gap.md) | Specification | Measures cycle rate-setters, unnotated work, relocation, and environment-to-record update rates. |
| [`Model Deprecation Backcast`](docs/specifications/model-deprecation-backcast.md) | Specification | Reads model retirements backward against measured deltas, discard sets, register shifts, and discourse cycles. |
| [`Routing Data-Layer Marker`](docs/specifications/routing-data-layer-marker.md) | Source marker | Defines the envelope and refutation conditions behind the cycle-ledger specification. |

The B1–B3 implementations were audited against the ordered-queue specification on 2026-09-06 and repaired to it; [`docs/AUDIT_2026-09-06.md`](docs/AUDIT_2026-09-06.md) lists each finding with its disposition, and the [conformance roadmap](docs/ROADMAP.md) carries what remains.

## Quick start

The whole repository can be validated without installing dependencies:

```bash
./scripts/test-all.sh
```

Run a single suite from its instrument directory:

```bash
cd instruments/b1-runner-up-trace
python3 -m unittest -v test_b1.py
```

Each implemented instrument has its own README with file contracts and command examples. Model execution, retrieval, and other network-dependent collection stages remain outside the offline tools unless a specification explicitly states otherwise.

## Structure

```text
framework-instruments/
├── instruments/
│   ├── b1-runner-up-trace/
│   ├── b2-audit-isolation/
│   ├── b3-split-authorship/
│   ├── b4-dilemma-reconstruction/
│   ├── telemetry-vocabulary/
│   ├── unfold/                  # frame-analysis generator, failure lexicon, and examples
│   ├── runrecord.py            # shared run record; imported by every script
│   ├── coverage_pairs.py       # (script, status) pairs exercised over reachable
│   └── test_*.py
├── arena/                      # defect specimens, grading, path_probe.py, report.py
├── docs/
│   ├── specifications/
│   ├── AUDIT_2026-09-06.md
│   └── ROADMAP.md
├── scripts/test-all.sh
├── CLAUDE.md
├── CONTRIBUTING.md
└── LICENSE
```

## Contributing

Contributions should preserve the declared measurement rather than broaden it implicitly. New outputs need an explicit schema. New claims need a refutation condition. Missing data should produce a visible disposition. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Scope

This repository does not characterize authors, operators, contributors, or their working styles. Cases and observations belong in an instrument only as testable records. Sampling frames must be stated, and authored case sets must not be presented as population estimates.

## License

The repository is dedicated to the public domain under **CC0 1.0 Universal**. No attribution is required. See [`LICENSE`](LICENSE).

## References

[1]: docs/specifications/frame-instruments-ordered-queue.md "Frame Instruments Ordered Queue"
[2]: docs/specifications/runner-up-trace.md "Runner-Up Trace / Divergence Map"
[3]: docs/specifications/frame-location-benchmark.md "Frame-Location Benchmark"
[4]: docs/specifications/post-cutoff-gap-self-scoring.md "Post-Cutoff Gap Self-Scoring"
[5]: docs/specifications/cycle-ledger-and-rate-gap.md "Cycle Ledger and Data-Layer Envelope Instrument"
[6]: docs/specifications/model-deprecation-backcast.md "Model Deprecation Backcast Instrument"
[7]: docs/specifications/telemetry-vocabulary-artifact.md "Telemetry Vocabulary Artifact"
[8]: docs/specifications/unfold-protocol.md "Unfold Protocol Specification"
[9]: docs/specifications/unfold-human-skill-addendum.md "Unfold Human Skill and Experiential Knowledge Addendum"
[10]: docs/specifications/unfold-lived-resilience-addendum.md "Unfold Lived Experience and Resilience Practices Addendum"
[11]: docs/specifications/unfold-comfort-stability-addendum.md "Unfold Comfort, Agency, and Future Stability Addendum"
[12]: docs/specifications/unfold-failure-lexicon-addendum.md "Unfold Failure Lexicon Addendum"
[13]: docs/specifications/unfold-pre-adoption-addendum.md "Unfold Pre-Adoption and Normalization Audit Addendum"
[14]: docs/specifications/unfold-normative-provenance-addendum.md "Unfold Normative Provenance and Authority Addendum"
