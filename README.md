# qa-agent

A Claude Code skill that works as the QA engineer of a Playwright repo.

I wrote down how I actually do QA, step by step, as small `.md` files in one
folder (`references/`). That folder is the agent's library. Every time you
call `/qa-agent`, it reads the files that match the task and follows them, so
anyone on the team gets the work done the same way, much faster than by hand.

The one part that stays human is judgement on the output. And it keeps
learning: when you correct it or hit a new case, the lesson goes into a new or
updated `.md`, so the next run already knows it.

## What it can do

| Skill (references/) | What it does | Ask it like this |
|---|---|---|
| `feature-maps/` | Matches a screenshot or bug report to the exact page or step and gives a selector that works | "Where is this on the checkout page?" + screenshot |
| `run-safely.md` | Runs any suite without sending email, submitting real transactions or clashing with scheduled runs | "Run the smoke suite for the login page" |
| `triage-failure.md` | Finds why a run failed and whose problem it is before anything is changed | "Why did last night's run fail?" |
| `new-page-automation.md` | Builds POM pages, test data and spec.js for a new page | "Automate the inventory page of saucedemo.com" |
| `xpath-locators.md` | Writes new XPaths and heals broken ones using a fixed set of patterns | "The CartItemName locator is failing, fix it" |
| `checker-urls.md`, `checker-pattern.md` | URL checks: 404, SEO, CTA links, inlinks, text compare; cleans up url.json | "Add these URLs to the 404 check" |
| `visual-compare.md` | PROD vs preview screenshots, pixel diff, Excel report | "Visual compare the homepage" |
| `shared-change-regression.md` | After a change to shared code, reruns every site that uses it | "Make sure nothing else broke" |
| `figma-check.md` (+ rules, report template) | Compares a live page to Figma by computed CSS, writes a findings Excel | "Validate: figma = <link>, environment = <url>" |
| `testcase-doc.md` | Writes manual test cases from a ticket into a copy of your Excel tracker | "Write test cases for PROJ-123" |

## Companion skill: joshtack-agent

`.claude/skills/joshtack-agent/` is the general coding partner that `qa-agent` builds on. It
holds the rules for every project, QA or not: OOP and config-driven code with
no comments, no side effects while testing, short Taglish replies that end
with the exact command to run, evidence-based debugging, and node-cron
schedulers on Windows.

| Reference | When it loads |
|---|---|
| `code-style.md` | Writing or changing any code or script |
| `safety.md` | Changes to an existing project, cleanup, delete, test runs |
| `communication.md` | Replies, explanations, handing over commands |
| `investigate.md` | Anything broken, slow or flaky |
| `schedulers-windows.md` | Cron jobs and schedulers on a Windows laptop |

## Install

Both skills ship pre-installed. They live in `.claude/skills/`, the folder
Claude Code scans when it opens a project, so there is nothing to copy:

1. Clone the repo and open the folder in Claude Code:
   ```
   git clone https://github.com/joshuaolin/qa-agent.git
   cd qa-agent
   claude
   ```
   Type `/` and `/qa-agent` and `/joshtack-agent` show up in the suggestions.
   If they don't, start a new session or reload the VS Code window.
2. To use them in another project, copy `.claude/skills/qa-agent/` and
   `.claude/skills/joshtack-agent/` into that project's `.claude/skills/`,
   or into `~/.claude/skills/` for every project. A copy doesn't update
   itself: copy again after you pull changes.
3. Open `.claude/skills/qa-agent/SKILL.md` and fill in **Project settings**
   (artifacts folder, Excel template, preview origin, schedule).
4. For the Figma check, install its tools once:
   ```
   cd .claude/skills/qa-agent/figma/scripts
   npm install
   npx playwright install chromium
   pip install openpyxl pillow
   ```
5. In Claude Code, type `/qa-agent` and describe the task in plain words.

## Expected repo layout

The references describe a POM + data-driven Playwright framework:

```
main/ActionDriver.js        generic actions, written once
main/<Thing>Checker.js      shared engines (extend BaseChecker)
pom/<Name>Page.js           one class per page: locators + actions
resources/<Site>/*.json     URLs, test data, per-site config
tests/<Site>/*.spec.js      thin loops over the data
reports/                    Excel per suite (git-ignored)
```

If your repo looks different, edit the references. They are plain markdown.

## Make it yours

- **Add a feature map** per site: copy
  `.claude/skills/qa-agent/references/feature-maps/_template.md`.
- **Add a new skill:** write `.claude/skills/qa-agent/references/<task>.md`
  with a `> Use when:` line at the top, then add one row to the table in
  `SKILL.md`, Step 1.
- **A whole new agent:** add a folder `.claude/skills/<name>/SKILL.md`. Every
  skill must sit directly under `.claude/skills/` or it won't be suggested.
- **Keep it honest:** whenever the agent gets something wrong, fix the
  reference, not just the output.

## Built by

Josh, SDE.
