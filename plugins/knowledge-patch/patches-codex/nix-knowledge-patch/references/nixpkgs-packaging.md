# Nixpkgs Packaging

## General derivation and hook migrations

### Broken-symlink enforcement (since nixos-25.05, nixos-25.11)

The `no-broken-symlinks` hook rejects dangling and reflexive output symlinks;
set `dontCheckForBrokenSymlinks = true` only for intentional cases. It also
rejects links into `$TMPDIR`, normally `/build`.

### Replace substitution helpers (since nixos-25.05)

`substituteAll` and `substituteAllFiles` are deprecated for removal. Use
`replaceVars`.

### Structured derivation environment (since nixos-25.11)

`stdenv.mkDerivation` and related builders require `env` to be an attribute
set. Put an environment variable literally named `env` at `env.env`.

```nix
stdenv.mkDerivation { env.env = "value"; }
```

### Debug outputs and reference checks (since nixos-25.11)

A derivation combining `separateDebugInfo` with `allowedReferences`,
`allowedRequisites`, `disallowedReferences`, or `disallowedRequisites` must
set `__structuredAttrs = true`. The checks do not apply to the generated
`debug` output.

### `meta.mainProgram` affects builds (since nixos-25.11)

`meta.mainProgram` determines `NIX_MAIN_PROGRAM`, so changing it can rebuild a
package. `versionCheckHook` may fail when `pname` differs from the selected
program instead of silently checking the `pname` executable.

### PIE and temporary symlinks (since nixos-25.11)

Toolchains enable PIE by default, so the `pie` hardening flag was removed.
Packages that cannot use PIE must add `-no-pie` through `CFLAGS`. Also remove
output symlinks that point into a temporary build directory.

### Flat input lists (since nixos-26.05)

Nested lists in build and runtime inputs are deprecated. Flatten them.

## Language-specific builders

### Stable Rust vendoring hashes (since nixos-25.05)

Cargo 1.84 invalidated prior `cargoHash` values.
`rustPlatform.fetchCargoVendor` replaces Cargo-format-dependent
`fetchCargoTarball`, and `rustPlatform.buildRustPackage` no longer accepts
`cargoSha256`. Use and regenerate `cargoHash` for out-of-tree packages.

### Go modules (since nixos-25.05)

`buildGoPackage` was removed; use `buildGoModule`. Put `CGO_ENABLED` at
`env.CGO_ENABLED`; direct `GOOS` and `GOARCH` arguments now error. Use the new
`goSum` and self-referencing `finalAttrs` inputs when needed.

### Python hook flags (since nixos-25.05)

Without structured attributes, Python hook flags are space-separated
variables; with structured attributes, they are Bash arrays. Values are not
Bash-evaluated. Use `pytestFlags` and `unittestFlags`; `pytestFlagsArray` and
`unittestFlagsArray` are compatibility-only.

### Explicit Python build formats (since nixos-25.11)

`buildPythonPackage` and `buildPythonApplication` require an explicit modern
format. For setuptools, set `pyproject = true` and `build-system = [ setuptools
]`. Passing `stdenv` directly is deprecated; override the build helper.

### Node package set and Yarn 1 (since nixos-26.05)

`nodePackages` and `node2nix` were removed; use top-level packages or current
JavaScript helpers. `yarn2nix`, `mkYarnPackage`, and related tooling were also
removed. Yarn 1 packages should use `yarnBuildHook`, `yarnConfigHook`, and
`yarnInstallHook`.

### Node wrappers and outputs (since nixos-26.05)

`nodejs_latest` names Node 26. `nodejs` is a non-overridable wrapper around
`nodejs-slim` plus npm and Corepack outputs. Override `nodejs-slim` directly
and include `nodejs-slim.corepack` explicitly when using the slim package.

### Pnpm dependency fetchers (since nixos-26.05)

Top-level `fetchPnpmDeps` and `pnpmConfigHook` replace `pnpm.fetchDeps` and
`pnpm.configHook`. Fetcher versions 1 and 2 are deprecated; regenerate pnpm
hashes with version 3. Npm workspaces may set `npmDepsFetcherVersion = 2` on
`buildNpmPackage` for packument caching.

## Builder and package-set APIs

### PostgreSQL tools and languages (since nixos-25.05)

`postgresql` and `libpq` no longer include `pg_config`; add
`postgresql.pg_config` or `libpq.pg_config` to `nativeBuildInputs`. Select
PL/Python, PL/Perl, and PL/Tcl with `postgresql.withPackages`, not legacy
support overrides.

### Recursive package scopes (since nixos-25.05)

`lib.packagesFromDirectoryRecursive` rejects unknown arguments and can build
nested scopes matching the source directory tree.

### `buildEnv` fixed point and structured attributes (since nixos-25.11, nixos-26.05)

`buildEnv` takes `finalAttrs: { ... }` fixed-point arguments; its custom
result `.override` is deprecated. Put additional `stdenv.mkDerivation`
arguments under `derivationArgs`; direct `nativeBuildInputs` and `buildInputs`
are compatibility-only. `buildEnv` now always uses structured attributes.

### Instantiated systemd format (since nixos-25.11)

Do not use `pkgs.formats.systemd` directly. Instantiate it as
`pkgs.formats.systemd { }`.

### Fixed-point-free Nixpkgs configuration (since nixos-26.05)

Nixpkgs configuration functions receive `lib` directly alongside `pkgs`.
Use that `lib` for values such as licenses to avoid unnecessary package
fixed-point dependencies and recursion.

### Literal `requireFile` fields (since nixos-26.05)

`requireFile` treats `message` and `url` as literal strings, not Bash
here-documents. Forms such as `$PWD` do not expand and need no shell escaping.

## Fetchers and binary-cache builders

### Mesa component inputs (since nixos-25.05)

Packages linked to different Mesa versions can coexist. A package needing GBM
or DRI metadata should depend on `libgbm` or `dri-pkgconfig-stub`, not Mesa
itself.

### Binary-cache compression (since nixos-25.05)

`mkBinaryCache` produces zstd-compressed caches by default. Pass
`compression = "xz";` to keep the previous format.

### Fetcher-wide policy controls (since nixos-25.11)

Nixpkgs configuration can provide `rewriteURL` and `hashedMirrors` to all
`fetchurl` calls, `gitConfig` or `gitConfigFile` to all `fetchgit` calls, and
`npmRegistryOverrides` or `npmRegistryOverridesString` to all `fetchNpmDeps`
calls. Individual `fetchgit` calls accept `gitConfigFile` and `rootDir`;
`fetchNpmDeps` accepts `npmRegistryOverridesString`.

### Expression-level fetcher migrations (since nixos-26.05)

`fetchFromSavannah` is deprecated; use `fetchgit` or a release mirror.

## Library and module author APIs

### Removed library helpers (since nixos-25.11)

Use these replacements:

- `cartesianProductOfSets` → `lib.attrsets.cartesianProduct`
- `zipWithNames` / `zip` → `zipAttrsWithNames` / `zipAttrsWith`
- `literalExample` → `literalExpression` or `literalMD`
- `mapAttrsFlatten` → `lib.attrsets.mapAttrsToList`
- `lib.modules.defaultPriority` → `defaultOverridePriority`
- `mkPackageOptionMD` → `mkPackageOption`
- `replaceChars` → `replaceStrings`
- `lib.sources.path*` → corresponding `lib.filesystem` helpers
- `lib.strings.isCoercibleToString` → `isStringLike` or the broader
  `isConvertibleWithToString`
- `lib.types.string` → an appropriate type such as `lib.types.str`

### Correct free-form type checking (since nixos-25.11)

`types.either` no longer accepts mismatched values inside `freeformType`; this
also affects `oneOf`, `number`, and `numbers.*`. Module authors often need to
wrap the union in `attrsOf` so the free-form value has the intended shape.

### Command-line rendering APIs (since nixos-25.11)

Replace deprecated `lib.cli.toGNUCommandLine` and
`lib.cli.toGNUCommandLineShell` with `lib.cli.toCommandLine`,
`lib.cli.toCommandLineShell`, `lib.cli.toCommandLineGNU`, or
`lib.cli.toCommandLineShellGNU`. Choose GNU variants only for GNU rendering.

## Package scopes, files, and wrappers

### Nerd Fonts split (since nixos-25.05)

The monolithic `nerdfonts` became per-font packages under `nerd-fonts`.
Installed files also gained a font-specific directory below
`share/fonts/{opentype,truetype}/NerdFonts/`; update package names and paths.

### Stable formatter package (since nixos-25.11)

Use `pkgs.nixfmt`. `pkgs.nixfmt-rfc-style` is deprecated; the older formatter
is temporarily `pkgs.nixfmt-classic`.

### Top-level desktop scopes (since nixos-26.05)

MATE and Xfce packages moved to top-level attributes, and `xorg` is deprecated
in favor of top-level packages. Use names such as `pkgs.caja` and
`pkgs.xfce4-whiskermenu-plugin`; the `xfce` compatibility scope is scheduled
for removal.

### Stateless command-not-found (since nixos-26.05)

When a Nixpkgs source contains `programs.sqlite`, as channel tarballs do,
`command-not-found` enables automatically and uses that source database
without mutable setup.

### Neovim configuration delivery (since nixos-26.05)

Nixpkgs disables Neovim Python 3 and Ruby providers by default. Lua
dependencies are recorded in generated `init.lua`, not `LUA_PATH` wrapper
arguments; commands needing them must run after initialization with `-c`.
With `wrapRc = false`, load the generated init file yourself.

### Package expression replacements (since nixos-26.05)

Replace `xfce.mkXfceDerivation` with `stdenv.mkDerivation`,
`mpv-unwrapped.scripts` and `.wrapper` with `mpvScripts` and `mpv.override`,
and flatten nested input lists.

## Platforms and toolchain defaults

### Nix and Darwin floors (since nixos-25.11)

Evaluating Nixpkgs 25.11 requires Nix 2.18 or newer. Darwin requires macOS
14.0 and defaults to SDK 14.4. Darwin uses the system libc++; raise the
deployment target for packages needing newer C++ library features.

### Split Linux kernel modules output (since nixos-25.11)

Every in-tree Linux kernel module is in a separate `modules` output. Consumers
must not assume modules are in the primary output.

### Compiler and runtime defaults (since nixos-26.05)

Defaults move from GCC 14 to GCC 15, Node.js 22 LTS to 24 LTS, and Ruby 3.3
to 3.4. Unpinned packages can encounter the upstream compatibility changes.

### glibc executable-stack policy (since nixos-26.05)

glibc 2.42 does not make the stack executable merely because a shared library
requests it. Rebuild with `env.NIX_LDFLAGS = "-z,noexecstack"` or clear an
incorrect flag using `patchelf --clear-execstack`. Use
`GLIBC_TUNABLES=glibc.rtld.execstack=2` only per process for code that truly
requires an executable stack.

### Final Intel Darwin release (since nixos-26.05)

This is the final Nixpkgs release supporting `x86_64-darwin`; support and
binaries end with the branch at the end of 2026. To suppress the warning, set
`allowDeprecatedx86_64Darwin` through an explicit Nixpkgs import; flake use
does not inherit `~/.config/nixpkgs/config.nix`.

### XFS feature compatibility (since nixos-26.05)

`xfsprogs` 6.18 enables parent pointers and exchange-range by default. Use a
6.18-or-newer kernel for filesystems created with those features; GRUB 2 may
not boot from them.
