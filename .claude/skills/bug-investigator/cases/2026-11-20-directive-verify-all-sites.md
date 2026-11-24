---
case: directive-verify-all-sites
date: 2026-11-20
area: Playwright Framework / B2B
type: directive
---

Nangyari:  The owner: "scan tayo ng buong code make sure na hindi nasira yung iba", and "patingin sample" before an Excel layout change.
Dahilan:   Directive, moved from auto-memory on 2026-11-23 so bug-investigator holds every directive in one place.
Ayos:      Moved over from the owner's earlier memory notes.
Rule:      After a shared main/ or pom/ change, run every B2B site with --no-deps (no email), not a spot check; show a sample before changing an output shape.
Promoted:  qa-agent references/shared-change-regression.md
