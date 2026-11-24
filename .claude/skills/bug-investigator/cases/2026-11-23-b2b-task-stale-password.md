---
case: b2b-task-stale-password
date: 2026-11-23
area: Playwright Framework / Task Scheduler / B2B batches
type: bug
---

Nangyari:  run-b2b-sanity-checks-am and -pm failed every attempt on 11/23, manual Runs included. 11/21 and 11/22 were missed only because the PC was off (System 1074 on 11/20 21:43, boot 6008/6005 on 11/23 07:51); logon failures are seen from the 11/23 07:56 StartWhenAvailable catch-up on. Last good log: reports/logs/b2b-NOON-20261120_113002.log.
Dahilan:   Proven: both tasks run with a stored credential (LogonType Password) that Windows now rejects. Event 104 "failed to log on ... LogonUserExEx" and Event 101 Error Value 2147943726 (0x8007052E, bad user name or password) on every 11/23 attempt. Not proven: why it went bad. Not a password rotation: pwdLastSet is 11/13 and the 11/20 runs succeeded after it. The owner disabled/updated -am at 09:00 (Claude touched no task).
Ayos:      The owner re-entered the credential on both tasks (Event 140 "updated" at 11/23 09:51). Pending: the 11/23 11:30 -pm run must show LastRunTime 11/23 11:30, LastTaskResult 0x0, Event 100/102 and no 104.
Rule:      A scheduled run that never starts: check Get-ScheduledTaskInfo LastRunTime and TaskScheduler/Operational events 101/104 before suspecting the suite; 0x8007052E means the task's stored password is stale.
Promoted:  pending go (target: qa-agent references/triage-failure.md, classification table)
