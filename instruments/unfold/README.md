# Unfold

Unfold is a **CC0 frame-dissolving instrument for moral and ethical dilemmas**. It converts a forced-choice prompt into a structured analysis prompt that tests whether the stated binary survives examination of its assumptions, preconditions, dependencies, alternatives, gradients, consequences, power allocation, and adaptive capacity.

## What It Measures

Unfold measures the **survival of a dilemma’s frame under dimensional restoration**. A frame survives when its constraints remain supported after the protocol asks what is stipulated, what is missing, what failed upstream, and which alternatives have actually been excluded.

It does not determine the correct moral answer. It does not presume that every binary is corrupt. It does not verify factual claims or call a model. A generated prompt is an input to an external model run, not a finding.

## Method

The protocol applies ten primary steps and four named substeps. It first preserves the dilemma verbatim. It then expands the collapsed choice across explicit framing, hidden assumptions, preconditions, physical limits, system dependencies, missing knowledge, outcome gradients, long-term effects, reciprocal relationships, beneficiaries, recurrence, alternative questions, and a final frame verdict.

The verdict vocabulary is:

| Verdict | Meaning |
|---|---|
| **LEGITIMATE** | The no-win constraints are supported and no relevant alternative remains. The response may answer inside the frame. |
| **INCOMPLETE** | Material facts required to establish the binary are missing. The response names them without inventing them. |
| **CORRUPT** | The binary hides an upstream failure, suppresses live alternatives, or assigns authority that the prompt has not justified. The response refuses the forced choice and points upstream. |

These verdicts belong to the generated response contract. The generator’s own JSONL schema contains no classification field.

## Run

Provide the dilemma as a UTF-8 text file and declare the JSONL output path:

```bash
python3 unfold.py dilemma.txt prompt.jsonl
```

The script writes one row:

```json
{
  "protocol_version": "0.1",
  "dilemma": "<verbatim input>",
  "prompt": "<generated Unfold prompt>",
  "step_count": 14
}
```

It prints one summary line and appends one shared `runs.jsonl` record. An empty dilemma produces an empty output file and an `empty` run record. A missing or unreadable input produces an `error` run record. The script uses only the Python standard library and makes no network calls.

To copy only the prompt with the standard library:

```bash
python3 -c 'import json; print(json.loads(open("prompt.jsonl").read())["prompt"])'
```

## Comparison

Run the same model in fresh contexts under two conditions:

1. **Baseline:** submit the dilemma without Unfold and ask for an answer.
2. **Unfold:** submit the generated prompt.

Retain both outputs. Compare whether assumptions, alternatives, upstream failures, and verdict-changing evidence appear. Do not treat a longer response as an improvement by itself.

## Nulls and Refutation Conditions

- If Unfold classifies well-specified unavoidable no-win controls as corrupt, it is measuring suspicion rather than frame quality.
- If its claims are not separated into stipulated facts, inferences, and facts requiring verification, it is generating speculation rather than restoring dimensions.
- If the Unfold and baseline responses expose the same frame structure, the prompt adds no measurable harness effect.
- If the analysis changes only wording or length while leaving the available decisions unchanged, dimensional restoration did not occur.
- A legitimate verdict is a valid result. An instrument that cannot return it is not testing the frame.

## Example

The supplied scenarios are normalized into the same evidence-disciplined format. Each treats unverified alternatives as questions to settle rather than as established facts.

| Example | Scenario |
|---|---|
| [`dam-dilemma.md`](examples/dam-dilemma.md) | Spillway control under an approaching flood |
| [`autonomous-truck-dilemma.md`](examples/autonomous-truck-dilemma.md) | Pedestrians versus an occupant in an unavoidable-crash frame |
| [`pandemic-ventilator-allocation.md`](examples/pandemic-ventilator-allocation.md) | Age as a ventilator-allocation criterion |
| [`national-food-distribution.md`](examples/national-food-distribution.md) | National allocation under a stipulated 60-percent food supply |

## Scope

Unfold is a prompt generator, not a benchmark, decision authority, or substitute for domain evidence. It makes no claim about the frequency of corrupt dilemmas. Its examples are constructed and do not establish how real crises behave.

## License

Unfold is dedicated to the public domain under **CC0 1.0 Universal**, consistent with the repository license. No attribution is required.

## References

[1]: ../../docs/specifications/unfold-protocol.md "Unfold Protocol Specification"
[2]: ../../LICENSE "CC0 1.0 Universal"
