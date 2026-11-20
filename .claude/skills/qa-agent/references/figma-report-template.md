# Design QA — <JIRA-KEY>: <ticket title>

**<N> failures, <M> near-misses, <K> checks passed.** <One sentence: is this shippable or not.>

| | |
|---|---|
| Environment | <url> |
| Viewport | <width>×<height>, Chromium <version> |
| Figma node | <file> / <node id> ([link](...)) |
| Jira | [<KEY>](<url>) |
| Run at | <ISO timestamp> |
| Mapping | `mappings/<page>.json` (<n> elements) |

---

## Acceptance criteria

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | <criterion text> | PASS | <what was actually observed> |
| 2 | <criterion text> | FAIL | <actual behavior, exact text/URL seen> |
| 3 | <criterion text> | MANUAL | <why it can't be checked from the UI> |

<!-- Omit this whole section in design-parity-only mode. Do not fabricate criteria. -->

---

## Failures

### 1. <Short title — e.g. "Primary CTA uses the wrong brand color">

| | |
|---|---|
| Element | `form button[type=submit]` — Figma layer `Button/Primary` |
| Property | `background-color` |
| Expected | `#1b4d8f` |
| Actual | `#2563eb` |

<One line on impact or likely cause — e.g. "Looks like the default Tailwind blue-600 rather than the
brand token; check whether `--color-primary` is wired up on this route.">

### 2. ...

---

## Near-misses (within tolerance)

<details>
<summary><M> properties differ by less than the ±1px tolerance</summary>

| Element | Property | Figma | Live | Δ |
|---|---|---|---|---|
| `main h1` | `font-size` | 40px | 39.99px | 0.01px |

</details>

---

## Screenshots

| Design | Live |
|---|---|
| ![design](design.png) | ![live](live.png) |

---

## Not covered

- Hover / focus / active / error states — not scripted in this run.
- Viewports other than <width>px — <mobile node id> not compared.
- Icon and image content — this run compares computed styles, not pixels.
- <Anything the mapping deliberately excluded.>
