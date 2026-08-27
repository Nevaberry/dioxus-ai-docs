# Browser Testing

## Locator selection and actionability

### Count and positional selection (since 1.1.0)

`Locator.count()` returns the number of matches immediately and does not wait
for visibility. Use `first()`, `nth(index)`, or `last()` to narrow a locator
that matches multiple elements.

```javascript
const rows = page.locator('tr');
console.log(await rows.count());
await rows.nth(2).click();
```

### String option labels (since 1.2.0)

`locator.selectOption()` accepts string labels directly, so an option can be
selected by its displayed label without constructing another selector.

### Text filters (since 1.3.0)

`locator.filter()` accepts `hasText` and `hasNotText`. The same filters can be
passed when creating locators from a page, frame, locator, or `FrameLocator`.

```javascript
const wanted = page.locator('li').filter({ hasText: 'Product 2' });
const others = page.locator('li').filter({ hasNotText: /Product 2/ });
```

### Visibility retries (since 1.3.0)

Locator actionability APIs retry when a target is temporarily hidden rather
than failing immediately. Keep using locators when an element becomes visible
asynchronously.

### Evaluation and DOM order (since 1.4.0)

`locator.evaluate()` runs a function in the page context with the matching
element and an optional argument. `locator.evaluateHandle()` returns a
`JSHandle`. Browser `QueryAll` methods return matches in DOM order.

```javascript
const text = await page.locator('#name')
  .evaluate((element, suffix) => element.textContent + suffix, '!');
const handle = await page.locator('#name').evaluateHandle(element => element);
```

### Character-by-character input (since 1.5.0)

`locator.pressSequentially()` emits `keydown`, `keypress`, and `keyup` for
every character and accepts a `delay`. Use it for autocomplete and
per-character validation. `fill()` performs simple form filling, while
`type()` types gradually without the complete keyboard-event sequence.

```javascript
await page.locator('#search').pressSequentially('pizza', { delay: 100 });
```

## Frames

### Locator-based iframe access (since 1.3.0)

`locator.contentFrame()` returns a `FrameLocator`. Its `locator()` keeps normal
locator auto-retry behavior inside the iframe.

```javascript
const payment = page.locator('iframe[name="payment-form"]').contentFrame();
await payment.locator('input[name="card-number"]').fill('4111111111111111');
```

### Chainable frame locators (since 1.6.0)

`frameLocator()` is available on pages, frames, locators, and frame locators.
Chain it to address nested iframes without manually switching context.

```javascript
const frame = page.frameLocator('#payment-iframe');
await frame.frameLocator('#nested-frame').locator('#submit').click();
```

## Routing and network waits

### Intercept requests (since 1.2.0)

`page.route()` intercepts matching requests before transmission. The handler
can abort, continue with changes, or fulfill with a mocked response.

```javascript
await page.route('**/api/users', route => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify([{ id: 1, name: 'Mock User' }]),
}));
```

### Wait for responses (since 1.3.0)

`page.waitForResponse()` accepts an exact URL string or regular expression.
Arm the wait alongside the triggering action to avoid missing a fast response.

```javascript
await Promise.all([
  page.waitForResponse(/\/api\/.*\.json$/),
  page.click('button[data-testid="load-data"]'),
]);
```

### Wait for requests and remove routes (since 1.4.0)

`page.waitForRequest()` accepts an exact URL or regular expression and should
also be started with the triggering action. `page.unroute(url)` removes routes
registered with the exact same matcher; `page.unrouteAll()` removes all routes.

```javascript
const matcher = /.*\/api\/pizza/;
await page.route(matcher, route => route.continue());
await page.unroute(matcher);
```

### Wait for page events (since 1.5.0)

`page.waitForEvent()` accepts a predicate directly or an options object with a
predicate and timeout. Create the promise before the emitting action.

```javascript
const responsePromise = page.waitForEvent('response', {
  predicate: response => response.url().includes('/api/data'),
  timeout: 5000,
});
await page.click('button#fetch-data');
const response = await responsePromise;
```

## Request lifecycle and redirects

### Completion and failure events (since 1.6.0)

Observe unsuccessful and completed requests with `requestfailed` and
`requestfinished` page events.

```javascript
page.on('requestfailed', request => console.log('failed', request.url()));
page.on('requestfinished', request => console.log('finished', request.url()));
```

### Complete redirect chains (since 1.7.0)

`response` and `requestfinished` handlers cover every request in a redirect
chain, not only the terminal request.

### Redirect metric emission (since 1.8.0)

Browser redirects emit request metrics only for the applicable hop. Earlier
hops are no longer re-emitted, so results no longer contain duplicate request
samples for redirects.

### Raw response headers (since 2.2.0)

Browser response header accessors return raw wire headers, including
`Set-Cookie` and security headers, associated with the correct redirect hop.
`headerValues()` matches names case-insensitively and splits repeated values on
newlines, not commas. Browser sent/received byte metrics include raw header
bytes.

## Browser environments

### Per-context proxy (since 2.1.0)

`browser.newContext()` accepts a `proxy` object. `proxy.server` is required;
`proxy.bypass` can exclude destinations.

```javascript
const context = await browser.newContext({
  proxy: {
    server: 'http://proxy.test:8080',
    bypass: 'localhost,127.0.0.1',
  },
});
```

### Browser failures in Cloud Logs (since 2.1.0)

Browser API failures in Grafana Cloud Logs carry `module=browser`, so filters
can separate them from other log sources.

### Attach over CDP (since 2.2.0)

`chromium.connectOverCDP()` attaches to a running Chromium-based browser using
a runtime WebSocket endpoint. This differs from the static
`K6_BROWSER_WS_URL` setting. k6 closes the returned browser connection at
iteration end, or the script can close it sooner.

```javascript
import { chromium } from 'k6/browser';

export default async function () {
  const remote = await chromium.connectOverCDP(
    'ws://localhost:9222/devtools/browser/<id>'
  );
  const page = await remote.newPage();
  await page.goto('https://quickpizza.grafana.com/');
  await page.close();
  await remote.close();
}
```

## Web-vital migration

### Replace FID with INP (since 1.3.0)

First Input Delay was scheduled to warn in the 1.4 line and be removed in v2.
Replace `browser_web_vital_fid` thresholds and integrations with Interaction to
Next Paint.

```javascript
export const options = {
  thresholds: { browser_web_vital_inp: ['p(95)<200'] },
};
```
