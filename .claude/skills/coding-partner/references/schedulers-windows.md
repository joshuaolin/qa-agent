> Use when: building or fixing anything that runs on a schedule on his Windows laptop (cron, timers, monitors).

# Schedulers on Windows

## A Node scheduler, not Task Scheduler

He disabled Task Scheduler jobs for bots ("hassle yun e, cron lang ako"),
except the B2B order checks, which stay on Task Scheduler (2026-11-25). A
scheduled bot is a long-running Node process with the schedule as data in
config, not hardcoded in the script. "cron" is the word he uses for it.

- Don't fire from `node-cron` timers. node-cron 4 drops a slot when its timer
  fires a few seconds late (Windows timer throttling, sleep). Poll instead:
  `setInterval` every 15 s, run the slot that has come due once, catch up a
  late slot and log how late it was.
- Config shape: `atMinutes: [1, 30]` (explicit minutes) beats
  `everyMinutes: 30` when the minutes matter. Don't keep both. If you
  switch, remove the old key and say so.
- One run at a time: skip a tick if the previous run is still going, so
  there's no double send.
- Keep the laptop awake only while a cycle runs (`SetThreadExecutionState`
  from a helper process, released when the cycle ends).
- The time zone is the **laptop's local time** unless the config names one.
  Teammates in **IST** running the same folder fire on *their* local clock.
  Say that explicitly whenever a schedule is shared, and set `timezone` in
  config when it must be fixed.
- Always state the **next trigger time** after any change ("run at 7:43pm
  with 5-min interval → next at 7:45pm").

## Building a new bot (monitor, health check, report)

Use this engine shape (the login-health monitor is built this way), don't invent a new one:

| Part | Where | Job |
| --- | --- | --- |
| Engine | `main/<Site>/<Name>Scheduler.js` | One class: reads `config.schedule`, `nextSlot()` + a 15 s poll, catch-up of late slots, skips ticks outside the window or while a run is going, keeps the laptop awake during a cycle, logs to `reports/<Name>/scheduler-<date>.log` |
| Config | `resources/<Site>/<name>.js` | `schedule: { from: 'HH:MM', to: 'HH:MM', atMinutes: [...] }` (or `everyMinutes`, never both) plus what the bot checks |
| Entry | `utilities/<name>-scheduler.js` | Loads the config, `new <Name>Scheduler(config, root).start()`; `--once` runs one cycle, `--now` also runs one at start |
| One cycle | npm script `test:<name>` | Runs once, no scheduler, for manual checks |
| Scheduler | npm script `schedule:<name>` | `node utilities/<name>-scheduler.js`, the long-running process |

Never hardcode the sender address in config, and keep only one of
`everyMinutes` / `atMinutes` (unless one is used for something else and
the README says so). A new bot takes its sender and recipients from `.env` keys named
after it (`<NAME>_SENDER`, `<NAME>_RECIPIENTS`), listed blank in
`.env.example`.

Before writing it, **always ask** (one message, all parts):
- the time range it runs in (`from`–`to`, and which days if not daily);
- the interval in minutes (or the exact minutes);
- if it sends mail: whose account sends it. Ask whether it is the
  requester's own account; if not, ask for the sender address. Never reuse
  an address already in another bot's config (it is someone else's
  account), and never guess one. Sender, recipients and any password go in
  `.env`, not in the code.

Never pick these yourself; another QA has to know when it fires and whose
mailbox it sends from.

Hand-over, every time, as a short block a QA can follow:

```
Folder:      <repo root>
Install:     npm ci   (and npx playwright install if it uses Playwright)
Run once:    npm run test:<name>
Start:       npm run schedule:<name>     (keep the window open)
Stop:        Ctrl+C in that window
Schedule:    <from>-<to>, every <n> min (<atMinutes>), laptop local time
Sender:      <address>, from .env <NAME>_SENDER, not in code
Next run:    <HH:MM>   (also printed as "Next cycle:" in the log)
Logs:        reports\<Name>\scheduler-<yyyymmdd>.log
Change it:   resources\<Site>\<name>.js → schedule
```

## It must run whatever state the laptop is in

"dapat mag run parin kahit naka sleep / naka lid close / Win+L". After a
Windows update these settings revert, so re-check them every time he reports
"di nagana nung idle":

```powershell
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0
powercfg /setactive SCHEME_CURRENT
powercfg /requests
```

Win+L (lock) does not stop Node. Sleep and hibernate do. Also check the
process is actually alive (`Get-CimInstance Win32_Process -Filter
"Name='node.exe'"`) before debugging the code.

## Delayed or duplicate emails

- A run fires on time but the email lands ~20 min late → check the relay or
  VPN path and the message `Received:` headers before touching the
  scheduler.
- A double send → two scheduler instances, or a retry that re-sends after a
  timeout that actually succeeded. Check processes first.
