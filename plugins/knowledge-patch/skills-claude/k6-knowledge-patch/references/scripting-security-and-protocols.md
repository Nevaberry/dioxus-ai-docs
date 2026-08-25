# Scripting, Security, and Protocols

## JavaScript and TypeScript runtime

### Run TypeScript directly (since 1.0.0)

k6 executes `.ts` test files without a separate transpilation step.

```typescript
import http from 'k6/http';

interface Target { url: string }
const target: Target = { url: 'https://quickpizza.grafana.com/' };

export default function () {
  http.get(target.url);
}
```

```sh
k6 run script.ts
```

### Global text encoding (since 2.2.0)

`TextEncoder` and `TextDecoder` are globals in both init and VU contexts.

```javascript
const encoded = new TextEncoder().encode('Hello, world!');
const decoded = new TextDecoder().decode(encoded);
```

### Frozen environments (since 2.2.0)

The experimental `freeze-env` feature freezes `__ENV`. Mutation throws a
`TypeError` in strict mode instead of persisting across iterations or
scenarios. Enable it through the normal feature-flag mechanisms.

```sh
k6 run --features freeze-env script.js
```

## Assertions

### Preview `expect()` library (since 1.2.0)

The URL-hosted `k6-testing` preview library provides `expect()` and
Playwright-style matchers for protocol and browser tests. It remains a preview,
so matcher coverage may be incomplete.

```javascript
import { expect } from 'https://jslib.k6.io/k6-testing/0.5.0/index.js';
import http from 'k6/http';

export default function () {
  expect(http.get('https://quickpizza.grafana.com/').status).toBe(200);
}
```

## Cryptography and one-time passwords

### PBKDF2 (since 1.6.0)

The stable crypto module supports PBKDF2 for deriving cryptographic keys from
passwords.

### RFC 6238 TOTP (since 1.6.0)

The TOTP jslib package generates and verifies time-based one-time passwords
from base32 secrets.

```javascript
import { TOTP } from 'https://jslib.k6.io/totp/1.0.0/index.js';

const totp = new TOTP('GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ', 6);
const code = await totp.gen();
const valid = await totp.verify(code);
```

## Secret sources

### URL-backed source (since 1.5.0)

Secret management can retrieve secrets from HTTP endpoints so a custom service
can provide test values. The 1.5 release included only a mock implementation,
not a production-ready external-secret-manager integration.

### Configure through the environment (since 1.7.0)

`K6_SECRET_SOURCE` is equivalent to `--secret-source` and accepts the same
value syntax.

```sh
K6_SECRET_SOURCE='mock=cool="not cool secret"' k6 run script.js
```

### Cloud-backed secrets in local runs (since 2.0.0)

On the 2.0 line, `k6 cloud run --local-execution` automatically enabled the
Cloud secret source and accepted `--no-cloud-secrets` as an opt-out. On the
1.8 maintenance line, this implicit source was removed in 1.8.1 so explicitly
configured sources work without conflict. Configure the intended source for
the exact release line in use.

## gRPC

### Special floating-point values (since 1.2.0)

gRPC marshals `NaN` and `Infinity` float values using their string
representations rather than `null`. Existing scripts do not need changes.

### Authority pseudo-header (since 1.2.0)

The gRPC module supports the `authority` pseudo-header for services that
require a specific authority value.

## WebSockets

### Close codes and reasons (since 1.5.0)

The then-experimental WebSockets API allowed `close()` to send a close code and
reason and exposed both on the close event.

```javascript
import ws from 'k6/experimental/websockets';

export default function () {
  const socket = ws.connect('ws://example.com', socket => {
    socket.on('close', event => console.log(event.code, event.reason));
  });
  socket.close(1000, 'Normal closure');
}
```

### Stable module path (since 1.6.0)

WebSockets are stable at `k6/websockets`. The API did not change, but
`k6/experimental/websockets` is deprecated and scheduled for removal.

```javascript
import ws from 'k6/websockets';
```

### Typed-array buffering (since 1.8.0)

Sending a TypedArray through `k6/websockets` increments `bufferedAmount`
correctly. The counter no longer becomes negative as typed-array data is
transmitted.

## Streams

### Writable streams (since 2.2.0)

`k6/experimental/streams` implements WHATWG-compatible `WritableStream` and
`WritableStreamDefaultWriter`, complementing readable streams.

```javascript
import { WritableStream } from 'k6/experimental/streams';

export default async function () {
  const stream = new WritableStream({ write: chunk => console.log(chunk) });
  const writer = stream.getWriter();
  await writer.write('hello');
  await writer.close();
}
```

## Execution status

### Explicit-failure distinction (since 1.6.0)

Status consumers can identify a test explicitly marked as failed through
`ExecutionStatusMarkedAsFailed`, distinct from other failure states.
