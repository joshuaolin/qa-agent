> Use when: adding, fixing or extending URL coverage for the page-level checker suites (404 status, SEO title/description, CTA links, inlinks, text compare, visual compare), or adding a new site of the same shape. Includes the recurring url.json reformat chore (a crawler dump pasted as one broken string). Trigger on "add these URLs", "cover this page for 404s", "fix the url.json", "ayusin mo yung url.json", "SEO check for <site>", "new site for visual compare".

# Checker suites: URLs and sites

Playbook: [checker-pattern.md](checker-pattern.md).
Shape: `resources/<Site>/url.json` (`{ "urls": [...] }`) → `main/<Thing>Checker.js`
(extends `BaseChecker`) → `tests/<Site>/<thing>.spec.js` (boilerplate loop).

## Which job is it?

| Ask | Do | Effort |
| --- | --- | --- |
| url.json arrived broken (crawler dump) | regex out `https?://[^\s"\\]+`, dedupe keeping first, re-emit as a JSON array, `ConvertFrom-Json` to verify; back up the old file to `%TEMP%` first | one-line report |
| Add URLs to an existing site | append to that `url.json`, dedupe, keep order; run that one spec | short report of what the new URLs returned |
| Existing check for a new site | new `resources/<Site>/url.json` + copy the closest spec, change only `projectName`, preview origin, require path | run the new spec |
| Checker needs new behaviour | constructor option, generic and opt-in, never a branch on a site name | [shared-change-regression.md](shared-change-regression.md) (every suite on that checker) |

Never write a new Checker class for a new site.

## Run

`npx playwright test tests/<Site>/<thing>.spec.js`: no email, no transactions
(see [run-safely.md](run-safely.md) for everything else). The spec asserts zero failures,
so a green run already proves that. Report what the new URLs actually
returned (status, title/description, diff counts) and the Excel path in `reports/`.
