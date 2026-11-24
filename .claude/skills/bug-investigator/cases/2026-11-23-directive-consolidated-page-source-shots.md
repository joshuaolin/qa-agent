---
case: directive-consolidated-page-source-shots
date: 2026-11-23
area: qa-agent / test cases from a ticket
type: directive
---

Nangyari:  GWS-3115: TC-02 (metadata) and TC-17 (link statuses) are read from the page source, so they had no screenshot. Claude asked whether one screenshot per check was right. The owner: "3. per check tama sooo tc-02 consolidated lahat ng sc, tapos hyperlink mo nalang hehe".
Dahilan:   Directive. Every test case needs viewable proof in the workbook, even when the check has nothing on screen.
Ayos:      qa-reports\TC-GWS3115\consolidate.cjs renders one table (all locales, page value vs spec / HTTP status) to TC-<T>-<seq>-all-step1.png; write_tc.py links it from the Evidence sheet and refuses to write a test case with no evidence; qa-agent references/testcase-doc.md step 2.
Rule:      One screenshot per check; a check with nothing on screen (page source, HTTP status) gets one consolidated table screenshot for all locales, linked from the Evidence sheet like the others.
Promoted:  qa-agent references/testcase-doc.md "Executing the test cases", step 2 (the owner's ask; reviewer-agent reviewed 2026-11-23)
Updated:   2026-11-24: the table is named after the column H step it proves, TC-<T>-<seq>-all-step<k>.png (GWS-3115: TC-02 step7, TC-17 step5), not always step1.
