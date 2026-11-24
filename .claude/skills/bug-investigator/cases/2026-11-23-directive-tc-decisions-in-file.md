---
case: directive-tc-decisions-in-file
date: 2026-11-23
area: qa-agent / test cases from a ticket
type: directive
---

Nangyari:  GWS-3115 hand-over asked the owner about TC-08 (confirm with the PO) and the be-fr ®/™ spec typo. The owner: "1. change status jan bro tapos lagay sa remark yung icoconfirm; 2. same sa #1 hehe remarks din, take note pag TC related laging update sa file lang".
Dahilan:   Directive. Test-case decisions belong in the TC workbook the team reads, not in a chat question.
Ayos:      TC-GWS3115.xlsx: TC-08 Passed with the PO question in Remarks; TC-12 be-fr counted as passed with the spec-typo note in Remarks.
Rule:      For anything test-case related (an item to confirm with the PO, a likely spec typo, a judgment call), set the status in the TC file and write what is to be confirmed in Remarks; update the file itself, and don't park it as a question in chat.
Promoted:  qa-agent references/testcase-doc.md "Fill the row" (the owner's ask; reviewer-agent reviewed 2026-11-23)
