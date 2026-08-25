# CLI, Configuration, SEA, and Releases

## Startup and environment controls

- Since 23.0.0, the main entry point may be a file URL, for example
  `node file:///absolute/path/app.mjs`.
- In 23.0.0, `--no-experimental-global-customevent`,
  `--no-experimental-fetch`, and `--no-experimental-global-webcrypto` are
  removed because those globals are no longer optional experiments;
  `--trace-atomics-wait` is also end-of-life.
- In 23.4.0, `--experimental-default-type` is removed. Startup commands can no
  longer use it to override the module type.
- Since 23.5.0, `require(ESM)` warnings are emitted only when
  `--trace-require-module` is requested.
- Since 23.7.0, `--disable-sigusr1` prevents creation of the SIGUSR1 signal I/O
  thread and therefore prevents signal-triggered inspector activation.
- Since 24.0.0, use `--permission`; `--experimental-permission` is removed.
- Since 24.4.0, `--watch-kill-signal` selects the signal used to stop a process
  for a watch restart. An empty `NO_COLOR` value is treated as absent, so use a
  non-empty value to suppress color.
- Since 24.6.0, `--max-old-space-size` accepts a percentage as well as a fixed
  MiB value. Since 25.9.0, `--max-heap-size` limits the entire V8 heap rather
  than only old space.
- In 26.0.0, `--experimental-transform-types` is removed.
- Since 24.14.0, `node --print` emits complete long strings rather than
  truncating them.

## JSON configuration

- In 23.10.0, CLI options can come from the `nodeOptions` object of a JSON
  configuration file. `--experimental-default-config-file` reads
  `node.config.json`; `--experimental-config-file=<path>` selects another
  file. Node does not sanitize or validate configuration contents, so trust the
  selected file.
- In 24.2.0, experimental JSON configuration supports namespaced options.
- In 25.1.0, configuration supports a separate `watch` namespace.
- In 25.4.0, configuration supports Permission Model and test settings. The
  test namespace is `test`, not `testRunner`, and declaring a namespace
  implicitly enables its associated mode.
- In 24.19.0, an empty file selected by `--experimental-config-file` is
  accepted and represents no overrides.

## Stability promotions

- In 24.10.0, built-in `.env` file support is stable.
- In 24.13.0, the 24.13.1 release makes `--heapsnapshot-near-heap-limit`,
  `--build-snapshot`, `--build-snapshot-config`, `crypto.hash()`, and
  `v8.queryObjects()` stable. Synchronous `module.registerHooks()` is release
  candidate, while dedicated-thread `module.register()` is active development.

## Watch mode

- In 23.7.0, watch-mode restarts reload the file passed through
  `--env-file-if-exists`, so edits are reflected after restarting.
- In 24.13.0, the 24.13.1 correction makes watch mode restart after ESM syntax
  errors.
- In 25.5.0, `fs.watch()` adds `ignore` for excluding selected paths before
  event delivery.
- In 24.19.0, normal watch output identifies the changed file that triggered a
  restart.

## Single executable applications

- In 24.7.0, SEA configuration accepts `execArgv` for baked-in Node execution
  arguments and `execArgvExtension` for runtime additions. Extension mode is
  `"none"`, `"cli"` for a `--node-options` argument, or `"env"` for
  `NODE_OPTIONS`; `"env"` is the default.
- In 24.8.0, single executables accept inspector flags such as `--inspect` and
  `--inspect-brk`.
- In 25.5.0, `node --build-sea <config>` directly builds an SEA and replaces
  the previous copy, preparation-blob, and `postject` sequence. The older
  `--experimental-sea-config` injection workflow remains supported for now.
- In 25.9.0, an SEA whose entry point is ESM can generate and use a code cache
  by setting `useCodeCache: true`.
- In 24.18.0, SEA support explicitly excludes `darwin-x64`; target another
  supported platform or architecture.
- In 26.5.0, Tier 2 macOS x64 support is due to end, so build and CI plans
  should avoid depending on that tier.

## Release verification and lifecycle

- The 23.11.1 security release fixes CVE-2025-23166 in asynchronous-crypto
  error handling. Upgrade deployments running 23.11.0.
- The 24.4.1 security release fixes CVE-2025-27209, a V8 RapidHash HashDoS, and
  CVE-2025-27210, a Windows reserved-device-name bypass in
  `path.normalize()`. Upgrade deployments running 24.4.0.
- Node.js 24.11.0 starts the Krypton LTS line, with updates through the end of
  April 2028. Other than LTS metadata such as `process.release`, it is
  unchanged from 24.10.0.
- Node.js 24.13.1 includes Permission Model, TLS, async-hooks, and Buffer
  security fixes described in the relevant topic references. Affected
  deployments should upgrade instead of attempting application workarounds.
- The 24.14.1 release hardens WebCrypto HMAC and KMAC comparison, HTTP/2
  flow-control errors, URL handling, and array-index hash collisions. It also
  changes `headersDistinct` and `trailersDistinct` to null-prototype objects
  and adds missing filesystem permission checks; use `Object.hasOwn()` for the
  header collections and grant required filesystem access.
- In 26.5.0, future releases may use Stewart X Addison's Ed25519 release key.
  Verification keyrings need fingerprint
  `655F3B5C1FB3FA8D1A0CA6BDE4A7D232B936D2FD`.

## Release cadence

- Under the release-schedule announced on 2026-07-28, 27.x starts a one-major-
  per-year cadence and every release line proceeds to LTS. A line spends six
  months in Alpha from October through March, six months as Current from April
  through October, and 30 months in LTS.
- Node.js 26 is the final line under the earlier model. Node.js 27 begins Alpha
  in October 2026, releases 27.0.0 in April 2027, enters LTS in October 2027,
  and reaches end-of-life in April 2030.
- Alpha releases may contain semver-major changes and change APIs between
  releases. Unlike automated, untested nightlies from `main`, they are signed,
  tagged, and CITGM-tested, may intentionally omit commits from `main`, and are
  intended for early library and CI compatibility testing rather than
  production.
