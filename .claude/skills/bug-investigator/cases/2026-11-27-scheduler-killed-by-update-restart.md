---
case: scheduler-killed-by-update-restart
date: 2026-11-27
area: qa-agent-public-demo / SauceDemo monitor
type: bug
---

Nangyari:  The SauceDemo monitor started at 22:45 on 2026-11-26 (next cycle 10:00) ran nothing at 10:00 on 2026-11-27; the log has no line between 22:48 and the owner's manual start at 10:26.
Dahilan:   System log: event 1074 at 07:54:03, MoNotificationUx.exe "initiated the restart ... Service pack (Planned)", boot at 07:54:53. A Windows Update restart ends every Node process, and nothing starts the scheduler again. Sleep at 04:33 alone would not have stopped it (the poll catches up), the restart did.
Ayos:      Restarted it by hand at 10:29 (first cycle sent 10:29:30). No auto-start built yet; it needs the owner's go (Startup-folder launcher vs. other).
Rule:      A long-running Node scheduler does not survive a restart: the hand-over says so, and after any reboot or "no runs today" check the process (`Get-CimInstance Win32_Process -Filter "Name='node.exe'"`) and System event 1074 before debugging the code.
Promoted:  pending go → coding-partner references/schedulers-windows.md ("It must run whatever state the laptop is in")
