> Use when: a screenshot, bug report or ticket names a part of <Site> and you need the page, how to reach it, and a selector that works, for FE QA, test cases, automation or a checker URL. Copy this file to `<site>.md`, fill it in, and add it to Step 1 in SKILL.md.

# Feature map: <Site>

One section per screen or step. Keep it to what a tester needs to find the
thing and touch it. Update it whenever a run shows the page changed.

## Sites

| Site | PROD | Preview / staging | Notes |
|---|---|---|---|
| <Site> | `https://www.example.com` | `https://preview.example.com` | cookie banner must be accepted first |

## <Screen or step name>

- **Reach it:** <URL or click path from the homepage, plus login if needed>
- **You see:** <what is on screen, in the words a bug report would use>
- **Controls:**

  | Element | Locator (see xpath-locators.md) | Notes |
  |---|---|---|
  | Username field | `//input[@id='user-name']` | |
  | Login button | `//input[@id='login-button']` | text differs per language |

- **Known quirks:** <lazy loading, animations, A/B variants, text that differs per locale>
- **Covered by:** <spec file / checker / test case IDs>

## Example (public demo site)

### SauceDemo: Inventory

- **Reach it:** log in at `https://www.saucedemo.com/` with a demo user.
- **You see:** a grid of products with name, price, image and an "Add to cart" button; a sort dropdown top right; a cart icon with a badge.
- **Controls:**

  | Element | Locator | Notes |
  |---|---|---|
  | Product name | `//div[@data-test='inventory-item-name']` | one per product |
  | Sort dropdown | `//select[@data-test='product-sort-container']` | default Name (A to Z) |
  | Cart badge | `//span[@class='shopping_cart_badge']` | only exists when the cart is not empty |

- **Known quirks:** the cart keeps its items after a reload (local storage).
- **Covered by:** `tests/inventory.spec.js`
