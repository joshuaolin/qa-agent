> Use when: changing an existing project, cleaning up, deleting, moving or renaming files, or running anything.

# Don't break it

"ingat para di mo masira" / "make sure na hindi masira yung entire file" is
the standing instruction.

## Before you change anything

1. **Baseline.** Run the project's cheapest full check first and note the
   result: a validate script, `npx playwright test --list` (test count), a
   build, or `node --check`. Run it again after. The two must match.
2. **Blast radius.** Grep who imports the file you're touching. If more
   than one site, flow or script uses it, every one of them gets re-verified,
   not a sample.
3. **Running processes.** Check that nothing scheduled is running before
   deleting outputs or restarting things:
   `Get-CimInstance Win32_Process -Filter "Name='node.exe'" | select ProcessId, CommandLine`.

## Side effects: never while testing

- **Email.** Find what sends mail before running anything: grep
  `nodemailer|smtp|sendMail|MailRelay|Mailer`, then trace which command
  reaches it (teardowns, post-hooks, "report" scripts). Run around it, e.g.
  `--no-deps` for Playwright teardowns, `--list`, or a render-only path. If
  there's no way around it, ask first.
- **Live systems.** No real orders, submissions, form posts, or production
  writes. Respect existing guards, and never weaken them to make a test pass.

## Copy, don't mutate

- Masters and templates (e.g. `TC.xlsx`) → copy first and edit the copy.
- Someone else's working setup or a handover ("papasa ko sa nag papaturo")
  → a fresh folder next to it, not edits in place.
- Excel files: check for a `~$<name>` lock before writing. If it's open,
  save as `-v2`. Read the file back from disk after saving.

## Delete and cleanup

- "Unused for a long time" = not imported, not referenced by config, scripts
  or schedulers, and untouched for weeks. Check all three before calling it dead.
- Generated output (reports, test-results, allure, caches) → delete.
- Source, docs, evidence, one-off scripts → move to
  `<project> - archive <date>\`, especially with no git commits, where a
  delete is permanent. Tell him the path and that he can delete it later.
- Duplicates of a repo that exists elsewhere → delete, and say where the original is.

## Secrets

Passwords and tokens go in `.env`, and their key names go in `.env.example`
with no values. Never repeat a credential he pastes, not in a reply, a log,
a commit or a doc. Say "updated in `.env`".

## Report

What changed, the before/after check result, and anything you deliberately
didn't touch and why. If something failed or was skipped, say so plainly.
