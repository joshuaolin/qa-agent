---
case: directive-short-actual-result
date: 2026-11-23
area: qa-agent / TC workbook
type: directive
---

Nangyari:  TC-GWS3115.xlsx: Actual Result (K) held up to ~3,700 characters per cell (every locale's full item list, quotes and URLs) in a 42-wide column with the row height capped, so it was cut off. The owner: "sa actual results mejo nakakalatan ako hirap basahin haha anywork around??", then "go mo lahat bro, if need mo pa ibreakdown into rows do it bro".
Dahilan:   The writer put the full per-locale details straight into K.
Ayos:      write_tc.py: Summary class writes a short K (FAILED lines with a cut reason, then pending / accepted / N/A / passed locale lists, then "click this cell"); DetailsSheet holds one row per TC and locale with the full text, a coloured result and a link to the Evidence row; K links to Details; K is 60 wide. qa-agent references/testcase-doc.md step 4.
Rule:      Actual Result stays short enough to read without clicking: failures with a short reason, other locales as lists; the full per-locale text goes one block per TC and locale on the Evidence sheet, next to its embedded screenshots, and K links to it.
Updated:   2026-11-23, Details sheet merged into the Evidence sheet (see directive-tc-status-and-evidence-links).
Promoted:  qa-agent references/testcase-doc.md "Fill the row" (the owner's "go mo lahat"; reviewer-agent ✗ 5 2026-11-23, all fixed)
