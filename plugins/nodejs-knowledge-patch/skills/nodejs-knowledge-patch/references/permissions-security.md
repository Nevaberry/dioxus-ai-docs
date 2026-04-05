# Permission Model & Security

## Permission Model

### Flag Change (v24+)

The permission model flag changed from `--experimental-permission` to `--permission`:

```bash
# v22-v23 (experimental)
node --experimental-permission --allow-fs-read=/app app.js

# v24+ (graduated)
node --permission --allow-fs-read=/app --allow-fs-write=/tmp app.js
```

### Network Permissions (v25+)

```bash
# Allow all network access
node --permission --allow-net app.js

# Without --allow-net, network operations are denied when --permission is active
```

### Inspector Permissions (v25+)

```bash
# Allow inspector/debugger access
node --permission --allow-inspector app.js
```

### Full Example

```bash
node --permission \
  --allow-fs-read=/app \
  --allow-fs-write=/app/data \
  --allow-net \
  --allow-inspector \
  app.js
```

## V8 Language Features (Security-Relevant)

### Explicit Resource Management (v24+)

`using` and `await using` declarations ensure cleanup via `Symbol.dispose` / `Symbol.asyncDispose`:

```js
function getConnection() {
  const conn = createConnection();
  return {
    conn,
    [Symbol.dispose]() {
      conn.close();
    }
  };
}

{
  using resource = getConnection();
  // resource.conn is available here
} // resource[Symbol.dispose]() called automatically

// Async version
async function getDbPool() {
  const pool = await createPool();
  return {
    pool,
    async [Symbol.asyncDispose]() {
      await pool.drain();
      await pool.clear();
    }
  };
}

{
  await using db = await getDbPool();
  // use db.pool
} // await db[Symbol.asyncDispose]() called automatically
```

### RegExp.escape() (v24+)

```js
const userInput = 'hello.world (test)';
const escaped = RegExp.escape(userInput);
// "hello\\.world\\ \\(test\\)"
new RegExp(escaped).test('hello.world (test)');  // true
```

### Error.isError() (v24+)

```js
Error.isError(new Error());        // true
Error.isError(new TypeError());    // true
Error.isError({ message: 'fake' }); // false
```

Works across realms (unlike `instanceof`).

## Crypto Deprecations & Removals

### Removed in v24

- `tls.createSecurePair` -- use `TLSSocket` directly

### Deprecated

| API | Version | Status |
|-----|---------|--------|
| `crypto.fips` | v23 | Runtime deprecated |
| `ECDH.setPublicKey()` | v25 | Runtime deprecated |
| `hash`/`mgf1Hash` options | v25 | EOL |
| `shake128`/`shake256` default output length | v25 | Runtime deprecated |

### crypto.Hash / crypto.Hmac Constructors

Runtime-deprecated since v22. Use `crypto.createHash()` and `crypto.createHmac()` instead:

```js
// Deprecated:
new crypto.Hash('sha256');

// Correct:
crypto.createHash('sha256');
```
