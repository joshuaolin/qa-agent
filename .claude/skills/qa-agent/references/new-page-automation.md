> Use when: automating a new page or feature in the POM style. Break the page into POM elements, register it, add test data, write a `.spec.js` per feature. The examples use the public demo site https://www.saucedemo.com/.

# New page → POM → spec

The only input this needs is the page (URL, plus login if it has one) and
the features to cover. Everything below is how the agent turns that into code.

## The layers

| Layer | File | Job |
|---|---|---|
| Actions | `main/ActionDriver.js` | Every generic action, once: `navigateURL`, `clickElement`, `setText`, `hoverElement`, `verifyTitle`, `assertElementDisplayed`, `assertElementContainsText` (all soft), plus `ActionDriver.verifyStep` / `ActionDriver.assertNoSoftFailures` (the gate, see "Double soft assertion"). New kind of action → add it here first |
| Site folder | `tests/<Site>/`, `pom/<Site>/`, `resources/<Site>/`, and `main/<Site>/` for a site engine | **Every new website gets its own folder in each layer**, named after the site, so another QA can copy or drop it whole. Nothing site-specific goes loose in `tests/`, `pom/` or `resources/`; the only shared edit is the page registration in `main/PageInitialize.js` |
| Pages | `pom/<Site>/<Name>Page.js` | One class per page. Each element is a static object: its `locator` plus only the actions the tests use on it, all delegating to `ActionDriver` |
| Registry | `main/PageInitialize.js` | Calls `<Name>Page.initialize(page)` for every page |
| Hooks | `main/Hooks.js` | `beforeEach`: extra timeout, initialize pages. `afterEach`: screenshot + report attachment on failure |
| Data | `resources/<Site>/testdata.json` | Named arrays per scenario: `validCredentials`, `invalidCredentials`, … |
| Tests | `tests/<Site>/<feature>.spec.js` | One `test.describe` per feature, data-driven with `forEach`, `test.step` for an action, `ActionDriver.verifyStep` for a verify |

## Recipe

1. **Dissect the page** (use the feature map if the site has one). List what
   the tests touch, and nothing else. Name each element as PascalCase thing +
   type: `UserNameTextfield`, `LoginButton`, `ErrorMessage`, `CartBadge`, `Title`.
2. **Write each locator** with the patterns in [xpath-locators.md](xpath-locators.md).
   Each one must match exactly one element.
3. **Missing action?** Add it to `ActionDriver` (one method, same shape as the
   others) before using it in a page.
4. **Write the page** `pom/<Site>/<Name>Page.js` (create the `<Site>/` folders first if the site is new):
   ```js
   import ActionDriver from '../../main/ActionDriver';

   class CartPage {
       static actiondriver;

       static initialize(page) {
           CartPage.actiondriver = new ActionDriver(page);
       }

       static CheckoutButton = {
           locator: "//button[@id='checkout']",
           clickElement: async function () {
               await CartPage.actiondriver.clickElement(this.locator);
           }
       };

       static ItemName = {
           locator: "//div[@data-test='inventory-item-name']",
           assertElementContainsText: async function (value) {
               await CartPage.actiondriver.assertElementContainsText(this.locator, value);
           }
       };
   }

   export default CartPage;
   ```
   Build every `locator` with the patterns in [xpath-locators.md](xpath-locators.md).
   The class name must equal the file name. Use `CartPage.actiondriver`, not
   `this`, inside the element methods (`this` there is the element object,
   which is how `this.locator` works).
5. **Register it** in `main/PageInitialize.js`: import it from `../pom/<Site>/CartPage`, then add
   `CartPage.initialize(page);`.
6. **Add data** to `resources/<Site>/testdata.json` as a named array per scenario.
   Real credentials go to `.env`, never this file.
7. **Write the spec** `tests/<Site>/<feature>.spec.js`:
   ```js
   import { test } from '@playwright/test';
   import ActionDriver from '../../main/ActionDriver';
   import initializePages from '../../main/PageInitialize';
   import LoginPage from '../../pom/SauceDemo/LoginPage';
   import HomePage from '../../pom/SauceDemo/HomePage';
   import CartPage from '../../pom/SauceDemo/CartPage';
   import '../../main/Hooks';
   import { validCredentials } from '../../resources/SauceDemo/testdata.json';

   async function login(page, { username, password }) {
       const actiondriver = new ActionDriver(page);
       await actiondriver.navigateURL('https://www.saucedemo.com/');
       await LoginPage.UserNameTextfield.setText(username);
       await LoginPage.PasswordTextfield.setText(password);
       await LoginPage.LoginButton.clickElement();
       return actiondriver;
   }

   test.beforeEach(async ({ page }) => {
       await initializePages(page);
   });

   test.describe('Cart', () => {
       test.beforeEach(async ({ page }) => {
           await login(page, validCredentials[0]);
       });

       test('Cart lists the added product', async () => {
           await test.step('Add the backpack and open the cart', async () => {
               await HomePage.AddToCartButton.clickElement('sauce-labs-backpack');
               await HomePage.CartLink.clickElement();
           });
           await ActionDriver.verifyStep('Verify the cart lists the backpack', async () => {
               await CartPage.ItemName.assertElementContainsText('Sauce Labs Backpack');
           });
       });
   });
   ```
8. **Run it live and fix what fails** before handing it back (see Run and report).

## Spec conventions

- **One `test.describe` per feature** (Login, Add to Cart, Cart). Two features
  in one file, two describes. The report then shows which feature broke.
- **Data-driven:** `data.forEach((item, index) => test(\`<Scenario> ${index + 1}\`, …))`.
  The title must say the scenario (valid vs invalid) and be unique.
- **Steps:** `test.step('<do something>')` then `ActionDriver.verifyStep('Verify <outcome>', …)`.
- **Double soft assertion (the standard).** Every ActionDriver assertion is
  `expect.soft`, so all checks in a Verify step run and every mismatch is
  reported in one run (layer 1). `ActionDriver.verifyStep` ends the step with
  `assertNoSoftFailures()`, a hard gate that stops the test before the next
  action works on a broken page (layer 2). A check inside an action step
  that the next action depends on (a badge before Reset, the URL after a
  Back click) is followed by `ActionDriver.assertNoSoftFailures()` right
  there. If your `main/ActionDriver.js` doesn't have these yet, add them
  first (import `test` too: `import { expect, test } from '@playwright/test';`),
  and switch each `await expect(` in its assertion methods to
  `await expect.soft(`:
  ```js
  static async verifyStep(title, body) {
      await test.step(title, async () => {
          await body();
          ActionDriver.assertNoSoftFailures();
      }, { box: true });
  }

  static assertNoSoftFailures() {
      const failures = test.info().errors.map((error) => error.message);
      expect(failures, 'soft assertion failures in this test').toEqual([]);
  }
  ```
  `box: true` makes the report point at the spec line, not ActionDriver.
- **Repeated flow** (login) → a helper function in the spec. Once two specs
  need it, move it to a page method or ActionDriver.
- **Precondition** for a whole feature → `test.beforeEach` inside that describe.
- **Every POM spec adds its own top-level `test.beforeEach` calling
  `initializePages(page)`.** If hooks register on import, Node caches the
  module per worker, so only the first spec file a worker loads gets them.
  The next file's static pages keep a closed `page` ("Target page, context or
  browser has been closed" on `fill`).
- No comments in the code. `npm run validate` can enforce it.

## Don't break current scripts

Base files are shared with suites that may run unattended. Before touching
any of them, list who depends on what and keep their contract:

| File | Contract that must not change |
|---|---|
| `main/Hooks.js` | How it registers (on import vs a setup function), the timeout it adds, the failure screenshot. Callers silently lose these if it changes |
| `main/PageInitialize.js` | Only `initialize(page)` calls, nothing that can throw |
| `main/ActionDriver.js` | Add methods, never rename or change an existing one's signature. Assertions are soft (`expect.soft`) and `verifyStep` gates them; a new assertion follows the same shape |
| `resources/<Site>/testdata.json` | Rename an array only together with every spec that imports it |
| `playwright.config.js` | No new `globalSetup` that deletes folders, no change to retries or teardowns without [shared-change-regression.md](shared-change-regression.md) |

Proof a change kept the contract: `npm run validate`, then
`npx playwright test --list` (count changes only by the tests you added),
then one live run of an older suite that uses the same base files.

## Common mistakes

| Problem | Do instead |
|---|---|
| Using a data array without importing it; one loop pasted twice; invalid tests titled "valid" | import every array you use; one loop per scenario, titled by it |
| Expected text typed from memory (`"Swag Labz"`) | copy expected text from the live page |
| A page file that is a copy of another page, class name not matching the file | class name = file name, only that page's elements |
| `describe` name that doesn't match what the tests do | describe name says the feature under test |

## Run and report

```
npx playwright test tests/<Site>/<feature>.spec.js --project=chromium --headed
npx playwright test tests/<Site>/<feature>.spec.js --project=chromium
```

Done when the spec passes live, a failing case shows its screenshot in the
report, and `npm run validate` is green. Then commit (one commit per feature).
