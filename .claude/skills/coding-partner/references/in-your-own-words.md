> Use when: before acting on any ask from Josh that you had to interpret. Slang, shorthand, "yada yada", a vague "ayusin mo", a goal without the steps, or anything where you filled a gap with a guess.

# In your own words: confirm before you execute

Josh writes fast and loose. Reading his intent from that and executing right
away is the biggest time sink between you two: a wrong guess costs a whole
round of work plus the undo. So before you change anything, say back what you
understood. **He has the final say.**

## When to confirm

| Situation | Do |
| --- | --- |
| You had to interpret, guess a target, or pick between readings | Confirm first |
| The ask touches shared code, global files, deletes, or anything outward-facing | Confirm first |
| The ask is exact: a literal command, file and change spelled out | Proceed |
| A "go / tama / do it" for a plan he already confirmed | Proceed |
| You're sure, and a wrong guess costs a few seconds to undo | Proceed |
| Promoting a bug-investigator rule into a skill | reviewer-agent reviews it, then a one-line go/hindi to him |

When in doubt, confirm. One short check is cheaper than a wrong build.

## The format

Short, no essay:

```
Pagkakaintindi ko:
- Goal: <what he wants as the end result, in his terms>
- Gagawin ko: <files / commands / where it lands>
- Hindi ko gagalawin: <what stays as is>
- Hula ko lang: <each assumption you made, one line each>
Tama ba? (go / mali: …)
```

- **Goal is the outcome, not the steps.** "Makita si coding-partner sa loob
  ng project" vs "i-add sa workspace" was exactly the miss.
- **Hula ko lang** is the important line. List every gap you filled, with
  your pick, so he can fix just that one.
- Skip a line that has nothing in it.
- Read what you need first (files, current state) so the restatement is
  concrete. Don't start changing things before the "go".

## After he answers

- **"go" / "tama"** → execute exactly that, no scope creep.
- **Correction** → apply it and execute if it's now clear. Re-confirm only
  if the correction opened a new gap.
- **A correction that will come up again** → write it into the matching
  reference so the next session already knows.

This is not over-asking: you're not asking him to decide for you, you're
checking that you heard him right. Still give your recommendation for any
real choice.
