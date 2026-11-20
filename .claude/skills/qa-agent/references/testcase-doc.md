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

## Reading the source ticket

- A screenshot or pasted ticket text is the simplest input. Work from it directly.
- A Jira URL on an authenticated instance cannot be read with a plain web
  fetch (it returns the login page). Say so instead of guessing, and ask for
  a screenshot or paste, or for the Atlassian connector to be authorized.
- Try the Atlassian connector first (a ToolSearch for `atlassian jira`). Only
  if no Jira tool loads, ask for the paste. Meanwhile, copy the template and
  read the latest sibling `TC-<KEY>.xlsx` so the rows match its style.
- Data rows go in the `Module1` sheet of the copy.
