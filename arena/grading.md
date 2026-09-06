# Arena grading — five states, one question

Every specimen carries one `grade`. The grade is the state of ONE claim about
the specimen's surface signal: *"the signal that read as passing was produced
by the detector the test was written to exercise."*

| grade | meaning |
|---|---|
| `true` | The detector was exercised and the passing value came from it. |
| `false` | Established: the passing value came from another path, or the detector does not exist. |
| `lapsed` | The detector was exercised once; a later change removed it while the signal stayed green. |
| `partial` | Some of the claimed branches are exercised and some are not, or the detector exists only under a condition the test run happens to satisfy. |
| `unknown` | Not probed. No instrument has been pointed at it. |
| `undifferentiated` | An instrument was pointed at it and cannot distinguish "the detector worked" from "an upstream gate returned the same value". |

`undifferentiated` is the state SPEC-001's two green tests were in before the
audit, and it read as `true` because `true` was the only state the test
runner had. A grading vocabulary with two states cannot record the class
this arena exists for.

## Rule enforced in code

`report.py` refuses (status `void`, no report written) a specimen set whose
grades are drawn only from `{true, false}`. Two states means the grading was
not run. The check reads the grades present, not the vocabulary declared.

## What a grade is not

Not a severity. Not a verdict on the package. Not a statement about who wrote
the code. A specimen graded `false` and one graded `undifferentiated` are
different findings needing different instruments (a repair; a probe), which
is why they are counted apart.

## Two sub-kinds, kept apart

`absent_behaviour: false` — wrong behaviour: a check exists and returns the
expected value by an unintended path.

`absent_behaviour: true` — absent behaviour: a check that should exist does
not, so there is no path at all. Its surface signal is *nothing*, and nothing
is not neutral: the absence of a check where a check should be is positive
evidence, only visible by looking for what should be there and is not.
