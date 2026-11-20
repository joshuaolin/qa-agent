# The generic Checker engine

Used for page-level checks that run over a flat list of URLs: 404 status,
SEO title/description, broken CTA links, inlinks, text compare, visual
compare. Each site gets a folder under `tests/<Site>/` of the same shape.

## The pattern, end to end

```
resources/<Site>/url.json        <- { "urls": [ "...", "...", ... ] }
main/<Thing>Checker.js           <- extends BaseChecker, does the real work
tests/<Site>/<thing>.spec.js     <- 15-25 lines, always the same shape
```

Every spec file looks like this:

```js
const { test, expect } = require('@playwright/test');
const UrlStatusChecker = require('../../main/UrlStatusChecker');
const testData = require('../../resources/MySite/url.json');
require('../../main/Hooks');

test.describe('404 Status Check', () => {
  test('Check all URLs for 404 errors and generate report', async ({ request }) => {
    const checker = new UrlStatusChecker({
      request,
      projectName: 'my-site',
      outputDir: './reports',
      filePrefix: '404-test-report',
      concurrency: 5,
      timeout: 20000
    });

    const { results } = await checker.run(testData.urls);
    const failures = results.filter(result => result.result === 'FAIL');
    expect(failures.length, `Found ${failures.length} failing URLs`).toBe(0);
  });
});
```

`SeoChecker`, `CtaLinkChecker`, `InlinkChecker`, `TextCompareChecker` and
`VisualCompareChecker` follow the same shape. Each extends
`main/BaseChecker.js` (Excel report plumbing: sheet columns, row styling,
`saveReport()`) and exposes a `.run(urls)` that returns `{ results, reportPath }`.

## Adding a page to an EXISTING check

This is the common case and it is a **data change only**:

1. Open the matching `resources/<Site>/url.json`.
2. Add the URL(s) to the `urls` array. Dedupe, and keep the existing order.
   Crawler dumps are often messy: requote into a clean JSON array rather
   than hand-editing around whatever formatting the dump arrived in.
3. Do not touch `main/<Thing>Checker.js` or the spec file. If you want to,
   you are probably handling a site-specific quirk (see "When you actually
   need new code").
4. Run the one suite you changed, not the whole repo:
   `npx playwright test tests/<Site>/<thing>.spec.js`
5. Report what the new URLs actually returned (title/description text,
   status code, whatever the checker reports), not just "ran successfully".

## Adding a NEW site folder for an existing kind of check

1. Create `resources/<NewSite>/url.json` with the same `{ "urls": [...] }` shape.
2. Create `tests/<NewSite>/<thing>.spec.js` by copying the closest existing
   spec and changing only: `projectName`, the preview origin (if the checker
   takes one), and the `require(...resources/<NewSite>/url.json)` path.
3. Do not write a new Checker class. The point of `BaseChecker` is that the
   per-site spec is boilerplate and the logic lives once, in `main/`.

## When you actually need new code

Only touch `main/<Thing>Checker.js` when the new site or page needs the
checker to do something no existing option covers (a different report
column, a different comparison rule). Even then:

- Keep the new behaviour **opt-in and generic**: a constructor option, not a
  hardcoded branch for one site's name.
- `BaseChecker` is shared by every suite built on it. Show a before/after
  sample from at least one other site that uses the same checker class
  before calling the change done.

## The url.json reformat chore

A crawler tool dumps URLs into `url.json` in a broken shape (unquoted lines,
trailing commas, duplicates, not valid JSON). Fixing it is a one-file,
one-line-report chore: requote into a proper `{ "urls": [...] }` array,
dedupe, keep the original order. It needs the shared-code pass only if the
fix also touches a Checker class.
