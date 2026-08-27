# Extensions and Dependencies

## Automatic extension resolution

### Default provisioning (since 1.2.0)

k6 detects extension imports and provisions a matching binary instead of
requiring a manual custom build. On the 1.2 line, community-list extensions
required `K6_ENABLE_COMMUNITY_EXTENSIONS=true` and worked only with local
`k6 run` or `k6 cloud run --local-execution`; Cloud execution accepted only
official extensions.

```sh
K6_ENABLE_COMMUNITY_EXTENSIONS=true k6 run script.js
```

### Static imports only (since 1.4.0)

Automatic discovery follows ES module `import` statements, not CommonJS
`require()` calls. CommonJS can declare an extension with a directive at the
beginning of every relevant file. Only a shebang, whitespace, or comments may
precede the directive.

```javascript
"use k6 with k6/x/redis"
const redis = require('k6/x/redis');
```

### v2 environment cleanup (since 2.0.0)

`K6_BINARY_PROVISIONING` and `K6_ENABLE_COMMUNITY_EXTENSIONS` were removed.
Community extensions resolve through the default build service.
`K6_AUTO_EXTENSION_RESOLUTION` is needed only when explicitly disabling
resolution.

### Provisioning diagnostics (since 1.8.0)

Automatic provisioning emits normal k6 log entries for artifact resolution,
cache hits, downloads, retries, and cache pruning at their corresponding log
levels. Use these messages to diagnose resolution without a separate trace
mechanism.

## Dependency inspection and archives

### Inspect dependencies (since 1.6.0)

`k6 deps` reports dependencies for a script or archive; `--json` provides
automation-friendly output. Like automatic resolution, it sees static imports
but not dynamic `require()` calls. `K6_DEPENDENCIES_MANIFEST` supplies
constraints for detected dependencies without a version pragma.

```sh
k6 deps --json script.js
K6_DEPENDENCIES_MANIFEST='{"k6/x/faker":">=v0.4.4"}' k6 run script.js
```

### Preserve dependencies in archives (since 2.0.0)

`k6 archive` records pre-manifest `k6/x/` dependency constraints in the
`dependencies` field of `metadata.json`. This preserves extension imports for
automatic resolution when an archive is executed later.

## Extension subcommands

### Register commands under `k6 x` (since 1.5.0)

Extensions can register custom CLI commands under the `k6 x` namespace.

```sh
k6 x my-tool --help
```

### Provision missing subcommands (since 1.7.0)

When a `k6 x` command requires an extension absent from the current binary,
k6 provisions a suitable binary and runs the command transparently. A manual
`xk6` build is not required.

```sh
k6 x httpbin
```

### Host-version contract (since 2.0.0)

Provisioned subcommands receive the invoking k6 version through
`K6_PROVISION_HOST_VERSION`, allowing a command to select compatible behavior
or documentation.

### Discover available commands (since 2.1.0)

Running `k6 x` lists commands compiled into the current binary and commands
advertised by official and community extension registries. Tab completion
shows the same set after a prior `k6 x` call caches the catalog locally.

## Extension author migration

### Go module path (since 2.0.0)

k6 v2 uses `go.k6.io/k6/v2`. Extensions and external Go packages must update
every k6 import.

```go
import "go.k6.io/k6/v2/js/modules"
```

### Standard-library JSON (since 2.0.0)

Public k6 Go types no longer expose easyjson-generated `MarshalJSON` and
`UnmarshalJSON` helpers. Extensions that used those methods must marshal with
the standard `encoding/json` package.

### Use k6 DNS configuration (since 1.5.0)

Extensions can use the k6 DNS resolver. Resolution then honors test `hosts`
overrides, custom DNS servers, and cache settings instead of requiring each
extension to reproduce the configuration.

## Official extensions

### DNS extension (since 1.4.0)

The officially supported `k6/x/dns` extension resolves A and AAAA records and
can be loaded through automatic resolution without a custom build.

```javascript
import dns from 'k6/x/dns';

export default function () {
  const answer = dns.resolve('grafana.com', { recordType: 'A' });
  console.log(answer.records.map(({ address }) => address).join(', '));
}
```

### Redis migration (since 1.5.0)

`k6/experimental/redis` is deprecated and scheduled for removal. Migrate Redis
tests to the official k6 Redis extension.

## Usage reporting

### Registry-listed extension details (since 2.2.0)

Anonymous usage reports include the Go module path, version, and type of a
registry-listed extension actually used through `k6/x/` imports, `--out`, or
`k6 x`. Private and unlisted extensions are not reported. Disable all such
reporting with `--no-usage-report`.
