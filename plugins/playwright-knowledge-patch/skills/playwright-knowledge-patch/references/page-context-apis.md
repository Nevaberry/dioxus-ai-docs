# Page & Context APIs

## Screencast API (1.59)

New `page.screencast` for video recording with annotations and overlays:
```js
// Record video
await page.screencast.start({ path: 'video.webm' });
await page.screencast.stop();

// Action annotations (highlight interactions)
await page.screencast.showActions({ position: 'top-right' });

// Chapter titles
await page.screencast.showChapter('Checkout flow', {
  description: 'Testing coupon application',
  duration: 1000,
});

// Custom HTML overlay
await page.screencast.showOverlay('<div style="color: red">Recording</div>');

// Real-time frame streaming
await page.screencast.start({
  onFrame: ({ data }) => sendToVisionModel(data),
  size: { width: 800, height: 600 },
});
```

Video config in `playwright.config.ts`:
```js
use: {
  video: {
    mode: 'on',
    show: {
      actions: { position: 'top-left' },
      test: { position: 'top-right' },
    },
  },
}
```

## storageState with IndexedDB (1.51)

Save and restore IndexedDB contents (useful for Firebase Auth tokens):
```js
await page.context().storageState({ path: authFile, indexedDB: true });
```

## browserContext.setStorageState() (1.59)

Clear and replace cookies, localStorage, and IndexedDB without creating a new context:
```js
await context.setStorageState({ path: 'new-state.json' });
```

## Cookie partitionKey (1.54)

`browserContext.cookies()` and `addCookies()` support `partitionKey` for CHIPS (partitioned cookies).

## consoleMessages(), pageErrors(), requests() (1.56)

Retrieve recent console messages, errors, and network requests from the page (no event listener setup needed).

## clearConsoleMessages() / clearPageErrors() (1.59)

Reset stored messages and errors.

## consoleMessage.timestamp() (1.59)

Get message timestamp from console messages.

## request.existingResponse() (1.59)

Get response without waiting.

## response.httpVersion() (1.59)

HTTP version string.

## page.emulateMedia({ contrast }) (1.51)

Emulate `prefers-contrast` media feature.

## failOnStatusCode for apiRequest (1.51)

`failOnStatusCode` option for `apiRequest.newContext()` — throw on non-2xx/3xx responses.

## browserContext.isClosed() (1.59)

Check if context is closed.

## Async Disposables (1.59)

Automatic cleanup for pages, routes, and init scripts using `await using`:
```js
await using page = await context.newPage();
{
  await using route = await page.route('**/*', r => r.continue());
  await using script = await page.addInitScript('console.log("hi")');
  await page.goto('https://example.com');
}
// route and script automatically removed here
```
