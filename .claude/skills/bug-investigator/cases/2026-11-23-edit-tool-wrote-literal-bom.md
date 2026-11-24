---
case: edit-tool-wrote-literal-bom
date: 2026-11-23
area: coding-partner / any code edit
type: mistake
---

Nangyari:  The BOM fix in bug-investigator-hook.mjs was typed as `/^\uFEFF/`, but the file got a literal invisible U+FEFF inside the regex. It worked, so nobody saw it; reviewer-agent caught it from the bytes (`2F-5E-EF-BB-BF-2F`).
Dahilan:   The Edit and Write tools both turn the `\uFEFF` escape into the real character. Invisible characters in source survive tests and vanish under a formatter.
Ayos:      Rewrote it with a byte-level patch script; verified no literal U+FEFF left and the pipe tests still pass. Nangyari ulit in this very case file (reviewer-agent round 2); fixed with a byte-level escaper and a scan of every file touched that day.
Rule:      Write invisible or special characters as escapes, and after editing one, check the bytes, not just that it runs.
Promoted:  coding-partner references/code-style.md "Invisible characters" (already in the source and public copy; bookkeeping fixed 2026-11-23 per reviewer-agent)
