---
case: npm-swallowed-script-flag
date: 2026-11-27
area: qa-agent-public-demo / SauceDemo monitor / utilities/saucedemo-monitor-scheduler.js
type: bug
---

Nangyari:  The owner ran `npm run schedule:saucedemo-monitor --now`; the scheduler came up with "Next cycle: 10:28" and ran nothing at start, so it looked broken.
Dahilan:   npm keeps a flag written before `--` as its own config: `npm run env --now` shows `npm_config_now=true`, and the script's argv had no `--now`. The README said `-- --now`, but the hand-over block never showed the flag form.
Ayos:      The entry reads each flag from argv or `npm_config_<flag>` (SauceDemoMonitorEntry.flag), so `--now`, `-- --now` and `--dry-run` work either way. Proven: `npm run test:saucedemo-monitor --dry-run` → "Dry run: email not sent"; `npm run schedule:saucedemo-monitor --now` → "Cycle started" 1 s after "Scheduler up", email sent 10:29:30.
Rule:      A script flag meant for an npm script is read from argv or `process.env.npm_config_<flag>`, and the hand-over shows each flag in the exact form the owner will type.
Promoted:  pending go → coding-partner references/schedulers-windows.md (Building a new bot, Entry row)
