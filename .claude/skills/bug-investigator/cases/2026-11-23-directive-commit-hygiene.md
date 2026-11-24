---
case: directive-commit-hygiene
date: 2026-11-23
area: all repos / git
type: directive
---

Nangyari:  Both repos touched today held the owner's own uncommitted work beside Claude's changes (Playwright Framework: ActionDriver.js, PageInitialize.js, POM pages, testdata.json and specs; qa-agent-public: main/, pom/, resources/, tests/, package*.json, playwright.config.js, visual-compare.md). Claude proposed a commit hygiene rule; the owner: "commit hygiene rules go bro".
Dahilan:   Directive. Both repos held the owner's WIP next to ours; a broad add would have shipped it. Today's three commits (17aa45d, 921f12b, e9c53bb) were staged by path; only 17aa45d carries a verified / still-to-verify line, so the rule tightens that going forward.
Ayos:      coding-partner references/safety.md, new "Commits" section.
Rule:      Commit and push only on the owner's say; commit only what you changed: note pre-existing changes first, stage by path (never add -A / . / commit -a), don't commit a file mixing the owner's edits and yours, read the staged list, message from a file outside the repo with what was verified, push only after review.
Promoted:  coding-partner references/safety.md, "Commits" (reviewer-agent ✅ after 5 wording fixes, go)
