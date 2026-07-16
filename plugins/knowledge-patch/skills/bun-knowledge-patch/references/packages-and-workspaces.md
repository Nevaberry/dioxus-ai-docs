# Packages and workspaces

Use this reference for lockfiles, dependency installation, linker behavior, workspaces, package scripts, audits, packing, publishing, and project tooling.

Entries are grouped by developer task. When entries describe evolving behavior, the later attribution supersedes earlier defaults or limitations.

## Installing, resolving, and linker behavior

### Text lockfile migration *(1.2-guide)*

New projects now generate the JSONC `bun.lock` instead of binary `bun.lockb`. Existing binary lockfiles remain supported and are not migrated automatically; opt in with `bun install --save-text-lockfile`.

### Dependency patching *(1.2-guide)*

`bun patch <package>` prepares an editable dependency under `node_modules`; after editing, `bun patch --commit <package>` writes a versioned file under `patches/` that future `bun install` runs apply automatically.

### Additional install compatibility *(1.2-guide)*

`bun install` accepts repeated `--omit=dev|optional|peer` flags, and package manifests can declare `bundleDependencies`. These close npm-compatibility gaps that previously required changing install or packaging workflows.

### Frozen lockfiles with overrides *(since 1.2.8)*

`bun install --frozen-lockfile` now works in projects that use `overrides`: override keys are sorted consistently before lockfile comparison, and even unused overrides are retained in the text lockfile. This prevents frozen installs from failing solely because of override ordering or currently unused entries.

### Isolated dependency installs *(since 1.2.19)*

`bun install --linker=isolated` creates a pnpm-style isolated, symlinked `node_modules` layout, with especially useful isolation for monorepos.

### Interactive dependency updates *(since 1.2.19)*

`bun update --interactive` opens a selector for choosing which dependencies to update instead of updating the whole eligible set.

### Dependency-group precedence *(since 1.2.19)*

If the same package appears in several dependency groups, resolution now follows `devDependencies` > `optionalDependencies` > `dependencies` > `peerDependencies`.

### Dependency provenance *(since 1.2.19)*

`bun why <package>` prints the dependency chain that installed a package. The selector can be a glob such as `"@types/*"`, and `--depth` and `--top` control the displayed chain.

### Automatic Yarn v1 lockfile migration *(since 1.2.20)*

Running `bun install` in a project with a Yarn v1 `yarn.lock` now automatically creates a `bun.lock` while preserving the resolved dependency versions.

### Automatic pnpm project migration *(since 1.2.23)*

Running `bun install` in a project with `pnpm-lock.yaml` creates `bun.lock` while preserving resolved versions. It also understands pnpm workspaces and `catalog:` dependencies; a `pnpm-workspace.yaml` is reflected into the root `package.json` `workspaces` field.

```sh
bun install
```

### Targeted optional dependencies *(since 1.2.23)*

Repeatable `--os` and `--cpu` flags select which platform-specific optional dependencies to install, including cross-target or multi-target installs; `'*'` selects every supported value.

```sh
bun install --os darwin --os linux --cpu x64
bun install --os '*' --cpu '*'
```

### Selective hoisting with the isolated linker *(since 1.3.1)*

`publicHoistPattern` exposes matching transitive dependencies at the root `node_modules`, while `hoistPattern` controls hoisting inside `node_modules/.bun/node_modules`. Both accept a string or array under `[install]`; `.npmrc` also supports `public-hoist-pattern`.

```toml
[install]
publicHoistPattern = ["@types*", "*eslint*"]
hoistPattern = ["@types*", "*eslint*"]
```

### Lockfile-pinned linker defaults *(since 1.3.2)*

Existing workspaces without an explicit linker setting now retain hoisted installs, while new workspace projects continue to default to isolated installs. `bun install` records this choice through lockfile `configVersion`: new projects and pnpm migrations use v1, while existing Bun projects and npm/Yarn migrations use v0; only v1 workspaces select the isolated default.

```toml
[install]
linker = "isolated"
```

### Hosted Git dependency forms *(since 1.3.2)*

`bun install` now recognizes npm-style `github:` shorthands and GitHub URLs with custom protocol prefixes. Distinct `git+ssh` and `git+https` references to the same repository are resolved and recorded independently.

```json
{
  "dependencies": {
    "library": "github:owner/repo#v1.2.3",
    "tooling": "git+ssh://git@github.com/owner/repo.git#main"
  }
}
```

### Streaming package extraction *(since 1.3.13)*

`bun install` now downloads and extracts package tarballs incrementally by default while still verifying integrity before promoting the extracted tree into the cache. Set `BUN_FEATURE_FLAG_DISABLE_STREAMING_INSTALL=1` to restore buffered extraction if the streaming path causes problems.

```sh
BUN_FEATURE_FLAG_DISABLE_STREAMING_INSTALL=1 bun install
```

### Experimental global virtual store *(since 1.3.14)*

The isolated package linker can share eligible immutable packages through one global `<cache>/links/` store instead of materializing them separately per project; the feature is off by default, and packages with patches, trusted lifecycle scripts, or an ineligible dependency closure fall back to project-local copies. Enable it in `bunfig.toml` and install with the isolated linker, or set `BUN_INSTALL_GLOBAL_STORE=1`.

```toml
[install]
globalStore = true
```

## Security, lifecycle trust, and supply-chain controls

### Global trusted postinstall scripts *(since 1.2.12)*

Global package installs now run postinstall scripts when the package has been explicitly opted in through `trustedDependencies`; Bun no longer blocks those scripts solely because the install is global.

### Dependency security audits *(since 1.2.15)*

`bun audit` scans the dependencies recorded in `bun.lock` for known vulnerabilities and suggests compatible or latest-version updates. It uses the same advisory endpoint as `npm audit`.

```sh
bun audit
```

### Install-time security scanners *(since 1.2.21)*

`bun install` can invoke an installed scanner package before installation and cancels the install when the scanner reports a `fatal` vulnerability.

```toml
[install.security]
scanner = "@my-company/bun-security-scanner"
```

### Audit filtering *(since 1.2.21)*

`bun audit` now filters by minimum severity with `--audit-level`, restricts checks to production dependencies with `--prod`, and accepts repeated `--ignore` flags for CVE IDs.

```sh
bun audit --prod --audit-level=high --ignore CVE-2023-12345
```

### Minimum package release age *(1.3-guide)*

`minimumReleaseAge` rejects package versions published fewer than the configured number of seconds ago, providing a delay window for newly published supply-chain attacks.

```toml
[install]
minimumReleaseAge = 604800 # 7 days
```

### Explicit trust for non-registry dependencies *(since 1.3.5)*

Packages installed through `file:`, `link:`, `git:`, or `github:` specifiers no longer inherit Bun's default lifecycle-script trust merely by matching a trusted package name. Such dependencies must be listed explicitly in `trustedDependencies` before their lifecycle scripts run.

## Workspaces, catalogs, and script orchestration

### Workspace script filtering *(1.2-guide)*

`bun run --filter` runs a script concurrently in every workspace matching a glob, interleaves their output, and accepts multiple filters; `bun` can replace `bun run` in the command.

```sh
bun --filter 'api/*' --filter 'frontend/*' dev
```

### Package-script working directory *(1.2-guide)*

`bun run` now starts a package script in the directory containing the discovered `package.json`, rather than preserving the shell's current subdirectory. Scripts that intentionally depended on invocation-directory-relative paths must adjust.

### Workspace dependency catalogs *(since 1.2.14)*

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

### Optional workspace package linking *(since 1.2.16)*

Set `install.linkWorkspacePackages = false` to install matching workspace dependencies from the registry instead of linking their local packages. The default remains `true`, and explicit `workspace:` specifiers are still respected.

```toml
[install]
linkWorkspacePackages = false
```

### Catalog-aware outdated checks *(since 1.2.16)*

`bun outdated` now reports updates for dependencies sourced from a workspace catalog; `-F` can select the workspace to inspect.

```sh
bun outdated -F app
```

### Top-level dependency catalogs *(since 1.2.19)*

The root `package.json` can now place `catalog` and named `catalogs` directly at the top level instead of nesting them in the `workspaces` object.

```json
{
  "workspaces": ["packages/*"],
  "catalog": { "react": "18.2.0" },
  "catalogs": { "testing": { "@testing-library/react": "16.0.0" } }
}
```

### Recursive workspace dependency updates *(since 1.2.20)*

`bun outdated` and interactive `bun update` accept `-r`/`--recursive` to operate across all workspaces. Interactive updates also accept `--filter` to target selected workspaces and show each dependency's workspace.

```sh
bun outdated --recursive
bun update --interactive --recursive
bun update --interactive --filter=my-app
```

### Workspace-wide scripts *(since 1.2.22)*

`bun run --workspaces` runs the named `package.json` script in every workspace package.

```sh
bun run --workspaces test
```

### Isolated workspace installs by default *(1.3-guide)*

Projects declaring `workspaces` now use the isolated linker by default, preventing packages from accessing dependencies they did not declare. Restore the previous flat layout through the CLI or configuration.

```toml
[install]
linker = "hoisted"
```

### Parallel and sequential package scripts *(since 1.3.9)*

`bun run --parallel` starts multiple scripts together, while `bun run --sequential` runs them one at a time; both add prefixed output, glob matching, lifecycle-script grouping, and `--filter`/`--workspaces` integration. Unlike plain `--filter`, these modes ignore workspace dependency order; failures stop remaining scripts unless `--no-exit-on-error` is used, and `--if-present` skips packages without the requested script.

```sh
bun run --parallel build test
bun run --sequential --workspaces --if-present build
```

## Package metadata, versioning, packing, and publishing

### JSONC `package.json` *(1.2-guide)*

Bun accepts comments and trailing commas in `package.json`, including when the file is loaded through `require()` or `import()`. Other ecosystem tools may still reject such files, so this is only safe when every consumer supports JSONC.

### Custom package tarball paths *(since 1.2.4)*

`bun pm pack --filename <path>` chooses the output tarball path relative to the project root; the path may include subdirectories.

```sh
bun pm pack --filename build/package.tgz
```

### Nested exclusions in `bun pack` *(since 1.2.8)*

`bun pack` now applies exclusion patterns to files and subdirectories nested beneath an included directory; exclusions are no longer limited to top-level entries.

```sh
bun pack --exclude "src/**/test/**" --include "src/**"
```

### Package metadata inspection *(since 1.2.15)*

`bun pm view` fetches npm package metadata, accepts versioned package selectors and nested property paths, and can emit the response as JSON.

```sh
bun pm view express@4.18.2
bun pm view next property.path
bun pm view bun --json
```

### Package metadata command rename *(since 1.2.17)*

`bun info` is now the primary spelling of `bun pm view`; the old command remains an alias.

```sh
bun info react repository.url
```

### Package version management *(since 1.2.18)*

`bun pm version` updates the `package.json` version using `patch`, `minor`, `major`, `prerelease`, `from-git`, or an exact version. It supports `--preid`, `--message`/`-m`, `--allow-same-version`, and `--no-git-tag-version` to skip Git operations.

```sh
bun pm version prerelease --preid beta
bun pm version 1.2.3 --no-git-tag-version
```

### Package metadata automation *(since 1.2.19)*

`bun pm pkg get|set|delete|fix` reads and edits `package.json`; dotted and bracket paths address nested fields. For archive scripts, `bun pm pack --quiet` suppresses diagnostics and writes only the generated tarball filename to stdout.

```sh
bun pm pkg get scripts.build
bun pm pkg set scripts.test="bun test"
bun pm pkg delete contributors[0]
tarball=$(bun pm pack --quiet)
```

### Packed package binaries *(since 1.3.1)*

`bun pm pack` now always includes paths declared by `bin` and `directories.bin`, even when the package's `files` allowlist omits them, and deduplicates paths present in both fields.

### Lifecycle-edited manifests in `bun pm pack` *(since 1.3.7)*

After `prepack`, `prepare`, and `prepublishOnly` run, `bun pm pack` re-reads `package.json`. Manifest changes made by those scripts are therefore included in the tarball.

### README metadata from `bun publish` *(since 1.3.14)*

`bun publish` now finds the first case-insensitive `README` or `README.*` file and sends its contents as registry version metadata for both workspace and tarball publishes. An explicit `readme` field in `package.json` takes precedence.

## Configuration, scaffolding, and command tooling

### npm and certificate configuration *(1.2-guide)*

`bun install` reads `.npmrc` from the project root and home directory for registries, scoped registries, authentication-related settings, and CA configuration. Certificates can also be configured as `install.ca`/`install.cafile` in `bunfig.toml` or passed with `--ca`/`--cafile`.

```toml
[install]
cafile = "path/to/cafile"
```

### npm token environment variable *(since 1.2.5)*

`bun publish` reads `NPM_CONFIG_TOKEN`, so CI jobs can authenticate without writing separate npm configuration.

```sh
NPM_CONFIG_TOKEN="$NPM_TOKEN" bun publish
```

### BOM-aware `.npmrc` parsing *(since 1.2.13)*

`bun install` now recognizes byte-order marks when reading `.npmrc`, including UTF-16 files commonly produced on Windows, instead of misparsing the configuration.

### Non-interactive React project initialization *(since 1.2.14)*

`bun init --react` selects the React template without a TTY; `--react=tailwind` and `--react=shadcn` select preconfigured variants, which is useful for programmatic scaffolding.

```sh
bun init --react=tailwind
```

### Cursor-aware project initialization *(since 1.2.15)*

When `bun init` detects Cursor, it now adds a Cursor rule that guides the agent to use Bun's CLI and APIs instead of Node.js, Vite, npm, or pnpm.

### Optional agent-rule scaffolding *(since 1.2.17)*

`bun init` can now generate shared coding-agent instructions when a supported agent CLI is detected and reuse them for detected editor rules. Set `BUN_AGENT_RULE_DISABLED` to suppress this generated project metadata.

```sh
BUN_AGENT_RULE_DISABLED=1 bun init
```

### npm-compatible install settings *(since 1.2.19)*

`bun install` and `bun add` now honor `link-workspace-packages` and `save-exact` from `.npmrc`. For example, `save-exact=true` makes `bun add` record an exact version rather than a caret range.

### Explicit packages for `bunx` *(since 1.2.21)*

`bunx --package` (or `-p`) runs a binary whose name differs from its package, including binaries supplied by scoped or multi-binary packages.

```sh
bunx -p @angular/cli ng new my-app
```

### Private-registry email authentication *(since 1.3.1)*

`bun install` now forwards registry-specific `:email` entries from `.npmrc` alongside usernames, passwords, or tokens for both default and scoped registries.

```ini
//registry.example.com/:email=user@example.com
//registry.example.com/:_authToken=xxxxxx
```

### Quoted and optional `.npmrc` variables *(since 1.3.5)*

Environment placeholders now expand inside both single- and double-quoted `.npmrc` values. `${NAME?}` expands an unset variable to an empty string; without `?`, an unset placeholder remains literal.

```ini
token = "${NPM_TOKEN}"
auth = 'Bearer ${TOKEN?}'
```
