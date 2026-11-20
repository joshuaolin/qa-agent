# Figma → CSS normalization rules

Read this before writing `figma.json`. Most false positives in design-parity QA come from unit and
naming mismatches between Figma and CSS, not from real implementation bugs.

## Property name mapping

| Figma concept | CSS property | Notes |
|---|---|---|
| Fill (on a frame/shape) | `background-color` | Only for solid fills. Gradients → compare `background-image`, or skip. |
| Fill (on text) | `color` | Text fill is `color`, never `background-color`. |
| Stroke | `border-color` + `border-width` | Figma stroke can be inside/center/outside; CSS borders are always outside the box for layout. Center/inside strokes shift box size by the stroke width. |
| Corner radius | `border-radius` | Per-corner radii in Figma map to the four `border-*-radius` longhands. |
| Auto-layout gap ("item spacing") | `gap` | Not `margin`. If implemented with margins, expect `gap: normal` on the live side — mapping issue, not a bug per se. |
| Auto-layout padding | `padding-top/right/bottom/left` | Figma often shows a single "horizontal/vertical" pair; expand to all four. |
| Effect: drop shadow | `box-shadow` | Figma gives x/y/blur/spread/color separately; assemble in that order. |
| Layer opacity | `opacity` | A fill with alpha is NOT the same as layer opacity — alpha lands in the color, opacity in `opacity`. |
| Text case | `text-transform` | Figma "UPPER" → `uppercase`. |
| Text decoration | `text-decoration-line` | |

## Unit normalization

- **Line height.** Figma reports `AUTO`, a percentage, or a px value. CSS computed `line-height` is
  almost always px. `AUTO` is **not comparable** — mark it `SKIP`, do not guess `normal`. For a
  percentage, convert: `line-height-px = font-size-px * pct / 100`.
- **Letter spacing.** Figma commonly uses a percentage of font size; CSS computes px.
  `px = font-size-px * pct / 100`. Figma `0%` → CSS `normal` (which computes to `0px`) — these match.
- **Font weight.** Figma gives style names. Map: Thin 100, ExtraLight 200, Light 300, Regular 400,
  Medium 500, SemiBold 600, Bold 700, ExtraBold 800, Black 900. Never compare the name to a number.
- **Font family.** Compare only the first family, case-insensitively, with quotes stripped. The live
  stack (`Inter, system-ui, sans-serif`) legitimately has fallbacks the design does not.
- **Colors.** Normalize both sides to lowercase `#rrggbb`, or `#rrggbbaa` when alpha < 1.
  `compare.mjs` already does this — do not pre-convert by hand and risk a rounding mistake.
- **Lengths.** Strip `px` and compare numerically with tolerance. Figma emits fractional values
  (`15.999996`); this is why the default tolerance is ±1px rather than exact.

## Things that are legitimately different — do not report as bugs

- **Font size rounding.** Figma 15.99px vs live 16px is the same design.
- **Fallback fonts in the stack.** See above.
- **`display` / layout mechanism.** Figma has no `display`. Flex vs grid vs block is an implementation
  choice; only the resulting geometry matters.
- **Scrollbar-induced width deltas.** A 1440px viewport renders ~1425px of content when a scrollbar is
  present. `inspect.mjs` reports the layout viewport width so you can account for this.
- **Text box height.** Figma text frames are often taller or shorter than the rendered line box. Compare
  `font-size` and `line-height`, not text-node `height`.
- **Hidden-layer leftovers.** Layers hidden in Figma have no live counterpart. Exclude them from the
  mapping instead of reporting them missing.

## Things that look cosmetic but are real bugs

- Color off by any amount — brand colors are exact by definition. A `#1b4d8f` vs `#2563eb` diff is a
  wrong token, not a rendering artifact.
- Consistent spacing drift (every gap 4px small) — usually a wrong spacing token or a base-unit bug,
  and worth one finding covering all of them rather than twelve separate ones.
- Font weight one step off (600 vs 700) — often a missing font file being synthesized by the browser.
- Border radius zero on the live side — a dropped style, very visible to users.

## Severity ordering for the report

1. Element missing or not rendered
2. Wrong color (text, background, border)
3. Wrong typography (family, size, weight)
4. Wrong spacing (padding, gap, margin)
5. Wrong radius, shadow, opacity
6. Everything else
