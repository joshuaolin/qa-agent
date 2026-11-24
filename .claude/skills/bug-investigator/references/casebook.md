> Use when: a bug is solved, a run failure is explained, or Josh corrected you. Log the case, then promote its rule.

# The casebook

One file per case in `cases/`, named `YYYY-MM-DD-<short-slug>.md`. Before
writing, search `cases/` for the same cause: if it's there, add a
`Nangyari ulit` line to that case instead of a new file, and ask why the
rule didn't stop it.

## What counts as a case

- A bug in the code or a site (after the cause is proven).
- **Our mistakes:** misread ask, wrong target, skipped verification, a
  sibling broken by a shared change, a side effect while testing.
- A correction from Josh that will come up again.
- **A directive from Josh:** anything he says should be done a certain way
  ("dapat…", "lagi…", "take note", "eto trip ko"; in English "should…",
  "always…", "from now on", "remember", "I like this"), even with no mistake
  behind it. `type: directive`, and its Rule is his instruction.

Not a case: a typo fixed in the same breath, or a one-off preference that
only matters to this conversation.

## Case format

```
---
case: <short-slug>
date: YYYY-MM-DD
area: <repo / site / suite / file / "communication">
type: bug | mistake | correction | directive
---

Nangyari:  <what happened, one or two lines>
Dahilan:   <root cause, with evidence>
Ayos:      <what fixed it>
Rule:      <one line, testable: what to do differently next time>
Promoted:  <skill/reference.md it was written into> | not promoted: <why>
```

Keep it short. The story fits in five lines or it isn't one case.

## Promote the rule

The rule only prevents a repeat if it's read at the moment it matters, so
put it where that moment loads it:

| Rule is about | Write it into |
| --- | --- |
| Understanding the ask, replies, handover | coding-partner `in-your-own-words.md` or `communication.md` |
| Code style, structure | coding-partner `code-style.md` |
| Changes, deletes, side effects, test runs | coding-partner `safety.md` |
| A suite, site, locator, Figma or test case flow | the matching qa-agent reference |
| How to investigate | this skill's `investigate.md` |
| Only this one area, nowhere general | stays in the case, `not promoted` |

reviewer-agent reviews every promotion first; Josh's go is still what applies it:

1. Draft the rule in the target reference's own style (short, imperative,
   why included).
2. Send reviewer-agent the case, the target file and the draft lines. ✗ → fix and
   re-check (max 2 rounds).
3. Ask Josh in one line, with the verdict:
   `Promote "<rule>" → <file>? (reviewer-agent ✅) go / hindi`. Batch several into
   one line when there are many. Until his go the case says
   `Promoted: pending go`; after it, `Promoted: <file> (reviewer-agent ✅, go)`.
