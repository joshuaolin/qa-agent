> Use when: running ANY suite in this repo without sending an email, without submitting a real transaction, and without colliding with the scheduled runs. Load this before every test run you start yourself: verifying a change, reproducing a failure, dry-running a batch, "run it", "test mo", "check if it still works".

# Run safely

Running a suite can have three side effects that are easy to trigger by
accident. Know which command causes which before you press enter.

## 1. Email and notifications: usually the teardowns

Keep this table current for your repo. It is the first thing to check.

| Command | Sends mail? | Why |
| --- | --- | --- |
| `npm run test:<suite-with-mailer>` | **YES** | the project's teardown runs the mailer |
| `npm run report:<suite>` | **YES** | runs that teardown directly |
| plain checker specs | no | they only write Excel |
| `node utilities/validate.js` | no | static checks only |
| anything with `--list` | no | nothing runs |

When testing yourself, drop the teardown:

```
npx playwright test --project=<project> --no-deps --grep <LABEL> --headed --workers=1
```

`--no-deps` skips dependent projects, so no report and no email. Verify it
with `--list`: the count drops by exactly the teardown test. Never run a
report or alert command "to check the workbook". If the Excel itself is what
you need to see, ask first.

## 2. Real transactions: guarded, but every run is a real flow

If a flow walks a live order, form or checkout, it must stop before the
final submit. Keep the guard that blocks submission, never weaken or bypass
it, and never add a click on Submit / Save / Place order. Each retry is
another abandoned in-progress record on a live site, so prefer
`--grep <LABEL>` over the whole suite unless you are doing a regression pass
([shared-change-regression.md](shared-change-regression.md)).

## 3. The schedule: don't run on top of it

List the unattended runs (`SCHEDULE` in SKILL.md) and their wrapper scripts.
The wrapper scripts are the truth, not an older README. Before a run, check
the clock and what is already running:

```powershell
Get-Date -Format HH:mm
Get-CimInstance Win32_Process -Filter "Name='node.exe'" | ? CommandLine -match 'playwright test' | select ProcessId, CommandLine
```

`... test-server ...` is the VS Code test explorer, harmless. A
`playwright test --project=<scheduled project>` process means a batch is
live: don't start another, and don't delete anything under `reports/`,
`test-results/` or `playwright-report/` while it runs. Within about 15
minutes of a scheduled start, wait.

## Quick picks

| Goal | Command |
| --- | --- |
| Does the config still load? | `node utilities/validate.js` then `npx playwright test --list` |
| One site, watch it | `npx playwright test --project=<project> --no-deps --grep <LABEL> --headed --workers=1` |
| One checker suite | `npx playwright test tests/<Site>/<check>.spec.js` |

Report what the run actually did (sites, attempts, PASS/FAIL, and "no email
sent, teardown skipped with --no-deps"), not what the config says it should do.
