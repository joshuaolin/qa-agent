> Use when: diagnosing why a scheduled or manual run FAILED: a site that went red in the report email, a FAIL or stuck RUNNING run folder, a checker suite with failing URLs, or a batch that died. Decides whose problem it is (live site down, app rejected the data, locator drift, config/data, machine) before anything is changed. Trigger on "why did it fail", "bakit nag fail", "red si X kanina", "flaky ba to".

# Triage a failure

Goal: name the cause with evidence, then hand off to the right fix.
**Do not change code or config during triage.** Most red rows are not
locator bugs.

## 1. Find the evidence

- **Run folders:** `reports/<Suite>/<YYYYMMDD_HHMMSS>_<LABEL>_<PASS|FAIL|RUNNING>/`
  ```powershell
  Get-ChildItem reports\<Suite> -Directory | ? Name -match '<LABEL>' | sort Name | select -Last 6 Name
  ```
  - Each retry is its own folder and the report takes the **latest**.
    `FAIL, FAIL, PASS` = passed on attempt 3 → flaky site, not broken.
  - A `RUNNING` folder left behind = the process was killed or crashed mid-flow.
  - In a FAIL folder, read the **HTML dump first** (real `aria-label`,
    `placeholder`, `disabled` state). A screenshot alone leads to wrong
    guesses. Then the step screenshots to see where it stopped.
- **Batch log:** `reports/logs/<batch>-<stamp>.log` (tail of the run, exit code).
- **Workbook:** the suite's Excel in `reports/`, Summary / Remarks columns.
- **Checkers:** the Excel lists each URL's result. The failure is the URL's
  status or content, not the test.

## 2. Classify

| Signal | Cause | Next |
| --- | --- | --- |
| Timeout at login / DNS / 5xx, siblings fine in the same batch | live site slow or down | re-run that site once ([run-safely.md](run-safely.md)); report, don't fix |
| App shows a validation message, Confirm stays disabled | data rejected (account, product) | data file, ask the user |
| Element not found, control renamed or translated in the HTML dump | locator / wording drift | [xpath-locators.md](xpath-locators.md), then [shared-change-regression.md](shared-change-regression.md) if the page is shared |
| Button not rendered yet (appears after fields are filled) | ordering, not a missing step | flow fix, shared code |
| The submission guard blocked a request | flow clicked something it must never | **stop, tell the user** |
| Exit 134 / out of memory in the log | machine | close browsers, lower the worker cap |
| Same failure on several sites at once | shared code or shared content | check what changed last, not each site |
| Text diff right after a planned release | baseline stale | re-record the baseline |

Compare against a **sibling** on the same platform that passed in the same
batch. Same failure on the sibling = environment or shared code. Only this
site = its data or its own wording.

## 3. Report

Three lines: **what failed** (site, step, attempt n/3), **why** (with the
file that shows it: the HTML dump line, the app message, the log line), and
**whose fix it is** (site/environment, data, code, machine). Propose the fix.
Don't apply it until the user says so.
