# Migration and Dependency-Build Security

Use this reference for pnpm 10-to-11 migration, dependency lifecycle-script
permissions, dependency patches, and install-time source restrictions.

## Migrate pnpm 10 Projects to pnpm 11

### Run the codemod first (batch `migration-10-to-11`)

From the project root:

```sh
pnpx codemod run pnpm-v10-to-v11
```

The codemod relocates supported configuration and updates the root
package-manager declaration. Review every item below; several require manual
work.

### Move configuration

pnpm 11 no longer reads `package.json#pnpm`, and `.npmrc` is limited to
authentication and registries. Move all other settings to camelCase keys in
`pnpm-workspace.yaml`. The codemod stores subproject-specific `.npmrc` settings
under `packageConfigs["<project-name>"]`.

Replace `managePackageManagerVersions`, `packageManagerStrict`, and
`packageManagerStrictVersion` with `pmOnFail`. Supported values are
`download`, `ignore`, `warn`, and `error`.

Rename pnpm configuration environment variables from `npm_config_*` to
`pnpm_config_*`.

### Convert audit policy manually

`auditConfig.ignoreCves` becomes `auditConfig.ignoreGhsas`. The codemod renames
the key but cannot translate identifiers. For every CVE, use `pnpm audit` to
find the corresponding GHSA in the More info column and replace the value.

```yaml
auditConfig:
  ignoreGhsas:
    - GHSA-xxxx-xxxx-xxxx
```

Later pnpm 11 releases prefer top-level `audit.level` and `audit.ignore`; see
the registry and supply-chain reference.

### Move runtime declarations

The codemod converts root `useNodeVersion` to `devEngines.runtime`. For each
workspace subpackage, manually replace
`package.json#pnpm.executionEnv.nodeVersion` with its own
`devEngines.runtime` declaration.

### Update removed or changed commands

- `pnpm link <package-name>` no longer looks in the global store. Pass a
  filesystem path, such as `pnpm link ./foo`.
- Argument-free `pnpm install -g` is removed. Use
  `pnpm add -g <package>`.
- `pnpm server` is removed without replacement.
- A package script named `clean`, `setup`, `deploy`, or `rebuild` shadows the
  pnpm built-in. Use `pnpm pm <name>` to force the built-in.

### Satisfy platform requirements (batch `11.0.0`)

pnpm 11 requires Node.js 22 or newer and ships as pure ESM. The standalone
executable requires glibc 2.27 or newer.

Global installations now use isolated groups, and binaries live under
`PNPM_HOME/bin`. Run `pnpm setup` after upgrading.

## Dependency Build Permissions

### pnpm 10 starts deny-by-default (batch `2025-01`)

pnpm 10 skips dependency lifecycle scripts during installation unless the
package appears in `pnpm.onlyBuiltDependencies`.

```json
{
  "pnpm": {
    "onlyBuiltDependencies": ["fsevents"]
  }
}
```

An empty `pnpm.neverBuiltDependencies` restores the older allow-all behavior.
`pnpm.ignoredBuiltDependencies` keeps selected packages unbuilt without the
informational skipped-build message.

Inspect and approve pending packages with:

```sh
pnpm ignored-builds
pnpm approve-builds
```

### Fail when builds have not been reviewed (batch `2025-02`)

`strict-dep-builds=true` makes installation exit nonzero if any dependency has
an unreviewed build script. pnpm 11 enables this behavior by default.

Use `pnpm approve-builds --global` to review scripts for dependencies of global
packages.

### Allow builds for one command (batch `2025-02`)

The package invoked by `pnpm dlx` or `pnpm create` may run its own postinstall
by default. Its dependencies remain blocked unless named with
`--allow-build`.

On `pnpm add`, the flag runs the named dependency scripts and records the
packages for later installs:

```sh
pnpm --allow-build=esbuild dlx bundle
pnpm --allow-build=esbuild add bundle
```

Early pnpm 10 persists these decisions in `onlyBuiltDependencies`. Newer
releases write to `allowBuilds` (batch `2026-03`).

### Allow every dependency explicitly (batch `2025-04`)

`dangerouslyAllowAllBuilds` permits all dependency build scripts and is
equivalent to an empty `neverBuiltDependencies` list.

```sh
pnpm config set dangerouslyAllowAllBuilds true
pnpm install --dangerously-allow-all-builds
```

This is intentionally broad; prefer package-specific approvals.

### Restrict approvals by version (batch `2025-10`)

`onlyBuiltDependencies` accepts exact versions and `||` disjunctions:

```yaml
onlyBuiltDependencies:
  - nx@21.6.4 || 21.6.5
  - esbuild@0.25.1
```

### Unified allow and deny map (batch `2025-12`)

`allowBuilds` replaces separate allowed and ignored lists. Map package or
version matchers to true to allow scripts or false to block them.

```yaml
allowBuilds:
  esbuild: true
  core-js: false
  nx@21.6.4 || 21.6.5: true
```

When an already-installed package is newly allowed, the next install runs its
previously skipped build (batch `2025-12`).

### Approve non-interactively (batches `2026-03` and `11.0.0`)

`pnpm approve-builds --all` accepts every pending build without opening the
selector.

pnpm 11 also accepts positional package decisions. Prefix a package with `!`
to deny it:

```sh
pnpm approve-builds esbuild '!core-js'
```

### Remove all legacy controls in pnpm 11 (batch `11.0.0`)

`onlyBuiltDependencies`, `onlyBuiltDependenciesFile`,
`neverBuiltDependencies`, `ignoredBuiltDependencies`, and
`ignoreDepScripts` are unsupported. Express all package allow and deny rules
in `allowBuilds`.

## Git Dependency Builds

Starting in pnpm 10.26, a Git-hosted dependency cannot run `prepare` unless
allowed by `onlyBuiltDependencies` or `allowBuilds`. pnpm 10.27 also honors
`dangerouslyAllowAllBuilds` for Git dependencies (batch `2025-12`).

An `allowBuilds` matcher may target the Git repository URL without a resolved
commit, preserving approval when a branch advances. A package-name-only rule
does not approve a Git-hosted artifact (batch `11.10-11.17`).

## Dependency Patches

### Select patches by range (batch `2025-03`)

`patchedDependencies` accepts name-only, version-range, and exact-version
keys. Exact keys win over ranges, which win over name-only keys. Avoid
overlapping ranges.

```yaml
patchedDependencies:
  foo: patches/foo-1.patch
  foo@^2.0.0: patches/foo-2.patch
  foo@2.1.0: patches/foo-3.patch
```

`foo@*` matches like a name-only key, except an application failure is not
ignored.

### Unused and failed patches in pnpm 10 (batch `2025-03`)

`pnpm.allowNonAppliedPatches` was renamed to
`pnpm.allowUnusedPatches`. The old name works with a deprecation warning.

`ignorePatchFailures` is tri-state:

- unset: exact/range patch failures are errors and name-only failures are
  ignored;
- `false`: every patch failure is an error;
- `true`: every failure is a warning.

### pnpm 11 patch policy (batch `migration-10-to-11`)

`ignorePatchFailures` is removed. Every patch failure throws; repair the patch
or remove the affected dependency.

Patch files may not escape the package directory. pnpm rejects
`diff --git` headers that write, delete, or rename paths outside the patched
package (batch `11.4-11.5`).

## Source and Resolution Restrictions

### Exotic transitive dependencies (batches `2025-12` and `11.0.0`)

`blockExoticSubdeps` rejects exotic transitive sources such as `git+ssh:` and
direct HTTPS tarballs. Direct dependencies may still use them. pnpm 11 enables
this policy by default.

```yaml
blockExoticSubdeps: true
```

### Git and alias validation (batch `11.4-11.5`)

Git resolutions require a full 40-character hexadecimal commit SHA. Dependency
aliases with path-traversal segments are rejected when reading manifests and
when linking into `node_modules`.

### Tarball integrity

HTTP tarballs receive a computed lockfile integrity on first fetch
(batch `2025-12`). pnpm 10.34 fails changed locked checksums by default and
requires the explicit `--update-checksums` acceptance path (batch `10.34.0`).
Missing tarball integrity is fatal in pnpm 11 except for Git and local
`file:` tarballs (batch `11.4-11.5`).

See the installation reference for recovery rules and generated-tarball
behavior.

## Security-Related Installation Defaults

pnpm 11 defaults the following settings (batch `11.0.0`):

```yaml
minimumReleaseAge: 1440
minimumReleaseAgeStrict: false
blockExoticSubdeps: true
strictDepBuilds: true
optimisticRepeatInstall: true
verifyDepsBeforeRun: install
```

Set `minimumReleaseAge: 0` to opt out of the publication delay. Evaluate each
default separately rather than disabling several protections to solve one
compatibility problem.

## Environment and Token-Helper Safety

pnpm 10.27 rejects environment-variable references in `tokenHelper` and
registry-scoped `<url>:tokenHelper` values (batch `2025-12`).

Unscoped credentials are bound to the registry from the same configuration
source at load time, preventing a later registry override from redirecting
them. See the registry reference for the complete credential behavior
(batch `10.34.0`).
