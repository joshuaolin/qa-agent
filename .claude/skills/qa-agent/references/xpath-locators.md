> Use when: writing a new POM `locator`, or a locator broke (timeout waiting for element, strict-mode "resolved to N elements", element not visible) and needs healing. Every XPath in `pom/` is built from the patterns below and nothing else.

# XPath locators and self-healing

## Allowed patterns

`*` = the preferred four. Try those first; use the others only when none of the four gives a unique match.

| Pattern | Shape | Example |
|---|---|---|
| \* Attribute | `//<tag>[@<attr>='<value>']` | `//button[@id='checkout']` |
| \* Contains text | `//<tag>[contains(text(),'<value>')]` | `//button[contains(text(),'Add to cart')]` |
| Contains attribute | `//<tag>[contains(@<attr>,'<value>')]` | `//div[contains(@class,'inventory_item')]` |
| \* Parent | `//<tag>[@<attr>='<value>']/parent::<tag>` | `//div[@data-test='inventory-item-name']/parent::a` |
| Ancestor | `//<tag>[@<attr>='<value>']/ancestor::<tag>[<index>]` | `//button[@id='add-to-cart']/ancestor::div[1]` |
| Preceding sibling | `//<tag>[@<attr>='<value>']/preceding-sibling::<tag>` | `//div[@class='pricebar']/preceding-sibling::div` |
| \* Following sibling | `//<tag>[@<attr>='<value>']/following-sibling::<tag>` | `//label[contains(text(),'Email')]/following-sibling::input` |

Always a real tag, never `//*`. Single quotes inside, because the locator sits in a double-quoted JS string. No absolute paths (`/html/body/div[2]/…`), no bare position indexes (`(//div)[3]`), no CSS, no `getByRole`, in `pom/`.

## Which attribute to anchor on

Most stable first: `data-test` / `data-testid` → `id` → `name` → `aria-label` / `placeholder` / `type` → visible text → `class` (with `contains`, since class lists change). If the element itself has nothing stable, anchor on a stable neighbour and walk with parent / ancestor / sibling.

## Healing a broken locator

1. Read the failure: which page object and element (`CartPage.CartItemName`), and why (not found, N matches, hidden).
2. Open the live page at that step (`--headed`, or Playwright inspector / DOM snapshot) and look at the element and its neighbours.
3. Rebuild it with the first pattern from the table that matches **exactly one** visible element. Check the count in the console: `$x("<xpath>").length === 1`.
4. Change only that element's `locator` string in its `pom/<Name>Page.js`. Don't touch the methods, the element name, or other pages.
5. Rerun the spec that failed, plus every spec that uses that page (`grep -r "<Name>Page" tests`). If the page is shared by more than one site, follow [shared-change-regression.md](shared-change-regression.md).
6. Report one line: element, old locator → new locator, the attribute it now anchors on.

Never heal by adding waits, `force: true`, or widening to a pattern that matches several elements and taking the first.
