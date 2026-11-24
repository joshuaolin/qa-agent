---
case: directive-testcase-continuous-execute
date: 2026-11-23
area: qa-agent / test cases from a ticket
type: directive
---

Nangyari:  Claude described the ticket flow (write TCs, execute with a screenshot per step, suggest Passed/Failed in Remarks) with a stop to show the owner the rows before executing. The owner: "continuous tayo after ng creation, then execute agad".
Dahilan:   Directive. The owner reviews rows and evidence together at hand-over; the stop in between only slowed it.
Ayos:      qa-agent references/testcase-doc.md "Executing the test cases" and docs/qa-testcase-agent.md step 7.
Rule:      Ticket → write the test cases → execute them right away with a screenshot per step, no stop for a go in between; ask only if the ticket names no environment; never submit anything that reaches real people.
Promoted:  qa-agent references/testcase-doc.md
