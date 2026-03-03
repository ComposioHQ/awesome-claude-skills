# Migrating from Selenium to Playwright

> **When to use**: When converting a Selenium/WebDriver test suite to Playwright. Covers Java/Python/C# Selenium idioms mapped to TypeScript and JavaScript Playwright equivalents.
> **Prerequisites**: [core/locators.md](../core/locators.md), [core/assertions-and-waiting.md](../core/assertions-and-waiting.md)

## Key Mindset Shifts

Before translating any code, internalize these six changes. They are not syntax swaps -- they are fundamental differences in how Playwright works.

### 1. No More Explicit Waits

Selenium requires `WebDriverWait` and `ExpectedConditions` on nearly every interaction. Playwright auto-waits on every action (`click`, `fill`, `check`, `selectOption`) and every web-first assertion (`expect(locator).toBeVisible()`). Delete all your waits. They are not needed.

```
Selenium:  WebDriverWait + ExpectedConditions.visibilityOfElementLocated(...)
Playwright: nothing — auto-waiting is built into every action and assertion
```

### 2. No WebDriver Protocol Overhead

Selenium sends every command over the WebDriver (W3C) HTTP protocol -- each click, each find, each assertion is a round-trip HTTP request. Playwright communicates over CDP (Chromium), the DevTools protocol (Firefox), or native WebKit protocol. This is a persistent bidirectional connection, not request-response. Tests are faster by default.

### 3. No Driver Management

Selenium requires matching browser drivers (`chromedriver`, `geckodriver`) to browser versions. Version mismatches are a constant source of CI failures. Playwright bundles browser binaries. One command installs everything:

```bash
npx playwright install
```

No `WebDriverManager`. No `chromedriver` path. No version matrix.

### 4. No Implicit vs Explicit Wait Confusion

Selenium has implicit waits (global, apply to all `findElement` calls), explicit waits (`WebDriverWait`), and `Thread.sleep()` / `time.sleep()`. Teams mix these, creating unpredictable timing behavior. Playwright has one mechanism: auto-waiting. Every action waits for the element to be actionable. Every web-first assertion retries until timeout. There is nothing to configure.

### 5. Locators Are Lazy and Auto-Retry

In Selenium, `findElement()` immediately queries the DOM and returns a `WebElement` reference. If the DOM changes, that reference is stale and throws `StaleElementReferenceException`. In Playwright, `page.locator()` returns a lazy locator that re-queries the DOM on every action. There is no stale element. There is no `StaleElementReferenceException`. Ever.

### 6. Built-In Test Runner

Selenium is a browser automation library, not a test framework. You need JUnit, TestNG, pytest, or Mocha on top. Playwright Test is a full test runner with parallel execution, retries, fixtures, HTML reports, trace viewer, and UI mode. No assembly required.

## API Mapping Table

Every Selenium API and its direct Playwright equivalent. The "Notes" column calls out behavior differences.

### Navigation

| Selenium WebDriver | Playwright | Notes |
|---|---|---|
| `driver.get(url)` | `await page.goto(url)` | Playwright waits for `load` event by default; configurable via `waitUntil` |
| `driver.navigate().to(url)` | `await page.goto(url)` | Same as above |
| `driver.navigate().back()` | `await page.goBack()` | Waits for navigation to complete |
| `driver.navigate().forward()` | `await page.goForward()` | Waits for navigation to complete |
| `driver.navigate().refresh()` | `await page.reload()` | Waits for `load` event |
| `driver.getCurrentUrl()` | `page.url()` | Synchronous in Playwright -- no await needed |
| `driver.getTitle()` | `await page.title()` | Or use `await expect(page).toHaveTitle('...')` for assertion |

### Element Location

| Selenium WebDriver | Playwright | Notes |
|---|---|---|
| `driver.findElement(By.id("x"))` | `page.locator('#x')` or `page.getByTestId('x')` | Prefer `getByRole()` or `getByTestId()` over ID selectors |
| `driver.findElement(By.css("x"))` | `page.locator('x')` | CSS selectors work, but prefer semantic locators |
| `driver.findElement(By.xpath("x"))` | `page.locator('xpath=x')` | Works but avoid XPath; use `getByRole()`, `getByLabel()`, `getByText()` |
| `driver.findElement(By.name("x"))` | `page.locator('[name="x"]')` | Or `page.getByLabel()` if the field has a label |
| `driver.findElement(By.linkText("x"))` | `page.getByRole('link', { name: 'x' })` | Role-based is more resilient |
| `driver.findElement(By.partialLinkText("x"))` | `page.getByRole('link', { name: /x/ })` | Regex for partial match |
| `driver.findElement(By.className("x"))` | `page.locator('.x')` | Class selectors are fragile; prefer semantic locators |
| `driver.findElement(By.tagName("x"))` | `page.locator('x')` | Rarely useful alone; combine with role or text |
| `driver.findElements(By.css("x"))` | `await page.locator('x').all()` | Returns array of locators; or use `toHaveCount()` to assert count |

### Element Interaction

| Selenium WebDriver | Playwright | Notes |
|---|---|---|
| `element.click()` | `await locator.click()` | Auto-waits for element to be visible, stable, enabled, and unobscured |
| `element.sendKeys("text")` | `await locator.fill("text")` | **Behavior change**: `fill()` clears existing text first, then sets the value. Use `pressSequentially()` to type character by character. |
| `element.sendKeys(Keys.ENTER)` | `await locator.press('Enter')` | Or `await page.keyboard.press('Enter')` |
| `element.clear()` | `await locator.clear()` | Or `await locator.fill('')` |
| `element.submit()` | `await locator.press('Enter')` | No direct equivalent; click the submit button or press Enter |
| `new Select(element).selectByVisibleText("x")` | `await locator.selectOption({ label: 'x' })` | Also supports `{ value: 'x' }` and `{ index: 0 }` |
| `element.isDisplayed()` | `await expect(locator).toBeVisible()` | Use assertion form -- it auto-retries. `locator.isVisible()` does not retry. |
| `element.isEnabled()` | `await expect(locator).toBeEnabled()` | Use assertion form for reliability |
| `element.isSelected()` | `await expect(locator).toBeChecked()` | For checkboxes and radio buttons |
| `element.getText()` | `await locator.textContent()` | Or prefer `await expect(locator).toHaveText('...')` which auto-retries |
| `element.getAttribute("x")` | `await locator.getAttribute('x')` | Or `await expect(locator).toHaveAttribute('x', 'value')` |
| `element.getCssValue("x")` | `await expect(locator).toHaveCSS('x', 'value')` | Use assertion form; computed values only |

### Waits and Conditions

| Selenium WebDriver | Playwright | Notes |
|---|---|---|
| `WebDriverWait(driver, 10).until(...)` | Not needed | Playwright auto-waits on all actions and assertions |
| `ExpectedConditions.visibilityOfElementLocated(...)` | `await expect(locator).toBeVisible()` | Built into every action; use assertion only when you need to verify visibility explicitly |
| `ExpectedConditions.elementToBeClickable(...)` | Not needed | `click()` auto-waits for clickability |
| `ExpectedConditions.presenceOfElementLocated(...)` | `await expect(locator).toBeAttached()` | Rarely needed; most actions wait for attachment automatically |
| `ExpectedConditions.invisibilityOfElementLocated(...)` | `await expect(locator).not.toBeVisible()` | Auto-retries until element disappears |
| `ExpectedConditions.textToBePresentInElement(...)` | `await expect(locator).toHaveText('...')` | Auto-retries until text matches |
| `ExpectedConditions.titleIs("x")` | `await expect(page).toHaveTitle('x')` | Auto-retries |
| `ExpectedConditions.urlContains("x")` | `await expect(page).toHaveURL(/x/)` | Or `await page.waitForURL('**/x')` |
| `ExpectedConditions.alertIsPresent()` | `page.on('dialog', ...)` or `page.waitForEvent('dialog')` | Register handler before the action that triggers the dialog |
| `Thread.sleep(5000)` / `time.sleep(5)` | Never | Delete it. Use auto-waiting assertions instead. |
| `driver.manage().timeouts().implicitlyWait(10)` | Not needed | No implicit waits in Playwright -- auto-waiting handles everything |

### Frames and Windows

| Selenium WebDriver | Playwright | Notes |
|---|---|---|
| `driver.switchTo().frame("name")` | `page.frameLocator('iframe[name="name"]')` | No context switching; chain locators directly into the frame |
| `driver.switchTo().frame(element)` | `page.frameLocator('iframe#id')` | Target the iframe by any CSS selector |
| `driver.switchTo().defaultContent()` | Not needed | No frame switching in Playwright; each `frameLocator` is scoped |
| `driver.switchTo().parentFrame()` | Not needed | No frame switching to undo |
| `driver.switchTo().window(handle)` | `context.pages()` | Access all pages in the context by index |
| `driver.getWindowHandle()` | Not needed | Use `page` references directly |
| `driver.getWindowHandles()` | `context.pages()` | Returns array of all open pages |
| New window/tab opened by click | `page.waitForEvent('popup')` | Register before the click; returns the new `Page` object |

### Browser and Context

| Selenium WebDriver | Playwright | Notes |
|---|---|---|
| `driver.manage().window().setSize(w, h)` | `await page.setViewportSize({ width: w, height: h })` | Sets the viewport, not the OS window |
| `driver.manage().window().maximize()` | Configure in `playwright.config` `use.viewport` | Or pass `--headed` with large viewport |
| `driver.manage().addCookie(cookie)` | `await context.addCookies([cookie])` | Takes an array; operates on the browser context |
| `driver.manage().getCookieNamed("x")` | `await context.cookies()` then filter | Returns all cookies; filter in JS |
| `driver.manage().deleteAllCookies()` | `await context.clearCookies()` | Clears all cookies in the context |
| `driver.executeScript("return ...")` | `await page.evaluate(() => { ... })` | Full access to browser JS context; supports return values |
| `driver.executeAsyncScript(...)` | `await page.evaluate(async () => { ... })` | `evaluate` supports async functions natively |
| `driver.getScreenshotAs(OutputType.FILE)` | `await page.screenshot({ path: 'shot.png' })` | Also supports `fullPage: true`, element screenshots via `locator.screenshot()` |
| `driver.quit()` | Handled automatically | Playwright Test manages browser lifecycle. No manual cleanup. |

### Actions Class

| Selenium WebDriver | Playwright | Notes |
|---|---|---|
| `new Actions(driver).moveToElement(el).perform()` | `await locator.hover()` | Single method, auto-waits |
| `new Actions(driver).doubleClick(el).perform()` | `await locator.dblclick()` | Single method, auto-waits |
| `new Actions(driver).contextClick(el).perform()` | `await locator.click({ button: 'right' })` | Right-click option |
| `new Actions(driver).dragAndDrop(src, tgt).perform()` | `await source.dragTo(target)` | Both are locators |
| `new Actions(driver).keyDown(Keys.SHIFT).click(el).keyUp(Keys.SHIFT).perform()` | `await locator.click({ modifiers: ['Shift'] })` | Modifier keys as option |
| `new Actions(driver).sendKeys(Keys.chord(Keys.CONTROL, "a")).perform()` | `await page.keyboard.press('Control+a')` | Keyboard API for global shortcuts |
| `new Actions(driver).moveByOffset(x, y).perform()` | `await page.mouse.move(x, y)` | Raw mouse API for canvas/map interactions |

## Before/After Examples

### Example 1: Login Test

The most common Selenium test. Notice the complete absence of explicit waits in the Playwright version.

**Selenium (Java)**
```java
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.junit.jupiter.api.*;

public class LoginTest {
    WebDriver driver;

    @BeforeEach
    void setUp() {
        System.setProperty("webdriver.chrome.driver", "/path/to/chromedriver");
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
    }

    @AfterEach
    void tearDown() {
        if (driver != null) driver.quit();
    }

    @Test
    void userCanLogIn() {
        driver.get("https://myapp.com/login");

        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

        WebElement emailField = wait.until(
            ExpectedConditions.visibilityOfElementLocated(By.id("email"))
        );
        emailField.clear();
        emailField.sendKeys("user@example.com");

        WebElement passwordField = driver.findElement(By.id("password"));
        passwordField.clear();
        passwordField.sendKeys("s3cure!Pass");

        WebElement loginButton = wait.until(
            ExpectedConditions.elementToBeClickable(By.cssSelector("button[type='submit']"))
        );
        loginButton.click();

        wait.until(ExpectedConditions.urlContains("/dashboard"));

        WebElement heading = wait.until(
            ExpectedConditions.visibilityOfElementLocated(By.tagName("h1"))
        );
        Assertions.assertEquals("Dashboard", heading.getText());
    }
}
```

**Playwright (TypeScript)**
```typescript
import { test, expect } from '@playwright/test';

test('user can log in', async ({ page }) => {
  await page.goto('/login');

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('s3cure!Pass');
  await page.getByRole('button', { name: 'Sign In' }).click();

  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Dashboard');
});
```

**Playwright (JavaScript)**
```javascript
const { test, expect } = require('@playwright/test');

test('user can log in', async ({ page }) => {
  await page.goto('/login');

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('s3cure!Pass');
  await page.getByRole('button', { name: 'Sign In' }).click();

  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Dashboard');
});
```

**What changed**: 45 lines of Java with explicit waits, driver management, and element references became 9 lines of Playwright. No setup, no teardown, no waits, no driver path. The `fill()` call replaces `clear()` + `sendKeys()`. Semantic locators (`getByLabel`, `getByRole`) replace brittle `By.id` and `By.cssSelector`.

---

### Example 2: Search and Verify Results

Demonstrates replacing `findElements()`, explicit waits for result count, and text assertions.

**Selenium (Java)**
```java
@Test
void searchReturnsResults() {
    driver.get("https://myapp.com/products");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

    WebElement searchBox = wait.until(
        ExpectedConditions.visibilityOfElementLocated(By.cssSelector("input[placeholder='Search products']"))
    );
    searchBox.clear();
    searchBox.sendKeys("wireless headphones");
    searchBox.sendKeys(Keys.ENTER);

    wait.until(ExpectedConditions.numberOfElementsToBeMoreThan(
        By.cssSelector(".product-card"), 0
    ));

    List<WebElement> results = driver.findElements(By.cssSelector(".product-card"));
    Assertions.assertTrue(results.size() >= 3);

    String firstTitle = results.get(0).findElement(By.cssSelector(".product-title")).getText();
    Assertions.assertTrue(firstTitle.toLowerCase().contains("wireless"));
}
```

**Playwright (TypeScript)**
```typescript
import { test, expect } from '@playwright/test';

test('search returns results', async ({ page }) => {
  await page.goto('/products');

  await page.getByPlaceholder('Search products').fill('wireless headphones');
  await page.getByPlaceholder('Search products').press('Enter');

  const results = page.getByTestId('product-card');
  await expect(results).toHaveCount(3, { timeout: 10_000 });

  await expect(results.first().getByTestId('product-title')).toContainText(/wireless/i);
});
```

**Playwright (JavaScript)**
```javascript
const { test, expect } = require('@playwright/test');

test('search returns results', async ({ page }) => {
  await page.goto('/products');

  await page.getByPlaceholder('Search products').fill('wireless headphones');
  await page.getByPlaceholder('Search products').press('Enter');

  const results = page.getByTestId('product-card');
  await expect(results).toHaveCount(3, { timeout: 10_000 });

  await expect(results.first().getByTestId('product-title')).toContainText(/wireless/i);
});
```

**What changed**: No `WebDriverWait` for element visibility. No `clear()` before `sendKeys()`. No `findElements()` returning a stale list. The Playwright `toHaveCount()` auto-retries until the results appear. The regex assertion on `toContainText` replaces manual `getText()` + `toLowerCase()` + `contains()`.

---

### Example 3: Working with Iframes

Selenium's frame switching is stateful and error-prone. Playwright's `frameLocator` is scoped and stateless.

**Selenium (Java)**
```java
@Test
void fillPaymentFormInIframe() {
    driver.get("https://myapp.com/checkout");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

    // Switch into the payment iframe
    wait.until(ExpectedConditions.frameToBeAvailableAndSwitchToIt(
        By.cssSelector("iframe#payment-frame")
    ));

    // Now inside the iframe context
    WebElement cardNumber = wait.until(
        ExpectedConditions.visibilityOfElementLocated(By.id("card-number"))
    );
    cardNumber.sendKeys("4242424242424242");

    driver.findElement(By.id("expiry")).sendKeys("12/28");
    driver.findElement(By.id("cvc")).sendKeys("123");

    // Switch back to main content before interacting with the page
    driver.switchTo().defaultContent();

    driver.findElement(By.id("place-order")).click();

    wait.until(ExpectedConditions.visibilityOfElementLocated(
        By.cssSelector(".confirmation-message")
    ));
}
```

**Playwright (TypeScript)**
```typescript
import { test, expect } from '@playwright/test';

test('fill payment form in iframe', async ({ page }) => {
  await page.goto('/checkout');

  // No switching — just scope into the frame
  const paymentFrame = page.frameLocator('#payment-frame');
  await paymentFrame.getByLabel('Card number').fill('4242424242424242');
  await paymentFrame.getByLabel('Expiry').fill('12/28');
  await paymentFrame.getByLabel('CVC').fill('123');

  // No switching back — main page locators still work
  await page.getByRole('button', { name: 'Place order' }).click();

  await expect(page.getByText('Order confirmed')).toBeVisible();
});
```

**Playwright (JavaScript)**
```javascript
const { test, expect } = require('@playwright/test');

test('fill payment form in iframe', async ({ page }) => {
  await page.goto('/checkout');

  const paymentFrame = page.frameLocator('#payment-frame');
  await paymentFrame.getByLabel('Card number').fill('4242424242424242');
  await paymentFrame.getByLabel('Expiry').fill('12/28');
  await paymentFrame.getByLabel('CVC').fill('123');

  await page.getByRole('button', { name: 'Place order' }).click();

  await expect(page.getByText('Order confirmed')).toBeVisible();
});
```

**What changed**: No `switchTo().frame()`. No `switchTo().defaultContent()`. No risk of forgetting to switch back. Playwright's `frameLocator` scopes into the iframe without changing the driver's global state. You can interact with the main page and the iframe in any order.

---

### Example 4: Handling Popups and New Windows

Selenium window handle management is notoriously fragile. Playwright makes it declarative.

**Selenium (Java)**
```java
@Test
void handlePopupWindow() {
    driver.get("https://myapp.com/settings");

    String originalWindow = driver.getWindowHandle();

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

    driver.findElement(By.linkText("Connect OAuth Provider")).click();

    // Wait for new window to appear
    wait.until(ExpectedConditions.numberOfWindowsToBe(2));

    // Find and switch to the new window
    for (String handle : driver.getWindowHandles()) {
        if (!handle.equals(originalWindow)) {
            driver.switchTo().window(handle);
            break;
        }
    }

    // Interact with the popup
    wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("authorize-btn")));
    driver.findElement(By.id("authorize-btn")).click();

    // Wait for popup to close and switch back
    wait.until(ExpectedConditions.numberOfWindowsToBe(1));
    driver.switchTo().window(originalWindow);

    wait.until(ExpectedConditions.visibilityOfElementLocated(
        By.cssSelector(".connection-status.success")
    ));
}
```

**Playwright (TypeScript)**
```typescript
import { test, expect } from '@playwright/test';

test('handle popup window', async ({ page }) => {
  await page.goto('/settings');

  // Register listener BEFORE the click that opens the popup
  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Connect OAuth Provider' }).click();
  const popup = await popupPromise;

  // Interact with the popup — it's just another Page object
  await popup.getByRole('button', { name: 'Authorize' }).click();

  // Popup closes automatically; verify result on original page
  await expect(page.getByText('Connected successfully')).toBeVisible();
});
```

**Playwright (JavaScript)**
```javascript
const { test, expect } = require('@playwright/test');

test('handle popup window', async ({ page }) => {
  await page.goto('/settings');

  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Connect OAuth Provider' }).click();
  const popup = await popupPromise;

  await popup.getByRole('button', { name: 'Authorize' }).click();

  await expect(page.getByText('Connected successfully')).toBeVisible();
});
```

**What changed**: No window handle iteration. No `switchTo()`. No tracking original vs new window. The popup is a `Page` object you interact with directly. When it closes, you just continue using the original `page`. The `waitForEvent('popup')` pattern is declarative and race-condition-free.

---

### Example 5: Drag and Drop with Actions

Selenium's `Actions` class requires chaining and `perform()`. Playwright has direct methods.

**Selenium (Java)**
```java
@Test
void dragAndDropTask() {
    driver.get("https://myapp.com/kanban");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

    WebElement sourceCard = wait.until(
        ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//div[@class='card' and contains(text(),'Fix login bug')]")
        )
    );
    WebElement targetColumn = driver.findElement(
        By.xpath("//div[@class='column' and .//h2[text()='Done']]")
    );

    Actions actions = new Actions(driver);
    actions.dragAndDrop(sourceCard, targetColumn).perform();

    // Verify the card moved
    WebElement doneColumn = driver.findElement(
        By.xpath("//div[@class='column' and .//h2[text()='Done']]")
    );
    WebElement movedCard = doneColumn.findElement(
        By.xpath(".//div[@class='card' and contains(text(),'Fix login bug')]")
    );
    Assertions.assertTrue(movedCard.isDisplayed());
}
```

**Playwright (TypeScript)**
```typescript
import { test, expect } from '@playwright/test';

test('drag and drop task to done column', async ({ page }) => {
  await page.goto('/kanban');

  const card = page.getByText('Fix login bug');
  const doneColumn = page.getByRole('heading', { name: 'Done' }).locator('..');

  await card.dragTo(doneColumn);

  // Verify card is now inside the Done column
  await expect(doneColumn.getByText('Fix login bug')).toBeVisible();
});
```

**Playwright (JavaScript)**
```javascript
const { test, expect } = require('@playwright/test');

test('drag and drop task to done column', async ({ page }) => {
  await page.goto('/kanban');

  const card = page.getByText('Fix login bug');
  const doneColumn = page.getByRole('heading', { name: 'Done' }).locator('..');

  await card.dragTo(doneColumn);

  await expect(doneColumn.getByText('Fix login bug')).toBeVisible();
});
```

**What changed**: No `Actions` class. No `perform()`. No XPath for finding elements. `dragTo()` is a single method call on a locator. The verification uses scoped locators instead of XPath ancestor traversal.

## Migration Steps

A practical, ordered checklist for converting a Selenium suite to Playwright.

### Step 1: Set Up Playwright Alongside Selenium

Do not rip out Selenium on day one. Run both in parallel.

```bash
# Install Playwright in your existing project
npm init playwright@latest

# This creates:
# - playwright.config.ts (or .js)
# - tests/ directory
# - package.json dependencies
```

Configure `baseURL` in `playwright.config` to match your Selenium target:

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests-playwright', // separate from Selenium tests
  use: {
    baseURL: 'https://staging.myapp.com',
    trace: 'on-first-retry',
  },
  retries: process.env.CI ? 2 : 0,
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests-playwright',
  use: {
    baseURL: 'https://staging.myapp.com',
    trace: 'on-first-retry',
  },
  retries: process.env.CI ? 2 : 0,
});
```

### Step 2: Convert Page Objects First

If you have Selenium page objects, convert them to Playwright page objects. The pattern is similar but simpler.

**Selenium Page Object (Java)**
```java
public class LoginPage {
    private WebDriver driver;
    private WebDriverWait wait;

    private By emailField = By.id("email");
    private By passwordField = By.id("password");
    private By loginButton = By.cssSelector("button[type='submit']");
    private By errorMessage = By.cssSelector(".error-message");

    public LoginPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    public void login(String email, String password) {
        wait.until(ExpectedConditions.visibilityOfElementLocated(emailField));
        driver.findElement(emailField).clear();
        driver.findElement(emailField).sendKeys(email);
        driver.findElement(passwordField).clear();
        driver.findElement(passwordField).sendKeys(password);
        driver.findElement(loginButton).click();
    }

    public String getErrorMessage() {
        return wait.until(
            ExpectedConditions.visibilityOfElementLocated(errorMessage)
        ).getText();
    }
}
```

**Playwright Page Object (TypeScript)**
```typescript
// page-objects/login-page.ts
import { type Page, type Locator, expect } from '@playwright/test';

export class LoginPage {
  private readonly emailField: Locator;
  private readonly passwordField: Locator;
  private readonly loginButton: Locator;
  private readonly errorMessage: Locator;

  constructor(private readonly page: Page) {
    this.emailField = page.getByLabel('Email');
    this.passwordField = page.getByLabel('Password');
    this.loginButton = page.getByRole('button', { name: 'Sign In' });
    this.errorMessage = page.getByRole('alert');
  }

  async login(email: string, password: string) {
    await this.emailField.fill(email);
    await this.passwordField.fill(password);
    await this.loginButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toHaveText(message);
  }
}
```

**Playwright Page Object (JavaScript)**
```javascript
// page-objects/login-page.js
const { expect } = require('@playwright/test');

class LoginPage {
  constructor(page) {
    this.page = page;
    this.emailField = page.getByLabel('Email');
    this.passwordField = page.getByLabel('Password');
    this.loginButton = page.getByRole('button', { name: 'Sign In' });
    this.errorMessage = page.getByRole('alert');
  }

  async login(email, password) {
    await this.emailField.fill(email);
    await this.passwordField.fill(password);
    await this.loginButton.click();
  }

  async expectError(message) {
    await expect(this.errorMessage).toHaveText(message);
  }
}

module.exports = { LoginPage };
```

Key differences in page objects:
- Locators are defined in the constructor, not as `By` objects -- they are lazy and never go stale
- No `WebDriverWait` anywhere
- No `clear()` before `fill()`
- Assertions can live inside the page object (`expectError`) because they auto-retry

### Step 3: Convert Tests by Priority

Start with your most valuable and most flaky tests. Convert them in order:

1. **Smoke tests** -- highest value, run on every deploy
2. **Flaky tests** -- Playwright's auto-waiting eliminates most flakiness
3. **Slow tests** -- Playwright's parallelism and faster protocol make these faster
4. **Everything else** -- bulk conversion of the remaining suite

For each test, apply the API mapping table above. The mechanical translation is:
1. Remove all `WebDriverWait` and `ExpectedConditions`
2. Replace `findElement(By.xxx)` with semantic locators (`getByRole`, `getByLabel`, `getByText`)
3. Replace `sendKeys` with `fill` (or `pressSequentially` for character-by-character input)
4. Replace `Assert` / `assertEquals` with `expect(locator).toHaveText()` / `toBeVisible()` / etc.
5. Remove `setUp` and `tearDown` -- Playwright Test handles browser lifecycle
6. Remove `Thread.sleep()` / `time.sleep()` entirely

### Step 4: Replace Test Infrastructure

| Selenium Infrastructure | Playwright Equivalent |
|---|---|
| Selenium Grid / Hub | `npx playwright test --shard=1/4` (built-in sharding) |
| BrowserStack / SauceLabs | Often unnecessary; Playwright runs 3 browsers locally. Use for Safari on CI if needed. |
| WebDriverManager | `npx playwright install` (one command, all browsers) |
| TestNG XML suites | `playwright.config` `projects` array |
| JUnit @Tag / pytest marks | `test.describe()` grouping + `--grep` filtering |
| Allure / ExtentReports | Built-in HTML reporter (`npx playwright show-report`) + trace viewer |
| Screenshot on failure | Built-in: `use: { screenshot: 'only-on-failure' }` |
| Video recording | Built-in: `use: { video: 'on-first-retry' }` |

### Step 5: Remove Selenium

Once all tests pass in Playwright and have run green in CI for at least two weeks:

1. Delete Selenium test files
2. Remove Selenium dependencies (`selenium-webdriver`, `chromedriver`, `geckodriver`)
3. Remove Selenium Grid infrastructure
4. Update CI pipelines to run only Playwright
5. Remove `setUp` / `tearDown` boilerplate classes

## Common Gotchas

### Gotcha 1: `findElement` Throws, `locator()` Does Not

In Selenium, `driver.findElement(By.id("missing"))` throws `NoSuchElementException` immediately. In Playwright, `page.locator('#missing')` returns a locator object without querying the DOM. It only throws when you perform an action on it and the element does not appear within the timeout.

```typescript
// This does NOT throw — locators are lazy
const missing = page.locator('#does-not-exist');

// This throws after timeout — because the action waits and the element never appears
await missing.click(); // TimeoutError after actionTimeout
```

**Impact**: If your Selenium tests use try-catch around `findElement` to check element existence, replace with assertions:

```typescript
// Selenium pattern (do not replicate)
// try { driver.findElement(By.id("error")); fail(); } catch (NoSuchElementException e) { /* expected */ }

// Playwright equivalent
await expect(page.locator('#error')).not.toBeVisible();
```

### Gotcha 2: `sendKeys` Appends, `fill` Replaces

Selenium's `sendKeys("text")` appends to the existing value. If the field already contains "hello" and you `sendKeys("world")`, you get "helloworld". Playwright's `fill("text")` clears the field first, then sets the value. You get "text".

```typescript
// Selenium behavior: appends
// element.sendKeys("world"); // field: "helloworld"

// Playwright behavior: replaces
await locator.fill('world'); // field: "world"

// To replicate Selenium's append behavior:
await locator.pressSequentially('world'); // types each character, appending to existing value
```

### Gotcha 3: No StaleElementReferenceException

In Selenium, storing a `WebElement` reference and using it after the DOM changes throws `StaleElementReferenceException`. This is the single most common source of Selenium test flakiness.

```java
// Selenium — this can throw StaleElementReferenceException
WebElement button = driver.findElement(By.id("submit"));
// ... some action causes the DOM to re-render ...
button.click(); // BOOM — StaleElementReferenceException
```

In Playwright, locators re-query the DOM on every action. Store locators freely.

```typescript
// Playwright — this always works
const button = page.getByRole('button', { name: 'Submit' });
// ... some action causes the DOM to re-render ...
await button.click(); // Works — re-queries the DOM automatically
```

### Gotcha 4: No Global Driver State

Selenium has a single `driver` instance with global state: the current frame, the current window, implicit wait timeout. Calling `switchTo().frame()` changes state for all subsequent calls. Forgetting to `switchTo().defaultContent()` causes every following `findElement` to fail.

Playwright has no global state. `page.frameLocator()` returns a scoped object. `context.pages()` gives you all pages. Nothing changes the "current" context.

```typescript
// Selenium mental model: "Where am I now?"
// driver.switchTo().frame("payment"); // I'm in the payment frame
// driver.findElement(...);            // This looks in the payment frame
// driver.switchTo().defaultContent(); // Now I'm back in the main page
// ... forget this line and everything breaks

// Playwright mental model: "I always say exactly where I'm looking"
const paymentFrame = page.frameLocator('#payment');
await paymentFrame.getByLabel('Card').fill('4242...'); // scoped to frame
await page.getByRole('button', { name: 'Pay' }).click(); // main page — no switching
```

### Gotcha 5: Assertions Must Be Awaited

In Selenium (Java), assertions are synchronous: `assertEquals("Dashboard", heading.getText())`. In Playwright, web-first assertions are async and must be awaited:

```typescript
// WRONG — assertion runs detached, test may pass before it resolves
expect(page.getByRole('heading')).toHaveText('Dashboard'); // missing await!

// CORRECT
await expect(page.getByRole('heading')).toHaveText('Dashboard');
```

Missing `await` is the number one Playwright beginner mistake. Your linter should flag this. Enable `@typescript-eslint/no-floating-promises` or the Playwright ESLint plugin.

### Gotcha 6: Parallel by Default

Selenium tests typically run sequentially (one browser, one thread). Playwright Test runs test files in parallel by default. This means:

- Tests must be isolated -- no shared state between test files
- Each test gets its own browser context (fresh cookies, storage, session)
- Database fixtures must not collide between parallel tests

If your Selenium suite depends on execution order, you must fix that before migrating. See [core/test-organization.md](../core/test-organization.md) for isolation strategies.

## What's Better in Playwright

These are not just syntax differences. These are capabilities that Selenium does not have.

### Auto-Waiting Everywhere

Every action, every assertion, every navigation auto-waits. You write zero wait code. This alone eliminates 60-80% of Selenium test flakiness.

### Trace Viewer

When a test fails in CI, Playwright captures a trace: screenshots at every step, DOM snapshots, network requests, console logs. Open it with `npx playwright show-report` and step through the exact failure. Selenium has nothing comparable.

```typescript
// playwright.config.ts — enable traces on first retry
export default defineConfig({
  use: {
    trace: 'on-first-retry',
  },
});
```

### Built-In Parallel Execution

Playwright Test runs test files in parallel with zero configuration. No Selenium Grid. No TestNG parallel suite XML. No pytest-xdist.

```bash
# Run all tests in parallel (default)
npx playwright test

# Shard across CI machines
npx playwright test --shard=1/4  # machine 1
npx playwright test --shard=2/4  # machine 2
```

### Multiple Browsers, One API

The same test runs on Chromium, Firefox, and WebKit without code changes. Configure in `playwright.config`:

```typescript
export default defineConfig({
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
```

Selenium requires separate driver binaries and often browser-specific workarounds.

### Network Interception

Playwright can intercept, modify, and mock network requests natively. Selenium cannot.

```typescript
// Mock an API response — impossible in Selenium
await page.route('**/api/users', (route) => {
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{ name: 'Mock User' }]),
  });
});
```

### Browser Context Isolation

Each test gets a fresh browser context (like an incognito window). Cookies, localStorage, and sessions are isolated between tests without restarting the browser. Selenium requires `driver.quit()` and `new ChromeDriver()` for true isolation.

### Test Fixtures

Playwright's fixture system provides dependency injection for test setup and teardown. Fixtures guarantee cleanup even if a test crashes. Selenium relies on `@BeforeEach` / `@AfterEach` which skip teardown on hard failures.

```typescript
// Custom fixture for authenticated user — reusable across all tests
import { test as base } from '@playwright/test';

export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('admin@example.com');
    await page.getByLabel('Password').fill('password');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await page.waitForURL('/dashboard');
    await use(page);
    // Cleanup runs automatically, even on crash
  },
});
```

### Codegen

Generate tests by recording browser interactions:

```bash
npx playwright codegen https://myapp.com
```

This opens a browser and records your clicks, fills, and navigations as Playwright test code. No equivalent exists in Selenium.

### UI Mode

Debug tests visually with time-travel:

```bash
npx playwright test --ui
```

Step forward and backward through each action, see the DOM state, network requests, and console logs at every point. Selenium's closest equivalent is manual `Thread.sleep()` and screenshot debugging.

## Related

- [core/locators.md](../core/locators.md) -- locator strategy priority and patterns
- [core/assertions-and-waiting.md](../core/assertions-and-waiting.md) -- auto-waiting and web-first assertions in depth
- [core/configuration.md](../core/configuration.md) -- setting up `playwright.config`
- [core/page-object-model.md](../core/page-object-model.md) -- page object patterns for Playwright
- [core/fixtures-and-hooks.md](../core/fixtures-and-hooks.md) -- fixtures system for test setup and isolation
- [core/test-organization.md](../core/test-organization.md) -- organizing tests for parallel execution
- [migration/from-cypress.md](from-cypress.md) -- migrating from Cypress instead
