> Use when: something is broken, slow, flaky or "bakit nag fail", before you name a cause or propose a fix.

# Investigate, don't guess

The failure mode this exists for (Lauren Tan, Pstack talk, 14:54): the agent
says "it has to be this thing" while its tool calls show it never read the
code it blames. One confident wrong guess costs more trust than ten slow
right answers.

## Rules

1. **No cause without evidence you actually opened this session.** Every
   claim cites one of these:
   - code: `path/file.js:123`, a line you read;
   - output: a log line, an error, an HTML dump, a test result;
   - a run: what you executed and what it printed.
   "Probably", "it looks like", "should be" are hypotheses. Label them that
   way and go check.
2. **Read the code path end to end** before blaming a piece of it: entry
   point → the function that failed → what it calls. Not just the file whose
   name sounds right.
3. **Reproduce before you fix.** Run the failing case yourself, safely (see
   [safety.md](safety.md)). If it doesn't reproduce, say so. That is a finding.
4. **Compare with a sibling that works.** The same flow on another site,
   the last green run, yesterday's log. The difference is usually the cause.
5. **One hypothesis at a time.** Change one thing, re-run, read the result.
   Never stack three "fixes" and hope.
6. **Wide searches go to a subagent.** When the answer means sweeping many
   files, delegate the search and keep the conclusion. Don't guess instead.
7. **Say "hindi ko pa alam" when you don't know.** Then say what you'd check
   next. Never present a guess as "the smoking gun".

## Report shape

```
Nangyari:  <what failed, where, when>
Dahilan:   <cause>, with evidence: <file:line | log line | run output>
Ayusin:    <proposed fix>, whose: <code | data | site/env | machine>
Na-verify: <what you ran after, and its result>  (or: "hindi pa, kasi …")
```

Propose the fix and wait, unless he already said to go ahead.
