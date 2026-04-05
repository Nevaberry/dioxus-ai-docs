# HTTP, Networking & TLS

## Built-in HTTP Proxy Support (v24.5+)

Node.js natively reads proxy environment variables without third-party packages.

### Enabling

```bash
# Environment variable
NODE_USE_ENV_PROXY=1 node app.js

# CLI flag
node --use-env-proxy app.js
```

When enabled, `http.request()`, `https.request()`, and `fetch()` automatically route through proxies specified in `http_proxy`, `https_proxy`, and `no_proxy` environment variables.

### Per-Agent Proxy Configuration

```js
import https from 'node:https';

const agent = new https.Agent({
  proxyEnv: {
    https_proxy: 'http://corporate-proxy:8080',
    no_proxy: 'localhost,internal.corp'
  }
});

https.request('https://api.example.com', { agent }, (res) => { /* ... */ });
```

Both `http.Agent` and `https.Agent` accept the `proxyEnv` option.

### fetch() Proxy

`fetch()` respects `NODE_USE_ENV_PROXY` when set. The global agent picks up proxy env vars.

## HTTP/2 Improvements

### Session Tracking and Graceful Close (v24+)

HTTP/2 server now tracks active sessions and supports graceful close:

```js
import http2 from 'node:http2';

const server = http2.createSecureServer(options);
// Server tracks sessions internally
// Graceful close waits for active sessions to finish
server.close();
```

### Stream Reset Rate Limit (v23+)

```js
http2.createServer({
  // Exposed nghttp2 option to limit stream reset rate
  streamResetRate: 100,
  streamResetBurst: 1000
});
```

### Diagnostics Channels (v25.2+)

HTTP/2 client stream request body now emits diagnostics channel events.

## TLS Changes

### setDefaultCACertificates() (v24.5+)

Dynamically configure the CA certificate list for TLS clients:

```js
import tls from 'node:tls';

// Get system CA certificates
const systemCAs = tls.getCACertificates('system');
const defaultCAs = tls.getCACertificates('default');

// Set custom CA certificates
tls.setDefaultCACertificates([...defaultCAs, customCA]);
```

### OpenSSL 3.5 (v24.5+)

Node.js 24.5 upgraded to OpenSSL 3.5.1 (supported until April 2030).

### Removals

- `tls.createSecurePair` removed in v24 (was deprecated)
- `tls.Server.prototype.setOptions` moved to end-of-life in v24
- TLS IP-address servername deprecation moved to EOL in v25

## Crypto Changes

### v23

- `crypto.fips` runtime-deprecated
- `KeyObject.prototype.toCryptoKey()` added
- Certificate `validTo`/`validFrom` available as `Date` objects (not just strings)
- `SubtleCrypto.deriveBits` allows `length=0` for HKDF and PBKDF2

### v24

- HKDF and PBKDF2 `length=0` support in `SubtleCrypto.deriveBits`
- `util.types.isFloat16Array()` added

### v25

- `ECDH.setPublicKey()` runtime-deprecated
- Deprecated `hash` and `mgf1Hash` options moved to EOL
- Default output lengths for `shake128`/`shake256` runtime-deprecated

## DNS

### Resolver Timeout (v24.5+)

`dns.resolve*` methods gain a max timeout option:

```js
import dns from 'node:dns';
const resolver = new dns.Resolver();
// Per-query timeout support
```

### Deprecation

- `dns.lookup()` with falsy hostname moved to EOL in v25

## Net Module

### BlockList Enhancements (v24.5+)

`net.BlockList` gains file save and file management capabilities.

### Deprecation

- `net._setSimultaneousAccepts()` moved to EOL in v24

### Network Family Autoselection (v25.2+)

Timeout for network family autoselection increased to 500ms (from previous lower default).

## Inspector Protocol (v24.5+)

- Initial support for `Network.loadNetworkResource`
- Inspector can inspect HTTP response body
- Inspector can inspect HTTP/2 request/response bodies
