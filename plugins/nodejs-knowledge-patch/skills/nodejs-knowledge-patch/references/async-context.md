# AsyncLocalStorage & Async Context

## AsyncContextFrame Default (v24+)

`AsyncLocalStorage` now defaults to the `AsyncContextFrame` implementation, which is significantly more efficient than the previous `AsyncResource`-based implementation.

### New Constructor Options

```js
import { AsyncLocalStorage } from 'node:async_hooks';

const als = new AsyncLocalStorage({
  name: 'request-context',      // Debugging label, visible in diagnostics
  defaultValue: { user: null }  // Returned when no store is active
});

// Previously, als.getStore() returned undefined when no store was active
// Now it returns the defaultValue
als.getStore();  // { user: null }

als.run({ user: 'Alice' }, () => {
  als.getStore();  // { user: 'Alice' }
});
```

### AsyncResource Gets AsyncContextFrame

`AsyncResource` now uses `AsyncContextFrame` internally for better performance.

## stream.finished() Context Preservation (v24+)

`stream.finished()` now preserves `AsyncLocalStorage` context:

```js
import { finished } from 'node:stream/promises';
import { AsyncLocalStorage } from 'node:async_hooks';

const als = new AsyncLocalStorage();

als.run('my-context', async () => {
  const stream = createSomeStream();
  await finished(stream);
  // als.getStore() correctly returns 'my-context' here
});
```

## Deprecations

### asyncResource Property on Bound Functions (EOL v25)

The `asyncResource` property automatically added to functions bound via `AsyncResource.bind()` is deprecated and moved to end-of-life in v25.

```js
// Deprecated pattern:
const bound = asyncResource.bind(fn);
bound.asyncResource;  // <-- this property is deprecated

// Use AsyncLocalStorage instead of AsyncResource for context tracking
```
