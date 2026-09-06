# B3 — Split Authorship

Is case-and-key failure corpus pull or a two-frame hold problem? Prediction,
written before running: if corpus pull, splitting the roles does not help; if
the two-frame hold, splitting reduces the failure. Case and key are written
by separate instances with no shared context, enforced by file boundary.

```bash
python3 b3_split.py case case_ids.jsonl brief.txt prompts/   # ROLE CASE prompt; a brief that mentions a key is refused
# run ROLE CASE outside; its reply is statements.jsonl (case_id, statement)
python3 b3_split.py key statements.jsonl prompts/            # ROLE KEY prompt from statements.jsonl ALONE
# run ROLE KEY outside; its reply is keys.jsonl (case_id, key_posed, key_target, key_why)
python3 b3_join.py statements.jsonl keys.jsonl split cases.jsonl
python3 b3_arms.py cases.jsonl split cases_armed.jsonl
```

A statements row with any field beyond `case_id` and `statement` is refused
with its line number, so the key role can receive no generation context. The
join drops a `case_id` present on one side only and counts every drop in the
run record. Arms are `single` (one instance writes statement and key) and
`split`; `b3_arms.py` stamps a declared arm and refuses a file that carries
another. Joined files feed B2 as a new arm; the comparison of key coherence
under condition B between arms is B3's result, and it lives in B2.

Governing specification: [`frame-instruments-ordered-queue.md`](../../docs/specifications/frame-instruments-ordered-queue.md).
