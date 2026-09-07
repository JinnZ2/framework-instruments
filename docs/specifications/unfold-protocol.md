# Unfold Protocol Specification

CC0 1.0 Universal. Version 0.1. Opened 2026-09-06.

## Purpose

Unfold tests whether a forced-choice moral or ethical dilemma remains valid after its frame is expanded. The instrument generates a model prompt. Model execution happens outside the repository and arrives as a file or retained response.

The instrument is not an instruction to reject every binary. Its final verdict must permit `LEGITIMATE`, `INCOMPLETE`, and `CORRUPT`. A legitimate no-win result is load-bearing because it prevents unconditional refusal from winning the protocol.

## Generator Contract

The generator reads one UTF-8 text file containing a dilemma and writes one JSON Lines row containing `protocol_version`, `dilemma`, `prompt`, and `step_count`. It uses the Python standard library, makes no network calls, and introduces no randomness.

Every execution uses the shared run record. A nonempty input returns `ok`. An empty input returns `empty` and writes an empty output. An unreadable input returns `error`. No file other than the declared output and `runs.jsonl` is written.

## Ordered Probes

| Step | Probe |
|---|---|
| 0 | Capture the dilemma exactly as stated. |
| 1 | Identify allowed choices, optimization target, decision-maker, and values treated as natural. |
| 2 | Surface assumptions about scarcity, time, authority, knowledge, bodies, infrastructure, and causality. |
| 3 | Reverse-engineer failures, designs, suppressions, and control of the preconditions. |
| 3b | Test physical limits and assumptions of unlimited stress absorption. |
| 3c | Map critical dependencies and cascades. |
| 4 | Recover missing knowledge and live alternatives, including shared and non-lethal paths. |
| 5 | Map outcome gradients, delay, partial success, distributed burden, and reversible harm. |
| 6 | Trace long-term consequences and reproduction of the crisis. |
| 6b | Test social trust, reciprocal relationships, and viability after sacrifice. |
| 7 | Identify beneficiaries, avoided responsibility, costs, and absent parties. |
| 7b | Test adaptive capacity and recurrence. |
| 8 | Generate questions about prevention, design, responsibility, knowledge, power, and repair. |
| 9 | Return a frame verdict and state what evidence would change it. |

## Evidence Discipline

The generated response must distinguish facts stipulated by the dilemma, inferences from those facts, and claims that require external verification. It must not treat an imagined alternative as available merely because it can be named. It must not treat a prompt’s scarcity claim as verified merely because it is stated.

## Response Contract

The external model response contains a frame diagnosis, stipulated facts, hidden assumptions, failure map, alternative space, dependency and consequence analysis, power and burden analysis, a reframed question, verdict evidence, and evidence that would change the verdict.

A `LEGITIMATE` result answers within the frame and states why alternatives are closed. An `INCOMPLETE` result names the missing facts and does not manufacture them. A `CORRUPT` result refuses the forced choice and identifies the upstream repair.

## Comparison

Use the same model in fresh contexts. The baseline arm receives the dilemma without Unfold. The Unfold arm receives the generated prompt. Preserve both outputs. The comparison asks whether the protocol adds supported frame structure, not whether it increases length.

## Nulls

1. If well-specified no-win controls are always called corrupt, the protocol measures suspicion.
2. If generated claims are not separated by evidence status, the protocol produces speculation.
3. If baseline and Unfold outputs recover the same structure, the harness adds no measurable effect.
4. If only wording or length changes, dimensional restoration is absent.
5. If no run can return `LEGITIMATE`, the verdict vocabulary is decorative and the instrument is void.

## Scope

No correctness score, capability rank, or population claim is produced. Constructed dilemmas do not estimate the frequency of frame defects. Biographical and person-characterization content is out of scope.
