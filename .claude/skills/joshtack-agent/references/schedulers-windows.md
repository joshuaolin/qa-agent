> Use when: building or fixing anything that runs on a schedule on his Windows laptop (cron, timers, monitors).

# Schedulers on Windows

## Use node-cron, not Task Scheduler

He disabled Task Scheduler jobs ("hassle yun e, cron lang ako"). A scheduled
job is a long-running Node process using `node-cron`, with the schedule as
data in config, not hardcoded in the script.

- Config shape: `atMinutes: [1, 30]` (explicit minutes) beats
  `everyMinutes: 30` when the minutes matter. Don't keep both. If you
  switch, remove the old key and say so.
- One run at a time: skip a tick if the previous run is still going, so
  there's no double send.
- The time zone is the **laptop's local time** unless the config names one.
  Teammates in **IST** running the same folder fire on *their* local clock.
  Say that explicitly whenever a schedule is shared, and set `timezone` in
  config when it must be fixed.
- Always state the **next trigger time** after any change ("run at 7:43pm
  with 5-min interval → next at 7:45pm").

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

## Handover

Give him: the folder, the start command (`node utilities/<x>-scheduler.js`),
how to see the next run time, how to stop it, and what to install
(`npm ci`, `npx playwright install` if it uses Playwright, and nothing else).
