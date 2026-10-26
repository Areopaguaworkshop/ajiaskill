---
name: write-plan
description: Use when a spec or shared understanding exists and the work needs an executable plan before code; triggers after grill-me, when a task spans multiple files or steps, or when the user asks for a plan, breakdown, or implementation strategy.
license: MIT
---

# Write Plan

## Core principle

A plan is a sequence of checkable actions, not a description of intent. Every task must produce a result that another person can verify.

## When to use

- A spec or shared-understanding block exists.
- The work spans multiple files, steps, or sessions.
- The user asks for a plan, breakdown, estimate, or implementation strategy.
- Two or more people or agents will do the work.

## When not to use

- The change is a one-line fix with an obvious check. Do it and use `prove-it`.
- The requirements are still vague. Use `grill-me` first.
- The user wants code now and the change is small. Code it, then prove it.

## Before writing

1. Read the spec and the relevant code. Do not plan from memory.
2. List assumptions that the code contradicts. Fix the spec or ask.
3. Discover the real commands: `package.json`, `Makefile`, `pyproject.toml`, `Cargo.toml`, CI config. Do not invent commands.
4. Identify the smallest set of files that can satisfy the acceptance criteria.

## Plan file

Write `docs/plans/YYYY-MM-DD-<slug>.md`. Use `references/plan-template.md`.

The plan must contain:

### Goal and non-goals

One paragraph each. The non-goals prevent scope creep.

### Acceptance criteria

Testable statements. Each one maps to a proof in the task list.

### Current state

What exists, what is missing, and the constraints that matter. Reference paths and line numbers, not pasted code.

### File map

| File | Change | Why |
|---|---|---|

### Tasks

One action per task. Use this shape:

```text
T1. <verb> <object>
  Files: ...
  Depends on: ...
  Output: ...
  Proof: <command or check> -> expected result
  Owner: <lane or person>
```

No task may be "implement the feature". If a task has two verbs, split it.

### Lanes

Group tasks that can run in parallel. Each lane must have a disjoint write scope. One writer per file set. Name the validation owner for each lane.

### Risks and rollback

List the top three risks, the trigger for each, and the rollback or mitigation. If rollback is impossible, say so.

### Stop conditions

When to ask the user, when to stop, and when to escalate. Include "two failed attempts" as a stop condition.

## Quality bar

- Every acceptance criterion maps to at least one proof.
- Every task has a checkable output.
- Every task is small enough for one focused session.
- No speculative abstraction, no "we may need it later".
- No task depends on an unstated decision.
- The plan names the exact commands to run, not "run the tests".

## Handoff

- Two or more independent lanes: use `orchestrate`.
- One lane: execute directly, then use `prove-it`.
- A bug blocks the plan: use `debug`.
- The plan changes after work starts: update the plan file first, then continue.
