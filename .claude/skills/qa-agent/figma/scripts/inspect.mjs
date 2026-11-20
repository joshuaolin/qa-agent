#!/usr/bin/env node
/**
 * inspect.mjs — capture computed styles for mapped elements on a live page.
 *
 *   node inspect.mjs --mapping ../mappings/contact.json --out live.json
 *                    [--viewport 1440] [--height 900] [--wait 500]
 *                    [--screenshot live.png] [--auth-storage storage.json]
 *                    [--url https://override] [--full-page]
 */
import { chromium } from 'playwright';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

// Properties worth comparing against a design. Anything not here is noise for design QA.
const PROPS = [
  'color', 'background-color', 'background-image', 'opacity',
  'font-family', 'font-size', 'font-weight', 'font-style',
  'line-height', 'letter-spacing', 'text-align', 'text-transform', 'text-decoration-line',
  'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
  'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
  'gap', 'row-gap', 'column-gap',
  'width', 'height', 'min-height', 'max-width',
  'border-top-left-radius', 'border-top-right-radius',
  'border-bottom-right-radius', 'border-bottom-left-radius',
  'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width',
  'border-top-color', 'border-top-style',
  'box-shadow',
  'display', 'flex-direction', 'justify-content', 'align-items', 'position', 'visibility',
];

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) continue;
    const key = a.slice(2);
    const next = argv[i + 1];
    if (next === undefined || next.startsWith('--')) out[key] = true;
    else { out[key] = next; i++; }
  }
  return out;
}

const args = parseArgs(process.argv.slice(2));
if (!args.mapping) {
  console.error('inspect.mjs: --mapping <file> is required');
  process.exit(2);
}

const mapping = JSON.parse(await readFile(args.mapping, 'utf8'));
const url = args.url || mapping.url;
if (!url) {
  console.error('inspect.mjs: no URL — pass --url or set "url" in the mapping file');
  process.exit(2);
}

const width = Number(args.viewport || mapping.viewport || 1440);
const height = Number(args.height || 900);
const waitMs = Number(args.wait || 400);
const outPath = args.out || 'live.json';

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width, height },
  deviceScaleFactor: 1,
  storageState: args['auth-storage'] ? args['auth-storage'] : undefined,
});
const page = await context.newPage();

const consoleErrors = [];
page.on('pageerror', (e) => consoleErrors.push(String(e.message).slice(0, 300)));

let status = null;
try {
  const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
  status = resp ? resp.status() : null;
} catch (err) {
  // networkidle can legitimately time out on pages with long-polling; fall back to DOM ready.
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
}
await page.waitForTimeout(waitMs);

// Fonts that never load produce a cascade of bogus typography failures. Surface it once, up front.
const fontStatus = await page.evaluate(async () => {
  try { await document.fonts.ready; return document.fonts.status; } catch { return 'unknown'; }
});

const layoutWidth = await page.evaluate(() => document.documentElement.clientWidth);

const results = {};
for (const el of mapping.elements || []) {
  const { id, selector, figmaLayer } = el;
  const record = { selector, figmaLayer, found: false };
  try {
    const locator = page.locator(selector).first();
    const count = await page.locator(selector).count();
    if (count === 0) {
      record.note = 'selector matched 0 elements';
      results[id] = record;
      continue;
    }
    record.matchCount = count;
    record.found = true;
    if (count > 1) record.note = `selector matched ${count} elements; using the first`;

    record.visible = await locator.isVisible();
    const box = await locator.boundingBox();
    record.box = box ? {
      x: round(box.x), y: round(box.y), width: round(box.width), height: round(box.height),
    } : null;

    record.text = (await locator.textContent() || '').trim().slice(0, 120) || null;

    record.styles = await locator.evaluate((node, props) => {
      const cs = getComputedStyle(node);
      const out = {};
      for (const p of props) out[p] = cs.getPropertyValue(p).trim();
      return out;
    }, PROPS);

    if (args.screenshot) {
      const dir = path.dirname(args.screenshot);
      const shot = path.join(dir, `element-${id}.png`);
      try { await locator.screenshot({ path: shot }); record.screenshot = path.basename(shot); }
      catch { /* off-screen or zero-size element; the page screenshot still covers it */ }
    }
  } catch (err) {
    record.error = String(err.message).split('\n')[0].slice(0, 200);
  }
  results[id] = record;
}

if (args.screenshot) {
  await page.screenshot({ path: args.screenshot, fullPage: Boolean(args['full-page']) });
}

const payload = {
  url,
  httpStatus: status,
  viewport: { width, height },
  layoutViewportWidth: layoutWidth,
  scrollbarWidth: width - layoutWidth,
  browser: `Chromium ${browser.version()}`,
  fontStatus,
  pageErrors: consoleErrors,
  capturedAt: new Date().toISOString(),
  mappingFile: path.basename(args.mapping),
  elements: results,
};

await writeFile(outPath, JSON.stringify(payload, null, 2), 'utf8');
await browser.close();

const found = Object.values(results).filter((r) => r.found).length;
const total = Object.keys(results).length;
console.log(`inspect: ${found}/${total} elements found at ${width}px -> ${outPath}`);
if (fontStatus !== 'loaded') console.log(`inspect: WARNING document.fonts.status = ${fontStatus}`);
if (consoleErrors.length) console.log(`inspect: WARNING ${consoleErrors.length} page error(s)`);
for (const [id, r] of Object.entries(results)) {
  if (!r.found) console.log(`inspect: MISSING ${id} (${r.selector}) — ${r.note || r.error || 'not found'}`);
}

function round(n) { return Math.round(n * 100) / 100; }
