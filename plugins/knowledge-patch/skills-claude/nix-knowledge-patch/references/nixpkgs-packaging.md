# Nixpkgs Packaging

## General derivation interfaces

### Strict `env` and structured attributes

`stdenv.mkDerivation` and related builders require `env` to be an attribute
set in nixos-25.11. To create an environment variable literally named `env`,
write:

```nix
stdenv.mkDerivation {
  env.env = "value";
}
```

A derivation combining `separateDebugInfo` with `allowedReferences`,
`allowedRequisites`, `disallowedReferences`, or `disallowedRequisites` must set
`__structuredAttrs = true`. The reference checks do not apply to the generated
`debug` output.

`buildEnv` switched to fixed-point `finalAttrs: { ... }` arguments in
nixos-25.11. Its custom result `.override` is deprecated; place extra
`stdenv.mkDerivation` values under `derivationArgs`. Direct `nativeBuildInputs`
and `buildInputs` remain only as compatibility inputs. In nixos-26.05,
`buildEnv` completes this migration and uses structured attributes exclusively.

### Symlinks, PIE, and input shapes

The `no-broken-symlinks` hook in nixos-25.05 rejects dangling and reflexive
links. Set `dontCheckForBrokenSymlinks = true` only for intentional cases. In
nixos-25.11, the hook also rejects output symlinks into `$TMPDIR` (normally
`/build`).

The `pie` hardening flag was removed because current toolchains enable PIE by
default. A package that genuinely cannot use PIE should add `-no-pie` through
`CFLAGS`. Nested lists in build and runtime inputs are deprecated in
nixos-26.05; flatten them.

### Main programs and fixed-point-safe configuration

`meta.mainProgram` sets `NIX_MAIN_PROGRAM` from nixos-25.11, so changing it can
trigger a rebuild. `versionCheckHook` can now fail when `pname` differs from
the selected executable instead of silently checking a `pname` binary.

In nixos-26.05, Nixpkgs configuration functions receive `lib` directly as
well as `pkgs`. Use the direct `lib` argument for licenses and other library
values to avoid pulling on the package fixed point and causing recursion.

## Language ecosystems

### Rust

Cargo 1.84 invalidated older `cargoHash` values in nixos-25.05. Regenerate
them, replace Cargo-format-dependent `fetchCargoTarball` with
`rustPlatform.fetchCargoVendor`, and remove the unsupported `cargoSha256`
argument from `rustPlatform.buildRustPackage`.

### Go

`buildGoPackage` was removed in nixos-25.05; use `buildGoModule`. Put
`CGO_ENABLED` below `env`, while direct `GOOS` and `GOARCH` builder arguments
now error. Use `goSum` and self-referencing `finalAttrs` inputs where required.

```nix
env.CGO_ENABLED = "1";
```

### Python

Python hooks use space-delimited flag variables without structured attributes
and Bash arrays with structured attributes (nixos-25.05). They no longer
Bash-evaluate values. Use `pytestFlags` and `unittestFlags`; the old `*Array`
names are compatibility-only.

`buildPythonPackage` and `buildPythonApplication` require an explicit format
in nixos-25.11. For a modern setuptools build:

```nix
(buildPythonPackage.override { stdenv = customStdenv; }) {
  pyproject = true;
  build-system = [ setuptools ];
}
```

Passing `stdenv` directly to the package definition is deprecated; override
the helper as shown.

### Node.js, npm, pnpm, and Yarn

Nixos-26.05 moves the default Node.js from 22 LTS to 24 LTS.
`nodejs_latest` denotes Node 26. `nodejs` is a non-overridable wrapper around
`nodejs-slim` plus npm and Corepack outputs; override `nodejs-slim` directly
and add `nodejs-slim.corepack` explicitly when using the slim package.

The `nodePackages` set and `node2nix` are removed. Move to top-level packages
or maintained JavaScript helpers. Yarn's `yarn2nix`, `mkYarnPackage`, and
related tooling are also removed; package Yarn 1 software with
`yarnBuildHook`, `yarnConfigHook`, and `yarnInstallHook`.

Replace `pnpm.fetchDeps` and `pnpm.configHook` with top-level
`fetchPnpmDeps` and `pnpmConfigHook`. Fetcher versions 1 and 2 are deprecated,
so regenerate pnpm hashes with version 3. For npm workspaces,
`buildNpmPackage` can set `npmDepsFetcherVersion = 2` for packument caching.

### Ruby and compiler defaults

Nixos-26.05 updates the default GCC from 14 to 15 and Ruby from 3.3 to 3.4, in
addition to Node 24. Unpinned package expressions inherit the corresponding
upstream incompatibilities.

### glibc executable stacks

glibc 2.42 no longer makes the process stack executable merely because a
loaded shared object requests it (nixos-26.05). Prefer rebuilding with
`env.NIX_LDFLAGS = "-z,noexecstack"` or clearing an erroneous marker using
`patchelf --clear-execstack`. Reserve
`GLIBC_TUNABLES=glibc.rtld.execstack=2` for individual programs that truly
require an executable stack.

## Fetchers and source handling

### Substitution and policy controls

`replaceVars` supersedes deprecated `substituteAll` and `substituteAllFiles`
from nixos-25.05.

Nixpkgs configuration in nixos-25.11 can apply `rewriteURL` and
`hashedMirrors` to `fetchurl`, `gitConfig` or `gitConfigFile` to all `fetchgit`
calls, and `npmRegistryOverrides` or `npmRegistryOverridesString` to all
`fetchNpmDeps` calls. Individual `fetchgit` calls accept `gitConfigFile` and
`rootDir`; `fetchNpmDeps` accepts `npmRegistryOverridesString`.

`fetchFromSavannah` is deprecated in nixos-26.05; use `fetchgit` or a release
mirror.

### Literal `requireFile` values

In nixos-26.05, `requireFile` treats `message` and `url` as literal strings,
not Bash here-document content. Text such as `$PWD` is not expanded and does
not need shell escaping.

## Native libraries, graphics, and kernels

### Mesa and PostgreSQL build inputs

Applications linked against different Mesa versions can coexist from
nixos-25.05. Depend on `libgbm` for GBM metadata or `dri-pkgconfig-stub` for
DRI metadata rather than depending on Mesa as a proxy.

`postgresql` and `libpq` no longer include `pg_config`; add
`postgresql.pg_config` or `libpq.pg_config` to `nativeBuildInputs`.
PL/Python, PL/Perl, and PL/Tcl are selected with `postgresql.withPackages`
instead of support overrides.

### Kernel output compatibility

Evaluating nixos-25.11 Nixpkgs requires Nix 2.18 or newer. In-tree Linux kernel
modules moved into each kernel package's separate `modules` output; consumers
must not expect them in the primary output.

### Darwin platform policy

Nixos-25.11 requires macOS 14.0 or newer and defaults to SDK 14.4. Darwin uses
the system libc++; packages needing newer C++ library features must raise the
deployment target.

Nixos-26.05 is the final Nixpkgs release for `x86_64-darwin`; support and
binaries end with its release branch at the end of 2026. Suppress the warning
with `allowDeprecatedx86_64Darwin`, passed through an explicit Nixpkgs import
for flakes rather than `~/.config/nixpkgs/config.nix`.

## Fonts, locales, and package scopes

### Fonts and locales

The monolithic `nerdfonts` package split into per-font packages below
`nerd-fonts` in nixos-25.05. Font files also gained per-font directories below
`share/fonts/{opentype,truetype}/NerdFonts/`; migrate package names and
hard-coded paths.

Prefer `i18n.extraLocales` for additional locales. `i18n.supportedLocales`
remains functional but is an implementation detail and warns when required
locales are absent. Use `i18n.defaultCharset` and `i18n.localeCharsets` for
global and per-locale character sets (nixos-25.05).

### Recursive and desktop package scopes

`lib.packagesFromDirectoryRecursive` rejects unknown arguments and can create
nested scopes mirroring the source directory tree (nixos-25.05).

In nixos-26.05, MATE and Xfce packages move to top-level attributes and the
`xorg` package set is deprecated in favor of top-level packages. Use, for
example, `pkgs.caja` and `pkgs.xfce4-whiskermenu-plugin`. The compatibility
`xfce` scope is scheduled for removal.

The same release deprecates `xfce.mkXfceDerivation` in favor of
`stdenv.mkDerivation`. Replace `mpv-unwrapped.scripts` and `.wrapper` with
`mpvScripts` and `mpv.override`.

### Nix formatter package names

Use stable `pkgs.nixfmt` from nixos-25.11. `pkgs.nixfmt-rfc-style` is
deprecated; the old implementation remains temporarily as
`pkgs.nixfmt-classic`.

## Nixpkgs library and format APIs

### Removed or renamed library functions

For nixos-25.11, apply these replacements:

| Removed or deprecated | Replacement |
| --- | --- |
| `cartesianProductOfSets` | `lib.attrsets.cartesianProduct` |
| `zipWithNames` | `zipAttrsWithNames` |
| `zip` | `zipAttrsWith` |
| `literalExample` | `literalExpression` or `literalMD` |
| `mapAttrsFlatten` | `lib.attrsets.mapAttrsToList` |
| `lib.modules.defaultPriority` | `defaultOverridePriority` |
| `mkPackageOptionMD` | `mkPackageOption` |
| `replaceChars` | `replaceStrings` |
| `lib.sources.path*` | corresponding `lib.filesystem` helpers |
| `lib.strings.isCoercibleToString` | `isStringLike` or broader `isConvertibleWithToString` |
| `lib.types.string` | a specific type such as `lib.types.str` |

`types.either` now correctly rejects mismatched values inside `freeformType`;
this also affects `oneOf`, `number`, and `numbers.*`. Module authors often need
`attrsOf (types.either ...)` so the free-form value has the intended shape.

### Command-line rendering

Replace deprecated `lib.cli.toGNUCommandLine` and `toGNUCommandLineShell` with
`lib.cli.toCommandLine`, `toCommandLineShell`, `toCommandLineGNU`, or
`toCommandLineShellGNU`. Choose GNU variants only for GNU-specific rendering.

### Format helper instantiation

Direct `pkgs.formats.systemd` use is deprecated. Instantiate it like other
format helpers in nixos-25.11:

```nix
systemdFormat = pkgs.formats.systemd { };
```

## Binary-cache derivations

`mkBinaryCache` creates zstd-compressed caches by default in nixos-25.05. Pass
`compression = "xz";` only when consumers require the previous format.

## Neovim packaging

Nixpkgs disables Neovim's Python 3 and Ruby providers by default in
nixos-26.05. Lua dependencies are recorded in generated `init.lua` instead of
wrapper `LUA_PATH` arguments. Run commands needing them after initialization
with `-c`; when `wrapRc = false`, load the generated init file yourself.

## Stateless command lookup

When the Nixpkgs source contains `programs.sqlite`, including channel tarballs,
`command-not-found` is automatically enabled in nixos-26.05 and reads that
database directly without maintaining separate state.
