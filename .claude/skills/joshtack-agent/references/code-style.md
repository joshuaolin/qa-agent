> Use when: writing, refactoring, migrating or reviewing any code or script.

# Code style

## OOP, always

He asks for "OOP approach" and "linisin mo" every time code arrives, and the
same holds for every script, one-offs included.

- **One class per concern.** Engine and logic classes in `main/<Suite>/` (or
  `src/`), page objects and locators in `pom/<Suite>/`, per-target values in
  `resources/<Suite>/`, and an entry point (spec, CLI) that only loops the
  config and calls the engine.
- **One-off, probe and builder scripts** get a `CONFIG` data object at the top,
  one class, and a single-line entry point:
  ```js
  const CONFIG = { url: 'https://…', viewport: { width: 375, height: 812 }, outDir: 'out' };
  class FooterProbe {
    constructor(config) { this.config = config; }
    async run() { … }
  }
  new FooterProbe(CONFIG).run();
  ```
- **Reuse before you write.** Search the repo for an existing base class or
  helper (BaseChecker, BasePanel, ActionDriver, …) and extend it. A second
  copy of a helper is the drift he consolidated away.
- **Consolidate.** N near-identical scripts become one engine plus N data
  entries. N locales, sites or URLs go in one data file and one report,
  "consolidated in 1 file". Never one file per item.
- **Per-target quirks are options, not branches.** Name the option for the
  difference (`opensOrderFormInPopup`), never for the site (`if (site === 'cgv')`).
- **Building ahead is fine.** He adds helpers before they're needed ("add
  hover sa ActionDriver kahit di pa gagamitin"). Put them in the shared class,
  following its existing method shape.

## No comments

He has asked four times ("para hindi mukang AI gumawa", "di mukang vibe coded").

- Code you create or change has **no** `//`, `/* */`, `#`, JSDoc or docstrings.
  That includes `// @ts-check` banners and section dividers.
- Make names do the work: `retryBackoffMs`, `assertAccountAccepted()`,
  `DANGEROUS_CLICK_TEXT`.
- Knowledge that would have been a comment (a site quirk, why a wait exists,
  a past failure) goes into the README or the project's reference docs.
  Don't lose it, move it.
- **"Pa remove ng comments" on existing code:** strip comments only. Change
  no logic, whitespace inside strings, or `eslint`/`ts` directives that alter
  behaviour. Then prove it still parses and runs: `node --check` each file,
  plus the project's list or validate command. Move any comment that
  explains a real failure into the README first, and tell him which ones.

## Invisible characters

The Edit and Write tools turn a typed unicode escape (BOM, zero-width space,
NBSP) into the real invisible character. It runs, tests pass, and a
formatter later strips it (case `edit-tool-wrote-literal-bom`).

- In code, build it from its code point: `String.fromCharCode(0xfeff)`, or
  patch the escape in with a byte-level script.
- After touching one, check the bytes (`EF BB BF` for U+FEFF), not just
  that it runs.

## Editing files from Windows PowerShell

PowerShell 5.1 corrupts text it round-trips (case
`powershell-text-edit-corruption`). `Get-Content` reads ANSI, so `→` comes
back as `â†’`. `-replace` ignores case, so `"Locale"` also hits `"locale"`.
`Set-Content -Encoding utf8` adds a BOM that `json.loads` rejects.

- Change code and data files with the Edit/Write tools, or with Python using
  an explicit encoding.
- If PowerShell is unavoidable, cover all three: read with
  `[IO.File]::ReadAllText(path)` (or `Get-Content -Raw -Encoding utf8`),
  replace with `-creplace`, and write with
  `[IO.File]::WriteAllText(path, text, [Text.UTF8Encoding]::new($false))`.
- Read JSON with `utf-8-sig` so a stray BOM can't break a run.

## Shape of a finished change

- Data change only → done after one live run of that item.
- Shared code touched → every consumer re-verified (see [safety.md](safety.md)).
- Output shape changed (Excel columns, email body, report layout) → show a
  sample or 2–3 options **before** building it. He picks.
