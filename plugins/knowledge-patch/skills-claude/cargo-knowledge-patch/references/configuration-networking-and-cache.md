# Configuration, networking, and cache

Use this reference for `.cargo/config.toml`, layered settings, cache
administration, registry transport, Git and SSH access, proxy trust, and
runner configuration.

## Configuration composition and precedence

### Atomic program-and-argument values

Since 1.86.0, layered configuration replaces rather than combines these
program-and-argument values:

- `registry.credential-provider`
- `registries.*.credential-provider`
- `target.*.runner`
- `host.runner`
- `credential-alias.*`
- `doc.browser`

Treat each as one atomic value when designing system, user, workspace, and
command-line overrides.

### Stable configuration includes

Cargo 1.94.0 stabilized the top-level `include` key for loading shared
configuration:

```toml
include = ["../shared/cargo.toml"]
```

The earlier `-Zconfig-include` form gained optional entries in 1.93.0:

```toml
include = [{ path = "local.toml", optional = true }]
```

A missing optional file is skipped. Includes must use list form, and
`include.path` does not accept glob or template syntax.

### Cargo-provided environment values

Build-script `rerun-if-env-changed` instructions correctly observe changes
originating in Cargo's `[env]` table as of 1.86.0.

Non-mergeable list values from `--config` outrank environment variables as of
1.93.0, and nested non-mergeable lists replace values from other layers.

## Cache lifecycle

### Automatic cleanup

Cargo 1.88.0 automatically removes network-downloaded cache files unused for
three months and locally obtained files unused for one month. Cleanup does not
run with `--offline` or `--frozen`.

Only Cargo 1.78 and newer record the access data cleanup needs. If one cache is
shared with older Cargo versions, consider disabling cleanup so entries used
only by those versions are not repeatedly downloaded:

```toml
[cache]
auto-clean-frequency = "never"
```

### Garbage-collection configuration

Under `-Zgc`, Cargo 1.88.0 renamed the former `[gc]` table to `[cache]`.
Low-level settings belong under `[cache.global-clean]`.

### Cache-path hash transition

Cargo 1.85.0 adopted `rustc-stable-hash` for dependency-cache path hashes.
Plan for a one-time redownload or reclone of cached registry and Git inputs
after the upgrade.

## HTTP and registry transport

### Proxy CA bundles

Cargo 1.90.0 added `http.proxy-cainfo` for TLS connections made through a
proxy:

```toml
[http]
proxy-cainfo = "proxy-ca.pem"
```

### Rate limiting

Since 1.89.0, Cargo honors a registry's `Retry-After` header after an HTTP 429
response before retrying.

### Registry API URL shape

For Cargo 1.97.0 registry configuration, the `api` URL in `config.json` should
not end with `/`:

```json
{
  "api": "https://registry.example/api"
}
```

## Git and SSH

### Bare repositories with CLI fetching

With `net.git-fetch-with-cli = true`, Cargo 1.85.0 sets `GIT_DIR`, allowing
fetches to work correctly in bare repositories.

### Shallow CLI fetching

The unstable `-Zgit` shallow-fetch implementation works with the Git CLI
backend selected by `net.git-fetch-with-cli` as of 1.93.0.

### Known-host patterns

Cargo's SSH host matching accepts `*` and `?` patterns as of 1.89.0. Since
1.95.0, `net.known_hosts` also parses negated patterns correctly, so exclusion
entries participate in SSH host verification.

## Runners and target selection

### Host runner

Under unstable `-Zhost-config`, Cargo 1.95.0 allows `host.runner` to wrap
executions for the host build target:

```toml
[host]
runner = "my-wrapper"
```

Because runners are atomic program-and-argument values, a higher-precedence
layer replaces the whole runner setting.

### Portable host target

Cargo 1.91.0 added the literal `host-tuple` for `--target` and `build.target`.
Cargo substitutes the machine's host target triple:

```console
cargo build --target host-tuple
```

Cargo metadata filtering gained the same spelling in 1.93.0:

```console
cargo metadata --filter-platform host-tuple
```

## Terminal and warning policy

### Terminal progress integration

Cargo 1.87.0 added `term.progress.term-integration`. Enabling it emits ANSI
OSC 9;4 progress reports, allowing compatible terminal emulators to surface
Cargo progress in UI such as a task bar.

### Warning-control evolution

Under unstable `-Zwarnings`, Cargo 1.96.0 stopped applying `build.warnings` to
non-local dependencies. `allow` cannot hide denied diagnostics or hard
warnings. Denied warnings and warning summaries fail the build unless
`--keep-going` permits other work to continue.

Cargo 1.97.0 stabilized `build.warnings` with `warn` (the default), `allow`,
and `deny`, plus the `CARGO_BUILD_WARNINGS` environment equivalent:

```toml
[build]
warnings = "deny"
```

Changing warning policy does not alter compiler flags used to identify cached
artifacts.
