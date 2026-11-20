#!/usr/bin/env node
/**
 * compare.mjs — deterministic design-vs-live style diff.
 *
 *   node compare.mjs --figma figma.json --live live.json
 *                    [--out diff.json] [--md diff.md] [--tolerance 1]
 *
 * Exit code 1 when there is at least one FAIL, so this can gate a pipeline later.
 */
import { readFile, writeFile } from 'node:fs/promises';

const COLOR_PROPS = new Set([
  'color', 'background-color', 'border-top-color', 'border-right-color',
  'border-bottom-color', 'border-left-color', 'border-color', 'outline-color',
]);

const LENGTH_PROPS = new Set([
  'font-size', 'line-height', 'letter-spacing',
  'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
  'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
  'gap', 'row-gap', 'column-gap',
  'width', 'height', 'min-height', 'max-width',
  'border-top-left-radius', 'border-top-right-radius',
  'border-bottom-right-radius', 'border-bottom-left-radius',
  'border-radius',
  'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width',
  'border-width',
]);

// Lower number = more severe. Drives report ordering.
const SEVERITY = {
  color: 1, 'background-color': 1, 'border-top-color': 2, 'border-color': 2,
  'font-family': 3, 'font-size': 3, 'font-weight': 3, 'line-height': 4, 'letter-spacing': 4,
  'padding-top': 5, 'padding-right': 5, 'padding-bottom': 5, 'padding-left': 5,
  gap: 5, 'row-gap': 5, 'column-gap': 5,
  'margin-top': 6, 'margin-right': 6, 'margin-bottom': 6, 'margin-left': 6,
  'border-top-left-radius': 7, 'border-top-right-radius': 7,
  'border-bottom-right-radius': 7, 'border-bottom-left-radius': 7,
  'box-shadow': 7, opacity: 7,
};

// Figma's enum spellings differ from CSS keywords for the same value. Treating these as diffs
// produces pure false positives, so fold them together before comparing.
const ENUM_ALIASES = {
  'text-transform': { upper: 'uppercase', lower: 'lowercase', title: 'capitalize', original: 'none' },
  'text-decoration-line': { strikethrough: 'line-through', 'line through': 'line-through' },
  'text-align': { start: 'left', end: 'right', justified: 'justify' },
  'font-style': { italic: 'italic', oblique: 'italic' },
};

// Differences below this are floating-point noise from Figma's sub-pixel geometry, not design intent.
const EPSILON_PX = 0.005;

const WEIGHTS = {
  thin: 100, extralight: 200, ultralight: 200, light: 300, book: 400, regular: 400,
  normal: 400, medium: 500, semibold: 600, demibold: 600, bold: 700,
  extrabold: 800, ultrabold: 800, black: 900, heavy: 900,
};

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    if (!argv[i].startsWith('--')) continue;
    const key = argv[i].slice(2);
    const next = argv[i + 1];
    if (next === undefined || next.startsWith('--')) out[key] = true;
    else { out[key] = next; i++; }
  }
  return out;
}

/** rgb()/rgba()/#rgb/#rrggbb/#rrggbbaa/transparent -> #rrggbb or #rrggbbaa */
function normColor(raw) {
  if (!raw) return null;
  const v = String(raw).trim().toLowerCase();
  if (v === 'transparent' || v === 'rgba(0, 0, 0, 0)') return '#00000000';
  if (v === 'none' || v === 'currentcolor' || v === 'inherit') return null;

  let m = v.match(/^rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)(?:[\s,/]+([\d.%]+))?\s*\)$/);
  if (m) {
    const [r, g, b] = [m[1], m[2], m[3]].map((n) => clamp255(Math.round(Number(n))));
    let a = 1;
    if (m[4] !== undefined) {
      a = m[4].endsWith('%') ? Number(m[4].slice(0, -1)) / 100 : Number(m[4]);
    }
    return hex(r, g, b, a);
  }
  m = v.match(/^#([0-9a-f]{3,8})$/);
  if (m) {
    let h = m[1];
    if (h.length === 3) h = h.split('').map((c) => c + c).join('');
    if (h.length === 4) h = h.split('').map((c) => c + c).join('');
    if (h.length === 6) return `#${h}`;
    if (h.length === 8) {
      const a = parseInt(h.slice(6), 16) / 255;
      return a >= 0.999 ? `#${h.slice(0, 6)}` : `#${h}`;
    }
  }
  return v; // named color or gradient — compared as a plain string
}

function clamp255(n) { return Math.max(0, Math.min(255, n)); }
function hex(r, g, b, a) {
  const base = '#' + [r, g, b].map((n) => n.toString(16).padStart(2, '0')).join('');
  if (a >= 0.999) return base;
  return base + clamp255(Math.round(a * 255)).toString(16).padStart(2, '0');
}

/** "16px" | "16" | 16 -> 16 ; non-px units and keywords -> null (not comparable) */
function normLength(raw) {
  if (raw === 0) return 0;
  if (!raw) return null;
  const v = String(raw).trim().toLowerCase();
  if (v === 'normal' || v === 'auto' || v === 'none' || v === 'inherit') return null;
  const m = v.match(/^(-?[\d.]+)(px)?$/);
  return m ? Number(m[1]) : null;
}

function normWeight(raw) {
  if (!raw) return null;
  const v = String(raw).trim().toLowerCase();
  if (/^\d+$/.test(v)) return Number(v);
  return WEIGHTS[v.replace(/[\s_-]/g, '')] ?? null;
}

function normFamily(raw) {
  if (!raw) return null;
  return String(raw).split(',')[0].trim().replace(/^["']|["']$/g, '').toLowerCase();
}

function normGeneric(raw, prop) {
  if (raw === undefined || raw === null) return null;
  const v = String(raw).trim().toLowerCase().replace(/\s+/g, ' ');
  return ENUM_ALIASES[prop]?.[v] ?? v;
}

const args = parseArgs(process.argv.slice(2));
if (!args.figma || !args.live) {
  console.error('compare.mjs: --figma <file> and --live <file> are required');
  process.exit(2);
}
const tolerance = Number(args.tolerance ?? 1);

const figma = JSON.parse(await readFile(args.figma, 'utf8'));
const live = JSON.parse(await readFile(args.live, 'utf8'));

const rows = [];
const missing = [];

for (const [id, fEl] of Object.entries(figma.elements || {})) {
  const lEl = (live.elements || {})[id];

  if (!lEl || !lEl.found) {
    missing.push({
      id,
      figmaLayer: fEl.figmaLayer || null,
      selector: lEl?.selector || null,
      reason: lEl ? (lEl.note || lEl.error || 'not found on page') : 'not present in live.json',
    });
    continue;
  }

  for (const [prop, fRaw] of Object.entries(fEl.styles || {})) {
    const lRaw = (lEl.styles || {})[prop];
    const row = {
      id, figmaLayer: fEl.figmaLayer || null, selector: lEl.selector,
      property: prop, figma: fRaw, live: lRaw ?? null,
      severity: SEVERITY[prop] ?? 8,
    };

    if (lRaw === undefined || lRaw === null || lRaw === '') {
      row.verdict = 'SKIP';
      row.note = 'property not captured on the live side';
      rows.push(row);
      continue;
    }

    if (COLOR_PROPS.has(prop)) {
      const f = normColor(fRaw), l = normColor(lRaw);
      if (f === null || l === null) { row.verdict = 'SKIP'; row.note = 'colour not comparable'; }
      else row.verdict = f === l ? 'PASS' : 'FAIL';
      row.normalized = { figma: f, live: l };
    } else if (prop === 'font-weight') {
      const f = normWeight(fRaw), l = normWeight(lRaw);
      if (f === null || l === null) { row.verdict = 'SKIP'; row.note = 'weight not parseable'; }
      else row.verdict = f === l ? 'PASS' : 'FAIL';
      row.normalized = { figma: f, live: l };
    } else if (prop === 'font-family') {
      const f = normFamily(fRaw), l = normFamily(lRaw);
      row.verdict = f === l ? 'PASS' : 'FAIL';
      row.normalized = { figma: f, live: l };
      if (row.verdict === 'FAIL') row.note = 'compared first family only';
    } else if (LENGTH_PROPS.has(prop)) {
      const f = normLength(fRaw), l = normLength(lRaw);
      if (f === null || l === null) {
        row.verdict = 'SKIP';
        row.note = 'non-px or keyword value — see comparison-rules.md';
      } else {
        const delta = Math.abs(f - l);
        row.delta = Math.round(delta * 100) / 100;
        if (delta < EPSILON_PX) row.verdict = 'PASS';
        else if (delta <= tolerance) row.verdict = 'NEAR';
        else row.verdict = 'FAIL';
      }
      row.normalized = { figma: f, live: l };
    } else {
      const f = normGeneric(fRaw, prop), l = normGeneric(lRaw, prop);
      row.verdict = f === l ? 'PASS' : 'FAIL';
      row.normalized = { figma: f, live: l };
    }

    rows.push(row);
  }
}

const by = (v) => rows.filter((r) => r.verdict === v);
const fails = by('FAIL').sort((a, b) => a.severity - b.severity || a.id.localeCompare(b.id));
const nears = by('NEAR');
const summary = {
  elementsCompared: Object.keys(figma.elements || {}).length - missing.length,
  elementsMissing: missing.length,
  checks: rows.length,
  pass: by('PASS').length,
  near: nears.length,
  fail: fails.length,
  skip: by('SKIP').length,
  tolerancePx: tolerance,
};

const result = {
  summary,
  environment: {
    url: live.url, httpStatus: live.httpStatus, viewport: live.viewport,
    layoutViewportWidth: live.layoutViewportWidth, browser: live.browser,
    fontStatus: live.fontStatus, pageErrors: live.pageErrors, capturedAt: live.capturedAt,
  },
  figmaNode: figma.node || null,
  missingElements: missing,
  failures: fails,
  nearMisses: nears,
  all: rows,
};

if (args.out) await writeFile(args.out, JSON.stringify(result, null, 2), 'utf8');
if (args.md) await writeFile(args.md, renderMarkdown(result), 'utf8');

console.log(
  `compare: ${summary.fail} FAIL · ${summary.near} NEAR · ${summary.pass} PASS · ` +
  `${summary.skip} SKIP · ${summary.elementsMissing} element(s) missing`
);
for (const f of fails.slice(0, 20)) {
  console.log(`  FAIL ${f.id}.${f.property}: expected ${fmt(f.normalized?.figma ?? f.figma)}, got ${fmt(f.normalized?.live ?? f.live)}`);
}
if (fails.length > 20) console.log(`  ... and ${fails.length - 20} more`);

process.exit(summary.fail > 0 || summary.elementsMissing > 0 ? 1 : 0);

function fmt(v) { return v === null || v === undefined ? '(none)' : String(v); }

function renderMarkdown(r) {
  const s = r.summary;
  const L = [];
  L.push(`## Style diff — ${s.fail} failures, ${s.near} near-misses, ${s.pass} passed`);
  L.push('');
  L.push(`\`${r.environment.url}\` at ${r.environment.viewport?.width}px · ${r.environment.browser} · ${r.environment.capturedAt}`);
  L.push('');
  if (r.environment.fontStatus && r.environment.fontStatus !== 'loaded') {
    L.push(`> **Fonts did not finish loading** (\`document.fonts.status = ${r.environment.fontStatus}\`). Treat typography findings below as suspect until this is fixed.`);
    L.push('');
  }

  if (r.missingElements.length) {
    L.push('### Missing elements');
    L.push('');
    L.push('| id | Figma layer | selector | reason |');
    L.push('|---|---|---|---|');
    for (const m of r.missingElements) {
      L.push(`| ${m.id} | ${m.figmaLayer ?? '—'} | \`${m.selector ?? '—'}\` | ${m.reason} |`);
    }
    L.push('');
  }

  L.push('### Failures');
  L.push('');
  if (!r.failures.length) {
    L.push('_None._');
  } else {
    L.push('| element | Figma layer | property | expected | actual | Δ |');
    L.push('|---|---|---|---|---|---|');
    for (const f of r.failures) {
      L.push(`| \`${f.selector}\` | ${f.figmaLayer ?? '—'} | \`${f.property}\` | ${fmt(f.normalized?.figma ?? f.figma)} | ${fmt(f.normalized?.live ?? f.live)} | ${f.delta ?? '—'} |`);
    }
  }
  L.push('');

  if (r.nearMisses.length) {
    L.push('<details>');
    L.push(`<summary>${r.nearMisses.length} near-misses (within ±${s.tolerancePx}px)</summary>`);
    L.push('');
    L.push('| element | property | Figma | live | Δ |');
    L.push('|---|---|---|---|---|');
    for (const n of r.nearMisses) {
      L.push(`| \`${n.selector}\` | \`${n.property}\` | ${fmt(n.figma)} | ${fmt(n.live)} | ${n.delta} |`);
    }
    L.push('');
    L.push('</details>');
    L.push('');
  }

  const skips = r.all.filter((x) => x.verdict === 'SKIP');
  if (skips.length) {
    L.push('<details>');
    L.push(`<summary>${skips.length} checks skipped (not comparable)</summary>`);
    L.push('');
    for (const k of skips) L.push(`- \`${k.selector}\` \`${k.property}\` — ${k.note ?? 'not comparable'}`);
    L.push('');
    L.push('</details>');
  }
  return L.join('\n') + '\n';
}
