---
case: directive-b2b-sanity-reruns
date: 2026-11-27
area: Playwright Framework / B2B order sanity / scheduled batches
type: directive
---

Nangyari:  The owner asked: "kung mag fail 8:30 check na order sanity, may way kaba para ireexecute or retrigger uli until mag pass? aside to sa retries? pero manyayari lang to if ang cause is due to timeout or slow internet?" The owner's answers: rerun a generic "Timeout ...ms exceeded" "Only if no error modal"; "3 reruns, 10 min apart"; "including 11:30"; "test mo na hindi ka nag ccomment sa jira". The flow the owner expects: "if may issue comment jira -> re-run, if may issue uli cocomment uli jira -> re run nag pass comment agad sa jira hehe, tas may cc na ha".
Dahilan:   Directive, no mistake behind it.
Ayos:      main/B2B/SanityRerunGate.js, resources/B2B/sanity-rerun.js, utilities/rerun-b2b-sanity.js, a RERUNS block in utilities/_b2b-batch.cmd (runs when the wrapper sets B2B_RERUN), a rerun note in SanityReportWorkbook, rerun wording in SanityJiraComment. Documented in tests/B2B/README.md "Reruns after a network or timeout failure".
Rule:      After the 08:30 and 11:30 batches (email and Jira comment as usual), rerun only the sites whose newest run failed on a network error (net::, ERR_, 5xx, Navigation timeout, page.goto), or on "Timeout ...ms exceeded" with no active error modal holding visible text on the saved FAILURE page (a spinner alone is not a modal). Never rerun on an app alert, a login or account rejection, or any other error. Run at most 3 reruns, 10 minutes apart, with --no-deps (no email, real guarded orders), and only while the round can still end before the next batch. After each rerun round, post a Jira comment with the cc ("<M/D> <slot> rerun N = PASS|FAILED", "<SITE> failed the <slot> run (<cause>), passed on rerun N"). Test reruns without posting to Jira.
Short:     Reruns after each batch: only sites whose newest run failed on a network error or a "Timeout ...ms exceeded" with no active error modal (spinner is not a modal); never on app alerts or login/account rejections; at most 3 reruns, 10 min apart, --no-deps (no email), ending before the next batch; a Jira comment with the cc after each round ("<slot> rerun N = ..."); test without posting to Jira.
Promoted:  tests/B2B/README.md "Reruns after a network or timeout failure"; qa-agent run-safely.md section 1 row; qa-agent references/b2b-jira-comment.md
