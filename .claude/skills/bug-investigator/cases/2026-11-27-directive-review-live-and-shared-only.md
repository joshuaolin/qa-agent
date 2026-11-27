---
case: directive-review-live-and-shared-only
date: 2026-11-27
area: all repos / reviewer-agent / token use / testing emails
type: directive
---

Nangyari:  The owner asked whether skills and agents mean fewer tokens ("mas less token naba ginagamit mo now na may mga skill kana or agent kana reference?? compare sa wala??"). Claude showed what each costs: reviews ran 70k-127k tokens each, and the directives injected at session start were about 16.7k characters. It offered two cuts: use the reviewer only on live or shared code, and trim the injected directives. The owner: "okay cool proceed bro". During the change the owner added: "dont send email sakanila ha while doing testing" (to the manager, a teammate, the lead and a teammate, who now get the login monitor's fail and pending alerts).
Dahilan:   Directive, no mistake behind it.
Ayos:      reviewer-agent SKILL.md "When" table and description; coding-partner SKILL.md rule 13; bug-investigator SKILL.md rule 6 (doc-only promotions skip the review). The hook prints a case's `Short:` line when it has one, and six long directives got Short lines (16.7k -> 13.4k chars per session). qa-agent run-safely.md section 1 login-health row covers testing without emailing the new recipients.
Rule:      Send work to reviewer-agent only when it touches code that runs live or on a schedule, shared code, hooks/settings or agent definitions, or a QA deliverable for others. Skip it for docs, cases, memory and small config edits (say what changed and how it was checked). A long directive gets a one-line Short: so the session-start context stays small. Never email the owner's bosses or teammates while testing: use --no-deps, dry runs, or LOGIN_HEALTH_TEST_TO.
Short:     reviewer-agent only for live/scheduled code, shared code, hooks/settings and deliverables, not for docs, cases or small config; long directives get a Short: line; never email the bosses or team while testing (--no-deps, dry runs, LOGIN_HEALTH_TEST_TO).
Promoted:  reviewer-agent SKILL.md "When"; coding-partner SKILL.md rule 13; bug-investigator SKILL.md rule 6; qa-agent run-safely.md section 1
