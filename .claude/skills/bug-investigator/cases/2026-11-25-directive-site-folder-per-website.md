---
case: directive-site-folder-per-website
date: 2026-11-25
area: coding-partner / qa-agent automation layout
type: directive
---

Nangyari:  The owner: "yung sa coding dapat if new website dapat gagawa ka ng own folder, di nakakalat para reusable yung folder na to for all project na gagawin ni QA". The SauceDemo automation was written loose: tests/login.spec.js, tests/inventory.spec.js, pom/LoginPage.js and siblings, resources/testdata.json, while B2B, GWS, AAV and HelixSolution each have their own folder.
Dahilan:   new-page-automation.md taught `tests/<feature>.spec.js`, `pom/<Name>Page.js` and one shared `resources/testdata.json`, with no site folder.
Ayos:      coding-partner rule 14; qa-agent new-page-automation.md layers and recipe now use `<Site>/` folders. Moving the existing SauceDemo files waits on the owner's go (main/PageInitialize.js is shared with every Hooks user).
Rule:      A new website or app under test gets its own folder in every layer, named after the site: tests/<Site>/, pom/<Site>/, resources/<Site>/, and main/<Site>/ for a site engine (as B2B, GWS, AAV, HelixSolution do), never loose files in the shared root; ActionDriver, Hooks and utilities stay site-agnostic, and the only shared edit is the one-line page registration in main/PageInitialize.js.
Promoted:  coding-partner SKILL.md rule 14; qa-agent references/new-page-automation.md
