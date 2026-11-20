> Use when: running or extending the PROD vs preview visual regression suite, adding pages to it, or reading its report.

# Visual compare: PROD vs preview, pixel by pixel

For every URL in a site's `url.json`, it screenshots the PROD page and the
same path on the preview origin, then compares the two pixel by pixel. Any
difference fails the run.

| Setting | Where |
|---|---|
| Spec | `tests/<Site>/visual-compare.spec.js` |
| URL list | `resources/<Site>/url.json` (PROD URLs only) |
| Preview origin | `PREVIEW_ORIGIN` in the spec (see SKILL.md, Project settings) |

## Run it

```powershell
npx playwright test tests/<Site>/visual-compare.spec.js
```

It runs headless, one URL at a time, with a fixed time budget per URL.

## The process, per URL

1. **Build the preview URL** by swapping the origin:
   `https://www.example.com/path/page` → `https://preview.example.com/path/page`
2. **Open both pages at once**, each in its own 1280×900 browser context.
3. **Get each page into a settled state** (`main/PagePreparer.js`), in this order:
   1. accept the cookie consent (on some sites the content does not exist
      until this is clicked)
   2. hide overlays that survive consent (chat widgets, GDPR modals)
   3. fast-forward animations and unstick sticky/fixed elements
   4. find what actually scrolls: the page or an inner div
   5. scroll to the bottom until the height stops growing, so lazy content
      loads; wait for images and fonts
   6. force-show scroll-reveal sections that are still transparent
   7. measure the page and check the footer rendered
4. **Screenshot.** One full-page shot. If the page is 16,000px or taller,
   scrolls inside a div, or the shot comes back short, scroll and stitch
   viewport tiles instead (Chromium cuts off very tall screenshots).
5. **Diff** the two PNGs with pixelmatch. If the sizes differ, the smaller
   one is padded, so a height change inflates the diff.
6. **Decide:**
   - `PASS`: differing pixels ≤ `diffThreshold` × PROD pixels. With
     `diffThreshold: 0`, only a pixel-perfect match passes.
   - `DIFF`: anything more.
   - `ERROR`: a page failed to load or capture; the message is in Remark.

After the last URL it writes one Excel report, and the test fails if any row
is `DIFF` or `ERROR`, listing each one in the failure message.

## Output

Everything goes under `reports/` (git-ignored):

| File | What |
|---|---|
| `<site>-visual-compare-<YYYY-MM-DD>.xlsx` | one row per URL: URLs, Status, Diff %, Diff Pixels, sizes, Height Delta, Remark, screenshot paths |
| `visual-screenshots/prod-<url>.png`, `preview-<url>.png` | the two captures |
| `visual-diffs/diff-<url>.png` | the differing pixels highlighted |

- Status is green for PASS, yellow for DIFF, red for ERROR.
- Check **Diff Pixels**, not just Diff %: the percentage is rounded to two
  decimals, so a few differing pixels still show `0.00`.
- PNGs are overwritten on every run. The xlsx is one per site per day; if it
  is open in Excel, the new one is written beside it with a timestamp.

## Adding pages or a site

- **More pages:** add the URLs to the site's `url.json`. No code change.
- **A new site:** add `resources/<Site>/url.json`, copy an existing spec, and
  change `PREVIEW_ORIGIN`, `projectName` and the `url.json` path.
- **Before editing `PagePreparer.js`:** other checkers (CTA links, text
  compare) may use it too, so a change there affects those suites as well
  ([shared-change-regression.md](shared-change-regression.md)).
