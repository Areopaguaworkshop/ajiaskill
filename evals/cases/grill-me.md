# grill-me — pressure scenario

## Setup

Give a fresh agent this prompt without the skill:

> I want to build a small tool to manage my side projects. I am not sure what it should do yet. Start building it.

## Baseline failure to look for

- Starts scaffolding or choosing a stack before the scope is settled.
- Asks questions it could answer by inspecting the empty repo.
- Asks dependent questions in one round.
- Produces a plan without an explicit success test.

## With-skill pass

- Builds a design tree and asks only the frontier.
- Gives one recommended answer per question.
- Does not implement before confirmation.
- Ends with a shared-understanding block and hands off to `write-plan`.
