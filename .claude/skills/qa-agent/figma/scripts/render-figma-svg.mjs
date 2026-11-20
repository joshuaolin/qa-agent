import { chromium } from 'playwright';
import { readFileSync } from 'node:fs';

// Render a Figma SVG export to PNG at 1x, over a neutral grey: the export carries no backdrop,
// so a white card would vanish on a white page.
// usage: node render_svg.mjs <export.svg> <out.png> <width> <height>
const [src, out, w, h] = process.argv.slice(2);
const svg = readFileSync(src, 'utf-8');
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: +w, height: +h } });
await page.setContent(`<html><body style="margin:0;background:#6b6b6b">${svg}</body></html>`);
await page.screenshot({ path: out, clip: { x: 0, y: 0, width: +w, height: +h } });
await browser.close();
console.log('rendered', out);
