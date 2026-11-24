---
case: directive-tc-itemized-cells
date: 2026-11-24
area: qa-agent / test case workbooks
type: directive
---

Said:      "upgrade muna natin yung testcase, napansin ko hindi readable in human perspective si precondition? maybe numbers will help? ... sobrang haba ng sentence, i-itemized mo para mas madali ma gets, excepts sa requirements syempre ... sa what was seen ng evidence tab mejo hirap din basahin"
Rule:      In every TC workbook the Precondition is a numbered list, and Test Data, Expected Result, Remarks and the Evidence "What was seen" are short items (one fact per line); only the Requirement Description stays a sentence. write_tc.py renders the lists and refuses a long one-sentence cell.
Applied:   write_tc.py (Itemized, WhatWasSeen, TopLevel), testcase-doc.md, TC-GWS3115 and TC-AAV2266 rebuilt.
Promoted:  testcase-doc.md ("Short items, not long sentences" bullet under writing the steps)
