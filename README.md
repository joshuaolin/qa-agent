# AI QA Agent

> Created and maintained by **Joshua Olin** · SDE · [Apache-2.0](LICENSE) · credit required, see [NOTICE](NOTICE)

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
| `team-doc-update.md` (+ `docs-kit/`) | Updates a team Word document in its own style: same-style diagrams, every claim checked, reviewed before hand-over | "Update the validation doc based on the current setup" |

## Agent names

> Renamed on 24 Nov 2026 so each name says what it does: joshtack-agent → coding-partner, conan-agent → bug-investigator, x-agent → reviewer-agent, analyst-agent → failure-analyst. If you installed the old folders, delete them, copy the new ones, and update the hook paths in step 5.

## Companion skill: coding-partner

`.claude/skills/coding-partner/` is the general coding partner that `qa-agent` builds on. It
holds the rules for every project, QA or not: OOP and config-driven code with
no comments, no side effects while testing, short Taglish replies that end
with the exact command to run, evidence-based debugging, and node-cron
schedulers on Windows.

| Reference | When it loads |
|---|---|
| `in-your-own-words.md` | Any request it had to interpret: it restates goal, plan and guesses, then waits for your go |
| `code-style.md` | Writing or changing any code or script |
| `safety.md` | Changes to an existing project, cleanup, delete, test runs |
| `communication.md` | Replies, explanations, handing over commands, status check-ins |
| `schedulers-windows.md` | Cron jobs and schedulers on a Windows laptop |

## Companion skill: bug-investigator

`.claude/skills/bug-investigator/` is the bug investigator and the team's memory.
It finds causes from evidence (code read, output seen, a run done), and logs
every bug, mistake and instruction as a case in `cases/` with a prevention
rule. A rule that applies beyond its case is drafted into the skill it
belongs to; reviewer-agent reviews the draft and a person gives the go.

| Reference | When it loads |
|---|---|
| `investigate.md` | Anything broken, slow or flaky (moved here from coding-partner) |
| `casebook.md` | A case is solved, a correction or an instruction was given |

## Companion agent: reviewer-agent

`.claude/agents/reviewer-agent.md` is a read-only reviewer subagent, and
`.claude/skills/reviewer-agent/` tells the main agent when to call it: before any
non-trivial work is reported done. It checks the work against the ask, the
skills' rules and the casebook, returns `✅ PASS` or `✗ ISSUES` with
file:line findings, and every review goes into `ledger.md`, with columns for
what a person confirmed and what reviewer-agent missed. The missed count is the
main signal for how far the review can be trusted.

## Install

All four ship pre-installed. The skills live in `.claude/skills/` and the
reviewer subagent in `.claude/agents/`, the folders Claude Code scans when
it opens a project, so there is nothing to copy:

1. Clone the repo and open the folder in Claude Code:
   ```
   git clone https://github.com/joshuaolinessilor/ai-qa-agent.git
   cd ai-qa-agent
   claude
   ```
   Type `/` and `/qa-agent` and `/coding-partner` show up in the suggestions.
   If they don't, start a new session or reload the VS Code window.
2. To use them in another project, copy the four folders under
   `.claude/skills/` into that project's `.claude/skills/` and
   `.claude/agents/reviewer-agent.md` into its `.claude/agents/`, or into
   `~/.claude/skills/` and `~/.claude/agents/` for every project. A copy
   doesn't update itself: copy again after you pull changes.
3. Open `.claude/skills/qa-agent/SKILL.md` and fill in **Project settings**
   (artifacts folder, Excel template, preview origin, schedule).
4. For the Figma check, install its tools once:
   ```
   cd .claude/skills/qa-agent/figma/scripts
   npm install
   npx playwright install chromium
   pip install openpyxl pillow
   ```
5. bug-investigator's hooks ship in this repo's `.claude/settings.json`, so
   they run as soon as you open the clone from its root folder (the hook path
   is relative to it; Claude Code may ask you to trust the project's hooks
   once). Each session starts with the standing
   directives and latest lessons from `cases/`, and a prompt with bug or
   correction keywords reminds the agent to load bug-investigator. To get
   them in another project, copy `bug-investigator/` (with `cases/`) and the
   `hooks` block of `.claude/settings.json` there. For every project, install
   the skill under `~/.claude/skills/` and put this in
   `~/.claude/settings.json` instead, with `<HOME>` replaced by your full
   home folder path (`args` are not expanded by a shell):
   ```json
   {
     "hooks": {
       "SessionStart": [{ "hooks": [{ "type": "command", "command": "node", "args": ["<HOME>/.claude/skills/bug-investigator/hooks/bug-investigator-hook.mjs", "session"], "timeout": 10 }] }],
       "UserPromptSubmit": [{ "hooks": [{ "type": "command", "command": "node", "args": ["<HOME>/.claude/skills/bug-investigator/hooks/bug-investigator-hook.mjs", "prompt"], "timeout": 10 }] }]
     }
   }
   ```
   Memory (`MEMORY.md`) is per user and is not in the repo; the cases are
   what carries the standing rules over.
6. In Claude Code, type `/qa-agent` and describe the task in plain words.

## Expected repo layout

The references describe a POM + data-driven Playwright framework:

```
main/ActionDriver.js        generic actions, written once
main/<Thing>Checker.js      shared engines (extend BaseChecker)
pom/<Site>/<Name>Page.js    one class per page: locators + actions
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

## Author and license

Created, designed and maintained by **Joshua Olin** · SDE.

Licensed under [Apache-2.0](LICENSE). You may use, change and share it,
under these conditions (section 4 of the license):

| You must | How |
| --- | --- |
| Keep the credit | Keep [NOTICE](NOTICE) and the "Built and maintained by Joshua Olin · SDE" line in every skill and agent, in every copy and fork |
| Mark your changes | Say in each changed file that you changed it |
| Credit when you share | Name "Joshua Olin · SDE" as the original author wherever you share, demo or present it |

Every Claude session in this repo shows the credit at start
(.claude/hooks/attribution.mjs). If the NOTICE, the LICENSE or a signature
line is removed, the session opens with an attribution warning instead.
