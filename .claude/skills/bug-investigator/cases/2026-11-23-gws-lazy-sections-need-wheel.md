---
case: gws-lazy-sections-need-wheel
date: 2026-11-23
area: qa-agent / GWS essilor.com preview pages
type: bug
---

Nangyari:  GWS-3115 evidence run: on ch-fr, ch-de, ch-it and jp-ja every product-page section after the benefits block was "not found" (page stuck at 1288px), so ~30 checks failed that were not real.
Dahilan:   Those locales show no consent prompt, and their sections lazy-load only on real wheel scrolling. PagePreparer's scrollTo pass loads nothing there (on fr/ca/be the consent click is what grew the page, 900 → 5851px). Confirmed with a probe: 25 mouse.wheel steps took ch-de from 1288px / 2 filled rows to 5817px / 8 filled rows.
Ayos:      In the GWS-3115 runner, a mouse.wheel pass (30 × 500px) before PagePreparer.prepare(); re-run gave ch-fr / ch-de 15 pass.
Rule:      On essilor.com pages, a section "missing" on some locales but not others is a loading problem until a probe proves otherwise: wheel-scroll before reading sections, and dump the real page text before calling any copy difference a finding.
Promoted:  qa-agent references/feature-maps/gws.md "Traps" (reviewer-agent reviewed, the owner: "4. go bro")
