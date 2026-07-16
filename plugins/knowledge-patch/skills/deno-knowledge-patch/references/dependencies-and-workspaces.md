# Dependencies and Workspaces
Manage manifests, registries, dependency resolution, lockfiles, installations, updates, and workspaces.
## Contents
- [Package commands and manifests](#package-commands-and-manifests)
- [Resolution and registries](#resolution-and-registries)
- [Workspaces](#workspaces)
- [Lockfiles and installation](#lockfiles-and-installation)
- [Updates and inspection](#updates-and-inspection)

## Package commands and manifests

### Exact dependency versions (2.7-guide)

`deno add --save-exact` (or `--exact`) records an exact version instead of the default caret range; the option also works with `deno install`.

```sh
deno add --save-exact npm:express
```

### Explicit `package.json` targeting (2.8-guide)

In mixed-manifest projects, `--package-json` makes `deno add`, `install`, `remove`, or `uninstall` operate on `package.json` rather than the otherwise preferred `deno.json`.

```sh
deno add --package-json express
```

### Global-install argument boundary and batching (2.6-guide)

`deno install -g` now requires `--` before arguments intended for an installed script, so preceding flags remain installer flags. It can also install multiple global packages in one invocation, such as `deno install -g npm:prettier npm:typescript`.

### JSR dependencies in `package.json` (2.7-guide)

`package.json` dependencies can use `jsr:` version specifiers directly, so consuming a JSR package no longer requires `deno.json`.

```json
{ "dependencies": { "@std/path": "jsr:^1.0.9" } }
```

### Package-command syntax (2.0.0)

JSR packages passed to `deno add` or `deno install` require the `jsr:` prefix, and `deno install --entrypoint` replaces `deno cache` for an explicit entrypoint. Permission flags on `deno install` require `-g`; without `-g`, `deno uninstall` aliases `deno remove`.

```sh
deno add jsr:@scope/pkg
deno install --entrypoint main.ts
```

### Package-manager mode (2.0-guide)

`deno install` creates `node_modules` when a project has `package.json`; without one, dependencies stay in Deno's global cache. `deno add` and `deno remove` can update either `package.json` or `deno.json`, so these commands do not make a manifest mandatory for single-file programs.

### Persistent `package.json` preference (2.9.0)

Set `preferPackageJson` in `deno.json` to persistently target `package.json` for package-management commands instead of passing `--package-json` to each command.

```json
{
  "preferPackageJson": true
}
```

### Registry shortcuts for `deno install` (2.3.0)

The `--npm` and `--jsr` registry flags are accepted by `deno install` as well as `deno add`, so following unqualified package names use the selected registry.

```sh
deno install --npm chalk
```

### Registry-wide `deno add` flags (2.3-guide)

`deno add --npm` and `deno add --jsr` apply a registry to following unqualified package names, making multi-package additions shorter; explicit specifiers may still be mixed into the command.

```sh
deno add --npm chalk react jsr:@std/fs
```

### Unprefixed npm package arguments (2.8-guide)

Package arguments to `deno add` and `deno install` now default to npm, while JSR packages still need `jsr:`. The `npm:` prefix remains valid on the CLI and remains required in explicit import specifiers.

```sh
deno add express
```

## Resolution and registries

### Additional `.npmrc` controls (2.8-guide)

`.npmrc` can set `min-release-age`, `certfile` and `keyfile` for registry mTLS, and an `email` on legacy `_auth` entries. `NPM_CONFIG_REGISTRY` now overrides a registry selected in `.npmrc`.

```ini
min-release-age=72h
```

### Environment-selected package conditions (2.4.0)

`DENO_NODE_CONDITIONS` can supply additional package-export conditions through the environment instead of a command-line flag.

```sh
DENO_NODE_CONDITIONS=react-server deno run app.ts
```

### Local npm package compatibility (2.3.0)

`patch` entries may use absolute paths, and dependencies in a local `package.json` may use `file:` specifiers, covering local-package layouts that previously failed installation or resolution.

### Local npm package links (2.4-guide)

The `links` setting replaces `patch` for redirecting npm dependencies to local packages. Existing `patch` configuration still works but produces a deprecation warning.

```json
{
  "links": ["../cowsay"]
}
```

### Local npm package overrides (2.3-guide)

A project can redirect an npm dependency to a local package by enabling a local `node_modules` directory and listing the package path under `patch`. The package name must also exist in the npm registry; with `nodeModulesDir: "manual"`, rerun `deno install` after changing the local package.

```json
{
  "nodeModulesDir": "auto",
  "patch": ["../path/to/local_npm_package"]
}
```

### npm dependency overrides (2.7-guide)

Deno honors npm-style `package.json` `overrides`, including global transitive pins and overrides scoped beneath a particular parent dependency.

```json
{
  "overrides": {
    "cookie": "0.7.0",
    "express": { "qs": "6.13.0" }
  }
}
```

### Package engine warnings (2.9-guide)

`deno install` reads `package.json`'s `engines` field and warns, but does not fail, when the active Node or Deno version violates a declared constraint.

### Private registries through `.npmrc` (2.0-guide)

Deno automatically reads scoped registry and authentication settings from `.npmrc`, with no Deno-specific registry configuration required.

```ini
@mycompany:registry=http://mycompany.com:8111/
//mycompany.com:8111/:_auth=secretToken
```

### Published local-path dependencies (2.8-guide)

When registry metadata contains stray `file:` or `link:` dependencies, Deno now skips those entries instead of failing resolution; the referenced development-only code is expected to be present in the published tarball.

## Workspaces

### Central workspace dependency catalogs (2.8-guide)

A workspace root can define shared versions under `catalog`, or named groups under `catalogs`; members reference them with `catalog:` or `catalog:<name>`. Catalog references also work in package overrides and object-form workspaces.

```json
{
  "workspace": ["./packages/api"],
  "catalogs": { "runtime": { "hono": "^4.6.0" } }
}
```

```json
{ "dependencies": { "hono": "catalog:runtime" } }
```

### Hybrid Deno and npm workspaces (2.0-guide)

A root `deno.json` declares members with `workspace`; members may independently use `deno.json` or `package.json` and have separate dependencies, lint settings, and format settings.

```json
{
  "workspace": ["./add", "./subtract"]
}
```

Running `deno publish` at the workspace publishes its JSR members in dependency order, so their release order does not need to be managed manually.

### Per-member workspace executables (2.9-guide)

In a workspace, `deno install` now creates `node_modules` in each member and populates its `.bin`, allowing tools launched inside that member to find its local dependencies and executables.

## Lockfiles and installation

### Automatic lockfile conflict resolution (2.9-guide)

When `deno.lock` contains git conflict markers, Deno now unions additive sections and chooses the higher version for genuine specifier conflicts instead of rejecting the lockfile for manual repair.

### Clean frozen CI installs (2.8-guide)

`deno ci` requires `deno.lock`, removes an existing `node_modules`, and installs with frozen-lockfile validation. It also accepts `--prod` and `--skip-types`.

```sh
deno ci
```

### Compiler-option dependencies in lockfiles (2.1.0)

The lockfile now tracks dependencies referenced through TypeScript compiler options, so those dependencies participate in locked resolution.

### Existing Node lockfiles and pnpm workspaces (2.9-guide)

When no `deno.lock` exists, `deno install` can seed one without re-resolving from `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, or `bun.lock`, preserving resolved versions and integrity hashes. It also detects `pnpm-workspace.yaml`, migrates its `packages`, `catalog`, and `catalogs` into `package.json` or `deno.json`, and asks for a rerun.

```sh
deno install
```

### Global npm installation layout (2.7.0)

Global installs accept `--node-modules-dir`; installing an `npm:` specifier can use a manual `node_modules` directory when the package needs a physical dependency tree.

```sh
deno install -g --node-modules-dir=manual npm:cowsay
```

### Hoisted `node_modules` (2.8-guide)

`nodeModulesLinker` selects either the default isolated dependency layout or an npm-style flat `"hoisted"` layout for legacy tools that expect undeclared packages at the top level.

```json
{
  "nodeModulesDir": "manual",
  "nodeModulesLinker": "hoisted"
}
```

### JSR packages in `node_modules` (2.9-guide)

Opt-in `jsrDepsInNodeModules` installs `jsr:` dependencies through JSR's npm-compatibility registry, materializes their complete tarballs so packages can read bundled assets and use `import.meta.dirname`, and links them under their original scoped names for Node-oriented tools. It is off by default; without it, JSR dependencies retain their HTTPS-backed resolution behavior.

```json
{
  "jsrDepsInNodeModules": true
}
```

### Lockfile v5 default (2.3.0)

New lockfiles now default to version 5, so tools that read or transform `deno.lock` must understand the new format.

### Lockfile-only installation (2.6-guide)

`deno install --lockfile-only` resolves dependencies and updates `deno.lock` without fetching or installing packages, allowing a later normal install to use the verified lockfile.

### npm executable and global-install resolution (2.9.0)

Global installs now resolve dependencies declared in the installed package's `package.json`. Deno also stops applying the active import map to an npm executable's main module, avoiding unintended rewrites of package binaries.

### Targeted and production npm installs (2.8-guide)

`deno install --os=<os> --arch=<arch>` resolves platform-specific optional dependencies for a target other than the host. `deno install --prod` omits both `devDependencies` and `@types/*` packages for deployment installs.

```sh
deno install --os=linux --arch=arm64
deno install --prod
```

### XDG cache placement on macOS (2.2.0)

Deno now honors `XDG_CACHE_HOME` for its Deno directory on macOS, so cache placement can follow XDG conventions.

```sh
XDG_CACHE_HOME="$HOME/.cache" deno info
```

## Updates and inspection

### Declared-dependency listing (2.9-guide)

`deno list` reports declared dependencies and resolved versions rather than the complete module graph shown by `deno info`. `--depth`, `--prod`, `-r`, and wildcard package filters expand or narrow the dependency tree.

```sh
deno list --depth 2
deno list --prod
deno list -r
deno list "*eslint*"
```

### Dedicated dependency updates (2.4.0)

`deno update` is now a separate subcommand for updating project dependencies, so update workflows no longer need to run through `deno outdated --update`.

```sh
deno update
```

### Dependency path explanations (2.8-guide)

`deno why <package>` prints every path from a direct npm or JSR dependency to the requested package; append a version to select one installed version.

```sh
deno why qs@6.15.1
```

### Interactive dependency updates (2.2-guide)

`deno outdated --update --interactive` allows selecting updates interactively. `--latest` is now valid without `--update`, and `deno outdated` can update dependencies stored in external import maps.

```sh
deno outdated --update --interactive
deno outdated --latest
```

### Lockfile-only dependency updates (2.8.0)

`deno update --lockfile-only` now leaves dependency constraints in project configuration unchanged and updates only the lockfile.

```sh
deno update --lockfile-only
```
