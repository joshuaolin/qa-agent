---
case: tc-layout-not-compared
date: 2026-11-24
area: qa-agent / test case execution (evidence run)
type: mistake
---

Nangyari:  GWS-3115 rerun: the owner saw the video block heading sitting on the left while the other headings are centred (Evidence row 61, ch-de) and asked whether it is a regression: "dapat na cacatch mo din yun e". The run had compared only text against the spec, so nothing in the workbook said whether the layout was right.
Dahilan:   The evidence run checked copy, order, links and images, never layout. No step compared a block's position with the same block on a live page, so an odd-looking alignment could be neither caught nor cleared.
Ayos:      Measured every block's heading alignment and left/right gap on all 7 locales against the same component on 4 PROD live Crizal pages (qa-reports\TC-GWS3115\align_probe.cjs, layout_check.cjs): all equal; the video module (TechnologyDemo) is left-aligned on live too, so not a regression. Added TC-18 with the table screenshot and two live reference shots.
Rule:      In every evidence run of a page built from existing modules, compare each block's layout (text-align, left/right gap, centring) with the same component on a live page, as its own TC with a table screenshot and a live reference shot; anything that looks off in a screenshot is checked and written in the file, never left for the owner to spot.
Promoted:  qa-agent references/testcase-doc.md "Executing the test cases", step 3
