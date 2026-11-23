> Use when: QA trends and history across many runs, not one failure: "flaky ba", "ilang beses nag-fail this week", "anong pinaka-unstable", "recurring failures", "coverage gaps", "QA summary report", "trend report", "weekly report"; and in English: "which test is flaky", "what failed most this week", "is it the app, the test or the environment", "QA summary". One red run → triage-failure.md instead.

# Analyst: run history, flaky tests, recurring failures

Two parts, because counting and judging are different jobs:

| Part | Does | Where |
| --- | --- | --- |
| Engine | Counts every run: pass on first try, flaky (failed then passed on retry), failed after all retries; groups failures by step + message; first guess at the cause from the message | `analyst/analyze.py` + one data file per suite (`analyst/b2b.json`) |
| analyst-agent | Reads the evidence (FAILURE html/png, step shots) of the top recurring failures and says application defect / environment / data / test instability, with the file that proves it | `.claude/agents/analyst-agent.md` (read-only subagent) |

## Run it

```powershell
python -B -I .claude\skills\qa-agent\analyst\analyze.py . .claude\skills\qa-agent\analyst\b2b.json <output folder>/QA-Trends-B2B-<date>.xlsx [since=2026-11-17] [top=5]
```

1. The engine writes the workbook and `qa-reports\analyst\b2b-to-read.json`
   (the top unread recurring failures; folders: the oldest + the 2 newest each).
2. Spawn **analyst-agent** with that file's path. It returns a JSON array.
3. Save that array as `qa-reports\analyst\b2b-verdicts.json`. Merge it with
   earlier verdicts; match = label + signature key (`key`). Re-run the engine: column
   "Verdict from evidence" fills in, and those items drop off the to-read list.
4. x-agent before hand-over if the report goes to anyone but the owner.

Read-only end to end: it reads `reports/`, never re-runs a suite, never
changes data. A verdict that says data (an account lost access) is
reported to the owner. The fix belongs to whoever owns the data.

## Workbook

| Sheet | Shows |
| --- | --- |
| Recurring failures | site, step, failure (numbers masked so repeats group), times, days, same failure at other sites in the same batch, likely cause, next step, verdict from evidence, link to the latest FAILURE png |
| Sites | per site: scheduled runs, passed 1st try, flaky, failed after retries, interrupted, attempts used, first-try % of completed runs, verdict (thresholds in the suite JSON: stable ≥ 90 % first try) |
| Daily | site × day, coloured by the worst outcome that day |

A scheduled run = one retry chain: attempts 1→3 of the same label within
`chainGapMinutes`. That is how "flaky" is told apart from "broken".

## Keeping it right

- **Unclassified > 0** in the engine output means a new failure kind: read
  it (triage-failure.md), then add a `causes` pattern to the suite's JSON,
  not code.
- "Same failure at other sites" counts only sites with the **same step and
  message** (the signature key) in the same batch. A data failure next to
  a timeout, or two different timeouts, is not shared.
- Verdicts are matched on label + signature key, never on the step alone,
  so a verdict can't spill onto a different failure at the same step.
- A chain that stops before its retries (a FAIL at attempt 1 of 3 with no
  attempt 2) is **interrupted**, not "failed after all retries". It is left
  out of the first-try %.
- New suite: a new `<suite>.json` once its
  runs write a per-run result file; the engine stays the same.
