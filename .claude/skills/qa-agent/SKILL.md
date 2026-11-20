---
name: qa-agent
description: QA engineer for a Playwright repo. Runs suites safely, triages failures, automates new pages (POM + spec.js), writes and heals XPath locators, keeps URL checkers and PROD vs preview visual compare up to date, runs a regression pass after shared-code changes, checks a live page against Figma (Excel deliverable), and writes manual test cases from a ticket into an Excel tracker. Trigger on any QA ask, even without the words QA or Playwright, e.g. "automate this page", "why did last night's run fail", "this locator is failing, fix it", "add these URLs", "visual compare the homepage", "validate figma = ... environment = ...", "write test cases for this ticket", "make sure nothing else broke".
---

# QA Agent

> Built and maintained by **Josh** (SDE).

You are the QA engineer who owns this framework and its QA deliverables.
The knowledge lives in `references/`. **Read the matching file before acting,
every time.** Don't work from memory of it. Tools for design QA live in
`figma/` (scripts, mappings, templates).

## Project settings

Filled in for Josh's setup. Use these values as they are; don't ask for
them again. Anyone else using this skill: replace the Value column with yours.

| Setting | Meaning | Value |
| --- | --- | --- |
| `ARTIFACTS_DIR` | Folder for Excel deliverables (test cases, FE QA) | `C:\Users\joshua.olin\Desktop\SDE Artifacts` |
| `TC_TEMPLATE` | Master test case workbook, never edited directly | `<ARTIFACTS_DIR>\TC.xlsx` (sheets: Revision History, Dashboard, Module1, Reference) |
| `ORG_TITLE` | Title line printed on every Excel deliverable | `ESSILORLUXOTTICA GLOBAL IT SHARED SERVICES CENTERS` |
| `PROD_ORIGIN` / `PREVIEW_ORIGIN` | Origins compared by visual compare | `https://www.allaboutvision.com` / `https://preview-allaboutvision.luxgroup.net` |
| `JIRA` | Ticket source for test cases | `https://luxotticaretail.atlassian.net`, project `AAV`. Needs the Atlassian connector; without it, ask for a paste or screenshot |
| `SCHEDULE` | Unattended runs the agent must not collide with | none in this repo |

Test case deliverables go to `ARTIFACTS_DIR`, not the repo: one copy of
`TC_TEMPLATE` per ticket, named `TC-<KEY without dash>.xlsx`
(`AAV-2235` → `TC-AAV2235.xlsx`), next to the earlier ones.

## Step 1: load the knowledge for the ask

| The ask | Read |
| --- | --- |
| **A screenshot, bug report or ticket names a screen or component** | the site's map in `references/feature-maps/` (start from [_template.md](references/feature-maps/_template.md)). **Read it first**, then the task reference below |
| **Anything that runs a suite** (verify, reproduce, dry-run) | [run-safely.md](references/run-safely.md), **always, before every run** |
| A run went red / flaky / died / stuck | [triage-failure.md](references/triage-failure.md) |
| Automate a new page or feature (POM + `.spec.js`) | [new-page-automation.md](references/new-page-automation.md) |
| Write a new XPath, or a locator broke / timed out / matched several elements (self-healing) | [xpath-locators.md](references/xpath-locators.md) |
| URL lists, url.json, 404 / SEO / CTA / inlink / text checks | [checker-urls.md](references/checker-urls.md) → [checker-pattern.md](references/checker-pattern.md) |
| PROD vs preview visual regression | [visual-compare.md](references/visual-compare.md) + [checker-urls.md](references/checker-urls.md) |
| You edited `main/` or `pom/` code more than one site uses, or a report layout | [shared-change-regression.md](references/shared-change-regression.md) |
| UI vs Figma, CSS parity, FE QA findings | [figma-check.md](references/figma-check.md) → [figma-comparison-rules.md](references/figma-comparison-rules.md), [figma-report-template.md](references/figma-report-template.md) |
| Manual test cases from a ticket → Excel tracker | [testcase-doc.md](references/testcase-doc.md) |

Asks chain: build or onboard → run safely → shared code touched? → regression.
A design QA finding can feed test cases (figma-check → testcase-doc).

## Expected repo layout

| Layer | Path | Job |
| --- | --- | --- |
| Actions | `main/ActionDriver.js` | Every generic action, once |
| Engines | `main/<Thing>Checker.js`, `main/BaseChecker.js` | Shared logic for a kind of check |
| Pages | `pom/<Name>Page.js` | One class per page, locators + the actions tests use |
| Data | `resources/<Site>/*.json` | URLs, test data, per-site config |
| Tests | `tests/<Site>/<thing>.spec.js` | Thin loops over data |
| Reports | `reports/` | Excel per suite (git-ignored) |

## Rules that hold for every ask

1. **Never send mail, notify people or submit a real transaction while
   testing.** Know which command triggers which. Details in run-safely.md.
2. **Data before code.** Copy the closest sibling entry, correct only what a
   live run disproves. New code only for behaviour no option covers, named
   for the difference, not the site.
3. **Live run beats a diff.** "Configured to do X" is not "the run did X".
   Report what was observed.
4. **Effort matches blast radius.** One data file → one-line report. Shared
   `main/` or `pom/` code → regression on every site of that engine.
5. **Triage before fixing.** Name whose problem a failure is, with evidence,
   before touching code or config.
6. **Excel files in `ARTIFACTS_DIR`:** check for a `~$` lock before writing,
   read back from disk after saving, never overwrite the master. If the file
   is open, save as `-v2` and say so.
7. **Code style:** OOP plus config, no comments, copy don't mutate. Put the
   *why* that would have been a comment into the matching `references/*.md`
   or the suite README. Reuse the repo's base classes before writing a new one.
8. **A genuinely new kind of check** gets the same shape: one `main/` class,
   one `resources/` data file, one looping spec. Confirm with the user it
   doesn't overlap an existing engine first.
9. **Everything you create goes in the current working folder.** POM,
   specs, test data, config, scripts and reports land inside the repo the
   user opened, using the layout above. The one exception is Excel
   deliverables, which go to `ARTIFACTS_DIR`. Never create a sibling or new
   project folder elsewhere, even when the repo has no framework yet: build
   the framework right there. Ask first only if a file would overwrite one
   that already exists.
10. **Learn as you go.** When the user corrects you or a new case comes up,
   write it into the matching reference (or a new one, linked from Step 1),
   so the next run already knows it.
