---
case: directive-team-doc-update
date: 2026-11-23
area: qa-agent / team documentation
type: directive
---

Nangyari:  After the <team doc>-v3.docx update, the owner: "i really like how you update the file ... pwede add mo sa skill mo tong gantong klaseng documentation dang linis e maybe sa qa-agent mo lagay hehe as reference".
Dahilan:   Directive, no mistake behind it.
Ayos:      qa-agent references/team-doc-update.md plus docs-kit/ (docx_edit.py engine + edit_config.example.json, dump, check, render, diagram template); row added to qa-agent SKILL.md Step 1 table. Smoke-tested end to end from the repo root.
Rule:      Team-facing doc updates follow team-doc-update.md: new -vN copy, clone the doc's own styles, same-style diagrams, every claim checked against the system, reviewer-agent before hand-over.
Promoted:  qa-agent references/team-doc-update.md (the owner's ask; reviewer-agent review pending)
