---
case: directive-double-soft-assertion
date: 2026-11-25
area: qa-agent automation / assertions
type: directive
---

Nangyari:  The owner: "tapos use double softassertion for validation ha eto na standard natin", then "gawin mo best approach". No soft assertions existed; every check was a hard expect, so the first mismatch hid the rest.
Dahilan:   Directive, no mistake behind it.
Ayos:      main/ActionDriver.js assertions use expect.soft; new static verifyStep(title, body) runs the step and ends with assertNoSoftFailures() (hard gate on test.info().errors). SauceDemo specs' 21 Verify steps use it (login 2, inventory 19); two flow checks inside action steps (badge before Reset, URL after Back) are followed by assertNoSoftFailures(); the step is boxed so reports point at the spec line. Probe spec proved: two wrong checks both reported, next step skipped, failure screenshot taken; probe deleted. SauceDemo 41 passed after.
Rule:      Validations use double soft assertion: soft expect for every check in a Verify step closed by a hard gate (ActionDriver.verifyStep / assertNoSoftFailures) so the test stops before the next action. A check inside an action step that the next action depends on is followed by ActionDriver.assertNoSoftFailures() right there. B2B does not use ActionDriver; its order steps are their own flow gates.
Promoted:  qa-agent references/new-page-automation.md (Spec conventions, Don't break table)
