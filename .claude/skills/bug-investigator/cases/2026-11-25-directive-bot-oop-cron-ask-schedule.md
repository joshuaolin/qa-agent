---
case: directive-bot-oop-cron-ask-schedule
date: 2026-11-25
area: coding-partner / scheduled bots
type: directive
---

Nangyari:  The owner: "kung gagawa ng bot like yung login-health natin pwede bang OOP natin in the future tapos matic na cron ang gagamitin mo then bigay mo rin instruction paano i run? tas always ask ang range time kung kelan to i rurun at ilan minutes interval para aware si another QA kung paano gagawin", then "dapat cautious ka sa email na gagamitin para sa sender haa ask mo sya if acc ba nya gagamitin then lapag mo yung or hingin mo email nya".
Dahilan:   Directive, no mistake behind it. The login-health monitor (LoginHealthScheduler + config schedule + schedule:login-health) is the shape to repeat.
Ayos:      coding-partner references/schedulers-windows.md "Building a new bot": the engine / config / entry / npm scripts table, the question to ask first, and the hand-over block.
Rule:      A new bot is OOP like login-health: one <Name>Scheduler class, the schedule as config data, a long-running Node scheduler that polls every 15 s with catch-up (not node-cron timers, not Task Scheduler; B2B order checks stay on Task Scheduler), npm scripts test:<name> (one run) and schedule:<name> (cron). Before building, always ask the time range it runs in, the interval in minutes, and, if it sends mail, whose account sends it (the requester's own account, or ask for the sender address); never pick them, never reuse another bot's sender address, and keep sender, recipients and passwords in .env. The hand-over gives the run block from schedulers-windows.md: install, run once, start cron, schedule, next run, logs, where to change it.
Promoted:  coding-partner references/schedulers-windows.md
