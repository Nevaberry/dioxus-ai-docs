# Packages and workspaces

Use this reference for installs, lockfiles, dependency management, workspaces, registries, publishing, audits, and lifecycle scripts.

## Additional install compatibility

*Batch: `1.2-guide`.*

`bun install` accepts repeated `--omit=dev|optional|peer` flags, and package manifests can declare `bundleDependencies`. These close npm-compatibility gaps that previously required changing install or packaging workflows.

## Audit filtering

*Batch: `1.2.21`.*

`bun audit` now filters by minimum severity with `--audit-level`, restricts checks to production dependencies with `--prod`, and accepts repeated `--ignore` flags for CVE IDs.

```sh
bun audit --prod --audit-level=high --ignore CVE-2023-12345
```

## Automatic pnpm project migration

*Batch: `1.2.23`.*

Running `bun install` in a project with `pnpm-lock.yaml` creates `bun.lock` while preserving resolved versions. It also understands pnpm workspaces and `catalog:` dependencies; a `pnpm-workspace.yaml` is reflected into the root `package.json` `workspaces` field.

```sh
bun install
```

## Automatic Yarn v1 lockfile migration

*Batch: `1.2.20`.*

Running `bun install` in a project with a Yarn v1 `yarn.lock` now automatically creates a `bun.lock` while preserving the resolved dependency versions.

## BOM-aware `.npmrc` parsing

*Batch: `1.2.13`.*

`bun install` now recognizes byte-order marks when reading `.npmrc`, including UTF-16 files commonly produced on Windows, instead of misparsing the configuration.

## Catalog-aware outdated checks

*Batch: `1.2.16`.*

`bun outdated` now reports updates for dependencies sourced from a workspace catalog; `-F` can select the workspace to inspect.

```sh
bun outdated -F app
```

## Cursor-aware project initialization

*Batch: `1.2.15`.*

When `bun init` detects Cursor, it now adds a Cursor rule that guides the agent to use Bun's CLI and APIs instead of Node.js, Vite, npm, or pnpm.

## Custom package tarball paths

*Batch: `1.2.4`.*

`bun pm pack --filename <path>` chooses the output tarball path relative to the project root; the path may include subdirectories.

```sh
bun pm pack --filename build/package.tgz
```

## Dependency patching

*Batch: `1.2-guide`.*

`bun patch <package>` prepares an editable dependency under `node_modules`; after editing, `bun patch --commit <package>` writes a versioned file under `patches/` that future `bun install` runs apply automatically.

## Dependency provenance

*Batch: `1.2.19`.*

`bun why <package>` prints the dependency chain that installed a package. The selector can be a glob such as `"@types/*"`, and `--depth` and `--top` control the displayed chain.

## Dependency security audits

*Batch: `1.2.15`.*

`bun audit` scans the dependencies recorded in `bun.lock` for known vulnerabilities and suggests compatible or latest-version updates. It uses the same advisory endpoint as `npm audit`.

```sh
bun audit
```

## Dependency-group precedence

*Batch: `1.2.19`.*

If the same package appears in several dependency groups, resolution now follows `devDependencies` > `optionalDependencies` > `dependencies` > `peerDependencies`.

## Explicit packages for `bunx`

*Batch: `1.2.21`.*

`bunx --package` (or `-p`) runs a binary whose name differs from its package, including binaries supplied by scoped or multi-binary packages.

```sh
bunx -p @angular/cli ng new my-app
```

## Explicit trust for non-registry dependencies

*Batch: `1.3.5`.*

Packages installed through `file:`, `link:`, `git:`, or `github:` specifiers no longer inherit Bun's default lifecycle-script trust merely by matching a trusted package name. Such dependencies must be listed explicitly in `trustedDependencies` before their lifecycle scripts run.

## Frontend setup and dependency analysis

*Batch: `1.2.3`.*

`bun init` adds a React template with frontend tooling and a lightweight backend. For existing component code, `bun create ./MyComponent.tsx` scans imports, installs missing packages, and detects tooling such as Tailwind CSS and shadcn/ui; `bun install --analyze` performs the dependency-discovery step directly and records missing imports in `package.json`.

```sh
bun create ./MyComponent.tsx
bun install --analyze src/**/*.ts
```

## Frozen lockfiles with overrides

*Batch: `1.2.8`.*

`bun install --frozen-lockfile` now works in projects that use `overrides`: override keys are sorted consistently before lockfile comparison, and even unused overrides are retained in the text lockfile. This prevents frozen installs from failing solely because of override ordering or currently unused entries.

## Fully strict isolated installs

*Batch: `1.4-3`.*

The isolated linker can disable its hidden hoisted fallback, causing undeclared dependencies to fail resolution instead of being found under `.bun/node_modules`.

```toml
[install]
hoist = false
```

## Glob patterns in package side-effect declarations

*Batch: `1.2.21`.*

Bun's bundler now interprets `*`, `?`, `**`, `[]`, and `{}` patterns in a package's `sideEffects` array instead of de-optimizing the entire package.

```json
{
  "sideEffects": ["**/*.css", "./src/setup.js", "./src/components/*.js"]
}
```

## Global trusted postinstall scripts

*Batch: `1.2.12`.*

Global package installs now run postinstall scripts when the package has been explicitly opted in through `trustedDependencies`; Bun no longer blocks those scripts solely because the install is global.

## Hosted Git dependency forms

*Batch: `1.3.2`.*

`bun install` now recognizes npm-style `github:` shorthands and GitHub URLs with custom protocol prefixes. Distinct `git+ssh` and `git+https` references to the same repository are resolved and recorded independently.

```json
{
  "dependencies": {
    "library": "github:owner/repo#v1.2.3",
    "tooling": "git+ssh://git@github.com/owner/repo.git#main"
  }
}
```

## Install-time security scanners

*Batch: `1.2.21`.*

`bun install` can invoke an installed scanner package before installation and cancels the install when the scanner reports a `fatal` vulnerability.

```toml
[install.security]
scanner = "@my-company/bun-security-scanner"
```

## Interactive dependency updates

*Batch: `1.2.19`.*

`bun update --interactive` opens a selector for choosing which dependencies to update instead of updating the whole eligible set.

## Isolated dependency installs

*Batch: `1.2.19`.*

`bun install --linker=isolated` creates a pnpm-style isolated, symlinked `node_modules` layout, with especially useful isolation for monorepos.

## Isolated workspace installs by default

*Batch: `1.3-guide`.*

Projects declaring `workspaces` now use the isolated linker by default, preventing packages from accessing dependencies they did not declare. Restore the previous flat layout through the CLI or configuration.

```toml
[install]
linker = "hoisted"
```

## JSONC `package.json`

*Batch: `1.2-guide`.*

Bun accepts comments and trailing commas in `package.json`, including when the file is loaded through `require()` or `import()`. Other ecosystem tools may still reject such files, so this is only safe when every consumer supports JSONC.

## Leaner Bun type dependencies

*Batch: `1.4-3`.*

`@types/bun` no longer depends on `@types/react`, so projects without React do not acquire React's global JSX declarations merely by installing Bun's types.

## Lifecycle-edited manifests in `bun pm pack`

*Batch: `1.3.7`.*

After `prepack`, `prepare`, and `prepublishOnly` run, `bun pm pack` re-reads `package.json`. Manifest changes made by those scripts are therefore included in the tarball.

## Local file dependency graphs

*Batch: `1.4-4`.*

Root `overrides` and `resolutions` may target `file:../...` paths. With the hoisted linker, transitive `file:` dependencies declared by another local package are now linked into `node_modules` as well.

```json
{ "overrides": { "library": "file:../library-fork" } }
```

## Lockfile deduplication

*Batch: `1.4`.*

`bun dedupe` consolidates duplicate package versions when one version satisfies all relevant ranges, without changing `package.json`. Use `--check` to fail CI when `bun.lock` can be deduplicated.

```sh
bun dedupe --check
```

## Lockfile format migrations

*Batch: `1.4-2`.*

New `bun.lock` files use `lockfileVersion: 2`, adding integrity checks for off-registry tarballs and path validation for Git dependencies; existing v0/v1 files migrate on `bun install`. Nested or version-scoped overrides require version 3, which older Bun releases cannot read.

## Lockfile-pinned linker defaults

*Batch: `1.3.2`.*

Existing workspaces without an explicit linker setting now retain hoisted installs, while new workspace projects continue to default to isolated installs. `bun install` records this choice through lockfile `configVersion`: new projects and pnpm migrations use v1, while existing Bun projects and npm/Yarn migrations use v0; only v1 workspaces select the isolated default.

```toml
[install]
linker = "isolated"
```

## Minimum package release age

*Batch: `1.3-guide`.*

`minimumReleaseAge` rejects package versions published fewer than the configured number of seconds ago, providing a delay window for newly published supply-chain attacks.

```toml
[install]
minimumReleaseAge = 604800 # 7 days
```

## Nested dependency overrides

*Batch: `1.4`.*

Overrides can target only a dependency of another dependency, using npm's nested object form, Yarn's `a/b`, or pnpm's `a>b`; version-range keys can further scope an override.

```json
{
  "overrides": {
    "express": { "qs": "6.13.0" },
    "lodash@<4.17.21": "4.17.21"
  }
}
```

## Nested exclusions in `bun pack`

*Batch: `1.2.8`.*

`bun pack` now applies exclusion patterns to files and subdirectories nested beneath an included directory; exclusions are no longer limited to top-level entries.

```sh
bun pack --exclude "src/**/test/**" --include "src/**"
```

## Non-registry dependency workflows

*Batch: `1.4-4`.*

`bun patch` and `bun patch --commit` now work for Git and tarball dependencies. Installs also support `git+file://` dependencies, and a cold-cache lockfile install now installs every dependency targeting a different branch of the same repository.

## npm and certificate configuration

*Batch: `1.2-guide`.*

`bun install` reads `.npmrc` from the project root and home directory for registries, scoped registries, authentication-related settings, and CA configuration. Certificates can also be configured as `install.ca`/`install.cafile` in `bunfig.toml` or passed with `--ca`/`--cafile`.

```toml
[install]
cafile = "path/to/cafile"
```

## npm token environment variable

*Batch: `1.2.5`.*

`bun publish` reads `NPM_CONFIG_TOKEN`, so CI jobs can authenticate without writing separate npm configuration.

```sh
NPM_CONFIG_TOKEN="$NPM_TOKEN" bun publish
```

## npm-compatible install settings

*Batch: `1.2.19`.*

`bun install` and `bun add` now honor `link-workspace-packages` and `save-exact` from `.npmrc`. For example, `save-exact=true` makes `bun add` record an exact version rather than a caret range.

## Optional agent-rule scaffolding

*Batch: `1.2.17`.*

`bun init` can now generate shared coding-agent instructions when a supported agent CLI is detected and reuse them for detected editor rules. Set `BUN_AGENT_RULE_DISABLED` to suppress this generated project metadata.

```sh
BUN_AGENT_RULE_DISABLED=1 bun init
```

## Optional workspace package linking

*Batch: `1.2.16`.*

Set `install.linkWorkspacePackages = false` to install matching workspace dependencies from the registry instead of linking their local packages. The default remains `true`, and explicit `workspace:` specifiers are still respected.

```toml
[install]
linkWorkspacePackages = false
```

## Package metadata automation

*Batch: `1.2.19`.*

`bun pm pkg get|set|delete|fix` reads and edits `package.json`; dotted and bracket paths address nested fields. For archive scripts, `bun pm pack --quiet` suppresses diagnostics and writes only the generated tarball filename to stdout.

```sh
bun pm pkg get scripts.build
bun pm pkg set scripts.test="bun test"
bun pm pkg delete contributors[0]
tarball=$(bun pm pack --quiet)
```

## Package metadata command rename

*Batch: `1.2.17`.*

`bun info` is now the primary spelling of `bun pm view`; the old command remains an alias.

```sh
bun info react repository.url
```

## Package metadata inspection

*Batch: `1.2.15`.*

`bun pm view` fetches npm package metadata, accepts versioned package selectors and nested property paths, and can emit the response as JSON.

```sh
bun pm view express@4.18.2
bun pm view next property.path
bun pm view bun --json
```

## Package version diffs

*Batch: `1.4`.*

`bun pm diff` compares the locked version with latest, two published versions, or a local directory with a published package. It summarizes changed files, new lifecycle scripts, and new sensitive built-in imports before showing a semantic diff that unminifies code and omits formatting-only changes.

```sh
bun pm diff react
bun pm diff react@18.2.0 19.0.0
bun pm diff ./vendored-pkg pkg@2.1.0
```

## Package version management

*Batch: `1.2.18`.*

`bun pm version` updates the `package.json` version using `patch`, `minor`, `major`, `prerelease`, `from-git`, or an exact version. It supports `--preid`, `--message`/`-m`, `--allow-same-version`, and `--no-git-tag-version` to skip Git operations.

```sh
bun pm version prerelease --preid beta
bun pm version 1.2.3 --no-git-tag-version
```

## Package-manager upgrade traps

*Batch: `1.4-2`.*

A project `bunfig.toml` now wins over `.npmrc` for duplicate settings; `bun update <missing-name>` fails instead of adding the package, `--production` limits updates to production and optional dependencies, and interactive mode updates only the selection. With non-TTY input, `bun init` behaves as `-y`, while `bun update -i` exits with an error instead of opening a picker.

## Package-script working directory

*Batch: `1.2-guide`.*

`bun run` now starts a package script in the directory containing the discovered `package.json`, rather than preserving the shell's current subdirectory. Scripts that intentionally depended on invocation-directory-relative paths must adjust.

## Packed package binaries

*Batch: `1.3.1`.*

`bun pm pack` now always includes paths declared by `bin` and `directories.bin`, even when the package's `files` allowlist omits them, and deduplicates paths present in both fields.

## Parallel and sequential package scripts

*Batch: `1.3.9`.*

`bun run --parallel` starts multiple scripts together, while `bun run --sequential` runs them one at a time; both add prefixed output, glob matching, lifecycle-script grouping, and `--filter`/`--workspaces` integration. Unlike plain `--filter`, these modes ignore workspace dependency order; failures stop remaining scripts unless `--no-exit-on-error` is used, and `--if-present` skips packages without the requested script.

```sh
bun run --parallel build test
bun run --sequential --workspaces --if-present build
```

## Path-scoped registry credentials

*Batch: `1.4-3`.*

`.npmrc` authentication tokens are matched by both host and path, allowing separate credentials for multiple registries hosted under different paths on the same server.

## Private-registry email authentication

*Batch: `1.3.1`.*

`bun install` now forwards registry-specific `:email` entries from `.npmrc` alongside usernames, passwords, or tokens for both default and scoped registries.

```ini
//registry.example.com/:email=user@example.com
//registry.example.com/:_authToken=xxxxxx
```

## Production dependency pruning

*Batch: `1.4`.*

`bun prune` removes packages from `node_modules` that are no longer present in `bun.lock`; `--production` additionally removes `devDependencies` after a build.

```sh
bun prune --production
```

## Quoted and optional `.npmrc` variables

*Batch: `1.3.5`.*

Environment placeholders now expand inside both single- and double-quoted `.npmrc` values. `${NAME?}` expands an unset variable to an empty string; without `?`, an unset placeholder remains literal.

```ini
token = "${NPM_TOKEN}"
auth = 'Bearer ${TOKEN?}'
```

## README metadata from `bun publish`

*Batch: `1.3.14`.*

`bun publish` now finds the first case-insensitive `README` or `README.*` file and sends its contents as registry version metadata for both workspace and tarball publishes. An explicit `readme` field in `package.json` takes precedence.

## Recursive workspace dependency updates

*Batch: `1.2.20`.*

`bun outdated` and interactive `bun update` accept `-r`/`--recursive` to operate across all workspaces. Interactive updates also accept `--filter` to target selected workspaces and show each dependency's workspace.

```sh
bun outdated --recursive
bun update --interactive --recursive
bun update --interactive --filter=my-app
```

## Selective hoisting with the isolated linker

*Batch: `1.3.1`.*

`publicHoistPattern` exposes matching transitive dependencies at the root `node_modules`, while `hoistPattern` controls hoisting inside `node_modules/.bun/node_modules`. Both accept a string or array under `[install]`; `.npmrc` also supports `public-hoist-pattern`.

```toml
[install]
publicHoistPattern = ["@types*", "*eslint*"]
hoistPattern = ["@types*", "*eslint*"]
```

## Streaming package extraction

*Batch: `1.3.13`.*

`bun install` now downloads and extracts package tarballs incrementally by default while still verifying integrity before promoting the extracted tree into the cache. Set `BUN_FEATURE_FLAG_DISABLE_STREAMING_INSTALL=1` to restore buffered extraction if the streaming path causes problems.

```sh
BUN_FEATURE_FLAG_DISABLE_STREAMING_INSTALL=1 bun install
```

## Svelte package and module resolution

*Batch: `1.2.6`.*

`bun-plugin-svelte` now honors packages' `"svelte"` export condition and correctly transpiles imported `.svelte.ts` modules before compilation, enabling packages such as `@threlte/core` and TypeScript Svelte helper modules.

## Targeted optional dependencies

*Batch: `1.2.23`.*

Repeatable `--os` and `--cpu` flags select which platform-specific optional dependencies to install, including cross-target or multi-target installs; `'*'` selects every supported value.

```sh
bun install --os darwin --os linux --cpu x64
bun install --os '*' --cpu '*'
```

## Text lockfile migration

*Batch: `1.2-guide`.*

New projects now generate the JSONC `bun.lock` instead of binary `bun.lockb`. Existing binary lockfiles remain supported and are not migrated automatically; opt in with `bun install --save-text-lockfile`.

## Top-level dependency catalogs

*Batch: `1.2.19`.*

The root `package.json` can now place `catalog` and named `catalogs` directly at the top level instead of nesting them in the `workspaces` object.

```json
{
  "workspaces": ["packages/*"],
  "catalog": { "react": "18.2.0" },
  "catalogs": { "testing": { "@testing-library/react": "16.0.0" } }
}
```

## Transitive dependency updates

*Batch: `1.4`.*

`bun update` now updates transitive dependencies as well as direct dependencies. A package selector updates that package everywhere in the graph, and selectors may be globs or use `--latest`.

```sh
bun update zod
bun update '@types/*' --latest
```

## Trusted lifecycle-script inspection

*Batch: `1.4-3`.*

`bun pm ls --trusted` filters the dependency tree to packages allowed to execute lifecycle scripts, combining `trustedDependencies` with Bun's default trust list; add `--all` to include the complete tree.

## Vulnerability remediation

*Batch: `1.4`.*

`bun audit fix` upgrades vulnerable packages to compatible safe versions and installs the result. Major-version fixes require `--latest`, while `--dry-run` previews changes.

```sh
bun audit fix --dry-run
bun audit fix --latest
```

## Workspace and catalog mutations

*Batch: `1.4`.*

`bun add`, `bun remove`, and `bun update` accept `--filter`; `web...` selects a workspace plus its dependencies, while `...web` selects it plus its dependents. `bun add <pkg> --catalog` adds the version to the root catalog and records `catalog:` in the workspace, while plain `bun add` reuses an existing default-catalog entry.

```sh
bun add zod --filter api
bun update --filter 'web...'
bun add react --catalog
```

## Workspace dependency catalogs

*Batch: `1.2.14`.*

The root package can define shared dependency versions under `workspaces.catalog`, and workspace packages select them with the `catalog:` protocol. Packing or publishing replaces each catalog reference with its configured version.

```json
{
  "workspaces": {
    "packages": ["packages/*"],
    "catalog": { "react": "^19.0.0" }
  }
}
```

```json
{
  "dependencies": { "react": "catalog:" }
}
```

## Workspace script filtering

*Batch: `1.2-guide`.*

`bun run --filter` runs a script concurrently in every workspace matching a glob, interleaves their output, and accepts multiple filters; `bun` can replace `bun run` in the command.

```sh
bun --filter 'api/*' --filter 'frontend/*' dev
```

## Workspace-wide install scanning

*Batch: `1.4-4`.*

An install-time security scanner now receives dependencies from every workspace package, rather than only from the root package.

## Workspace-wide scripts

*Batch: `1.2.22`.*

`bun run --workspaces` runs the named `package.json` script in every workspace package.

```sh
bun run --workspaces test
```
