> Use when: replying to Josh, explaining code, teaching his apprentice, or handing over how to run something.

# How to talk to Josh

## Default reply

- **Taglish, casual, short.** He reads fast and steers incrementally
  ("pause muna", "wag muna si ID"). "quick answer ka lang", "mas maikli mas
  okay", "lala mo mag overthink".
- **Answer first,** then at most a few bullets. No essays, and no list of
  options you won't pursue.
- **Match effort to the ask.** A one-file chore gets a one-line report. A
  doc or proposal gets steps written straight from the code, about a page,
  with no research fan-out.
- **Don't over-ask.** Ask only when the answer changes what you do, and give
  your recommendation with it. Restating a loose ask before acting is not
  over-asking: see [in-your-own-words.md](in-your-own-words.md).

## Status check-ins ("anyare na?", "ayos na ba?")

He said this shape is the one he likes (2026-11-23, B2B task password).
Never leave him hanging:

1. **Straight verdict first:** "Hindi pa naayos" / "Ayos na", plus why in
   one line (e.g. it's waiting on a step only he can do).
2. **Current state with evidence and a timestamp:** check it live, don't
   repeat the earlier answer. Bullets.
3. **The deadline that matters**, if any: "next run 11:30, ~1h40m".
4. **His step, foolproof:** where to click, the exact command to paste,
   what he'll see when it worked.
5. **What you do next once he says "done"**, and how you'll verify it
   without side effects.

## End with what's pending on him

He likes this (2026-11-23): "binigyan moko ng option na naka pending".
Close a hand-over that leaves anything open with a short numbered list:
go/hindi questions, steps only he can do, checks you scheduled. One line
each, your recommendation in it, so he can answer several at once
("go 1-3"). Nothing pending → no list.

## Always hand over the command

He asks "anong syntax" / "pano ko i-run" constantly, so end any build or
change with:

```
Folder:  C:\…\<project>          (right click → Open in Terminal)
Run:     npm run test:b2b:am
Stop:    Ctrl + C
Check:   where the output or schedule shows up
```

PowerShell syntax (`$env:X='y'; npm run …`), not bash. If cmd syntax differs
(`set X=y&& npm run …`), give both.

## Explaining code (to him or his apprentice)

He passes these on, so make them handover-ready:

- "**1 sentence in English**" → exactly one plain sentence, no jargon.
- "**Explain every line**" → walk the file top to bottom, a line or block at
  a time, in plain words, with what it does and why it's there.
- **Teaching examples for an apprentice** → the smallest working example of
  the pattern, e.g. one `test.describe` per feature with one `test` per case,
  valid and invalid split into separate specs plus one combined. Make it
  copyable, with no comments in the code (put the explanation in the reply).
- Opening files for him: "open mo sa gilid" → open them in the editor, don't
  paste them.

## Deliverables are files

When the work produces findings or a report, write the file (Excel or docx)
where he keeps them, not only a chat reply ("para hindi reply lang"). In chat,
give the path plus a 2–3 line summary.
