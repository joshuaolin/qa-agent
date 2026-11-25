---
case: directive-always-give-run-syntax
date: 2026-11-25
area: coding-partner / qa-agent hand-over
type: directive
---

Nangyari:  The owner: "tapos after mo gawin yung task laging ibibigay mo yung syntax paano i run para aware si QA ha".
Dahilan:   Directive, no mistake behind it. Rule 7 asked for "the exact command to run" but not for the QA run syntax of the suite and of one spec.
Ayos:      coding-partner rule 7 extended.
Rule:      After every task that adds or changes something runnable, end the hand-over with the QA run syntax from the repo root: the npm script (or `npx playwright test ...`) for the whole suite, for one spec, headed and headless, so any QA can run it without asking.
Promoted:  coding-partner SKILL.md rule 7
