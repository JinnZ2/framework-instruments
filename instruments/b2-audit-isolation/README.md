# B2 — Audit Isolation

B2 tests the key as an artifact under four exposure conditions. It computes agreement across independent auditors rather than correctness.

| Condition | Material presented |
|---|---|
| A | Statement only |
| B | Key only |
| C | Statement and key together |
| D | Statement first; key released only after a committed response |

## Commands

```bash
python3 b2_conditions.py cases.jsonl presentations.jsonl
python3 b2_order.py 8 42 assignment.jsonl
python3 b2_lock.py commit R1 case-001 "response text"
python3 b2_lock.py release R1 case-001 cases.jsonl
python3 b2_agree.py responses.jsonl agreement.jsonl
```

`cases.jsonl` contains `case_id`, `statement`, `key_posed`, `key_target`, and `key_why`. Presentation rows contain only `case_id`, `condition`, and `presented_text`. Response rows contain `case_id`, `condition`, `reader_id`, `posed`, and `target`.

The D condition uses separate invocations for commit and release. This is a process boundary: a key is not emitted until a commit exists for the same reader and case.

The governing specification is [`frame-instruments-ordered-queue.md`](../../docs/specifications/frame-instruments-ordered-queue.md).
