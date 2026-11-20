> Use when: design-vs-implementation QA, a live or staging page against its Figma design (computed CSS diff, not pixel diff), optionally verifying a ticket's acceptance criteria. Trigger on "validate: figma = <link or SVG path>, environment = <url>", "compare Figma to staging", "CSS parity", "FE QA of the footer".

# Figma vs environment

Paths: run everything from the repo root, with

```powershell
$F = ".claude\skills\qa-agent\figma"     # scripts/, mappings/, templates/
```

Working files go to `qa-reports\<KEY>\` (git-ignored, regenerated per run).
**The deliverable is not there.** It is one `.xlsx` in `ARTIFACTS_DIR`
(see Deliverable).

| Source | Tool | Produces |
|---|---|---|
| Design | Figma MCP (`get_design_context`, `get_screenshot`), or the user's SVG export | `figma.json` |
| Requirements | Atlassian MCP (Jira), or a screenshot/paste of the ticket | AC checklist |
| Reality | `$F\scripts\inspect.mjs` (Playwright) | `live.json` |

The comparison is **deterministic**: `compare.mjs` does it, not the model.
Never eyeball numbers and declare parity.

## Preflight (stop on first failure)

1. **MCP.** Figma must be connected; Atlassian only if a ticket key is given
   (not authenticated → ask the user to authorize the connector, fall back to
   a ticket screenshot). Don't scrape Figma or Jira over HTTP.
2. **Playwright deps.** If `$F\scripts\node_modules` is missing:
   `cd $F\scripts; npm install; npx playwright install chromium`.
3. **Figma call limits.** View-only seats can have a tight call limit. Spend
   calls on `get_design_context` / `get_screenshot`, not exploration. If it
   says "nothing selected", the link is a page, not a frame → ask for
   right-click frame → Copy link to selection. Don't search for it.

**Figma blocked → SVG fallback.** Ask the user to export the whole FRAME as
SVG and give a **file path**, not a chat attachment (large exports can
overflow the context). Text usually arrives outlined, so measure with
`python -I $F\templates\measure_svg.py <export.svg> <out.json>` (rect size,
radius, fill; glyph boxes → cap height ≈ font size, baseline pitch ≈ line
height, case). Render it for the Figma rows with
`node $F\scripts\render-figma-svg.mjs <export.svg> <out.png> <width> <height>`.
Mark derived values as *derived*.

## Workflow

1. **AC** → `qa-reports\<KEY>\ac.md`, one verifiable assertion per line;
   not verifiable from the UI → keep it, mark `MANUAL`. No ticket →
   design-parity only, say so, skip AC coverage.
2. **Mapping**: reuse `$F\mappings\<page>.json` if it exists, else propose
   one (8 to 20 elements the ticket touches, `{ id, figmaLayer, selector }`,
   start from `example.contact.json`) and **show it to the user before comparing**.
3. **Design truth** → `figma.json`, only properties Figma specifies. Read
   [figma-comparison-rules.md](figma-comparison-rules.md) first. Save `design.png`.
4. **Reality**
   `node $F\scripts\inspect.mjs --mapping $F\mappings\<page>.json --viewport 1440 --out qa-reports\<KEY>\live.json --screenshot qa-reports\<KEY>\live.png`
   (`--wait`, `--auth-storage`: see `$F\scripts\README.md`). `found: false`
   is itself a finding. Use a cookie-rejected full-page capture for crops.
5. **Compare**
   `node $F\scripts\compare.mjs --figma qa-reports\<KEY>\figma.json --live qa-reports\<KEY>\live.json --out qa-reports\<KEY>\diff.json --md qa-reports\<KEY>\diff.md`
   PASS / NEAR (±1px) / FAIL / SKIP. Don't widen the tolerance to look clean.
6. **AC on the live page**: interaction checks with evidence (text seen, URL landed on).
7. **Deliverable** (below), then a short summary in chat.

Outlined text has no CSS: strip photos and gradient backgrounds with
`python -I $F\templates\make_text_only_svg.py <export.svg> <out.svg>`, then
measure the glyph boxes with `measure_svg.py` and compare them to the live
element boxes from `inspect.mjs`. For mobile, run `inspect.mjs` at
`--viewport 375`; to prove a fix, inject the proposed CSS in a small probe
script and re-measure.

## Deliverable: ALWAYS an .xlsx in ARTIFACTS_DIR

One file: `<ARTIFACTS_DIR>\FE-QA-<Site>-<Component>.xlsx`. Not a chat reply,
not report.md plus loose screenshots.

- **Findings** sheet: one 3-row block per finding. Row 1 ENV (live) crop,
  row 2 Figma crop, row 3 feedback (what differs, expected vs actual,
  selector + Figma layer, remarks). Severity High/Medium/Low.
- **Summary** sheet: environment, viewport, Figma source, ticket, verdict,
  findings index, severity counts, what matches, not covered.
- **CSS Diff** sheet: the raw `diff.json` rows.
- Build it with the generic builder: write `qa-reports\<KEY>\findings.json`
  (shape: `$F\templates\findings.example.json`, crops under `evidence\`),
  then `python -I $F\templates\build_findings_xlsx.py qa-reports\<KEY> "<ARTIFACTS_DIR>\FE-QA-<Site>-<Component>.xlsx"`.
  It reads `diff.json` from the same folder when present.
- **Produce it even when Figma is blocked**: live-only findings, Figma rows
  say `Pending: <reason> (node X)` via `figmaPending`, verdict PARTIAL. Even
  if the live page can't be checked, a Summary-only workbook saying what blocked it.
- **File open in Excel** (`~$` lock / PermissionError) → save as `-v2.xlsx`
  and say so. Never leave it only in `qa-reports\`.
- Fold in anything FE-visible noticed on the way (copy mismatches, empty elements).

Report content rules: [figma-report-template.md](figma-report-template.md):
verdict first, every FAIL with expected / actual / where, sorted by severity,
environment + viewport + browser + time stated, not covered listed.

## Honest limits (say them in the Summary)

Static styles only (no hover/focus unless scripted) · one viewport per run ·
no pixel diff by design (icons, images, font rendering not caught) · fonts that
fail to load cascade into fake typography FAILs, so check `document.fonts.status` first.
