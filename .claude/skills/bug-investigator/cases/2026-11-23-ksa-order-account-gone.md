---
case: ksa-order-account-gone
date: 2026-11-23
area: Playwright Framework / B2B order sanity / KSA001
type: bug
---

Nangyari:  NOON run 11/23 09:53: KSA001 failed 3/3 at job_type_selected.
Dahilan:   Data, not slowness. result.json remark on every attempt: no Order Account option ends with "<account code>" (resources/B2B/entities.js:687); the dropdown offered only "<another customer> - <account code>". The account code changed or the test user lost access to it.
Ayos:      Not code: the admin reverted the customer (the owner asked their leads). Confirmed 11/23 11:52 and 11:55: KSA001 PASS on attempt 1, account "<expected customer> - <account code>". No change to entities.js.
Rule:      Same failure on every attempt with an app-reported remark is data or account, not timing; never raise timeouts for it.
Promoted:  not promoted: triage-failure.md already has the "account rejected → data, ask user" row.
