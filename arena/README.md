# arena — defect investigation arena

Defects that pass every normal signal are the specimens here. The audited
class: a test passes, output is well formed, no exception is raised, and the
passing value was produced by an upstream gate short-circuiting rather than
by the detector the test was written to exercise. Green suite, unexercised
detector. It is only visible by asking WHICH PATH produced the result.

Files:

- `specimens.jsonl` — one record per defect (schema below). Seeds SPEC-001..004
  are transcribed from the work order that opened this arena and describe a
  suite (`full_instrument_suite`) that is NOT in this repository; their
  `defect_text` is verbatim and nothing about them is verified here.
  SPEC-005 onward are defects found in this repository's own audit.
- `grading.md` — the five-state grade and the one claim it grades.
- `claims.jsonl` — for `path_probe.py`: which test claims which branch.
- `path_probe.py` — the instrument. Disables one claimed branch at a time
  and re-runs the claiming test.
- `report.py` — the six required sections, in order.

Specimen fields: `specimen_id, package, defect_text, surface_signal,
actual_path, intended_path, detector_exercised, masked_by, found_by, grade,
absent_behaviour, settled_by` (`settled_by` names the instrument that would move an
`undifferentiated` grade; null otherwise). No label, category or interpretation field.

## path_probe

```
python3 arena/path_probe.py arena/claims.jsonl SEED probe_results.jsonl
```

A claim names a test, a module, the source text of an `if` guard in that
module, and which branch (`if` body or `else` body) the test claims to
exercise. The probe rewrites that one guard (`False` disables the if-body,
`True` disables the else-body), loads the rewritten module in a fresh
subprocess in place of the real one, and runs the claiming test. It first
runs the test unmutated; a test that fails at baseline voids the claim. A
test that still passes with its claimed branch disabled is not exercising
that branch, and the probe emits a specimen record for it.

Seeded: the seed orders the claims and is written into every output row.
Nothing else is random. One question only; this is not a mutation-testing
framework.

## Refutation conditions for the arena itself

- If `path_probe` returns `still_passes: false` for every test in the suite,
  the class is not present here and the four seed specimens were the whole
  population.
- If specimens accumulate only in `gap_cases` (or, for this repository, only
  in one package), the class is a property of that package's construction,
  not a general defect class.
- If every specimen turns out to be masked by exactly one upstream defect,
  the arena is recording one bug in four rows.

`report.py` section 3 (masking chains) and section 4 (packages per sub-kind)
carry the numbers those conditions turn on; the report does not adjudicate
them.
