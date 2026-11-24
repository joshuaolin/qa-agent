---
case: word-com-left-running
date: 2026-11-24
area: qa-agent / team docs (Word COM export)
type: mistake
---

Nangyari:  The v19 PDF export via Word COM failed with RPC_E_CALL_REJECTED. The hidden WINWORD it started (pid 26216, `/Automation -Embedding`) kept running and locked Downloads v19, so the fixed v19 could not be copied over. Closing it was denied by the permission classifier, so the owner has to end it.
Dahilan:   The `finally { $word.Quit() }` ran against the same busy COM server and was rejected too. No `Get-Process WINWORD` check followed, so the leftover was found only when the copy failed.
Ayos:      Reported to the owner with the PID and the Task Manager step; the fixed build waits in out.docx.
Rule:      After any Word COM attempt, check `Get-Process WINWORD` for an instance started at that minute with no window. If one is left, tell the owner its PID before going on, and copy outputs to Downloads before trying the export.
Promoted:  not yet (candidate for qa-agent team-doc-update.md step 6, pending the owner's go)
