---
case: tc-from-truncated-ticket
date: 2026-11-26
area: qa-agent / test cases from a Jira ticket
type: mistake
---

Nangyari:  AAV-2324 (site search, 47 comments) was read with a 9,000-character cut, then a second read that stopped at the 12 Nov comments. The 19 TCs were written from that. reviewer-agent found the 18-23 Nov comments that change three rows: business accepts non-article results with a logo placeholder (TC-15 expected "no category pages"), the sidebar and footer newsletter are now excluded (TC-13 asked the PO a question the ticket had answered), and the IT "fotofobia" count bug (TC-17).
Dahilan:   The output was truncated on purpose to save context, and the rows were written without going back for the rest. The latest comments hold the current decisions, so they matter most.
Ayos:      Read the rest of ticket.md; TC-13, TC-15 and TC-17 rewritten from the 18-23 Nov comments, the workbook rebuilt.
Rule:      Before writing TCs, read the whole ticket text and every comment through the last one (read ticket.md in parts if it's long, never stop at a cut); the newest comments override the description.
Promoted:  pending go (qa-agent references/testcase-doc.md, "Reading the source ticket")
