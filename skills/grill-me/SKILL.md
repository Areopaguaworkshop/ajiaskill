---
name: grill-me
description: Use when the user has a vague idea, plan, or design and needs to sharpen it before building; triggers on "grill me", "stress-test this", "what am I missing", "help me decide", or before writing a spec or plan.
license: MIT
---

# Grill Me

## Core principle

Interview the user until you share one understanding. **Facts are your job. Decisions are the user's.**

Do not implement, scaffold, or write a plan until the user confirms the shared understanding.

## When to use

- The user says "grill me", "stress-test this", "what am I missing", or "help me decide".
- The request is vague: the goal, user, scope, or success test is missing.
- The user is about to build something expensive, irreversible, or cross-cutting.
- A plan exists but its assumptions have not been challenged.

## When not to use

- The user gave a complete spec with acceptance criteria. Go to `write-plan`.
- The answer is in the repository, docs, or a tool. Inspect it; do not ask.
- The change is small and reversible. Do the change, then use `prove-it`.
- The user explicitly says "just build it". Record the assumptions in one paragraph, confirm them, and continue.

## Map the design tree

Treat the subject as a tree. Each decision has prerequisites:

```text
Goal -> User -> Scope -> Constraints -> Success test
                  -> Non-goals
                  -> Data / integrations
                  -> Failure modes
                  -> Rollout / rollback
```

A question is **ready** when every decision it depends on is settled. The set of ready questions is the **frontier**.

## Work in rounds

1. Build the frontier from the current tree.
2. Ask every frontier question in one message. Do not ask a question whose answer depends on another open question.
3. Put the recommended answer under each question. Word it so "yes" accepts the recommendation.
4. Wait for the user. Do not answer for them.
5. Recompute the tree with their answers. Repeat.
6. Stop when the frontier is empty.

## Question format

```text
❓ **Q1 — Title**: One decision, in plain language.
➡️ Recommended: The answer you would choose, and why in one sentence.

---

❓ **Q2 — Title**: ...
➡️ Recommended: ...
```

Keep each question to one decision. If a question needs a fact, get the fact first.

## Rules

- **Facts:** inspect the repository, run a command, read the docs, or delegate research. Never ask the user for a fact you can find.
- **Decisions:** put each one to the user. Do not silently choose scope, trade-offs, or risk.
- **One recommendation:** every question has a recommended answer. "It depends" is not an answer.
- **No dependency inversion:** do not ask "which database?" before "what workload?".
- **No question spam:** ask the frontier, not the whole tree.
- **No early implementation:** a sketch is allowed only to make a decision concrete. Label it and delete it if the decision changes.
- **No infinite interview:** if two rounds produce no new decisions, ask what is blocking and propose a default.

## Done

When the frontier is empty, write a short shared-understanding block:

```text
Goal:
User:
Scope:
Non-goals:
Constraints:
Success test:
Key decisions:
Open assumptions:
```

Ask the user to confirm or correct it. Only then hand off to `write-plan`.

If the user wants a durable record, save the block to `docs/specs/YYYY-MM-DD-<slug>.md`. Otherwise keep it in the conversation.
