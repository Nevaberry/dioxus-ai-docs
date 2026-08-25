# Extensions and Dependencies

## Stable built-in modules

`k6/browser`, `k6/net/grpc`, and `k6/crypto` are stable and production-ready
(since 1.0.0). WebSockets became stable later at `k6/websockets` (since 1.6.0);
the API did not change, but `k6/experimental/websockets` is deprecated and
scheduled for removal:

```javascript
import ws from 'k6/websockets';
```

`k6/experimental/redis` is deprecated; migrate to the official k6 Redis
extension (since 1.5.0).

## Automatic extension resolution

### Prefer static imports

Automatic resolution detects extension imports and provisions a matching
binary instead of requiring a manual build (since 1.2.0). At introduction,
community-list extensions required `K6_ENABLE_COMMUNITY_EXTENSIONS=true`,
worked only with local `k6 run` or `k6 cloud run --local-execution`, and were
not permitted in Cloud execution; official extensions were permitted.

Discovery follows static ES module `import` statements, not dynamic CommonJS
`require()` calls (since 1.4.0). CommonJS files can declare dependencies with a
directive at the beginning of every relevant file, after only an optional
shebang, whitespace, or comments:

```javascript
"use k6 with k6/x/redis"
const redis = require('k6/x/redis');
```

### Remove obsolete v2 environment switches

`K6_BINARY_PROVISIONING` and `K6_ENABLE_COMMUNITY_EXTENSIONS` are removed in
v2 (since 2.0.0). Community extensions resolve through the default build
service. Use `K6_AUTO_EXTENSION_RESOLUTION` only when resolution must be
disabled explicitly.

### Read provisioning logs

Resolution, cache hits, downloads, retries, and cache pruning appear as normal
k6 log entries at corresponding log levels (since 1.8.0).

## Dependency inspection and archives

### Inspect imports and constrain versions

`k6 deps` reports a script or archive's dependencies, with `--json` for
automation (since 1.6.0). It finds static imports but not dynamic `require()`.
Use `K6_DEPENDENCIES_MANIFEST` to constrain detected dependencies that have no
version pragma:

```sh
k6 deps --json script.js
K6_DEPENDENCIES_MANIFEST='{"k6/x/faker":">=v0.4.4"}' k6 run script.js
```

### Preserve extension constraints in archives

On v2, `k6 archive` writes pre-manifest `k6/x/` constraints into the
`dependencies` field of `metadata.json` (since 2.0.0), preserving imports for
automatic resolution when the archive is run again.

## Extension subcommands

### Register commands under `k6 x`

Extensions can register utilities in the `k6 x` namespace (since 1.5.0):

```sh
k6 x my-tool --help
```

If an invoked `k6 x` command is absent from the current binary, k6 can
provision a suitable binary and run it transparently without a manual `xk6`
build (since 1.7.0).

### Discover available commands

Running `k6 x` lists commands compiled into the binary and commands advertised
by the official and community registries (since 2.1.0). Tab completion exposes
the same registry commands after a prior invocation caches the catalog.

### Detect the host version

Provisioned v2 subcommands receive the invoking k6 version through
`K6_PROVISION_HOST_VERSION` (since 2.0.0), allowing command extensions to
choose compatible behavior or documentation.

## Official extensions and extension services

### Resolve DNS with `k6/x/dns`

The officially supported `k6/x/dns` extension supports A and AAAA lookups and
works with automatic resolution without a custom build (since 1.4.0):

```javascript
import dns from 'k6/x/dns';

export default function () {
  const answer = dns.resolve('grafana.com', { recordType: 'A' });
  console.log(answer.records.map(({ address }) => address).join(', '));
}
```

### Use k6 DNS policy in an extension

Extensions can use k6's resolver (since 1.5.0), inheriting the test's `hosts`
overrides, custom DNS servers, and DNS cache policy instead of reimplementing
resolution.

### Use the built-in dashboard

The web dashboard ships in the v2 binary, so a separate xk6-dashboard
extension is no longer needed (since 2.0.0):

```sh
k6 run --out=web-dashboard script.js
```

## Go extension migration

### Update the module path for v2

All Go imports must use the v2 module path (since 2.0.0):

```go
import "go.k6.io/k6/v2/js/modules"
```

### Use standard JSON encoding

Public v2 k6 Go types no longer expose easyjson-generated `MarshalJSON` and
`UnmarshalJSON` methods (since 2.0.0). Extensions that called those methods
must use `encoding/json`.

## WebSocket details

### Close with a code and reason

The WebSockets API can pass a close code and reason to `close()` and exposes
both on the close event (since 1.5.0):

```javascript
import ws from 'k6/websockets';

export default function () {
  const socket = ws.connect('ws://example.com', socket => {
    socket.on('close', event => console.log(event.code, event.reason));
  });
  socket.close(1000, 'Normal closure');
}
```

### Send typed arrays safely

Sending a TypedArray through `k6/websockets` increments `bufferedAmount`
correctly, preventing the value from becoming negative during transmission
(since 1.8.0).

## Usage reporting

Anonymous usage reports include the Go module path, version, and type of
registry-listed extensions actually used through `k6/x/` imports, `--out`, or
`k6 x` (since 2.2.0). Private and unlisted extensions are excluded. Pass
`--no-usage-report` to disable reporting.
