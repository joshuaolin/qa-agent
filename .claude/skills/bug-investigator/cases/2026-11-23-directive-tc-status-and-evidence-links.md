---
case: directive-tc-status-and-evidence-links
date: 2026-11-23
area: qa-agent / test cases from a ticket
type: directive
---

Nangyari:  TC-GWS3115.xlsx first draft left every Status at "In Progress" with the outcome only in Remarks. The owner: "napansin ko lang yung status is stuck sa in progress, dapat pass hehe, tas may way ba tayo para ma link yung mga screenshot or evidence sa loob ng file? para mas seemless".
Dahilan:   Directive. The Status column is what the team reads; the evidence should be one click away inside the file.
Ayos:      qa-agent references/testcase-doc.md "Fill the row" and docs/qa-testcase-agent.md steps 8-9; write_tc.py sets J to the outcome and adds an Evidence sheet with hyperlinks.
Rule:      Set Status to the real outcome (Passed / Failed / Blocked), never leave it In Progress; Remarks says why; screenshots are embedded in the workbook's Evidence sheet (one file for dev, no separate Details sheet) and each test case's Actual Result links to its block there.
Promoted:  qa-agent references/testcase-doc.md
Updated:   2026-11-23, the owner: "seems redundant yung details and reference, di ba pwede imerge tapos lahat ng screenshot nasa excel nalang din ... para pag binigay ko sa DEV ... isang file nalang?", then "go 1 and 2". Details + Evidence merged into one Evidence sheet with embedded screenshots; shared writer .claude\skills\qa-agent\testcase\write_tc.py.
