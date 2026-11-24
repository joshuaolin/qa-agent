---
case: directive-tc-steps-anyone-can-follow
date: 2026-11-23
area: qa-agent / test cases from a ticket
type: directive
---

Nangyari:  TC-AAV2266 steps read "Open the sample article on Preview at 1440 / Inspect the title element", and the screenshots were crops of the element with no URL. The owner: "maybe if di IT yung mag follow ng TC is malito sya ... lets start talaga kung paano inanavigate from go to www... until ma reach yung specific na component? then yung screenshot if kaya dapat kasama URL tas naka mark nalang yung specific na component", then "go sa lahat".
Dahilan:   Directive. The TC goes to people outside QA/IT (dev, PO, business testers).
Ayos:      qa-agent references/testcase-doc.md "Writing the steps: anyone can follow them" and step 2; shared .claude\skills\qa-agent\testcase\evidence-shot.cjs (component in page context, red box + label, URL/viewport/time strip); write_tc.py widens H/I/M and sizes rows from the wrapped text.
Rule:      Test steps start from "Open Google Chrome" and the full URL and walk every click and scroll to the component by what is on screen, with checks a non-IT tester can do (Inspect / Ctrl+U explained); every component screenshot shows the page URL and the component marked in its page context.
Promoted:  qa-agent references/testcase-doc.md
