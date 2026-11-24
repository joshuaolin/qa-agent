---
case: stale-commit-message-file
date: 2026-11-23
area: coding-partner / commit hygiene (qa-agent-public)
type: mistake
---

Nangyari:  qa-agent-public commit 0e78881 (docx_edit.py + team-doc-update.md, the right two files) was pushed with an old message, "Add conan-agent and x-agent, update joshtack-agent to v1.1".
Dahilan:   The new message was written to scratchpad\commit-msg.txt, a name already used by an earlier commit. The Write tool refused (file not read yet), but `git add; git commit -F <file>; git push` ran in the same call, so git took the stale file and pushed it before anyone read the error.
Ayos:      Reported to the owner; fixing the message needs an amend + force-push to the owner's public repo, which waits on the owner's go.
Rule:      Write each commit message to a new, unique file and read it back (or `git log -1` before push) in a separate step; never chain commit and push in the same command as the step that writes the message.
Promoted:  not yet (candidate for coding-partner commit hygiene, pending the owner's go)
