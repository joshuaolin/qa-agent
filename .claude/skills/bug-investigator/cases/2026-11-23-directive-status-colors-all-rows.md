---
case: directive-status-colors-all-rows
date: 2026-11-23
area: qa-agent / TC workbook
type: directive
---

Nangyari:  TC-GWS3115.xlsx: only rows 6-9 of the Status column had colours. The owner: "napansin ko yung status column bro di lahat may kulay pa take note nyan ha".
Dahilan:   The template colours Status with one conditional-format rule set per cell, and only for J6:J9 (Not Started / Passed / Failed / In Progress / Out of Scope / Blocked). New rows past J9 got the dropdown (the sqref was extended) but no colour rules.
Ayos:      write_tc.py extend_status_colors(): copies J6's six rules to every new row with the cell reference changed; qa-agent references/testcase-doc.md "Sheet structure".
Rule:      Every row written into a TC workbook gets the same Status colour rules as the template rows (and the dropdowns); check colours on every row, not just the first four, before hand-over.
Promoted:  qa-agent references/testcase-doc.md "Sheet structure" (sheet renamed "Test Cases" 2026-11-23) (the owner's "take note", go 2026-11-23 "go mo lahat bro"; reviewer-agent reviewed 2026-11-23)
