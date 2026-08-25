# CLI, Configuration, SEA, and Releases

Use this reference for cli, configuration, sea, and releases work.

## Alpha releases are qualified but unstable (`release-schedule`)

Alpha releases may contain semver-major changes and change APIs between releases. Unlike automated, untested nightlies from `main`, they are signed, tagged, and CITGM-tested, may intentionally omit commits from `main`, and are intended for early library and CI compatibility testing rather than production use.

## Burst-safe asynchronous filesystem watching (`24.3.0`)

The async iterator returned by `fs.promises.watch()` now handles bursts of filesystem events correctly, which matters when events arrive faster than a `for await` consumer processes them.

## Complete `--print` string output (`24.14.0`)

`node --print` no longer truncates long string results, so scripts consuming its standard output receive the complete value.

## Configurable watch-mode termination signal (`24.4.0`)

`--watch-kill-signal` selects the signal used to stop the running process before a watch-mode restart.

```sh
node --watch --watch-kill-signal=SIGINT app.js
```

## CPU profiling through `NODE_OPTIONS` (`23.9.0`)

The `--cpu-prof*` family is now allowed in `NODE_OPTIONS`, so CPU profiling can be enabled without changing the application command.

```sh
NODE_OPTIONS=--cpu-prof node app.js
```

## Direct single-executable builds (`25.5.0`)

`node --build-sea` builds a Single Executable Application directly from its configuration, replacing the previous multi-step copy, preparation-blob, and `postject` workflow. The older `--experimental-sea-config` and injection-based process remain supported for now.

```sh
echo 'console.log("Hello")' > hello.js
echo '{ "main": "hello.js", "output": "sea" }' > sea-config.json
node --build-sea sea-config.json
./sea
```

## Empty `NO_COLOR` values (`24.4.0`)

An empty `NO_COLOR` environment variable is now treated as absent rather than disabling color; use a non-empty value when color must be suppressed.

## Empty experimental configuration (`24.19.0`)

An empty configuration selected with `--experimental-config-file` is now accepted, allowing generated or optional configuration to represent no overrides without failing at startup.

## ESM code caches in single-executable applications (`25.9.0`)

Single-executable applications can now generate and use a code cache when their entry point is an ES module.

```json
{
  "main": "app.mjs",
  "output": "app",
  "useCodeCache": true
}
```

## ESM watch and synchronous-hook fixes (`24.13.0`)

Watch mode now restarts after ESM syntax errors in 24.13.1. Synchronous resolution hooks also handle `require()` calls for `node:`-prefixed built-ins correctly.

## Execution arguments for single executable applications (`24.7.0`)

SEA configuration accepts `execArgv` for baked-in Node execution arguments and `execArgvExtension` to control runtime additions. The extension mode is `"none"`, `"cli"` for a `--node-options` argument, or `"env"` for `NODE_OPTIONS`; `"env"` is the default.

```json
{
  "main": "/path/to/bundled/script.js",
  "output": "/path/to/generated.blob",
  "execArgv": ["--no-warnings"],
  "execArgvExtension": "cli"
}
```

```sh
sea --node-options="--max-old-space-size=4096" user-arg
```

## Experimental JSON configuration files (`23.10.0`)

CLI options can be supplied through a JSON file's `nodeOptions` object. `--experimental-default-config-file` reads `node.config.json`, while `--experimental-config-file=<path>` selects another file; Node does not sanitize or validate its contents, so configuration files must be trusted.

```json
{
  "$schema": "https://nodejs.org/dist/v23.10.0/docs/node-config-schema.json",
  "nodeOptions": {
    "test-coverage-lines": 80,
    "test-coverage-branches": 60
  }
}
```

```sh
node --experimental-config-file=node.config.json --test --experimental-test-coverage
```

## Heap profiling through `NODE_OPTIONS` (`23.1.0`)

The `--heap-prof` flag is now accepted in `NODE_OPTIONS`, so heap profiling can be enabled without changing the application command.

```sh
NODE_OPTIONS=--heap-prof node app.js
```

## Inspector flags for single-executable applications (`24.8.0`)

Single-executable applications now accept inspector command-line flags such as `--inspect` and `--inspect-brk`, allowing packaged executables to be debugged through the inspector.

## macOS x64 is excluded from SEA support (`24.18.0`)

Single Executable Application platform support explicitly excludes `darwin-x64`; SEA tooling must target another supported platform or architecture.

## Namespaced JSON configuration options (`24.2.0`)

Experimental JSON configuration files now support namespace options, expanding which structured Node options can be represented in the configuration file.

## New release-signing key (`26.5.0`)

Future Node.js releases may be signed with Stewart X Addison's Ed25519 release key, fingerprint `655F3B5C1FB3FA8D1A0CA6BDE4A7D232B936D2FD`. Release-verification keyrings need to include this key.

## Node.js 24 enters LTS (`24.11.0`)

Node.js 24.11.0 begins the "Krypton" LTS line, which receives updates through the end of April 2028. Apart from LTS metadata such as `process.release`, it is unchanged from 24.10.0.

## One annual major and an LTS path for every release line (`release-schedule`)

Starting with 27.x, Node.js moves from two major releases per year to one, and every release line proceeds to LTS. Each line spends six months in Alpha from October through March, six months as Current from April through October, and 30 months in LTS; Node.js 26 is the final line under the old model, while Node.js 27 begins Alpha in October 2026, releases 27.0.0 in April 2027, enters LTS in October 2027, and reaches EOL in April 2030.

## Optional environment files in watch mode (`23.7.0`)

Watch-mode restarts now reload an environment file supplied through `--env-file-if-exists`, so edits to the file are reflected after a restart.

```sh
node --watch --env-file-if-exists=.env app.js
```

## Removed default-type experiment flag (`23.4.0`)

The `--experimental-default-type` CLI option is removed, so startup commands can no longer rely on that module-type override.

## Retired CLI opt-outs (`23.0.0`)

The `--no-experimental-global-customevent`, `--no-experimental-fetch`, and `--no-experimental-global-webcrypto` switches are removed now that those globals are no longer optional experiments. `--trace-atomics-wait` is also end-of-life.

## Stable `.env` file support (`24.10.0`)

Node's built-in `.env` file support is now stable rather than experimental.

## Watch exclusions (`25.5.0`)

`fs.watch()` adds an `ignore` option, allowing a watcher to exclude selected paths instead of filtering their events after delivery.

## Watch settings in JSON configuration (`25.1.0`)

JSON configuration files now have a `watch` namespace, allowing watch-mode settings to be grouped separately from general Node options.

## Watch-mode restart provenance (`24.19.0`)

Watch mode now prints the name of the changed file that triggered a restart, making restart causes visible in its normal output.
