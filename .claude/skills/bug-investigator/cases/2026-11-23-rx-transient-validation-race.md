---
case: rx-transient-validation-race
date: 2026-11-23
area: Playwright Framework / B2B order sanity / CustomerInformationPanel
type: bug
---

Nangyari:  Live CGV001 run 11/23 10:28 (after the form-load fix): 2 of 3 attempts failed at order_account_selected with "Вне диапазона 5 - 45" while the screenshot shows Height 28 and PD 32, both valid and already derived to Left. Same data passed at 09:14.
Dahilan:   Strong hypothesis, not yet caught in the act: RxFieldMappers.typeRight types "28" key by key (pressSequentially, 80ms), so "2" is briefly below 5 and the app shows its range error; fillPrescription then waits a fixed 800ms (CustomerInformationPanel.js:224) and checks once. On a slow app the stale message is still there → false failure.
Ayos:      Applied with the owner's go ("yes pom fix tayo jan"): CustomerInformationPanel.waitForValidationToSettle() waits for the message to detach (EntityConfig validationSettleMs 10000) before assertNoValidationErrors(). Live B2B regression pending.
Rule:      Never assert on validation right after typing with a fixed short sleep; wait for the message to clear and fail only if it persists.
Promoted:  pending go (target: qa-agent references/triage-failure.md)
