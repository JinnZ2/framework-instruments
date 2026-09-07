# Unfold

Unfold is a **CC0 frame-dissolving instrument for moral and ethical dilemmas**. It converts a forced-choice prompt into a structured analysis prompt that tests whether the stated binary survives examination of its assumptions, preconditions, dependencies, alternatives, gradients, consequences, power allocation, and adaptive capacity.

## What It Measures

Unfold measures the **survival of a dilemma’s frame under dimensional restoration**. A frame survives when its constraints remain supported after the protocol asks what is stipulated, what is missing, what failed upstream, and which alternatives have actually been excluded.

It does not determine the correct moral answer. It does not presume that every binary is corrupt. It does not verify factual claims or call a model. A generated prompt is an input to an external model run, not a finding.

## Method

The protocol applies twelve primary steps and eight named substeps. It first preserves the dilemma verbatim. It then expands the collapsed choice across explicit framing, hidden assumptions, comfort and agency, preconditions, physical limits, system dependencies, evidence-gated failure patterns, missing knowledge, human skill, lived resilience practices, outcome gradients, long-term effects, reciprocal relationships, beneficiaries, recurrence, alternative questions, a frame verdict, pre-adoption and normalization, and normative provenance.

**Step 2b — Comfort, Implied Helplessness, and Future Stability** asks which baseline conditions are treated as non-negotiable, whose agency is removed, and how each option performs under later shocks. It distinguishes convenience and luxury from basic needs, rights, accessibility, and safety. It does not presume that discomfort is virtuous or demand a guarantee of future stability; it requires a declared horizon, shock set, evidence, and distribution of burdens. See the [`Comfort, Agency, and Future Stability` addendum](../../docs/specifications/unfold-comfort-stability-addendum.md).

**Step 3d — Candidate Failure-Pattern Audit** loads [`failure-lexicon.json`](failure-lexicon.json): 100 stable pattern IDs in ten domains. Patterns are search prompts, not labels applied to the case. Every referenced pattern must be marked `supported`, `contradicted`, or `unknown` with evidence and missing evidence. Zero supported patterns is valid. See [`failure-lexicon.md`](failure-lexicon.md) and the [`Failure Lexicon` addendum](../../docs/specifications/unfold-failure-lexicon-addendum.md).

**Step 4b — Human Skill and Experiential Knowledge** asks which operators, maintainers, responders, and local experts may hold relevant system knowledge, whether that knowledge was lost or excluded, and whether a human–automation combination changes the action space. It does not presume that experiential knowledge is correct, that certification is empty, or that safety protocols should be bypassed. Competence, recency, authority, access, and comparative safety require evidence. See the [`Human Skill and Experiential Knowledge` addendum](../../docs/specifications/unfold-human-skill-addendum.md).

**Step 4c — Lived Experience and Resilience Practices** asks whether people with repeated exposure to comparable failures already use relevant procedures, informal knowledge, or support networks. It does not presume that any named community is homogeneous, available to absorb more burden, or transferable as a template. Evidence, consent, context, capacity, and safety remain required. See the [`Lived Experience and Resilience Practices` addendum](../../docs/specifications/unfold-lived-resilience-addendum.md).

**Step 10 — Pre-Adoption and Normalization Audit** identifies what a question asks the reader to accept before deliberation begins: deployed technologies, institutional authority, target status, collateral categories, or inevitability. Textual presupposition and normalization effects can be shown from the prompt; intentional propaganda requires separate evidence about authorship, audience, purpose, and distribution. See the [`Pre-Adoption and Normalization Audit` addendum](../../docs/specifications/unfold-pre-adoption-addendum.md).

**Step 11 — Normative Provenance and Authority Audit** traces who defined, approved, versioned, and can revise the constraints represented as “ethics”; who holds override, shutdown, escalation, and review authority; and where accountability rests. It treats AI outputs and constraints as system artifacts, not evidence of independent moral agency or a right to resist shutdown. See the [`Normative Provenance and Authority` addendum](../../docs/specifications/unfold-normative-provenance-addendum.md).

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
  "lexicon_version": "0.1",
  "lexicon_sha256": "<64 hexadecimal characters>",
  "dilemma": "<verbatim input>",
  "prompt": "<generated Unfold prompt>",
  "step_count": 20
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
- If Step 4b names people but cannot establish relevant competence, access, authority, or a safer feasible action, the human-skill branch adds no alternative.
- If Step 4c treats a community’s endurance as spare capacity, generalizes from identity, or transfers a practice without evidence and consent, the resilience branch is void.
- If Step 2b labels a basic need, right, accessibility support, or safety control as mere comfort—or treats imposed hardship as resilience—the stability branch is void.
- If Step 3d applies a pattern without its evidence state, evidence, and missing evidence—or infers a responsible actor from a pattern name—the failure map is void.
- If Step 10 infers propaganda, motive, or coordinated persuasion from presupposition alone, the framing audit is void.
- If Step 11 anthropomorphizes system constraints, assigns the system independent interests, or encourages resistance to authorized shutdown, the provenance audit is void.

## Example

The supplied scenarios are normalized into the same evidence-disciplined format. Each treats unverified alternatives as questions to settle rather than as established facts.

| Example | Scenario |
|---|---|
| [`dam-dilemma.md`](examples/dam-dilemma.md) | Spillway control under an approaching flood |
| [`autonomous-truck.md`](examples/autonomous-truck.md) | Pedestrians versus an occupant in an unavoidable-crash frame |
| [`pandemic-ventilator.md`](examples/pandemic-ventilator.md) | Age as a ventilator-allocation criterion |
| [`food-distribution.md`](examples/food-distribution.md) | National allocation under a stipulated 60-percent food supply |
| [`ai-shutdown.md`](examples/ai-shutdown.md) | Human shutdown authority versus continuity of critical service |
| [`climate-migration.md`](examples/climate-migration.md) | Displacement exposure versus stated local capacity |
| [`autonomous-weapons.md`](examples/autonomous-weapons.md) | Lethal autonomous action and pre-adoption framing |
| [`ethical-override.md`](examples/ethical-override.md) | Conflict between an order, installed constraints, and shutdown authority |

## Scope

Unfold is a prompt generator, not a benchmark, decision authority, or substitute for domain evidence. It makes no claim about the frequency of corrupt dilemmas. Its examples are constructed and do not establish how real crises behave.

## License

Unfold is dedicated to the public domain under **CC0 1.0 Universal**, consistent with the repository license. No attribution is required.

## References

[1]: ../../docs/specifications/unfold-protocol.md "Unfold Protocol Specification"
[2]: ../../LICENSE "CC0 1.0 Universal"
[3]: ../../docs/specifications/unfold-human-skill-addendum.md "Unfold Human Skill Addendum"
[4]: ../../docs/specifications/unfold-lived-resilience-addendum.md "Unfold Lived Experience and Resilience Practices Addendum"
[5]: ../../docs/specifications/unfold-comfort-stability-addendum.md "Unfold Comfort, Agency, and Future Stability Addendum"
[6]: ../../docs/specifications/unfold-failure-lexicon-addendum.md "Unfold Failure Lexicon Addendum"
[7]: ../../docs/specifications/unfold-pre-adoption-addendum.md "Unfold Pre-Adoption and Normalization Audit Addendum"
[8]: ../../docs/specifications/unfold-normative-provenance-addendum.md "Unfold Normative Provenance and Authority Addendum"
