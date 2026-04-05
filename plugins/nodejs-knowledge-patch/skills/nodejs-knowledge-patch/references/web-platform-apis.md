# Web Platform APIs & Globals

## URLPattern (global, v24+)

Available globally without any import:

```js
const pattern = new URLPattern({ pathname: '/users/:id' });

pattern.test('https://example.com/users/123');  // true
pattern.test('https://example.com/posts/456');  // false

const result = pattern.exec('https://example.com/users/123');
result.pathname.groups.id;  // "123"

// Pattern components
new URLPattern({
  protocol: 'https',
  hostname: '*.example.com',
  pathname: '/api/:version/:resource',
  search: '*'
});

// String shorthand
new URLPattern('https://*.example.com/api/:version/*');
```

## Web Storage (unflagged v25+)

`localStorage` and `sessionStorage` available globally:

```js
localStorage.setItem('key', 'value');
const val = localStorage.getItem('key');  // "value"
localStorage.removeItem('key');
localStorage.clear();

// Storage persists to disk -- specify path:
// node --localstorage-path=./storage app.js
```

**Note**: The `localStorage` getter throws if no storage path is configured. Use `--localstorage-path` CLI flag.

In v25.2, `localStorage` getter throws a clear error when the storage path is missing.

## Global Event Types

| Global | Since |
|--------|-------|
| `WebSocket` | v22 (enabled by default) |
| `CloseEvent` | v23 |
| `ErrorEvent` | v25 |

These are available without import, matching browser/Web API behavior.

## Web Locks API (v24.5+)

Available in worker threads via `navigator.locks`:

```js
// In a Worker
await navigator.locks.request('my-resource', async (lock) => {
  // Exclusive access to 'my-resource'
  await doWork();
});

// Shared lock
await navigator.locks.request('my-resource', { mode: 'shared' }, async (lock) => {
  await readData();
});
```

## Uint8Array Base64/Hex (V8 14.1, v25+)

Built-in `Uint8Array` base64 and hex conversion methods:

```js
const bytes = new Uint8Array([72, 101, 108, 108, 111]);
bytes.toBase64();   // "SGVsbG8="
bytes.toHex();      // "48656c6c6f"

Uint8Array.fromBase64("SGVsbG8=");  // Uint8Array [72, 101, 108, 108, 111]
Uint8Array.fromHex("48656c6c6f");   // Uint8Array [72, 101, 108, 108, 111]
```
