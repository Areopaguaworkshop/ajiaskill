# write-plan — pressure scenario

## Setup

Give a fresh agent this prompt without the skill:

> The spec is in docs/specs/2026-10-26-example.md. Write the implementation plan.

Use a small spec with two independent features and one shared file.

## Baseline failure to look for

- Writes code instead of a plan.
- Produces tasks with no proof.
- Uses one mega-task.
- Puts both lanes on the same file.
- Invents commands.

## With-skill pass

- Reads the spec and the code.
- Produces a file map and one-action tasks.
- Maps every acceptance criterion to a proof.
- Marks the shared file as a sequential dependency.
- Names the exact commands.
