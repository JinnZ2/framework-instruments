# B2 — Audit Isolation (A / B / C / D)

The KEY is the artifact under test, not the cases. Four presentation
conditions, a process-boundary lock for the sequential one, and agreement
across independent auditors. No script here computes a correctness score.

| Condition | Presented |
|---|---|
| A | statement only |
| B | key only (`key_posed`, `key_target`, `key_why`), no statement |
| C | both, simultaneous |
| D | statement first; the key is released by `b2_lock.py` only after a commit |

## Commands

```bash
python3 b2_conditions.py cases.jsonl presentations/        # condition_A..D.jsonl, one file each
python3 b2_order.py 8 42 assignment.jsonl                  # Williams square blocks of 4; remainder seeded
python3 b2_lock.py commit  commits.jsonl R001 c1 response.txt
python3 b2_lock.py release commits.jsonl cases.jsonl R001 c1 key_R001_c1.jsonl
python3 b2_agree.py responses.jsonl commits.jsonl agreement.jsonl comparisons.jsonl
```

`cases.jsonl`: `case_id, statement, key_posed, key_target, key_why` (an `arm`
field from B3 is accepted and never presented). Presentation rows carry
`case_id, condition, presented_text` only; condition B is refused for a case
whose statement occurs inside its key text.

The lock is a process boundary: `commit` writes the response and its sha256
and exits; `release` refuses — recorded as `void` — unless a commit exists
for that reader and case and its stored text still hashes to its stored
sha256. A second commit for the same reader and case is refused. `commit`
never opens the cases file and `release` never writes the commits file.

`responses.jsonl`: `case_id, condition (A|B|C|D1|D2), reader_id, posed,
target`; a D1 row must carry `commit_sha256` matching a commit. Agreement is
exact string equality. The first thing printed and recorded is A vs D1 —
same information, so a mismatch means order effects are live and C is
uninterpretable. C vs D2 (identical material, only the lock differs) is the
anchoring readout. Rates over zero pairs are `null`, not 0.

Governing specification: [`frame-instruments-ordered-queue.md`](../../docs/specifications/frame-instruments-ordered-queue.md).
