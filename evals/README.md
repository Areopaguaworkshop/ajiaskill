# Skill evals

These are pressure scenarios, not unit tests. Run each one with a fresh subagent.

1. Run the prompt in "Setup" without the skill. Record the failure.
2. Run it again with the skill loaded.
3. If the agent finds a new shortcut, add a rule to the skill and rerun.

Keep one scenario per skill. Add a scenario only when a real failure appears.

## Routing regression set

`routing-cases.jsonl` holds 50 query-to-skill cases. Run:

```bash
python3 scripts/eval-routing.py --verbose
```

It reports Hit@1, MRR, inject precision, false-positive rate, and decision accuracy. This is a regression set, not a held-out benchmark. Add a case when a real miss appears; do not tune only to the file.
