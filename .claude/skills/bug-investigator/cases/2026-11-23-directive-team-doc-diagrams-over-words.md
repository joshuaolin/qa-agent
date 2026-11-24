---
case: directive-team-doc-diagrams-over-words
date: 2026-11-23
area: qa-agent / team doc update
type: directive
---

Nangyari:  The team doc v9 explained the agents, the workbook and the workflow status in long bullet paragraphs. The owner: "ang daming words, hehe kung may need ka iexplain maybe use table tapos bullet bullet sa loob? tapos capitalized natin yung linear diagram if need mag dagdag gawin kasi feel ko mas madali ma intindihan kung diagram ang ipapakita natin instead na puro words ... baka may ibang way para ma ano natin present na malinis".
Dahilan:   Directive. The leads skim; a linear diagram or a table reads faster than paragraphs.
Ayos:      v10: each section is one short line + a linear diagram; explanations moved into tables whose cells hold short bullets; docs-kit docx_edit.py fills a table cell from a list as bullet paragraphs.
Rule:      Team docs lead with diagrams (add one when a section explains a flow or a set of parts): linear when the real flow is a line, a main lane plus side loops when parts are called on demand or feed back; text is one short line per section; anything more goes in a table with short bullets inside the cells, never in paragraphs.
Update:    2026-11-24, on the v15 ecosystem chart the owner: "baka mas mas better ka pang chart dito masyadong linear e?". Claude proposed a main lane + side loops (coding-partner on demand above qa-agent, bug-investigator casebook below) and the rule change; the owner: "go go update mo na". Built as v16; v17 and v18 fixed the failure-analyst arrows (it reads the casebook and returns its verdicts to qa-agent's analyst; case diagram-arrow-direction-unchecked).
Confirmed: The owner on v10: "god damn eto!!! ang hinahanap ko solid solid solid, pa take note ng lahat ha!" v10 (<team doc>-v10.docx, config the team doc folder/v10.json) is the reference layout for team docs: one line + linear diagram per section, tables with bullet cells, a step diagram for How to Start. The v10 layout stands; each diagram's shape follows the Rule (the v18 ecosystem chart is the side-loop example).
Promoted:  qa-agent references/team-doc-update.md step 4 (the owner's ask, 2026-11-23; layout confirmed on v10)
