---
case: directive-url-json-reformat
date: 2026-09-14
area: Playwright Framework / checkers
type: directive
---

Nangyari:  The owner: Repastes resources/<Site>/url.json as a crawler dump (one open quote, no commas) and asks for it fixed; asked three times, dedupe explicitly requested.
Dahilan:   Directive, moved from auto-memory on 2026-11-23 so bug-investigator holds every directive in one place.
Ayos:      Moved over from the owner's earlier memory notes.
Rule:      url.json dump: back up, regex out the URLs, dedupe keeping first occurrence, re-emit as a JSON array matching HelixSolution/url.json, verify with ConvertFrom-Json, one-line report.
Promoted:  qa-agent references/checker-urls.md
