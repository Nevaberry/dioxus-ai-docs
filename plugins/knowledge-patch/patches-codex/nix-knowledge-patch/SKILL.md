---
name: nix-knowledge-patch
description: Nix
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Nix Knowledge Patch

Use this skill when changing Nix expressions, Nix CLI automation, flakes,
stores, binary caches, NixOS modules, Nixpkgs packages, or Home Manager
configurations. Check the project and host versions first, because several
defaults and migrations are gated by `system.stateVersion` or
`home.stateVersion`.

## Reference index

| Reference | Topics |
| --- | --- |
| [Core CLI, Evaluation, and Configuration](references/core-cli-evaluation.md) | CLI behavior, evaluator rules, configuration, profiles, REPL, JSON formats, installers, and build execution |
| [Flakes and Fetchers](references/flakes-and-fetchers.md) | Inputs, lock files, Git features, registries, prefetching, archives, and flake checks |
| [Stores, Caches, and Remote Builds](references/stores-caches-and-remote-builds.md) | GC roots, daemon stores, substituters, SSH, S3, HTTP, signing, retries, hooks, and build traces |
| [Native APIs and Source Builds](references/native-api-and-source-builds.md) | C and C++ API migrations, headers, plugins, and the Nix source build system |
| [NixOS System and Service Migrations](references/nixos-system-and-services.md) | Rebuilds, boot, networking, storage, security, and service-module migrations |
| [Nixpkgs Packaging](references/nixpkgs-packaging.md) | Builder migrations, language ecosystems, hooks, library APIs, platforms, and package scopes |
| [Home Manager](references/home-manager.md) | Activation, profile ownership, state-gated defaults, module renames, XDG paths, and application configuration |

## Start with compatibility gates

Before editing:

1. Read `nix --version` and the pinned Nixpkgs or flake lock revision.
2. Read `system.stateVersion` and `home.stateVersion`; do not raise either as
   a general upgrade step.
3. Identify experimental features used by the configuration.
4. Check whether automation consumes unstable JSON or human-readable output.
5. For remote stores, inspect the exact store URI, authentication provider,
   signing configuration, and underlying cache ordering.
6. For NixOS switches, inspect boot, initrd, storage, database, and secret
   migrations before activation.

## Highest-impact breaking changes

### Treat state versions as migration switches

New defaults for databases, Home Manager paths and formats, service data, and
other modules can be state-version gated. Preserve existing state versions
unless the operator deliberately performs every associated migration. A
package-channel update and a state-version change are separate operations.

### Use structured settings and current option names

Many NixOS and Home Manager modules replaced free-form configuration strings,
flat options, or renamed modules with typed `settings` attributes. Remove old
options rather than setting both old and new forms. Pay special attention to
systemd manager, coredump, sleep, SSH, Postfix, rsyncd, Yggdrasil, firewall,
and application-service modules.

### Expect systemd in the initrd

Current NixOS uses systemd stage 1 by default. Use stable device paths for the
root filesystem and LUKS mapping, review LVM-on-LUKS timeouts, and keep the
scripted initrd only as a temporary compatibility measure.

### Update packaging builders and hashes

Out-of-tree packages commonly need these migrations:

- Rust packages use `cargoHash` and the stable vendoring path.
- Go packages use `buildGoModule`; put `CGO_ENABLED` in `env`.
- Python packages declare a modern build format and build system.
- Node and Yarn packages use current top-level helpers and hooks.
- pnpm packages use top-level dependency fetchers and regenerate current
  hashes.
- `buildEnv` and derivations that need structured behavior use structured
  attributes.

### Parse machine output by explicit schema

Pass an explicit JSON format to commands that offer one. Derivation JSON,
path-info JSON, content addresses, signatures, store paths, and build traces
have all gained structured or versioned representations. Never parse
human-readable sizes as fixed MiB values, and do not assume terminal JSON is
single-line.

### Audit service data and secrets before switching

Database major versions, Nextcloud stepping, Immich vector extensions,
TaskChampion and Stalwart directories, OAuth2 Proxy secrets, Grafana keys,
Yggdrasil private keys, ACME dependencies, and PostgreSQL readiness semantics
can require operator action. Keep secret values out of the Nix store and
verify backup and rollback procedures first.

## Common Nix CLI patterns

### Profiles and copied paths

Use `nix profile add` for profile additions. When copying a path that must
survive concurrent garbage collection, create its profile or output-link root
as part of the copy operation.

```sh
nix profile add nixpkgs#hello
nix copy --from ssh://builder --out-link ./result "$path"
```

### Stable JSON in automation

Force formatting behavior when terminal detection could vary, and select the
document schema for versioned commands.

```sh
nix eval --json --no-pretty --expr '{ answer = 42; }'
nix path-info --json --json-format 3 "$path"
```

### Evaluation diagnostics

Use stack sampling for performance investigations, IFD tracing for migration
work, and JSON log mirroring for structured observability. Short and absolute
path-literal checks are tri-state lints; choose `warn` during migration and
`fatal` only after cleanup.

```ini
trace-import-from-derivation = true
lint-short-path-literals = warn
lint-absolute-path-literals = warn
```

### Flake fetching

Declare submodule and LFS requirements on the flake where possible. Relative
path inputs affect lock-file compatibility. Use parallel input prefetching
when fetching unused inputs is acceptable, and use output links when a
prefetched or checked result must be retained.

## Store and cache safety

### Configure complete substituter chains

An overlay cache must be listed with the cache that supplies its referenced
closure. Incomplete substituted closures are no longer filled by mixing a
partial substitution with local builds.

### Make remote behavior explicit

SSH store URLs may include ports and bracketed IPv6 addresses; percent-encode
IPv6 zone separators. Shell-style `NIX_SSHOPTS` parsing supports quoted proxy
commands. For HTTPS or S3 stores, configure authentication, retry policy,
compression, addressing style, and metadata lifetime deliberately.

### Write concurrent-safe hooks

Post-build hooks may overlap up to `max-jobs`; dependent builds still wait for
their own hook. Build hooks receive graceful termination, so handle `SIGTERM`
and clean up temporary resources. Do not infer a derivation name from an
opaque temporary build-directory name.

## NixOS migration workflow

1. Evaluate with warnings enabled and resolve removed or renamed options.
2. Build without switching and inspect the resulting unit and boot changes.
3. Check database and service-data migrations, secret paths, filesystem types,
   and initrd device paths.
4. Use a test or boot activation only after rollback access is confirmed.
5. Treat switch inhibitors as actionable checks; use `NIXOS_NO_CHECK=1` only
   for an understood emergency override.
6. Reboot when changing the D-Bus implementation or other changes that cannot
   be completed safely by a live switch.

## Nixpkgs package review

For every package update:

- Flatten nested build and runtime input lists.
- Check for dangling or build-directory symlinks.
- Keep `env` as an attribute set and use `env.env` for a variable literally
  named `env`.
- Confirm `meta.mainProgram`, since it now affects the build environment.
- Add explicit dependencies for split tools, metadata, modules, and wrapper
  outputs.
- Re-run fixed-output hash discovery after changing language-specific
  dependency fetchers.
- Check platform floors, toolchain defaults, filesystem feature requirements,
  and provider defaults rather than inheriting them accidentally.

## Home Manager review

Do not invoke a generated activation script as if it owned profile updates.
Use supported switch flows, choose legacy profile management only as a
temporary bridge, and consider login-time activation for late-mounted homes.
When raising `home.stateVersion`, audit application paths, generated formats,
service integration, automatic updates, and renamed per-profile options.

## Final verification

After a change:

- Run evaluation and the narrowest relevant build or check.
- Confirm lock-file changes are intentional and usable by deployment clients.
- Verify store paths remain rooted for as long as needed.
- Exercise parsers against the selected JSON schema.
- Inspect generated systemd units and secret references.
- Confirm hooks and cache clients behave under concurrency and authentication
  failures.
- Keep rollback generations until stateful migrations are verified.
