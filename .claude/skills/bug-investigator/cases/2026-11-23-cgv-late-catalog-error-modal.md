---
case: cgv-late-catalog-error-modal
date: 2026-11-23
area: Playwright Framework / B2B order sanity / CGV001
type: bug
---

Nangyari:  NOON run 11/23 09:53: CGV001 failed 3/3 (the owner: "mabagal talaga mag load yung mga sites sa noon"). Attempts 1-2 at order_popup_opened (waitFor 20s), attempt 3 at order_form_loaded (click 15s). Also flaky on 11/20 noon (FAIL, FAIL, PASS) and 11/23 09:13 (FAIL, PASS).
Dahilan:   Not only slowness. FAILURE_CGV001.png (20261123_100331) shows the catalog-load error modal ("Повторить") over the form. recoverFromOrderFormLoadError() (pom/B2B/EssilorProPortalPage.js:261) runs once, right after the popup opens (OrderSanityFlow.js:112), and checks isVisible() with no wait. Attempt 3 has no order_form_load_error_retried checkpoint, so the modal appeared after the check. Attempts 1-2 took the retry once, then the form did not load within CustomerInformationPanel.waitForLoaded's hard-coded 20s.
Ayos:      The owner's go 2026-11-23: OrderSanityFlow.waitForOrderForm() watches for the retry modal while the form loads and once more after networkidle (only for entities with orderFormRetryButtonText); new EntityConfig option orderFormLoadTimeoutMs (default 20000 = old behaviour, CGV 60000). Live CGV run + full B2B regression pending.
Rule:      A load-error modal the app can raise late must be watched for during the wait, not checked once; check the FAILURE png before blaming slowness.
Promoted:  qa-agent references/triage-failure.md, classification table (the owner's go 2026-11-23)
Nangyari ulit: the owner's manual CGV run 10:55-11:01 with the fix: 3/3 FAIL. Attempts 1-2: popup sat on the Черновики (Drafts) page under a loading spinner for the full 60s, no error modal; attempt 3: form loaded, then a spinner curtain blocked the Job Type click. Site-side slowness beyond any sane timeout, not the late modal. Remark 'Timeout 9920ms' hides that 60s were waited.
Resolved for now: scheduled NOON batch 11/23 11:30 with commit 17aa45d: CGV001 PASS on attempt 1 (EOS, ZA, QATAR, ELO PASS; KSA FAIL on its account, separate case). The owner's manual CGV-only run 11:21 also PASS (attempt 2, load-error retry taken). Auto-reload when stuck on the loading spinner (the owner's manual fix: re-run) is held, not built: add it only if a stuck-loading failure shows up again.
