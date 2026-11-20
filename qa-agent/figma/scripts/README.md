# scripts/

Two small tools. The model orchestrates; these do the measuring and the arithmetic.

## One-time setup

```powershell
cd ".claude\skills\qa-agent\figma\scripts"   # from the repo root
npm install
npx playwright install chromium
```

## inspect.mjs — read reality

```powershell
node inspect.mjs --mapping ..\mappings\contact.json --out live.json --screenshot live.png
```

| Flag | Default | Purpose |
|---|---|---|
| `--mapping` | *required* | Mapping file listing `{ id, figmaLayer, selector }` per element |
| `--url` | mapping's `url` | Override the page under test (staging vs prod) |
| `--viewport` | mapping's `viewport`, else 1440 | Viewport width in px |
| `--height` | 900 | Viewport height |
| `--wait` | 400 | Extra settle time in ms after network idle |
| `--out` | `live.json` | Where to write captured styles |
| `--screenshot` | — | Page screenshot path; also writes `element-<id>.png` per element |
| `--full-page` | off | Full-page rather than viewport screenshot |
| `--auth-storage` | — | Playwright storage-state JSON for pages behind a login |

Also reports `document.fonts.status`, page errors, HTTP status, and the scrollbar width — check these
before trusting typography or width findings.

### Pages behind a login

Capture a storage state once, by hand:

```powershell
npx playwright open --save-storage=storage.json https://staging.example.com/login
# log in in the browser window, then close it
node inspect.mjs --mapping ..\mappings\contact.json --auth-storage storage.json --out live.json
```

`storage.json` holds live session cookies — keep it out of version control and delete it when the
engagement is done.

## compare.mjs — do the diff

```powershell
node compare.mjs --figma figma.json --live live.json --out diff.json --md diff.md
```

| Flag | Default | Purpose |
|---|---|---|
| `--figma` | *required* | Expected styles per element, extracted from Figma |
| `--live` | *required* | Output of `inspect.mjs` |
| `--out` | — | Structured `diff.json` |
| `--md` | — | Ready-to-paste markdown tables |
| `--tolerance` | `1` | Length tolerance in px |

Normalizes colors to hex, lengths to px numbers, font weight names to numbers, and font families to
the first family — then compares. Verdicts: `PASS`, `NEAR` (within tolerance), `FAIL`, `SKIP`
(not comparable, e.g. Figma `AUTO` line height).

**Exits 1 when there is any FAIL or missing element**, so the same command can gate CI later without
being rewritten.

## figma.json shape

Written by the model from `get_design_context`. Only include properties Figma actually specifies:

```json
{
  "node": "1:1496",
  "elements": {
    "hero-title": {
      "figmaLayer": "Hero/Heading",
      "styles": { "font-size": "40px", "font-weight": "Bold", "color": "#1b4d8f" }
    }
  }
}
```

Keys under `styles` are CSS property names. `font-weight` accepts Figma style names (`Bold`,
`SemiBold`) — the comparator maps them to numbers.
