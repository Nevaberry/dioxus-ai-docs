# Packages and workspaces

## Lockfiles and migrations

### Text lockfile and package JSON (`1.2-guide`)

- The default lockfile is JSONC `bun.lock`. Existing `bun.lockb` projects are
  not migrated automatically; run `bun install --save-text-lockfile`.
- `package.json` may contain comments and trailing commas, including when loaded
  with `require()` or `import()`.
- `bundleDependencies` is honored.

### Lockfile imports (`1.2.20`, `1.2.23`, `1.4-3`)

- `bun install` migrates Yarn v1 lockfiles while preserving resolved versions.
- It migrates `pnpm-lock.yaml` and `pnpm-workspace.yaml`, including workspaces
  and `catalog:` dependencies; the workspace file becomes a root `workspaces`
  array.
- Migration also covers npm lockfile versions 1–4, including nested/bundled
  dependencies, optional peers and overrides, plus pnpm v9 patches, aliases,
  catalogs, git paths, multi-document files, `runtime:` entries and named
  registries.

### New lockfile contracts (`1.4`, `1.4-2`)

- `bun.lock` records SHA-512 integrity for GitHub and tarball dependencies and
  adds it to an existing lockfile on the next install.
- New files use `lockfileVersion: 2`, requiring integrity for out-of-registry
  tarballs and rejecting path traversal in git entries.
- Nested or version-scoped overrides require `lockfileVersion: 3`, which older
  Bun cannot read. Versions 0 and 1 remain loadable without those checks and
  are migrated by install.

## Install layout and resolution

### Isolated linker (`1.2.19`, `1.3-guide`, `1.3.2`)

`bun install --linker=isolated` uses pnpm-style symlinked trees so packages can
import only declared dependencies. Although workspace isolation briefly became
the default, the final rule is lockfile-driven:

- `configVersion: 1` plus workspaces is isolated; without workspaces it is
  hoisted.
- `configVersion: 0` is hoisted.
- A new project gets `1`; an existing lockfile without the field gets `0`.
- A pnpm migration gets `1`; npm and Yarn migrations get `0`.

Existing monorepos must opt in through `[install] linker = "isolated"` or the
CLI flag. Isolated installs are notably faster on Windows.

### Hoisting controls (`1.3.1`, `1.4-3`)

`publicHoistPattern` places selected packages in root `node_modules`, while
`hoistPattern` controls `node_modules/.bun/node_modules`; both take a string or
array. `.npmrc` supports repeatable `public-hoist-pattern[]=`. Set
`[install] hoist = false` or `.npmrc` `hoist=false` to remove the isolated
linker's hidden fallback so undeclared dependencies fail with
`MODULE_NOT_FOUND`.

```toml
[install]
publicHoistPattern = ["@types*", "*eslint*"]
hoistPattern = ["@types*"]
hoist = false
```

### Workspace linking and global storage (`1.2.16`, `1.3.14`)

- `[install] linkWorkspacePackages = false` installs workspace dependencies
  from the registry rather than symlinking them; `workspace:*` is still
  honored.
- Experimental `[install] globalStore = true` or
  `BUN_INSTALL_GLOBAL_STORE=1` shares eligible immutable packages through
  `<cache>/links/`. Patched packages, trusted lifecycle scripts, or an
  ineligible transitive closure fall back to project-local copies. Entries are
  keyed by their resolved dependency closure.
- A `peerDependenciesMeta` entry missing from `peerDependencies` implies an
  optional `"*"` peer.

### Dependency selection (`1.2.19`, `1.2.23`, `1.4`, `1.4-2`)

- Duplicate group priority is `devDependencies` > `optionalDependencies` >
  `dependencies` > `peerDependencies`.
- Repeatable `--cpu` and `--os` select target-specific optional dependencies;
  each accepts `'*'`.
- Nested overrides accept npm object form, Yarn `a/b`, pnpm `a>b`, and optional
  version ranges.
- `workspace:` ranges are honored only in root/workspace manifests, not inside
  downloaded packages.
- Root override/resolution `file:../` targets are accepted (`1.4-4`).

### Install mechanics (`1.3.2`, `1.3.13`, `1.4`)

- Bun may skip known-unnecessary postinstall scripts and link native binaries
  itself. Set `BUN_FEATURE_FLAG_DISABLE_IGNORE_SCRIPTS=1` to run every script,
  or `BUN_FEATURE_FLAG_DISABLE_NATIVE_DEPENDENCY_LINKER=1` to disable native
  binlinking.
- Tarballs are extracted and integrity-hashed while downloading, then promoted
  only after verification. Disable with
  `BUN_FEATURE_FLAG_DISABLE_STREAMING_INSTALL=1`.
- `nativeDependencies` names packages Bun should link without postinstall;
  `ignoreScripts` skips lifecycle scripts even for a trusted package.
- `bun update` now updates transitive dependencies. A named update changes that
  package everywhere; patterns such as `bun update '@types/*' --latest` work.

### Minimum release age (`1.3-guide`)

`[install] minimumReleaseAge = <seconds>` refuses package versions published
more recently than that age, allowing time for malicious releases to be
identified.

## Registry and configuration

### `.npmrc`, CAs, and precedence (`1.2-guide`, `1.2.19`, `1.3.1`, `1.3.5`, `1.4-2`)

- Bun reads project and home `.npmrc` files for registries, auth and `cafile`.
  Installs also accept `--ca`/`--cafile` and `[install] ca`/`cafile`.
- `link-workspace-packages` and `save-exact` are honored.
- Registry `:email` is forwarded for both default and scoped registries.
- `${VAR}` expands inside quoted values. `${VAR?}` becomes empty when unset;
  an unmodified `${VAR}` remains literal when unset.
- `bunfig.toml` wins when it and `.npmrc` set the same key.

### Registry credentials (`1.2.5`, `1.4-2`, `1.4-3`, `1.4-4`)

- `bun publish` reads `NPM_CONFIG_TOKEN`.
- Registry credentials are not forwarded to another host or across an
  `https:` to `http:` downgrade.
- `.npmrc` tokens are matched by both host and path so multiple registries on
  one host keep distinct tokens.
- Credentials embedded in a registry URL are sent as `Authorization`, whether
  configured by `--registry`, `BUN_CONFIG_REGISTRY`, `npm_config_registry`, or
  a bunfig registry object.

## Workspaces and catalogs

### Workspace script execution (`1.2-guide`, `1.2.22`, `1.3.9`)

- `bun run --filter '<glob>' <script>` runs concurrently across matching
  workspaces; filters are repeatable.
- `bun run --workspaces <script>` targets every workspace.
- `bun run --parallel` and `--sequential` accept several script names or globs
  and compose with filters/workspaces. They do not wait for dependency order.
  Failure stops remaining scripts unless `--no-exit-on-error`; pre/post scripts
  stay grouped. `--if-present` and colored `package:script` prefixes are
  supported.

### Recursive and filtered dependency commands (`1.2.20`, `1.4`, `1.4-2`, `1.4-3`)

- `bun outdated --recursive` and `bun update -i -r` cover every workspace;
  interactive update accepts `--filter` and marks workspace/catalog origins.
- `bun add`, `remove`, and `update` accept filters. Topological suffixes mean
  `web...` includes dependencies and `...web` includes dependents.
- `bun install <pkg> --filter x` edits workspace `x`, not root; `add`/`remove
  --filter '*'` excludes root.
- Filters are repeatable and negatable for update and outdated. Recursive
  update writes each selected manifest but preserves `catalog:` spelling.

```sh
bun update --filter 'pkg-*' --filter '!pkg-c'
```

### Catalogs (`1.2.14`, `1.2.19`, `1.4`)

The original catalog location was `workspaces.catalog`; `catalog` and named
`catalogs` may now live at the root, while the nested form remains valid.
Workspace packages reference versions through `catalog:`; pack and publish
replace it with the real version. `bun outdated` resolves catalog entries.

`bun add <pkg> --catalog` writes the root catalog and a workspace `catalog:`
reference. Plain `bun add` reuses a default-catalog entry. A nameless
`bun update` rewrites root catalog versions without replacing workspace
references (`1.4-2`).

## Lifecycle-script security

### Trust and scanners (`1.2.21`, `1.3-guide`, `1.3.5`, `1.4-2`, `1.4-3`)

- Configure a third-party install scanner under `[install.security] scanner`.
  Fatal findings cancel installation. Warn findings prompt interactively and
  abort in CI.
- Bun's default trusted list applies only to npm packages. `file:`, `link:`,
  `git:` and `github:` sources require explicit `trustedDependencies`.
- `trustedDependencies` and `--trust` match exact package names rather than a
  truncated hash.
- `bun pm ls --trusted` lists packages allowed to run lifecycle scripts and
  composes with `--all`.

### Global installs (`1.2.12`)

`bun install -g` runs postinstall scripts for packages in
`trustedDependencies`; earlier global installs skipped them unconditionally.

## Inspection, updates, and maintenance

### Core commands (`1.2-guide`, `1.2.15`, `1.2.17`, `1.2.19`)

- `bun outdated [pattern] [--filter=<ws>]`, `bun publish`, `bun pm pack`, and
  `bun pm whoami` are available.
- `bun update <pkg> --latest` ignores the manifest's semver range.
- `bun install --omit=dev|optional|peer` is repeatable.
- Package metadata is `bun info` (`bun pm view` remains an alias) and accepts a
  property path or `--json`.
- `bun why <package>` prints dependency chains and accepts globs, `--depth`,
  and `--top`.
- `bun pm pkg get|set|delete|fix` reads or edits manifest keys with dot or
  bracket notation.
- `bun update --interactive` selects updates.

### Versioning and listing (`1.2.18`, `1.3.2`)

`bun pm version` accepts npm-like `patch`, `minor`, `major`, `prerelease`,
`from-git`, or a literal version, with `--no-git-tag-version`,
`--allow-same-version`, `--message`/`-m`, and `--preid`. `bun list` aliases
`bun pm ls` and supports `--all`.

### Auditing and diffing (`1.2.15`, `1.2.21`, `1.4`)

- `bun audit` checks `bun.lock` against npm advisories. It supports
  `--audit-level=low|moderate|high|critical`, `--prod`, and repeatable
  `--ignore <CVE>`.
- `bun audit fix` upgrades vulnerable dependencies and installs them;
  `--latest` permits major bumps and `--dry-run` previews. It reports fixes
  blocked by dependent ranges.
- `bun pm diff` compares lockfile and candidate packages, un-minifies content,
  suppresses formatting-only changes, and highlights new install scripts and
  new imports of `child_process`, `fs`, `net`, or `vm`.
- `bun dedupe` collapses duplicate lockfile versions; `--check` is suitable for
  CI. `bun prune --production` removes entries absent from the lockfile or
  needed only by dev dependencies. `bun pm licenses --prod --json` groups
  dependencies by license.

### Changed update behavior (`1.4-2`)

`bun update <name>` exits `1` if no dependency has that name instead of adding
it. `bun update -i` exits `1` on non-TTY input rather than opening a picker.

## Patching, packing, and publishing

### Patches (`1.2-guide`, `1.4-4`)

Run `bun patch <pkg>`, edit its installed files, then
`bun patch --commit <pkg>` to create an automatically applied patch. Git and
tarball dependencies are supported as well as registry packages. Registry
patches are written as `patches/<pkg>@<version>.patch`.

### Packing (`1.2.4`, `1.2.19`, `1.3.1`, `1.3.7`, `1.4-4`)

- `bun pm pack --filename <path>` controls the tarball path relative to project
  root and permits subdirectories.
- `--quiet` prints only the filename.
- Paths named by `bin` and `directories.bin` are included even if absent from
  `files`.
- The manifest is re-read after `prepublishOnly`, `prepack`, and `prepare`, so
  lifecycle rewrites affect the tarball name and metadata.

### Publishing (`1.2.14`, `1.3.7`, `1.3.14`)

Catalog references are replaced with real versions during pack/publish.
Manifest rewrites by preparation scripts are honored. Registry uploads include
`readme` and `readmeFilename`, discovered from the first `README*` unless the
manifest supplies `readme`.

## Project creation and tooling

### Scaffolding (`1.2.3`, `1.2.5`, `1.2.14`, `1.4-2`)

- `bun init` prompts for Blank, React, or Library; the React template includes
  a backend. A target folder may be supplied and is created if absent.
- `--react`, `--react=tailwind`, and `--react=shadcn` select React templates;
  generated `tsconfig.json` uses `module: Preserve`.
- `bun init --react=tanstack` scaffolds TanStack Start.
- `bun init` writes `typescript@^7` and behaves like `-y` without a TTY.

### Source analysis and agent rules (`1.2.3`, `1.2.15`, `1.2.17`)

- `bun create ./Component.tsx` detects imports, missing packages,
  Tailwind/shadcn, and wires the dev server. `bun install --analyze <files...>`
  only scans and adds missing imports.
- `bun init` can create Cursor guidance. When the `claude` CLI is on `PATH`, it
  writes `CLAUDE.md` and may link Cursor rules to it; disable with
  `BUN_AGENT_RULE_DISABLED` or `CLAUDE_CODE_AGENT_RULE_DISABLED`.

### Miscellaneous CLI (`1.2.21`, `1.3.13`, `1.4-2`)

`bunx --package <pkg> <bin>`/`-p` runs a differently named binary.
`bunx claude` aliases `bunx @anthropic-ai/claude-code`. The `bun feedback`
command was removed after its earlier introduction.
