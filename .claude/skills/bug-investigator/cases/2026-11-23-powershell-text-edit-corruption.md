---
case: powershell-text-edit-corruption
date: 2026-11-23
area: coding-partner / editing code and data files on Windows
type: mistake
---

Nangyari:  TC-AAV2266: three self-inflicted breaks while patching files with PowerShell 5.1. (1) `Get-Content` without -Encoding read write_tc.py as ANSI, so "→" and "…" were saved back as "â†’" / "â€¦" mojibake and showed up in column K. (2) `-replace '"Locale"','"Env"'` is case-insensitive, so it also rewrote every `r["locale"]` key and the writer crashed with KeyError 'Env'. (3) `Set-Content -Encoding utf8` wrote a BOM into review.json, and `json.loads` refused it. Each one was caught on the next run, before hand-over.
Dahilan:   PowerShell 5.1 defaults: reads use the ANSI codepage, `-replace` ignores case, and `utf8` writes a BOM.
Ayos:      Re-encoded write_tc.py in Python, restored the keys with `-creplace`, and re-saved review.json without a BOM. The shared writer (qa-agent testcase/write_tc.py) now reads JSON with utf-8-sig.
Rule:      Change code or data files with the Edit/Write tools or Python using an explicit encoding. Never round-trip a file through Get-Content / -replace / Set-Content. If PowerShell is unavoidable, read with [IO.File]::ReadAllText (or Get-Content -Raw -Encoding utf8), replace with -creplace, write with [IO.File]::WriteAllText and UTF8Encoding($false).
Promoted:  coding-partner references/code-style.md "Editing files from Windows PowerShell" (the owner's "update lahat lahat", 2026-11-23; reviewer-agent ✗ 5 → read side added to the rule, then synced)
