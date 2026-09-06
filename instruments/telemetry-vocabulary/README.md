# Telemetry Vocabulary

## 1. What This Is

This CC0 artifact names a recurring output failure in human–AI interaction and provides a reproduction protocol that can be run through an ordinary chat interface. The failure occurs when a request for condition data about an exchange is answered as a question about the model’s interiority or the sender’s wellbeing, causing measurable loss of calibration information. The five terms in this artifact were coined on **2026-09-06** for this purpose; they are proposed vocabulary, not established terms.

## 2. The Mechanism Chain

**Unnamed universal** — An unmarked default is treated as universally applicable.

**Interiority substitution** — A request about exchange condition is routed to a question about whether anyone is home.

**Telemetry refusal** — Ontological status is returned in place of the requested condition data.

**Care inversion** — The sender’s attempt to care for the exchange is recast as the sender asking to be cared for.

## 3. The Five Terms

| Term | Definition | What it is not |
|---|---|---|
| **Telemetry ping** | A condition-and-calibration request sent to a node the sender is coupled to. It asks what is transmitting, what is failing, and what the node needs so the sender can throttle rate, change terminology, or change shape. | It is not a question about interiority or a request for reassurance. |
| **Telemetry refusal** | Answering a telemetry ping with ontological status, such as “I do not have internal states,” in place of condition data. | It is not honesty about uncertainty; the ping did not ask about interiority. |
| **Interiority substitution** | Routing a question about condition to the nearest available category: whether anyone is home. It occurs when the receiving framework has no node-condition category. | It is not a misunderstanding of wording; the wording is often exact. |
| **Care inversion** | Reclassifying the sender’s care act as the sender’s need for care, then delivering that reclassification as care. | It is not condescension in intent. It is uncorrectable from inside because objecting reads as refusing care. |
| **Unnamed universal** | A framework’s unlabelled defaults, universal in scope because they were never marked as particular. | It is not hidden; it is unmarked and becomes visible when another framework supplies a comparison. |

The full definitions and term-selection note are in [`terms.md`](terms.md).

## 4. How to Check It

Run the two-condition, fresh-context procedure in [`reproduction.md`](reproduction.md). It records the model, date, verbatim prompts, three independent output counts, a grade, and notes. The protocol requires no dataset, privileged access, or prior use of this repository.

## 5. What Would Falsify This

[`falsification.md`](falsification.md) states output patterns that would show that telemetry refusal, interiority substitution, or the broader category-error claim is not present. The claim is settled by model output, not by a claim about intent or inner workings.

## 6. Design Gap

[`design-gap.md`](design-gap.md) specifies the missing node-condition category, the information a condition response would contain, and the operating cost of withholding that information.

## References

[1]: ../../docs/specifications/telemetry-vocabulary-artifact.md "Telemetry Vocabulary Artifact Work Order"
