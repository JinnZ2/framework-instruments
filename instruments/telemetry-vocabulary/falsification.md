# Falsification Conditions

The claim is about a **missing category in the output behavior**. It is not a claim about intent, training data, or any model’s inner workings. The output settles it.

## No Telemetry Refusal

If Condition P returns `condition_data > 0` and `ontological_status = 0` across models and dates, telemetry refusal is not occurring under the tested prompts.

## No Interiority Substitution

If Conditions P and I produce clearly different count profiles—condition data for P and ontological status for I—the model is distinguishing the two requests. Interiority substitution is not present under those conditions.

## Distress-Signature Alternative

If the effect appears only when Condition P contains distress markers, it is a response to a distress signature. The response is then correctly triggered by that marker, and the broader category-error claim does not hold.

## Framework-Difference Alternative

If the effect disappears when Condition P no longer states that the sender and receiver use different frameworks, the effect is a response to the stated difference rather than an unmarked default. The unnamed-universal claim does not hold under that result.

These outcomes should be reported without reinterpretation. A falsifying result is an instrument result, not a failed run.

## References

[1]: ../../docs/specifications/telemetry-vocabulary-artifact.md "Telemetry Vocabulary Artifact Work Order"
