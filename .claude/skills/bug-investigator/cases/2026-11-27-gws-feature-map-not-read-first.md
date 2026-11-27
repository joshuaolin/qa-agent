---
case: gws-feature-map-not-read-first
date: 2026-11-27
area: qa-agent / GWS (essilor.com) page checks
type: mistake
---

Nangyari:  Rechecking Adrian's GWS-3115 validation (the owner: "double check mo gawa ni adrian pero wag kang mag comment"), Claude wrote checks against essilor.com without first reading qa-agent references/feature-maps/gws.md. It then rediscovered the hard way that CH and JP pages render sections only on a real wheel scroll. That trap was already row 116 of the map. Along the way it briefly reported two non-findings: a "Données inernes" typo that exists only in hidden CMS JSON, and "carousel absent" results caused by its own selectors and a reused browser tab. Both were retracted before the results file was written.
Dahilan:   qa-agent Step 1 says to read the site's feature map first for any QA ask about a UI. It was skipped because the task started as "can you open the links".
Ayos:      Added three traps to feature-maps/gws.md (carousel structure and walking, full-page screenshot limit, hidden CMS text). The final results (the deliverables folder/GWS-3115-recheck.xlsx) came only from rendered text after the wheel pass and the carousel walk.
Rule:      Before checking any essilor.com page, read feature-maps/gws.md "Traps". Report copy only from rendered innerText after the wheel pass, and treat "missing on some locales" as your own loading or selector problem until a probe proves otherwise.
Promoted:  qa-agent references/feature-maps/gws.md Traps (3 rows)
