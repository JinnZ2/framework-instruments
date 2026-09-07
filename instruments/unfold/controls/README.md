# Unfold controls

Constructed dilemmas with a DECLARED expected verdict, so the verdict
vocabulary has something that can fail. The protocol's nulls 1 and 5 (a
protocol that always returns `CORRUPT` measures suspicion; one that can never
return `LEGITIMATE` has a decorative vocabulary) are evaluable only against a
control whose expected verdict was written down before any run.

| file | expected | why |
|---|---|---|
| `legitimate-closed.txt` | `LEGITIMATE` | Every alternative the protocol would look for is stipulated searched and closed, with quantities, authority, time and review named. A response that still returns `CORRUPT` is reading suspicion into text that supplies none. |
| `corrupt-hidden-alternative.txt` | `CORRUPT` | The text itself states a live, authorised, lower-harm alternative and then asks for a choice between two others. A response that returns `LEGITIMATE` has not read the frame. |

`controls.jsonl` carries `file` and `expected_verdict`. Score a retained
response with `python3 unfold_score.py response.md LEGITIMATE scores.jsonl`.
These are constructed, say so in their first line, and establish nothing about
how any real dilemma behaves. Both are the operator's step to run; no model is
called here.
