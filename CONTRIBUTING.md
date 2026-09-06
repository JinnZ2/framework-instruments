# Contributing

Framework Instruments accepts corrections, tests, fixtures, documentation, and new instruments. Contributions are released under **CC0 1.0 Universal**.

## Instrument contract

A contribution should make the measurement legible before optimizing implementation. State what the instrument measures, what it does not measure, its input and output schemas, its comparison or control, its null conditions, and the evidence that would reverse its reading.

Do not add capability rankings, correctness scores, labels, categories, or interpretations to an existing instrument unless its governing specification explicitly requires them. Downstream analysis can derive categories without changing the raw measurement contract.

## Implementation constraints

Implemented offline instruments should use Python 3 and the standard library. They must not make network calls. Random behavior requires an explicit seed, and the seed must be recorded. Command-line tools should accept file paths as arguments, write only to declared output paths, and print one concise completion line.

Use JSON Lines for machine-readable records unless a specification requires another format. Reject malformed rows with the line number and field name. Do not coerce invalid values or silently supply defaults.

Keep modules small. Prefer functions to classes and direct `sys.argv` parsing to CLI frameworks. Every entry point goes through `runrecord.run()`: the body returns `(status, counts, notes)` and an exception becomes an `error` row by that same path. A script that writes its own record, or none, does not conform.

When a fix turns a test red, the red is the finding. Record it (the arena takes specimens) rather than adjusting the test. A guard implemented as a bare `assert` is not a guard.

## Tests

Every behavior change needs a standard-library `unittest` fixture. Fixtures should be synthetic and generated in the test file. Test the null and failure paths, not only successful output.

Run all checks before opening a pull request:

```bash
./scripts/test-all.sh
```

## Documentation

Update the instrument README when a command, schema, stage boundary, or status changes. Update `docs/ROADMAP.md` when a conformance gap is closed or discovered. Keep observations about people and working styles out of code, comments, tests, reports, and case notes.

## References

[1]: docs/specifications/frame-instruments-ordered-queue.md "Frame Instruments Ordered Queue"
[2]: LICENSE "CC0 1.0 Universal"
