---
case: directive-ask-for-linked-docs
date: 2026-11-23
area: qa-agent / test cases from a ticket
type: directive
---

Nangyari:  GWS-3115 (Crizal Natural Look product page, Wave 9) says "Please refer to the page layout and copy required in this document"; the document is a link Claude can't open. The owner: "spacial case yan since my "this document" e like pag may ganto always ask mo sakin saan location yung file okay?"
Dahilan:   Directive. The linked document holds the expected layout and copy; test cases written without it would guess the requirements.
Ayos:      qa-agent references/testcase-doc.md, "Reading the source ticket".
Rule:      When a ticket points to a document or file ("this document", a linked doc, an attachment), ask the owner where the file is before writing the test cases that depend on it; never guess its contents.
Promoted:  qa-agent references/testcase-doc.md
