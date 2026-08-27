# Browser Testing

## Locators and element selection

### Count and select matches

`Locator.count()` returns the number of matches immediately and does not wait
for visibility (since 1.1.0). Select among multiple matches with
`first()`, `nth(index)`, and `last()`:

```javascript
const rows = page.locator('tr');
console.log(await rows.count());
await expect(await rows.first()).toContainText('Name');
await expect(await rows.nth(4)).toContainText('Pizza');
```

Browser `QueryAll` methods return matches in DOM order (since 1.4.0).

### Filter, select, and retry

`locator.filter()` accepts `hasText` and `hasNotText`; the same filters work
when creating locators from a page, frame, locator, or `FrameLocator` (since
1.3.0). `locator.selectOption()` accepts visible string labels directly (since
1.2.0). Locator actionability APIs retry when the target is temporarily not
visible instead of immediately failing (since 1.3.0).

### Evaluate against an element

`locator.evaluate()` runs a function in the page context with the matching
element and an optional argument. `locator.evaluateHandle()` returns a
`JSHandle` instead of a serialized result (since 1.4.0):

```javascript
const text = await page.locator('#pizza-name')
  .evaluate((element, suffix) => element.textContent + suffix, '!');
const handle = await page.locator('#pizza-name')
  .evaluateHandle(element => element);
```

### Type with full keyboard events

`locator.pressSequentially()` enters characters one at a time and emits
`keydown`, `keypress`, and `keyup` for each character (since 1.5.0). Its
`delay` option supports autocomplete and per-character validation tests:

```javascript
await page.locator('#search').pressSequentially('test query', { delay: 100 });
```

Use `fill()` for simple form filling. `type()` is gradual but does not provide
the full per-character event sequence of `pressSequentially()`.

## Frames

### Enter an iframe from a locator

`locator.contentFrame()` returns a `FrameLocator`, retaining locator auto-retry
inside the iframe (since 1.3.0):

```javascript
const payment = page.locator('iframe[name="payment-form"]').contentFrame();
await payment.locator('input[name="card-number"]').fill('4111111111111111');
```

### Chain frame locators

`frameLocator()` is available on pages, frames, locators, and frame locators
(since 1.6.0). Chain it for nested frames without manually switching context:

```javascript
await page.frameLocator('#payment-iframe')
  .frameLocator('#nested-frame')
  .locator('#submit')
  .click();
```

## Network synchronization and events

### Wait for a response or request

`page.waitForResponse()` accepts an exact URL or regular expression (since
1.3.0). `page.waitForRequest()` supports the same matcher forms (since 1.4.0).
Arm the wait alongside the triggering action:

```javascript
const [request] = await Promise.all([
  page.waitForRequest(/\/api\/.*\.json$/),
  page.click('button[data-testid="load-data"]'),
]);
```

### Wait for a page event

`page.waitForEvent()` accepts either a predicate directly or an options object
with `predicate` and `timeout` (since 1.5.0). Create the promise before the
action that emits the event:

```javascript
const responsePromise = page.waitForEvent('response', {
  predicate: response => response.url().includes('/api/data'),
  timeout: 5000,
});
await page.click('button#fetch-data');
const response = await responsePromise;
```

### Track request lifecycle and redirects

Pages emit `requestfailed` and `requestfinished` for unsuccessful and completed
requests (since 1.6.0). From 1.7.0, `response` and `requestfinished` handlers
cover every request in a redirect chain.

## Request interception

### Route and mock requests

`page.route()` intercepts a matching request before it is sent; a handler can
abort it, continue it with changes, or fulfill it with a mock (since 1.2.0):

```javascript
await page.route('**/api/users', route => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify([{ id: 1, name: 'Mock User' }]),
}));
```

### Remove routes

`page.unroute(url)` removes routes registered with exactly the same URL
matcher; `page.unrouteAll()` removes every route (since 1.4.0). Preserve the
matcher object when using a regular expression so the same matcher can be
passed to `unroute()`.

## Browser networking and connections

### Configure a proxy per context

`browser.newContext()` accepts a `proxy` object (since 2.1.0).
`proxy.server` is required; `proxy.bypass` excludes destinations:

```javascript
const context = await browser.newContext({
  proxy: { server: 'http://proxy.test:8080', bypass: 'localhost,127.0.0.1' },
});
```

### Attach over CDP

`chromium.connectOverCDP()` connects at runtime to an existing Chromium-based
browser WebSocket endpoint (since 2.2.0), unlike static
`K6_BROWSER_WS_URL`. k6 closes the returned connection at iteration end, or
the script can close it earlier:

```javascript
import { chromium } from 'k6/browser';

export default async function () {
  const remote = await chromium.connectOverCDP(
    'ws://localhost:9222/devtools/browser/<id>',
  );
  const page = await remote.newPage();
  await page.goto('https://quickpizza.grafana.com/');
  await remote.close();
}
```

## Browser metrics and diagnostics

### Replace FID with INP

First Input Delay was planned to warn on the 1.x line and be removed in v2
(since 1.3.0). Replace `browser_web_vital_fid` thresholds and integrations with
`browser_web_vital_inp`:

```javascript
export const options = {
  thresholds: { browser_web_vital_inp: ['p(95)<200'] },
};
```

### Redirect metrics

Redirects emit request metrics only for the applicable redirect rather than
duplicating samples from every earlier redirect (since 1.8.0).

### Cloud log filtering

Browser API failures in Grafana Cloud Logs carry `module=browser`, enabling
browser-specific filters (since 2.1.0).

### Raw response headers

Browser response header accessors expose raw wire headers, including
`Set-Cookie` and security headers, for the correct redirect hop (since 2.2.0).
`headerValues()` matches names case-insensitively and splits repeated values on
newlines, not commas. Browser sent/received byte metrics include raw header
bytes.
