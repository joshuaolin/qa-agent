> Use when: writing manual QA test cases into the team's Excel test case tracker from a Jira ticket URL, pasted ticket text, or a screenshot of a ticket. This produces a human-readable document for someone to execute by hand, not Playwright code. Trigger whenever asked to create, write, or break down test cases for a ticket, add rows to the tracker, or "gumawa ng test case" from a ticket/screenshot/URL. Examples: "write test cases for PROJ-123", "breakdown mo into more detailed test cases", "gumawa ka ng test case base sa ticket na to".

# Test case document

Produces rows in the team's Excel test case tracker from a ticket (URL,
pasted text, or screenshot). If the ask is actually about automation
coverage (a new spec, POM method, checker entry), that is automation, not
this file.

## The template file is sacred: never edit it directly

The master template is `TC_TEMPLATE` (see SKILL.md, Project settings).

**Never write into the master.** Every ticket gets its own copy, named
`TC-<TICKET>.xlsx` (e.g. `TC-PROJ123.xlsx`), in `ARTIFACTS_DIR`, made with a
plain file copy of the current master *before* any edits. All new rows go in
that copy. Editing the master while someone has it open in Excel can corrupt
it and wipe historical rows.

## Before every write: check the file isn't open in Excel

Excel leaves a hidden lock file (`~$<name>.xlsx`) next to a file it has open:

```powershell
Get-ChildItem "<ARTIFACTS_DIR>" -Force | Where-Object { $_.Name -like '~$*' }
```

If one exists for the file you are about to touch, ask the user to close it,
then re-check. Don't retry blindly in a loop. A write while the file is open
fails with `PermissionError` (safe), but a write that lands just after the
user's own save can silently race it.

## After every write: verify from disk, not from memory

`openpyxl`'s in-memory object prints the values you just set even if the save
had a problem. After `wb.save(path)`, open a **fresh** `load_workbook(path)`
and read the cells back before saying it is done.

## Sheet structure (example tracker)

Adapt this table to your own template. Headers on row 5, data from row 6:

| Col | Field |
| --- | --- |
| A | Requirement Description |
| B | Complexity (dropdown: High/Medium/Low) |
| C | Test Case Priority (dropdown: High/Medium/Low) |
| D | Test Case No./ID |
| E | Prerequisite/Precondition |
| F | Test Case Description/Name |
| G | Test Data |
| H | Test Steps |
| I | Expected Result |
| J | Status (dropdown: Not Started/Passed/Failed/In Progress/Blocked/Out of Scope) |
| K–Q | Actual Result, Written/Created By, Remarks, Associated Defect, Test Start/End Date, Tested/Executed By |

- Dashboard `COUNTIF` formulas usually cover a fixed row range. Check it
  before adding many rows.
- Dropdowns are `DataValidation` objects scoped to a row range (e.g. `B6:C9`).
  Rows past that range need the `sqref` extended, or they lose the dropdown.
- New rows need their style copied cell by cell from an existing filled row
  (font, border, fill, alignment, number_format via `copy.copy()`) and a
  taller `row_dimensions[row].height` for multi-line steps.

## Naming convention: `TC-<ticket>-<seq>`

ID new test cases as `TC-<ticket>-<sequence>`, e.g. `TC-PROJ123-01`,
`TC-PROJ123-02`, tied to the ticket. Leave older rows in any previous scheme
exactly as they are.

## Breaking a ticket down into test cases

One condition per row, not one mega-row per ticket: separate rows for "old
content removed", "new content renders correctly" per breakpoint or layout
the ticket shows, and "existing functionality not regressed".

A check added from QA judgement rather than stated in the ticket
(accessibility, error and edge cases, SEO impact) is real coverage, but label
it visibly, e.g. prefix the name with `[Added QA check, not in ticket]`, so
the requester can tell ticket coverage from judgement calls at a glance.

## Build and execute with the shared tools

The ticket folder (`qa-reports/TC-<TICKET>/`, git-ignored) holds only data: `tc_rows.json` (the rows; `order` = the locale/env list; `unit` = Locale or Env; `summary`), `results.json` from the evidence run, and an optional `review.json` (per-row status or remark overrides).

- **Steps anyone can follow:** from opening the browser and typing the full URL, through every click and scroll, to the component named by what is on screen. Precondition: 1–2 short lines (browser + the site that must open).
- **Evidence run:** a one-time Playwright script shoots each component with `testcase/evidence-shot.cjs` (the component in its page, red box + label, page URL strip) and paints page-source checks as one table with `testcase/table-painter.cjs`.
- **Build:** `python .claude/skills/qa-agent/testcase/write_tc.py qa-reports/TC-<TICKET> <TC_TEMPLATE> <ARTIFACTS_DIR>/TC-<TICKET>.xlsx`. It renames `Module1` to `Test Cases` (Dashboard formulas follow), sets Written/Executed By to `qa-agent`, adds a blank `Final Validation By` column, and embeds every screenshot in one `Evidence` sheet so the workbook alone can be shared. It refuses to write while the file is open and archives the previous copy.

## Executing the test cases (evidence run)

Continuous: as soon as the rows are written and verified from disk, execute
every row on the environment the ticket names, without waiting for a go
(ask only if the ticket names no environment). The reviewer checks the rows
and the evidence together at hand-over. Run safely: read
[run-safely.md](run-safely.md) first; never submit an order, form or email
that reaches real people while executing.

1. **Expected look.** Save the ticket's mockup or screenshot attachments to
   `<ARTIFACTS_DIR>/TC-<TICKET>-evidence/jira-<n>.png`. They are the expected
   result for the rows that show UI; the row's Expected Result (I) is the rest.
2. **Run the steps.** A one-time Playwright script in `qa-reports/TC-<TICKET>/`
   (git-ignored, not a repo spec) follows each row's Test Steps (H) and takes a
   screenshot for each check that shows something on screen:
   `TC-<TICKET>-<seq>-<locale>-step<k>.png`, named after the step it proves.
   Viewport and browser per the row (default 1440 desktop; the ticket's mobile width when it shows mobile). Take component
   shots with `testcase/evidence-shot.cjs` (`EvidenceShot.capture(page, locator,
   file, label)`): the component in its page context, red box and label, a
   strip with the page URL, viewport and time (a caption, never a fake browser
   bar). A step that cannot be done (element missing, page error) is itself
   evidence: screenshot it and stop that row. A check with nothing on screen
   (metadata, HTTP status) gets one table shot for all locales, page value next
   to the expected value, painted with `testcase/table-painter.cjs`. A pass
   that rests on markup also gets such a table, because a picture can't show
   the tag. No test case goes into the workbook without evidence.
3. **Compare.** Put the last step's shot next to the ticket image and the
   Expected Result and say concretely what matches and what differs. When a
   copy spec gives the expected text, compare both ways: every spec line is on
   the page, AND nothing on the page is missing from the spec. Scope each check
   to the item it is about (one card, one accordion item), never the whole
   section. Dump the real page text before calling a copy difference a finding.
   For exact CSS parity use [figma-check.md](figma-check.md).
4. **Fill the row.**
   - **K Actual Result:** short enough to read without clicking: one line per
     failed locale with the reason, then one line each for the other outcomes,
     then a "click this cell" line linking to the TC's block on the Evidence
     sheet. A Blocked row's line carries the reason.
   - **Evidence sheet:** one block per TC and locale with the full "what was
     seen" text and that line's screenshots embedded. A line with no
     screenshot says why; "component not on this page" is a gap to close, not
     a pass. A ticket image is captioned "ticket screenshot (expected look, not
     a run)", never as a run step.
   - **J Status:** the outcome itself, `Passed` / `Failed` / `Blocked`, never
     left at `In Progress`. **M Remarks** says why, starting `qa-agent:`.
   - **Judgment calls go in the file, not in chat:** an item to confirm with
     the PO or a likely spec typo gets its status in J and the open point in M
     ("to confirm with the PO: ...").
   - **O/P dates:** the run's date. **Q Executed By:** `qa-agent`.
5. **Hand-over.** One line per row (ID, outcome, the screenshot to look at),
   the evidence folder path, and what could not be executed. The reviewer
   gives the final status and the feedback to dev / PO.

If the same ticket area keeps coming back, offer to turn the throwaway script
into a real spec ([new-page-automation.md](new-page-automation.md)).

## Reading the source ticket

- A screenshot or pasted ticket text is the simplest input. Work from it directly.
- A Jira URL on an authenticated instance cannot be read with a plain web
  fetch (it returns the login page). Say so instead of guessing, and ask for
  a screenshot or paste, or for the Atlassian connector to be authorized.
- Try the Atlassian connector first (a ToolSearch for `atlassian jira`). Only
  if no Jira tool loads, ask for the paste. Meanwhile, copy the template and
  read the latest sibling `TC-<KEY>.xlsx` so the rows match its style.
- Data rows go in the `Module1` sheet of the copy.
  The shared writer (above) renames that sheet to `Test Cases`.
- When the ticket points to a document or file ("this document", a linked doc, an attachment), ask where the file is before writing the test cases that depend on it; never guess its contents.
