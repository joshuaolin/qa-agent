---
case: spec-compare-missed-extra-items
date: 2026-11-23
area: qa-agent / test case execution against a copy spec
type: mistake
---

Nangyari:  GWS-3115 first evidence run marked TC-04 (benefits) Passed on ca-fr. The ca-fr spec lists 7 benefits; the page shows 8, with "Résistant à la chaleur" that ca-fr should not have. reviewer-agent caught it before hand-over.
Dahilan:   The runner only checked that every spec line appears on the page (Text.missing). It never looked for page lines the spec does not have, which is exactly what "remove" / "replace" requirements need.
Ayos:      run.cjs listCheck: missing AND extra (page lines not in the spec) for benefits, key figures, technologies and legal; carousel checks scoped to the Crizal Natural Look card instead of the whole carousel text.
Rule:      A copy check against a spec is two-way: everything in the spec is on the page, and nothing on the page is missing from the spec; scope each check to the item it is about, never the whole section.
Promoted:  qa-agent references/testcase-doc.md "Executing the test cases", step 3 (reviewer-agent reviewed, the owner: "4. go bro")
