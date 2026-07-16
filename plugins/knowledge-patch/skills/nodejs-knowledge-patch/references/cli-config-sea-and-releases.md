# CLI, Configuration, SEA, and Releases

Runtime flags, JSON and environment configuration, watch mode, single-executable applications, and release policy.

## Contents

- [JSON, environment, and watch configuration](#json-environment-and-watch-configuration)
- [Single-executable applications](#single-executable-applications)
- [Runtime flags and options](#runtime-flags-and-options)
- [Release lines and distribution](#release-lines-and-distribution)

## JSON, environment, and watch configuration

### Experimental JSON configuration files (since 23.10.0)

Node CLI options can now be placed under `nodeOptions` in a trusted JSON file. Load an explicit file with `--experimental-config-file=path`, or use `--experimental-default-config-file` to load `node.config.json`; Node does not sanitize or validate the file.

```json
{
  "$schema": "https://nodejs.org/dist/v23.10.0/docs/node-config-schema.json",
  "nodeOptions": {
    "test-coverage-lines": 80,
    "test-coverage-branches": 60
  }
}
```

```console
node --experimental-config-file=node.config.json --test --experimental-test-coverage
```

### Multiple environment files in watch mode (since 25.2.0)

Watch mode now handles multiple environment files correctly across restarts.

### Namespaced configuration options (since 24.2.0)

The experimental JSON configuration-file parser now accepts namespace-owned options. Config generators should follow the schema for the matching Node version rather than assuming that every supported setting is a flat ordinary Node option.

### Permission and test configuration namespaces (since 25.4.0)

JSON configuration files now support `permission` and `test` namespaces. Rename the former `testRunner` namespace to `test`; a configured namespace is implicitly enabled.

### Stable `.env` file support (since 24.10.0)

Node's built-in `.env` file support is now stable rather than experimental.

### Watch configuration namespace (since 25.1.0)

Node's JSON configuration files now support a watch namespace, allowing watch-mode settings to be grouped in their own configuration section.

### Watch-mode environment reloads (since 23.7.0)

When `--watch` is combined with `--env-file-if-exists`, process restarts now reload the environment file, so edits take effect on the next restart.

### Watch-mode restart signals (since 24.4.0)

`--watch-kill-signal` selects the signal used to stop the running process before a watch-mode restart; for example, `node --watch --watch-kill-signal=SIGINT app.js`.


## Single-executable applications

### Direct single-executable builds (since 25.5.0)

`node --build-sea sea-config.json` now performs SEA preparation and binary generation in one step, writing the final executable named by the configuration's `output` field. The older `--experimental-sea-config` and postject-based workflow remains supported for now.

```json
{ "main": "hello.js", "output": "sea" }
```

### ESM code caches in single-executable applications (since 25.9.0)

SEA code caching now supports an ES module entry point, so `useCodeCache` can be enabled for an `.mjs` main.

```json
{ "main": "app.mjs", "output": "app", "useCodeCache": true }
```

### Execution arguments in single-executable applications (since 24.7.0)

SEA configuration accepts `execArgv` for baked-in Node arguments and `execArgvExtension` to control runtime additions: `"none"` rejects them, `"cli"` accepts the special `--node-options` flag, and the default `"env"` reads `NODE_OPTIONS`.

```json
{
  "main": "./app.js",
  "output": "./sea-prep.blob",
  "execArgv": ["--no-warnings"],
  "execArgvExtension": "cli"
}
```

```console
sea --node-options="--max-old-space-size=4096" user-arg
```

### SEA built-in warning suppression (since 23.9.0)

A single-executable application built with `disableExperimentalSEAWarning: true` now also suppresses its built-in experimental warning.


## Runtime flags and options

### Percentage-based old-space limits (since 24.6.0)

`--max-old-space-size` now accepts a percentage as well as an absolute size.

```console
node --max-old-space-size=75% app.js
```

### Removed CLI opt-outs (since 23.0.0)

The `--no-experimental-fetch`, `--no-experimental-global-webcrypto`, and `--no-experimental-global-customevent` flags have been removed, so those globals can no longer be disabled with these switches. The deprecated `--trace-atomics-wait` flag also reached end-of-life.

### Removed experimental default-type flag (since 23.4.0)

The `--experimental-default-type` CLI flag has been removed. Declare module type explicitly with package metadata or `.mjs` and `.cjs` extensions instead of relying on that override.


## Release lines and distribution

### Alpha channel (release-schedule)

Each upcoming line now has an October-through-March Alpha phase for compatibility testing. Alpha builds use semver prerelease versions such as `27.0.0-alpha.1`; semver-major changes and API churn are allowed, the cadence is flexible, and they are not for production.

Unlike automated, untested nightlies from `main`, Alpha releases are selected, signed, tagged, and tested with CITGM, and may omit changes present on `main`. Library authors should add Alphas to CI early—especially if they otherwise test only LTS—so breaking changes can be reported before that line reaches users.

### Annual all-LTS release cycle (release-schedule)

Starting with 27.x, Node.js moves from two majors per year to one Current release each April, and every major becomes LTS in October; the odd/even LTS distinction is gone. Version numbers align with the year of the initial Current release (`27.0.0` in 2027, `28.0.0` in 2028), and each line has six months as Current followed by 30 months of LTS, reaching EOL 36 months after its Current release.

Node.js 26 is the final old-model line, entering LTS in October 2026, maintenance in October 2027, and EOL in April 2029. Node.js 27 is the first new-model line: Alpha starts in October 2026, `27.0.0` ships in April 2027, LTS begins in October 2027, and EOL is April 2030.

### Bundled package tooling (since 24.0.0)

Node.js 24 ships with npm 11. Corepack is still documented as being removed from the Node.js distribution in version 25 and later, so deployments that rely on it should arrange a separate installation before that upgrade.

### Node.js 24 enters LTS (since 24.11.0)

Node.js 24.11.0 starts the "Krypton" LTS line, which receives updates through the end of April 2028. Apart from LTS metadata it is unchanged from 24.10.0; runtime detection can use `process.release.lts`, whose value is `'Krypton'` for this line.

### Release signing key (since 26.5.0)

Future Node.js releases may be signed with Stewart X Addison's Ed25519 release key, fingerprint `655F3B5C1FB3FA8D1A0CA6BDE4A7D232B936D2FD`; release-verification keyrings need this key.
