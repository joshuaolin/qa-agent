---
case: diagram-arrow-direction-unchecked
date: 2026-11-24
area: qa-agent / team doc diagrams
type: mistake
---

Nangyari:  The v16 ecosystem chart drew failure-analyst → bug-investigator casebook. The owner: "mali ata arrow ng failure analyst papuntang bug investigator? hehe".
Dahilan:   The arrow followed the layout idea ("every lesson goes below"), not the files. analyst.md steps 2-3 send the verdicts to b2b-verdicts.json and the trend workbook; failure-analyst.md "Read first" 3 reads cases/. So the data flows casebook → failure-analyst.
Ayos:      v17: arrow reversed (casebook → failure-analyst), and its input named in the box. The reviewer also caught the title and intro saying the request runs "on top" when it is the middle row; both fixed in v17. v17 then added an unproven arrow failure-analyst → Output (failure-analyst.md:41/47 returns JSON to its caller only; analyst.md:21-24 the engine fills the workbook and reviewer-agent reviews before hand-over); v18 removed it, box text: "Called by qa-agent's analyst; checks known cases; verdicts go back to it".
Rule:      Before rendering a team-doc diagram, name the file and line that proves each arrow's direction; an arrow with no proof is left out.
Promoted:  pending go (target: qa-agent references/team-doc-update.md step 5, "Every claim matches the system")
