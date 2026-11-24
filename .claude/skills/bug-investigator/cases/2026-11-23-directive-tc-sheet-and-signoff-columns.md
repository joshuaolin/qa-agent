---
case: directive-tc-sheet-and-signoff-columns
date: 2026-11-23
area: qa-agent / TC workbook
type: directive
---

Nangyari:  TC-AAV2266.xlsx kept the template's sheet name "Module1" and "the owner's name" as Written By. The owner: "from now on Module 1 -> Testsuite? or Testcases? rename mo basta wag module 1 hehe, tapooos Written by qa-agent from now on haaaa, tapos tama lang din na executed by qa-agent tapos add ka new row na final validation by: then leave it blank lang, dont forget yung UI haaa dapat di yan bungi".
Dahilan:   Directive. The workbook shows who wrote and ran it (the agent) and leaves the sign-off to QA.
Ayos:      .claude\skills\qa-agent\testcase\write_tc.py: SheetRename ("Module1" → "Test Cases", 12 Dashboard COUNTIFs + 2 labels rewritten, stops if a reference is left), L and Q = qa-agent, ExtraColumn R "Final Validation By" styled from Q (no gap), Dashboard Tested By / Date Executed filled, Reviewed by blank. Checked by an Excel render of the header, Dashboard (counts and 3 charts) and Evidence. qa-agent references/testcase-doc.md "Sheet structure".
Rule:      Every TC workbook: the test case sheet is "Test Cases", never Module1 (Dashboard formulas follow the rename); Written By and Executed By are qa-agent; a blank "Final Validation By" column after Executed By with the same look as its neighbours; check the look in an Excel render, not just the cell values.
Promoted:  qa-agent references/testcase-doc.md
