---
name: nix-knowledge-patch
description: Nix
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Nix Knowledge Patch

Use this skill when changing Nix expressions, Nix CLI integrations, flakes,
stores and caches, NixOS modules, Nixpkgs packages, or Home Manager
configurations. Check the relevant reference before preserving an old option,
output format, package name, service default, or builder interface.

## Reference index

| Reference | Topics |
| --- | --- |
| [Nix language, CLI, flakes, and APIs](references/nix-language-cli-flakes.md) | Evaluation, flake inputs and locks, CLI behavior, JSON formats, installers, C and C++ APIs |
| [Stores, builds, transports, and caches](references/stores-builds-caches.md) | Store settings, garbage collection, builders, SSH and HTTP transport, S3 and binary caches, hooks |
| [NixOS systems and services](references/nixos-systems-services.md) | Rebuild and boot flows, networking, systemd, security, databases, service migrations |
| [Nixpkgs packaging](references/nixpkgs-packaging.md) | Builders, hooks, package scopes, language ecosystems, library and expression migrations |
| [Home Manager](references/home-manager.md) | Activation, profiles, state-version behavior, program and service migrations, XDG and Darwin integration |

## Start with migrations that can break evaluation

### Use current path-literal lint settings

Replace the old URL-literal feature and Boolean short-path warning with the
tri-state settings. Each accepts `ignore`, `warn`, or `fatal`.

```ini
lint-url-literals = fatal
lint-short-path-literals = warn
lint-absolute-path-literals = warn
```

Write relative paths as `./foo/bar`; do not use relative paths in `file:`
tarball references.

### Treat integers as signed 64-bit values

Arithmetic overflow is an evaluation error. `builtins.fromJSON` rejects
larger integers, and negative numeric values are invalid for flake `nixConfig`
options.

### Build structured derivations explicitly

Do not serialize JSON into the `__json` environment variable. Set
`__structuredAttrs = true` on `builtins.derivation`; it is also required when
debug-info splitting is combined with derivation reference checks.

```nix
builtins.derivation (attrs // { __structuredAttrs = true; })
```

### Select current CLI and JSON interfaces

- Use `nix profile add`; `nix profile install` is only a compatibility alias.
- Pass `--json-format` to `nix path-info --json`; format 2 changes store-path
  keys and content-address representation, and format 3 structures signatures.
- Produce and consume derivation JSON version 4; `nix derivation add` rejects
  older versions.
- Do not parse human-readable sizes as fixed MiB values.
- Force `--pretty` or `--no-pretty` when JSON formatting must not depend on
  whether stdout is a terminal.

### Update C and C++ integrations

Include C++ headers as `nix/<component>/...`, rely on pkg-config's include
directory, and use public `NIX_` configuration macros. Configure flakes on
each evaluator-state builder; the global flake initializer is gone.

Indexed C accessors accept mutable values. Prefer lazy list and attribute
accessors when a sub-value must remain unevaluated. Plugins may resolve the
Nix executable's exported C symbols dynamically. Primop errors are sticky
unless returned as `NIX_ERR_RECOVERABLE`.

## Flake and source quick reference

### Declare repository features on inputs

Relative `path:` inputs can point to flakes in the same repository, but their
locks are incompatible with older clients. A Git-backed flake can declare
`inputs.self.submodules = true` and `inputs.self.lfs = true`. Git URLs can also
request LFS with `lfs=1`.

Lock generation ignores user and system registries for indirect inputs. Pin
URLs explicitly, use `nix registry resolve` to inspect registry resolution,
and remember that input updates preserve nested locks from the updated input.

### Prefer explicit source operations

- `nix flake prefetch-inputs` fetches all inputs concurrently.
- `nix flake prefetch --out-link` protects or exposes a prefetched source.
- `nix flake archive --no-check-sigs` can copy directly to a remote store.
- `nix formatter build` builds the configured formatter and prints its
  executable path.
- `nix fmt` with no arguments does not imply `.`.
- `builtins.getFlake` accepts path values, although paths outside the store
  remain unsupported.

## Store, cache, and build quick reference

### Account for changed build locations and concurrency

Temporary builds live below the Nix state directory and their directory names
are opaque. `build-cores = 0` performs automatic CPU detection. Post-build
hooks can overlap up to `max-jobs`; build hooks receive `SIGTERM` on shutdown.

### Configure durable and safe garbage collection

Enable `fsync-store-paths` when new paths must reach durable storage before
registration. Runtime roots can be served by `nix store roots-daemon` for a
daemon without `/proc` tracing capability. Recursive deletion can keep live
paths with `nix store delete --recursive --skip-alive`.

### Keep cache automation format-aware

HTTP caches can compress narinfo, listing, and log metadata. Configure cache
metadata lifetime with `narinfo-cache-meta-ttl`, refresh with
`nix store info --refresh`, and supply mTLS credentials in HTTPS store URLs.
Authentication failures are reported distinctly from missing objects.

S3 stores support STS, web-identity and container credentials, object version
IDs, storage classes, multipart controls, and explicit addressing styles.
Configure every overlay cache alongside its underlying cache to avoid local
rebuilds of incomplete substituted closures.

## NixOS migration quick reference

### Review boot and switching assumptions

The initrd uses systemd by default. Replace `/dev/root` with a stable device,
name LUKS mapper paths explicitly, and retain scripted stage 1 only as a
temporary compatibility measure. `nixos-rebuild-ng` and the Rust system switch
are the supported paths; remove obsolete switch implementation toggles.

`/etc/nixos/system.nix` can be a channel-free system entry point. Use
`nixos-rebuild --attr` for an attribute set and `--file` for another entry.

### State dependencies explicitly

Services needing connectivity must both want and follow
`network-online.target`. Depend on `postgresql.target` when the database must
be writable and initialized. Depend on the ACME certificate service when a
syntactically valid certificate is required.

### Migrate structured settings and secrets

Move legacy `extraConfig` and flat option values into their RFC 42-style
`settings` attribute sets. Prefer secret-file and systemd-credential options;
never place private keys or application secrets in the Nix store.

### Treat state versions as migration switches

Use valid `"YY.MM"` NixOS state versions and change them only with the
corresponding data and default migrations. Database and application defaults,
private data directories, and several Home Manager paths are state-gated.

## Nixpkgs packaging quick reference

### Use current builders and dependency hooks

- Use `buildGoModule`, with `env.CGO_ENABLED` where required.
- Use `cargoHash` and `rustPlatform.fetchCargoVendor` for Rust vendoring.
- Set an explicit modern Python format, normally `pyproject = true` with a
  declared `build-system`.
- Use top-level `fetchPnpmDeps` and `pnpmConfigHook`, regenerating version-3
  pnpm dependency hashes.
- Use Yarn build, config, and install hooks for remaining Yarn 1 packages.

### Expect stricter derivation validation

`env` must be an attribute set, nested input lists are deprecated, dangling
and build-directory symlinks fail checks, and `meta.mainProgram` can affect
build output. Use structured attributes with `buildEnv` and put custom
derivation arguments in `derivationArgs`.

### Replace removed package and library names

Prefer top-level desktop packages, `pkgs.nixfmt`, current `lib.cli` rendering
functions, and current `lib.attrsets`, `lib.filesystem`, and string-type
helpers. Consult the packaging reference for exact one-to-one replacements.

## Home Manager quick reference

### Let the command own profile updates

Use `home-manager switch --rollback` or `--specialisation NAME` for safe
activation. Direct activation-script callers must update the profile
themselves. Legacy shadow-profile management is only a temporary escape hatch.

### Review activation and login behavior

User services restart during activation by default. Use
`home-manager.startAsUserService` when the home is unavailable until login.
Minimal mode imports only essential modules; explicitly import everything else.

### Migrate program configuration

Use structured SSH settings, per-profile Firefox extensions and Anki sync,
`services.syncthing.tray.enable`, `guiCredentials`, dedicated editor-fork
modules, and the renamed Neovim, man-viewer, and wallpaper-service options.
State-version changes also affect XDG paths, Hyprland and Neovim configuration
formats, application copying on Darwin, and automation defaults.

## Verification checklist

Before shipping a migration:

1. Identify whether the change belongs to Nix, NixOS, Nixpkgs, or Home Manager.
2. Check state-version gates separately from package or executable versions.
3. Validate option types and renamed paths with evaluation, not string search.
4. Exercise machine-readable output with an explicit format version.
5. Test store and hook changes with concurrent jobs and garbage collection.
6. Read the topic reference for defaults, escape hatches, and exact replacements.
