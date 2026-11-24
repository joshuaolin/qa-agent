---
case: absent-component-no-screenshot
date: 2026-11-23
area: qa-agent / test case evidence run
type: bug
---

Nangyari:  TC-GWS3115: TC-06 ca-fr, TC-08 jp-ja, TC-13 jp-ja and TC-15 jp-ja had no screenshot. The owner: "bat walang screenshot nga pala sa 1??". reviewer-agent caught the gap in review; the Details sheet first labelled it "nothing on screen to capture", which was not true.
Dahilan:   qa-reports\TC-GWS3115\run.cjs Evidence.section() screenshots the component itself and returns null when the component is not on the page (index == null); checkCarousel() returned evidence: null when no carousel exists. So exactly the "element missing" checks, the ones testcase-doc.md step 2 says are themselves evidence, got none, silently.
Ayos:      run.cjs Evidence.absent(): a full-page screenshot when the component is missing, used by section() and checkCarousel(). The owner said go ("sige pa re-run ng execution"); the re-run screenshots showed jp-ja DOES have the carousel ("クリザールシリーズを見る", 1-2 cards) on the brand, easy-pro and product pages, so TC-08 "missing", TC-13 N/A and TC-15 N/A were wrong. Second cause: carouselSection() found the carousel by the spec heading, and its structural fallback needed 3+ product links. Now it falls back to any section with an image-only card link to a /crizal/crizal-*/ page, and a heading that differs from the spec is reported as a finding (TC-08 too). All 7 locales re-run; only jp-ja changed (13 and 15 now fail on the English "Discover" CTA and the heading). review.json remarks for 8/13/15 rewritten.
Rule:      An evidence helper that targets an element must fall back to a full-page screenshot when the element is absent; never return "no evidence" silently. Before hand-over, list every check/locale with no screenshot and treat each as a gap. A "not present" / N/A result needs a full-page screenshot that was looked at before it is reported, and a finder keyed on spec text must have a structural fallback that doesn't depend on item count.
Promoted:  not yet; testcase-doc.md step 2 already says it, this is the code following it
