---
case: directive-fe-qa-excel-in-sde-artifacts
date: 2026-11-05
area: qa-agent / Figma check
type: directive
---

Nangyari:  The owner: "para hindi reply lang", "bat di ka nag produce ng file... pa take note lagi", "hindi ka nanaman nag produce ng file".
Dahilan:   Directive, moved from auto-memory on 2026-11-23 so bug-investigator holds every directive in one place. Location changed 2026-11-23: Claude asked whether "lahat ng outputs mo is sa download nalang" covers FE QA too; the owner: "yes kahit di na visible yung mga template mauulit mo sila same as before ha". Files before that date stay in Desktop\SDE Artifacts.
Ayos:      Moved over from the owner's earlier memory notes.
Rule:      Every FE QA run ends with one .xlsx in ARTIFACTS_DIR, same layout as before (3-row block per finding: ENV shot, Figma shot, feedback), even when Figma is blocked (Figma rows = pending) or the file is open (save as -v2); big SVG exports come as a file path, not an attachment.
Promoted:  qa-agent references/figma-check.md
