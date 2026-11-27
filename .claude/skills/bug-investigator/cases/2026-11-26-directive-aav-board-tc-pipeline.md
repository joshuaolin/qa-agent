---
case: directive-aav-board-tc-pipeline
date: 2026-11-26
area: qa-agent / test cases from the AAV Jira board
type: directive
---

Nangyari:  Once Claude could read Jira (qa-agent references/jira-api.md), the owner set how AAV board 697 tickets are handled: "lahat muna ng naka in progress na status is gagawan mo ... dont comment ha gawa ka folder sa download ko then lagay mo kung anong board number sya, then pag na pansin mong nandun yung ticket gawan mo na ng testcase pero dont execute, eexecute lang yan once nasa UAT ready na". Then: "pag nagawan mo na dapat if mag pabalik balik na tong ticket ... aware na na nagawan mo na sya before ... baka gawan mo kasi uli"; "board number is yung sa url mismo nung jira since walang sprint"; "only related sa frontend ... if backend/cms ... hindi naman doable sa QA side ... make sure mo na front end or live site or dev tools possible ma test".
Dahilan:   Directive, no mistake behind it. It replaces directive-testcase-continuous-execute for AAV board tickets: write now, execute later, by Jira status.
Ayos:      pending (qa-agent references/testcase-doc.md + jira-api.md).
Rule:      AAV board tickets: In Progress → write TCs only (no run) into the deliverables folder/AAV-<board id from the URL>\<KEY>\; UAT Ready → execute them; only tickets testable on the front end, live/preview site or dev tools (skip backend/CMS-only, Epics); keep a per-ticket ledger and check it first so a ticket that comes back is re-executed, not rewritten; never comment or write in Jira.
Promoted:  pending go
