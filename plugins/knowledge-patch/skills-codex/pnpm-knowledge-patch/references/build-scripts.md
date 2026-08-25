# Dependency Build Scripts and Approvals

## Default blocking and review (2025-01)

pnpm 10 does not run dependency lifecycle scripts during installation unless the package is listed in `pnpm.onlyBuiltDependencies`. An empty `pnpm.neverBuiltDependencies` array restores the pre-v10 allow-all behavior.

```json
{
  "pnpm": {
    "onlyBuiltDependencies": ["fsevents"]
  }
}
```

Use `pnpm ignored-builds` to list dependencies whose build scripts were skipped and `pnpm approve-builds` to approve dependencies to run scripts during installation. Packages in `pnpm.ignoredBuiltDependencies` remain unbuilt without the informational skipped-build message.

```sh
pnpm ignored-builds
pnpm approve-builds
```

## One-command allowances (2025-02)

Packages executed by `pnpm dlx` or `pnpm create` may run their own postinstall scripts by default. Their dependencies remain blocked unless named with `--allow-build`. On `pnpm add`, the same flag runs the named dependencies' scripts and records them in `pnpm.onlyBuiltDependencies` for later installs.

```sh
pnpm --allow-build=esbuild dlx bundle
pnpm --allow-build=esbuild add bundle
```

## Strict review and global approvals (2025-02)

Set `strict-dep-builds=true` to make installation exit nonzero when a dependency has an unreviewed build script. Use `pnpm approve-builds --global` to review and allow postinstall scripts for dependencies of globally installed packages.

```ini
strict-dep-builds=true
```

```sh
pnpm approve-builds --global
```

## Explicit allow-all control (2025-04)

`dangerouslyAllowAllBuilds` permits every dependency build script without individual approval. It may be enabled globally or for one command and has the same effect as an empty `neverBuiltDependencies` list.

```sh
pnpm config set dangerouslyAllowAllBuilds true
pnpm install --dangerously-allow-all-builds
```

## Version-scoped approvals (2025-10)

`onlyBuiltDependencies` accepts exact package versions and `||` disjunctions, so approval need not cover every version of a dependency.

```yaml
onlyBuiltDependencies:
  - nx@21.6.4 || 21.6.5
  - esbuild@0.25.1
```

## Build newly approved installed dependencies (2025-12)

When an already-installed dependency is added to `onlyBuiltDependencies`, the next `pnpm install` runs its previously skipped build script.

## Unified `allowBuilds` permissions (2025-12)

`allowBuilds` is the preferred replacement for `onlyBuiltDependencies` and `ignoredBuiltDependencies`. It maps package matchers to `true` to allow scripts or `false` to block them, and supports version matchers and `||` disjunctions.

```yaml
allowBuilds:
  esbuild: true
  core-js: false
  nx@21.6.4 || 21.6.5: true
```

## Git dependency prepare scripts (2025-12)

Starting in pnpm 10.26, Git-hosted dependencies cannot run `prepare` during installation unless permitted by `onlyBuiltDependencies` or `allowBuilds`. pnpm 10.27 also honors `dangerouslyAllowAllBuilds` for them.

## Persist command allowances to `allowBuilds` (2026-03)

`--allow-build` permissions are persisted in the unified `allowBuilds` map instead of the legacy allowlist.

```sh
pnpm --allow-build=esbuild add bundle
```

```yaml
allowBuilds:
  esbuild: true
```

## Approve every pending build (2026-03)

`pnpm approve-builds --all` approves all pending dependency builds without opening the interactive selector.

```sh
pnpm approve-builds --all
```

## pnpm 11 build permission migration (migration-10-to-11, 11.0.0)

pnpm 11 removes `onlyBuiltDependencies`, `onlyBuiltDependenciesFile`, `neverBuiltDependencies`, `ignoredBuiltDependencies`, and `ignoreDepScripts`. Express both allowed and denied dependency builds in `allowBuilds`.

`pnpm approve-builds` also accepts positional package names for non-interactive approval; prefix a name with `!` to deny it explicitly.

```sh
pnpm approve-builds esbuild '!core-js'
```

## Approve Git builds by repository (11.10-11.17)

An `allowBuilds` entry for a Git-hosted dependency may match its repository URL without the resolved commit hash, so the approval survives branch updates. A package-name-only entry does not approve a Git-hosted artifact.
