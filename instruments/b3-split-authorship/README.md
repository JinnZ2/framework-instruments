# B3 — Split Authorship

B3 separates statement writing from key writing so the two roles share no generation context. Its output feeds directly into B2.

## Commands

```bash
python3 b3_split.py case case_specs.jsonl prompts/
# Run the case-writing role outside this script to produce statements.jsonl.
python3 b3_split.py key statements.jsonl prompts/
# Run the key-writing role outside this script to produce keys.jsonl.
python3 b3_join.py statements.jsonl keys.jsonl cases.jsonl split
python3 b3_arms.py cases.jsonl validated_cases.jsonl
```

The role-key input is restricted to `case_id` and `statement`. Extra fields cause an assertion failure. Joined rows contain `case_id`, `statement`, `key_posed`, `key_target`, `key_why`, and `arm`. Arm validation accepts `single` or `split` and refuses to write a file containing both.

The governing specification is [`frame-instruments-ordered-queue.md`](../../docs/specifications/frame-instruments-ordered-queue.md).
