> Use when: the regression pass required after editing SHARED code, meaning anything under main/ or pom/ that more than one site runs through (base classes, any *Page, *Panel, *Checker, flow classes, page-preparation helpers). Also for any change to a report or Excel layout. Trigger after such an edit before saying "done", and on "make sure nothing broke", "make sure walang nasira", "check the other sites".

# Regression pass for shared code

A one-site fix in shared code runs for every site on the next scheduled batch.

## Is this change shared?

```powershell
Select-String -Path main\*.js,main\*\*.js,pom\*\*.js,tests\*\*.js -Pattern "<FileName>'" | select Path -Unique
```

- Only `resources/**` data for one site, no `main/` or `pom/` touch → **not shared**.
  One live run of that site, one-line report. Stop here.
- Anything else → do the pass below.

## The pass

1. **Static first** (seconds, no side effects):
   `node utilities/validate.js` and `npx playwright test --list`.
   The test count must match what it was before your change.
2. **Live, the site you changed it for**, headed:
   `npx playwright test --project=<project> --no-deps --grep <LABEL> --headed --workers=1`
3. **Live, every site on that engine**, not a sample:
   - The whole project with `--no-deps`. Partial batches each cover only some
     sites, so none of them alone is a regression check. Keep the default retries.
   - Checker class: run every `tests/*/<check>.spec.js` that uses it.
   Follow [run-safely.md](run-safely.md) for timing and the no-email rule.
4. **Output-shape changes** (Excel columns, sheets, email body): show the user
   a sample or 2 to 3 layout options *before* implementing, then compare an
   old and new file side by side.

## Report

- Files touched and which engines and sites import them.
- Per-site result table from step 3 (PASS / FAIL / attempts).
- Any site that failed: is it your change? Compare with that site's last
  scheduled run. If it failed the same way before your change, say so and
  hand to [triage-failure.md](triage-failure.md).

Don't call it done on a spot check of one site.
