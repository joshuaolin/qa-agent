> Use when: updating or writing a team-facing Word document about the framework, the agents or a QA process ("update mo tong file", "i-update yung doc based sa current", a write-up for the team or leads).

# Team doc update

The reader is the QA team and leads, not the author. Write in English, in the author's
first person ("I"), short and factual. Start the hand-over with one line
naming that audience.

Tools live in `docs-kit/` (run everything from the repo root):

| File | Job |
| --- | --- |
| `scripts/dump_docx.py <docx>` | Every paragraph with its style, every table row, `[IMG]` markers |
| `scripts/docx_body.py <docx> <i…>` | Raw XML of body elements, to pick templates |
| `scripts/check_docx.py <docx>` | XML parses, image refs resolve, unique `docPr` ids, png type, no literal U+FEFF |
| `scripts/render_diagrams.cjs <workdir>` | Renders every `.card[id]` in `<workdir>\diagrams.html` to `<id>.png` with the repo's Playwright |
| `scripts/docx_edit.py <config.json>` | The engine: clones the doc's own paragraphs and tables and applies the operations listed in the JSON. Paths in the JSON are relative to it |
| `templates/edit_config.example.json` | A real doc update as data: `templates` (element indices to clone, picked with `docx_body.py`) and `operations` |
| `templates/diagrams.example.html` | Plain diagram style: light card, teal heading, boxes and arrows, status tags. No robot or person figures |

Operations (`docx_edit.py`), each found by exact paragraph text:
`set_text` (`at`, or `after` + `offset`; optional `style`), `append_text`,
`insert` (`before`/`after`, `items`), `insert_after_image`, `replace_image`
(optional `nth`: the n-th image after the anchor, default 1),
`append_rows` (first table after a heading), `replace_row` (`after`, `key` =
the row's first cell, `values`), `insert_row` (`after`, `before` = the first
cell of the row it goes above, `values`), `replace_until_end` (from a
heading to the end of the doc), `remove` (`from`, optional `until`, which is
kept), `remove_section` / `move_section` (`heading`, and `before` for the
move; a section runs to the next paragraph with the heading's own style,
and a heading with no style stops the engine). An item is `{style, text}`,
`{style, rich}`, `{image, name}`, `{table, rows}` or `{raw}`; add
`"list": <numId>` to a text item to make it a bullet. A table cell value
can be a list of strings: each becomes a bullet paragraph in that cell, using
the config's `list_num`. The numId must be a bullet list that already
exists in the doc's `word/numbering.xml`. A mark can also be a literal
`{"rpr": "<w:rPr>…</w:rPr>"}` when no paragraph in the doc has that look.
Cloned paragraphs that would repeat a `w14:paraId` lose the repeat. `rich` keeps inline formatting:
`**bold**` and `` `code` `` take their run properties from the config's
`marks` (`{"bold": {"template": "<key>", "run": <i>}, "code": {...}}`, the
i-th run of a template paragraph that already has that look). A code span
inside bold is not handled: close the bold first (`**Needs** `x``). Tags with attributes (Word's `w:rsidR`) are
handled. Not handled: nested tables, body-level `<w:sdt>` (a TOC) or
bookmarks between paragraphs (dropped on write), and template cells with
several runs (only the first run's text is replaced). An empty template
cell (no `<w:t>`) stops the engine: pick a filled row as the template.
`replace_row` on a row that has a blank cell stops too: type something in
that cell in Word first. A row must have
exactly as many values as the template row has cells, or the engine stops.

## Steps

1. **Find the file and never touch it.** Newest match in the folder the owner
   names. Work in `qa-reports\<doc-name>\` (git-ignored): copy it in as
   `src.docx`. The result is a new `<name>-v<N>.docx` next to the original.
2. **Read it before writing.** `dump_docx.py` for the structure, view each
   image in `word/media/`, then list what is now out of date against the
   real system (skills, agents, hooks, ledgers, repo).
3. **Clone, don't restyle.** Don't assume python-docx or LibreOffice are installed.
   Write `<workdir>\config.json` (start from `edit_config.example.json`):
   pick the doc's own heading, body, note, step, image and table elements
   as `templates` with `docx_body.py`, then list the `operations`. No new
   code per doc; a change the operations can't express goes into
   `docx_edit.py` as a new op. Run Python with `-B -I` so no `__pycache__`
   lands in the skill folder.
4. **Diagrams over words.** The leads skim (asked on 2026-11-23: "ang daming
   words ... use table tapos bullet bullet sa loob"). Each section is one
   short line plus a diagram; add a diagram whenever a section
   explains a flow or a set of parts. Linear when the real flow is a
   line; a main lane plus side loops when parts are called on demand or
   feed back (e.g. an agents chart: the request lane, an on-demand helper
   above, the casebook below). Anything more goes in a table with
   short bullets inside the cells, never in paragraphs.
   **Diagrams in the same style.** Copy `diagrams.example.html` to the work
   folder as `diagrams.html`, one `.card` per diagram, render, then *look* at
   each PNG and fix labels that wrap. Replace an outdated image; don't
   leave it describing the old flow. Plain diagrams only: boxes, arrows
   and labels, no cartoon figures (the leads asked for this on
   2026-11-23). When the leads give notes, put them in a diagram as
   written, with the real status of each item.
5. **Every claim matches the system.**
   - Who approves what: reviewer-agent reviews, the owner gives the go.
   - What teammates actually get: anything only on one person's machine says
     "on my setup" / "(my machine)"; check `qa-agent-public` before
     saying something ships.
   - Hooks and automation described as what the code does, not more.
   - Numbers come from a ledger, a log or a run.
6. **Check the file.** `check_docx.py` on the output. Word COM export to
   PDF may be rejected (`RPC_E_CALL_REJECTED`); if so, say the pages were
   not rendered and ask the owner to scroll it once. Close any Word process you
   started.
7. **Copy `<workdir>\out.docx` to `<name>-v<N>.docx` next to the original**, then run
   `check_docx.py` on that copy. Locked target (`~$` file or an open
   handle) → the next `-v<N>`, and say so; never overwrite a file someone has open.
8. **reviewer-agent before hand-over**, max 2 rounds, then a ledger row.
9. **Hand-over:** the path, a "what changed" table, reviewer-agent's verdict, and
   what was not checked.

Unicode in the config JSON (curly quotes, dashes) is fine as typed characters;
invisible ones are not. See coding-partner code-style, "Invisible
characters".
