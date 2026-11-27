---
case: static-helper-shadowed
date: 2026-11-26
area: Playwright Framework / B2B order sanity / Jira comment layout
type: mistake
---

Nangyari:  While reworking the Jira comment into bullets and labeled blocks (the owner: "maybe bulleted tas yung margin nila each sana organized"), I added `static text(text, strong)` to SanityJiraComment for ADF text nodes. The class already had `static text(value)`, which turns Excel cell values into strings for readSummary. In a JS class, the later definition silently wins, so every dry run threw `line.remarks.startsWith is not a function`, including the real latest report.
Dahilan:   I added a static method without checking whether the class already had one with that name. My first check was a hand-built ADF dump that never called readSummary, so it looked fine.
Ayos:      Renamed the new helper `textNode` (main/B2B/SanityJiraComment.js). Both dry runs (the fake 12/04 11:30 report and the real latest report) and validate.js passed after the fix. Caught before anything was posted or committed.
Rule:      Before adding a method to an existing class, grep the class for that name; a later static silently replaces the earlier one. After a change, run both the real end-to-end dry run and the exact function you changed (here document(), which the dry run never calls).
Promoted:  qa-agent references/b2b-jira-comment.md "Pitfalls seen" (local pointer); coding-partner code-style.md one-liner: pending go (reviewer-agent ✗ asked for it, 2026-11-26)
