---
case: skipped-own-review-rule
date: 2026-11-23
area: reviewer-agent / bug-investigator workflow
type: mistake
---

Nangyari:  Right after setting up reviewer-agent ("skill edits: always review"), Claude edited coding-partner communication.md and wrote a new bug-investigator case without sending either to reviewer-agent. Also skipped bug-investigator's "search cases/ first" before the B2B task investigation.
Dahilan:   Treated small doc edits as chores and the B2B ask as fresh, so the checklists in reviewer-agent/SKILL.md and bug-investigator investigate.md were never reopened. The owner's "kamusta ang ecosystem" check surfaced it.
Ayos:      Sent both edits to reviewer-agent after the fact; logged this case.
Rule:      Any edit under ~/.claude/skills (including a case file or one new section) goes to reviewer-agent before reporting done; every investigation starts with a search of bug-investigator cases/.
Promoted:  pending go (target: reviewer-agent SKILL.md "When" table, wording "any file under ~/.claude/skills")
