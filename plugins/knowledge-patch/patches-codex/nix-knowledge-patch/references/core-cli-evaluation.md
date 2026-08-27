# Core CLI, Evaluation, and Configuration

## Evaluation and expression behavior

### Integer overflow fails (since 2.25.0)

Signed 64-bit integer overflow is an evaluation error rather than a wrapping
operation. `builtins.fromJSON` also rejects integers above the signed 64-bit
maximum, and flake `nixConfig` rejects negative values for configuration
options.

### Supported structured derivations (since 2.30.0)

Do not create structured derivations by putting serialized JSON in `__json`.
That path is deprecated. Set `__structuredAttrs = true` on
`builtins.derivation` instead.

```nix
builtins.derivation (attrs // { __structuredAttrs = true; })
```

### Short and absolute path-literal linting (since 2.31.0, 2.34.0)

The earlier `warn-short-path-literals` Boolean warned about paths such as
`foo/bar`; spell them `./foo/bar`. The stable replacement is the tri-state
`lint-short-path-literals`. `lint-url-literals` replaces the experimental
`no-url-literals`, and `lint-absolute-path-literals` checks `/...` and `~/...`.
Each accepts `ignore` (default), `warn`, or `fatal`.

```ini
lint-url-literals = fatal
lint-short-path-literals = warn
lint-absolute-path-literals = warn
```

### Dynamic attributes in `let` (since 2.32.0)

The simple string-literal dynamic-attribute special case in `let` was broken
in early 2.32 releases and restored in 2.32.5. Other dynamic attributes in
`let` remain unsupported.

### Path values for `builtins.getFlake` (since 2.35.2)

`builtins.getFlake ./subflake` is accepted. The path still cannot be outside
the store, and the call does not force a lazily hashed source to be copied
into the store.

## CLI commands and output

### Formatter invocation (since 2.25.0, 2.29.0)

Zero-argument `nix fmt` no longer receives an implicit `.`; a formatter may
distinguish it from `nix fmt .`; for example, treefmt may format the whole
tree. `nix formatter build` builds and links the configured formatter without
running it and prints the full executable path.

### Raw legacy evaluation output (since 2.26.0)

`nix-instantiate --eval --raw` requires a string result and prints it verbatim
without quoting or escaping.

### Terminal-sensitive JSON (since 2.29.0)

Commands using `--json` pretty-print when stdout is a terminal and stay
single-line when redirected. Use `--pretty` or `--no-pretty` when a stable
format matters, especially under a pseudoterminal.

### REPL reloading and bindings (since 2.29.0, 2.34.0)

`:reload` reloads flakes added with `:load-flake` as well as files and
command-line loads. The REPL also accepts semicolon-separated bindings,
nested attribute bindings, and `inherit` statements.

```text
a = { x = 1; y = 2; }
inherit (a) x y
p = 1; q = 2;
```

### `nix profile add` (since 2.30.0)

Use `nix profile add`; `nix profile install` remains an alias.

### Versioned `path-info` JSON (since 2.33.0, 2.35.2)

Always pass `--json-format` with `nix path-info --json`; omitting it currently
warns and defaults to format 1 but is planned to fail. Format 1 uses absolute
store paths and string hashes/content addresses. Format 2 wraps data in
`version`, `storeDir`, and `info`, uses path basenames, and structures `ca`.
Format 3 represents signatures as `{ "keyName": ..., "sig": ... }` objects;
parsers still accept the older colon-separated strings.

### Derivation JSON migrations (since 2.32.0, 2.33.0)

Unstable derivation JSON uses store-path basenames rather than absolute store
paths. `nix derivation show` emits version 4 with top-level `version` and
`derivations`; `inputSrcs` and `inputDrvs` become `inputs.srcs` and
`inputs.drvs`, and fixed-output content addresses are structured. `nix
derivation add` rejects version 3 and earlier.

### Human-readable size units (since 2.33.0)

Commands and progress displays choose size units dynamically. Parsers must not
assume MiB or assume that every value on a line shares one unit.

## Configuration and execution

### Nix-specific XDG overrides (since 2.25.0)

`NIX_CACHE_HOME`, `NIX_CONFIG_HOME`, `NIX_DATA_HOME`, and `NIX_STATE_HOME`
override the matching XDG variables for Nix only. Use them to isolate Nix
without changing the rest of a user's XDG layout.

### Build directories use the state directory (since 2.30.0)

Temporary build directories no longer follow `$TMPDIR` or default to `/tmp`.
`build-dir` defaults to `builds` below `$NIX_STATE_DIR`, normally
`/nix/var/nix/builds`. Update storage provisioning and build monitors.

### Automatic core detection (since 2.31.0)

`build-cores = 0` detects the available CPU count and exports that value in
`NIX_BUILD_CORES`, just like an unset value. Builders no longer receive zero.

### Daemon protocol floor (since 2.32.0)

Nix 2.32 cannot communicate with daemon worker-protocol peers older than Nix
2.0 (protocol version 18). Upgrade both client and daemon sides before mixing
them.

### Opaque temporary directory names (since 2.32.0)

Build directory paths no longer contain the derivation name. Monitoring tools
must obtain derivation identity elsewhere.

### External builders (since 2.32.0)

The experimental `external-builders` setting dispatches derivations for
selected system types to helper programs, for example a QEMU-based emulator.

## Diagnostics and observability

### Stack-sampling evaluator profiles (since 2.30.0)

`--eval-profiler flamegraph` emits collapsed stacks for `flamegraph.pl`,
speedscope, and compatible tools. `--eval-profile-file` selects the
destination (default `nix.profile`) and `--eval-profiler-frequency` sets the
sample rate (default 99 Hz).

### Trace import from derivation (since 2.30.0)

Set `trace-import-from-derivation = true` to warn for each IFD while leaving
`allow-import-from-derivation` enabled. This supports gradual CI cleanup.

### Mirror logs as JSON (since 2.30.0)

`json-log-path` copies every Nix log message in JSON form to a file or Unix
domain socket.

## Installation and shell integration

### Rust installer and uninstall (since 2.34.0)

The Rust installer is beta and can run over an existing script-based
installation. Its uninstall command removes the entire Nix installation,
including installations created by the older installer.

### FreeBSD support boundary (since 2.35.2)

The traditional installer supports `x86_64-freebsd`, whose builds use
FreeBSD `libjail` sandboxing by default. The beta Rust installer does not
support FreeBSD.

### Fish profile links (since 2.35.2)

Fish profile scripts derive `NIX_PROFILE` from `$NIX_LINK`; custom profile
links no longer fall back unconditionally to `$HOME/.nix-profile`.
