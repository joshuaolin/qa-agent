---
case: directive-ask-for-linked-docs
date: 2026-11-23
area: qa-agent / test cases from a ticket
type: directive
---

Nangyari:  GWS-3115 (Crizal Natural Look product page, Wave 9) says "Please refer to the page layout and copy required in this document"; the document is a link Claude can't open. The owner: "spacial case yan since my "this document" e like pag may ganto always ask mo sakin saan location yung file okay?" Extended 2026-11-26, once Claude could read Jira through the REST API (which downloads Jira attachments): AAV-2328 links its FR and IT reference .docx on SharePoint. The owner: "note that may mga external file yan always ask mo sakin if may mga need kang files ha since i know di mo yan kaya i access".
Dahilan:   Directive. The linked document holds the expected layout and copy; test cases written without it would guess the requirements.
Ayos:      qa-agent references/testcase-doc.md, "Reading the source ticket"; qa-agent references/jira-api.md, the external-links paragraph.
Rule:      Download Jira attachments through the API; for every other file a ticket needs (SharePoint/Drive/Confluence link, "this document", a failed download) list it to the owner with its purpose and ask for it before writing what depends on it; never guess its contents.
Promoted:  qa-agent references/testcase-doc.md; qa-agent references/jira-api.md (reviewer-agent ✗ → fixed, go 2026-11-26 "save this all")
