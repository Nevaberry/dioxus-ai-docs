# Nix Language, CLI, Flakes, and APIs

## Evaluation and language behavior

### Integer and configuration validation

Since 2.25.0, signed 64-bit overflow is an evaluation error instead of
wrapping. `builtins.fromJSON` rejects integers above the signed 64-bit maximum,
and flake `nixConfig` rejects negative values for numeric configuration options.

### Path values and literals

Enable explicit path diagnostics with the tri-state settings introduced in
2.34.0: `lint-url-literals`, `lint-short-path-literals`, and
`lint-absolute-path-literals`. They accept `ignore`, `warn`, or `fatal`.
`lint-url-literals` replaces the experimental `no-url-literals`, while
`lint-short-path-literals` replaces the 2.31.0 Boolean
`warn-short-path-literals`. Spell short relative paths as `./foo/bar`.

Relative paths in `file:` tarball references are rejected. By contrast,
`builtins.getFlake` accepts path values as of 2.35.2, so
`builtins.getFlake ./subflake` is valid when the path is in the store. It does
not force a lazily hashed source into the store.

### Structured derivations and dynamic attributes

The supported structured-derivation interface since 2.30.0 is:

```nix
builtins.derivation (attrs // { __structuredAttrs = true; })
```

Do not place serialized JSON in an environment variable named `__json`; that
construction is deprecated. Early 2.32 releases also regressed simple
string-literal dynamic attributes in `let`; 2.32.5 restores that special case,
but other dynamic attributes in `let` remain unsupported.

## CLI output and interactive use

### Raw and JSON output

`nix-instantiate --eval --raw` requires a string and prints it without quoting
or escaping (2.26.0). Modern `--json` commands pretty-print when stdout is a
terminal but stay single-line through a pipe or redirect (2.29.0). Use
`--pretty` or `--no-pretty` whenever automation must be terminal-independent.

Human-readable commands choose size units dynamically since 2.33.0. Never
assume MiB or one common unit per output line.

### Versioned `nix path-info` JSON

Pass `--json-format` with `nix path-info --json`. In 2.33.0, omission warns and
temporarily selects format 1:

- Format 1 uses absolute store-path keys and references, string hashes, and
  string content addresses.
- Format 2 wraps results in `version`, `storeDir`, and `info`, uses path
  basenames, and structures `ca` into a method and SRI hash.
- Format 3, added in 2.35.2, represents signatures as `{ keyName, sig }`
  objects. Readers still accept the older colon-delimited representation.

### Derivation JSON

The unstable derivation JSON representation uses store-path basenames rather
than full store paths from 2.32.0 onward. Derivation JSON version 4 in 2.33.0
wraps output in `version` and `derivations`, moves `inputSrcs` and `inputDrvs`
to `inputs.srcs` and `inputs.drvs`, and represents fixed-output content
addresses as objects. `nix derivation add` rejects version 3 and older.

### REPL and profiler behavior

`:reload` reloads flakes loaded with `:load-flake` as well as files and
command-line values (2.29.0). Since 2.34.0 the REPL accepts semicolon-separated
bindings, nested attribute bindings, and `inherit` statements.

Use the stack-sampling evaluator profiler from 2.30.0 with
`--eval-profiler flamegraph`; select the destination with
`--eval-profile-file` (default `nix.profile`) and sampling rate with
`--eval-profiler-frequency` (default 99 Hz). The collapsed stack output works
with FlameGraph, speedscope, and compatible viewers.

### Profile and formatter commands

Use `nix profile add` (2.30.0); `nix profile install` remains an alias. `nix
fmt` without arguments no longer supplies an implicit `.` to the formatter
(2.25.0), allowing formatters to define repository-wide no-argument behavior.
`nix formatter build` builds and links the formatter and prints the complete
executable path without running it (2.29.0).

## Flake inputs, locks, and sources

### Relative repository inputs

Flakes can use a sibling flake through a relative path input (2.26.0):

```nix
inputs.foo.url = "path:./foo";
```

This changes the lock format; older Nix versions cannot read locks containing
relative-path inputs. During lock generation, indirect inputs such as
`nixpkgs` ignore system and user registries. Only the global registry and
command-line `--override-flake` values participate, so pin explicit input URLs
for reproducibility.

When an input reference changes, lock updates preserve nested versions from
that input's own lock rather than fetching the newest nested inputs (2.31.0).

### Git submodules, LFS, and hashing

Since 2.27.0 a Git-backed flake can declare its own source requirements:

```nix
inputs.self.submodules = true;
inputs.self.lfs = true;
```

Git references can request LFS with `lfs=1`. LFS-over-SSH honors `NIX_SSHOPTS`
and URL ports and follows the endpoint returned by `git-lfs-authenticate`
(2.31.0). Experimental Git-hashed store objects can use SHA-256 as well as
SHA-1 from that release.

`builtins.fetchGit` and Git `builtins.fetchTree` inputs again accept SCP-like
URLs in 2.35.2, including literal `~` paths and bracketed IPv6 hosts:

```nix
builtins.fetchGit "host:~/relative/to/home"
builtins.fetchTree { type = "git"; url = "user@[::1]:~/repo"; }
```

The `github:` fetcher now rejects unknown URL parameters; for example, `tag`
is invalid rather than ignored (2.35.2).

### Non-flake inputs and source subdirectories

Since 2.30.0, an input declared with `flake = false` exposes its containing
source's `sourceInfo`. A non-flake input can select a subdirectory with
`?dir=subdir`, distinguishing the parent source from the selected child.

```nix
inputs.data = {
  url = "path:./sources?dir=subdir";
  flake = false;
};
```

### Fetch and inspection commands

- `nix flake prefetch --out-link ./result REF` creates an output link
  (2.27.0).
- `nix flake prefetch-inputs .` fetches all inputs concurrently and may fetch
  inputs evaluation would not use (2.31.0).
- `nix flake archive --to STORE --no-check-sigs .` bypasses signature checks
  for direct remote archiving (2.30.0).
- `nix flake show` skips IFD-dependent outputs and displays the rest instead of
  failing the complete command (2.29.0).
- `nix flake check` may leave substitutable derivations unrealized (2.32.0).
- `nix flake check --print-out-paths` prints outputs, and `--out-link` creates
  links; without it, no links are created (2.35.2).

### Registry, clone, and channel operations

`nix registry resolve NAME` prints the flake reference selected for an indirect
registry input without fetching or evaluating it (2.33.0). `nix flake clone`
can clone arbitrary input types, including tarball-backed flakes. Built-in
channel URLs now use `https://channels.nixos.org/`; migrate persisted URLs and
allowlists away from the redirecting `https://nixos.org/channels/` endpoint.

The channel server's `nixexprs.tar.xz` implements the lockable HTTP tarball
protocol (nixos-25.05), so it can be used directly as a pinned flake input.

## C, C++, and embedding APIs

### C++ headers and build system

Installed headers use component-qualified paths as of 2.28.0:

```cpp
#include <nix/store/derived-path.hh>
#include <nix/util/configuration.hh>
```

pkg-config supplies `-I${includedir}` rather than an include path ending in
`/nix`. Configuration headers need not be force-included, and remaining public
configuration macros use the `NIX_` prefix. Nix source builds use Meson and
Ninja; the Make build was removed in 2.26.0.

### Flake C APIs

`nix_flake_init_global` was removed in 2.28.0. Add settings to each evaluator
state builder with `nix_flake_settings_add_to_eval_state_builder`.

In 2.29.0, C consumers gained direct flake loading and basic locking. Choose a
mode with `nix_flake_lock_flags_set_mode_check`, `_virtual`, or
`_write_as_needed`; adding an input override also enables virtual mode. The
`nix-fetchers-c` library manages `nix.conf` settings for built-in fetchers.

### Value and store C APIs

Since 2.32.0, `nix_get_attr_name_byidx` and `nix_get_attr_byidx` take mutable
`nix_value *` because lookup can mutate a value. This is ABI-compatible but can
require const-correctness source fixes. Use `nix_get_list_byidx_lazy`,
`nix_get_attr_byname_lazy`, and `nix_get_attr_byidx_lazy` to forward members
without forcing them.

The 2.34.0 API adds `nix_store_query_path_from_hash_part()` and
`nix_store_copy_path()` for path lookup and controlled inter-store copying.
C primop failures are sticky when a thunk is forced again; mark intentionally
retryable failures with `NIX_ERR_RECOVERABLE`.

The `nix` executable exports C-binding symbols as of 2.35.2, so C API plugins
can resolve those symbols dynamically instead of linking every `libnix*c.so`.

### Binary-directory assumptions

Separately packaged `libnixstore` cannot infer a Nix binary directory
(2.25.0). Applications using remote builds must put Nix tools on `PATH` or set
`build-hook` explicitly. The Perl bindings no longer expose `getBinDir`.

## Installation and platform entry points

The Rust installer rewrite entered beta in 2.34.0. It can install over an
existing script-based installation, and its `uninstall` removes the complete
installation even when an older installer created it. Review that destructive
scope before invoking it.

The traditional installer supports `x86_64-freebsd` in 2.35.2 and uses
FreeBSD `libjail` sandboxing by default. The Rust installer does not yet support
FreeBSD.

## Environment locations

Since 2.25.0, `NIX_CACHE_HOME`, `NIX_CONFIG_HOME`, `NIX_DATA_HOME`, and
`NIX_STATE_HOME` override the corresponding XDG variables for Nix alone. Use
them for an isolated Nix environment without changing other applications'
XDG layout.

Fish profile scripts derive `NIX_PROFILE` from `$NIX_LINK` in 2.35.2 rather
than always using `$HOME/.nix-profile`, so custom profile links work in Fish
sessions too.
