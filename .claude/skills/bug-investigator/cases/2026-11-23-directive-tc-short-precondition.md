---
case: directive-tc-short-precondition
date: 2026-11-23
area: qa-agent / test cases from a ticket
type: directive
---

Nangyari:  TC-AAV2266 precondition grew to ~440 characters (browser, site, full sample URL, window size, SEO extension, PROD reference), repeated on every row, so every row became 324 pt tall. The owner: "ayoko nung precondition mo dang haba HAHA short and simple for pre-condition pa take note".
Dahilan:   Directive. The precondition is read once; the detail belongs where it is used.
Ayos:      qa-reports\TC-AAV2266\tc_rows.json precondition = "Google Chrome, window maximised. / Preview site opens: <base URL>"; the SEO extension moved to TC-03 Test Data. qa-agent references/testcase-doc.md "Writing the steps" (Precondition bullet).
Rule:      Precondition is 1–2 short lines, the same on every row: browser + the site that must open. Page URLs go in the steps; a tool, account or PROD reference one TC needs goes in that TC's Test Data.
Promoted:  qa-agent references/testcase-doc.md
