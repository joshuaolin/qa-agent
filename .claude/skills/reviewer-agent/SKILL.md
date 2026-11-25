---
name: reviewer-agent
description: Josh's crosscheck. Before reporting non-trivial work as done (code, scripts, QA deliverables, skill/config/hook edits), send it to the reviewer-agent subagent, fix or answer its findings, show Josh the verdict, and log the review in the trust ledger so he can see how far the review can be trusted before he automates more. Trigger before any "tapos na" on work bigger than a one-line chore, and when Josh says "review mo", "crosscheck", "i-x mo", "pa-check kay x", "review this", "double-check it", "have x look at it", or asks how much to trust the reviews. Formerly x-agent: "x", "x-agent", "kay x", "pa-review kay reviewer" mean this skill.
---

# reviewer-agent

> Built and maintained by **Joshua Olin** · SDE · v1.0 (2026-11-23)

Josh's role now is mostly review. reviewer-agent reviews first, the way he would,
so he can build trust step by step before handing over more. Formerly
x-agent (X = crosscheck, and the ✗ a reviewer marks).

The reviewer itself is the subagent `.claude/agents/reviewer-agent.md` (or `~/.claude/agents/` when installed globally)
(read-only, fresh context). This skill is how you use it.

## When

| Work | Review |
| --- | --- |
| Code, scripts, POM/specs, shared `main/` or `pom/` changes | Always |
| QA deliverables (Excel, test cases, Figma findings) | Always |
| Any file under `.claude/skills` or `.claude/agents` (a case file and one new section included), hooks, settings, schedulers | Always |
| A bug-investigator rule being promoted into a skill | Always, before it goes to Josh for his go |
| One-line chore, a pure answer, a file listing | Skip |
| Josh says "skip review" / "wag na i-review" | Skip, note it in the ledger |

## How

1. **Brief it like a stranger.** Spawn the `reviewer-agent` subagent with:
   - the ask in Josh's own words (quote him), plus any correction he made;
   - the files changed or the diff command to see them;
   - what you ran and what it printed.
   **Don't give your conclusion** ("I think it's fine because…"). It anchors
   the review.
2. **Handle the verdict.**
   - A finding you agree with → fix it, then re-run reviewer-agent on the fix.
   - A finding you disagree with → keep it, and say why in one line.
     Josh decides.
   - Max 2 rounds. Still ✗ after that → hand it to Josh as is.
3. **Show Josh the verdict** in the handover, short:
   `reviewer-agent: ✗ 2 found → 2 fixed, re-check ✅` or `reviewer-agent: ✅ PASS`.
   List any finding you left open.
4. **Log it** in [ledger.md](ledger.md). One row per review.
5. **A real finding about our own mistake** → bug-investigator case, so the rule
   gets promoted and reviewer-agent checks for it next time.

## Josh's directives

reviewer-agent exists to check work against what Josh said should be done. Every
directive he gives ("dapat…", "lagi…", "take note", "from now on", "always")
is logged by bug-investigator as a
`type: directive` case and promoted into a skill, and reviewer-agent reads both
the skills and `cases/` on every review. In each brief, also quote any
directive he gave in the current session that isn't logged yet.

## Trust ledger

[ledger.md](ledger.md) is how Josh sees whether the reviews can be trusted.
Fill in your columns at the time of the review. Josh's columns get filled
when he answers:

- **Confirmed**: findings he agreed were real.
- **Missed**: issues *he* found that reviewer-agent passed. This is the number
  that matters most; every miss also becomes a bug-investigator case.

When he asks "pwede na ba i-automate X?", answer from the ledger: reviews
in that area, misses, and the last miss's date.
