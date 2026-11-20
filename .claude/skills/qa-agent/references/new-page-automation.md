> Use when: automating a new page or feature in the POM style. Break the page into POM elements, register it, add test data, write a `.spec.js` per feature. The examples use the public demo site https://www.saucedemo.com/.

# New page → POM → spec

The only input this needs is the page (URL, plus login if it has one) and
the features to cover. Everything below is how the agent turns that into code.

## The layers

| Layer | File | Job |
|---|---|---|
| Actions | `main/ActionDriver.js` | Every generic action, once: `navigateURL`, `clickElement`, `setText`, `hoverElement`, `verifyTitle`, `assertElementDisplayed`, `assertElementContainsText`. New kind of action → add it here first |
| Pages | `pom/<Name>Page.js` | One class per page. Each element is a static object: its `locator` plus only the actions the tests use on it, all delegating to `ActionDriver` |
| Registry | `main/PageInitialize.js` | Calls `<Name>Page.initialize(page)` for every page |
| Hooks | `main/Hooks.js` | `beforeEach`: extra timeout, initialize pages. `afterEach`: screenshot + report attachment on failure |
| Data | `resources/testdata.json` | Named arrays per scenario: `validCredentials`, `invalidCredentials`, … |
| Tests | `tests/<feature>.spec.js` | One `test.describe` per feature, data-driven with `forEach`, `test.step` for action then verify |

## Recipe

1. **Dissect the page** (use the feature map if the site has one). List what
   the tests touch, and nothing else. Name each element as PascalCase thing +
   type: `UserNameTextfield`, `LoginButton`, `ErrorMessage`, `CartBadge`, `Title`.
2. **Write each locator** with the patterns in [xpath-locators.md](xpath-locators.md).
   Each one must match exactly one element.
3. **Missing action?** Add it to `ActionDriver` (one method, same shape as the
   others) before using it in a page.
4. **Write the page** `pom/<Name>Page.js`:
   ```js
   import ActionDriver from '../main/ActionDriver';

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
   The class name must equal the file name. Use `CartPage.actiondriver`, not
   `this`, inside the element methods (`this` there is the element object,
   which is how `this.locator` works).
5. **Register it** in `main/PageInitialize.js`: import it, then add
   `CartPage.initialize(page);`.
6. **Add data** to `resources/testdata.json` as a named array per scenario.
   Real credentials go to `.env`, never this file.
7. **Write the spec** `tests/<feature>.spec.js`:
   ```js
   import { test } from '@playwright/test';
   import ActionDriver from '../main/ActionDriver';
   import initializePages from '../main/PageInitialize';
   import LoginPage from '../pom/LoginPage';
   import CartPage from '../pom/CartPage';
   import '../main/Hooks';
   import { validCredentials } from '../resources/testdata.json';

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

       test('Checkout from cart', async () => {
           await test.step('Open checkout', async () => {
               await CartPage.CheckoutButton.clickElement();
           });
           await test.step('Verify checkout page', async () => {
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
- **Steps:** `test.step('<do something>')` then `test.step('Verify <outcome>')`.
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
| `main/ActionDriver.js` | Add methods, never rename or change an existing one's signature |
| `resources/testdata.json` | Rename an array only together with every spec that imports it |
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
npx playwright test tests/<feature>.spec.js --project=chromium --headed
npx playwright test tests/<feature>.spec.js --project=chromium
```

Done when the spec passes live, a failing case shows its screenshot in the
report, and `npm run validate` is green. Then commit (one commit per feature).
