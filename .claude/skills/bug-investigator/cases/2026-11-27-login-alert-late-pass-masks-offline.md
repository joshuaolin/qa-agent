---
case: login-alert-late-pass-masks-offline
date: 2026-11-27
area: Playwright Framework / B2B login health / alert email (login-health-only live copy and repo copy)
type: bug
---

Nangyari:  The owner: "currently sakin lang naka tagged yan e kasi may mga fails na naka cc sila bossing tapos not run lang naman pala minsan hindi nagana yung pending" and "intended ko na fail is sakin lang kasi nga di pa to masyadong consistent dahil sa net". Evidence from the 2026-11-25 17:30 cycle (login-health-only/reports/LoginHealth, scheduler-20261125.log lines 2085-2671):
- attempt 1 (17:30:30): all four sites got `net::ERR_INTERNET_DISCONNECTED`;
- attempt 2 (17:31:53): FNL001 passed, while ELO, MY and NOUK hit `page.goto: Timeout 60000ms`;
- attempt 3 (17:34): ELO, MY and NOUK timed out again.
The alert called ELO, MY and NOUK real failures ("other monitored sites signed in during the same cycle — so the network was working"). At 17:35 the mail relay itself was unreachable (`getaddrinfo ENOTFOUND the internal mail relay`), so the alert was spooled and sent later. The 18:00 cycle passed on all four.
Dahilan:   tests/B2B/login-alert.teardown.js judges each site by its final attempt only, and treats any site signing in at any point in the cycle as proof that the network worked. On a connection that drops and comes back, one site that passes late turns the others' network timeouts into FAIL. The earlier `ERR_INTERNET_DISCONNECTED` attempts and the unreachable relay are ignored.
Ayos:      Fixed in the repo copy (main/B2B/LoginAlertCycle.js classify, `connection` in resources/B2B/login-health.js) with the owner's go ("lets do that bro"). A FAIL becomes PENDING ("this PC's internet was unstable") when any attempt that cycle hit a local fault, or when a neutral connectivity check (msftconnecttest / google generate_204) fails. App messages stay FAIL. With the check OK, a lone failure is FAIL, and so is "all sites down" (previously guessed to be "fault at this end"). I dropped "3+ sites together", because it would hide a platform outage. Tested on the real 11/25 17:30 attempts (ELO, MY and NOUK now PENDING) and five fake cases. Not yet in the live copy: login-health-only still has the older inline teardown, and porting it there needs the owner's go. The daily Jira login comment (LoginJiraComment) already classifies this cycle as "slow connection on the PC".
Rule:      Never treat one site's sign-in as proof that the network was fine. Judge a cycle on all of its attempts (any local fault in any attempt, how many sites failed together), and prove a "real failure" only with the PC's connection known good.
Promoted:  pending (fix and go)
