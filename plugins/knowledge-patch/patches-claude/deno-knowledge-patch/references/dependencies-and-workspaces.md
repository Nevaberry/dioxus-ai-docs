# Dependencies and Workspaces

Choose manifests, resolve registries, maintain lockfiles, and operate mixed Deno and npm workspaces.

## Automatic lockfile conflict resolution (2.9-guide)

When `deno.lock` contains git conflict markers, Deno now unions additive sections and chooses the higher version for genuine specifier conflicts instead of rejecting the lockfile for manual repair.

## Bundled npm dependencies (2.5-guide)

Deno's npm compatibility now supports packages that declare `bundleDependencies` in `package.json`.

## Central workspace dependency catalogs (2.8-guide)

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

## Clean frozen CI installs (2.8-guide)

`deno ci` requires `deno.lock`, removes an existing `node_modules`, and installs with frozen-lockfile validation. It also accepts `--prod` and `--skip-types`.

```sh
deno ci
```

## Compiled global installs (2.7-guide)

`deno install --global --compile` compiles an npm package into a standalone executable that starts without an installed Deno runtime.

```sh
deno install --global --compile -A npm:@example/tool
```

## Compiled-install flag combinations (2.7.0)

Compiled installs now work with `--force`, and global compiled installs support `--allow-scripts` when trusted lifecycle scripts are required.

## Compiler-option dependencies in lockfiles (2.1.0)

The lockfile now tracks dependencies referenced through TypeScript compiler options, so those dependencies participate in locked resolution.

## Declared-dependency listing (2.9-guide)

`deno list` reports declared dependencies and resolved versions rather than the complete module graph shown by `deno info`. `--depth`, `--prod`, `-r`, and wildcard package filters expand or narrow the dependency tree.

```sh
deno list --depth 2
deno list --prod
deno list -r
deno list "*eslint*"
```

## Dedicated dependency updates (2.4.0)

`deno update` is now a separate subcommand for updating project dependencies, so update workflows no longer need to run through `deno outdated --update`.

```sh
deno update
```

## Dependency path explanations (2.8-guide)

`deno why <package>` prints every path from a direct npm or JSR dependency to the requested package; append a version to select one installed version.

```sh
deno why qs@6.15.1
```

## Encoded npm subpaths (2.9.1)

Subpaths in `npm:` specifiers are now percent-decoded during resolution.

## Exact dependency versions (2.7-guide)

`deno add --save-exact` (or `--exact`) records an exact version instead of the default caret range; the option also works with `deno install`.

```sh
deno add --save-exact npm:express
```

## Explicit `package.json` targeting (2.8-guide)

In mixed-manifest projects, `--package-json` makes `deno add`, `install`, `remove`, or `uninstall` operate on `package.json` rather than the otherwise preferred `deno.json`.

```sh
deno add --package-json express
```

## Explicit packages for `deno x` (2.8-guide)

`deno x --package` (or `-p`) selects the package when its published binary has a different name.

```sh
deno x --package npm:typescript tsc
```

## Global npm installation layout (2.7.0)

Global installs accept `--node-modules-dir`; installing an `npm:` specifier can use a manual `node_modules` directory when the package needs a physical dependency tree.

```sh
deno install -g --node-modules-dir=manual npm:cowsay
```

## Global-install argument boundary and batching (2.6-guide)

`deno install -g` now requires `--` before arguments intended for an installed script, so preceding flags remain installer flags. It can also install multiple global packages in one invocation, such as `deno install -g npm:prettier npm:typescript`.

## Hybrid Deno and npm workspaces (2.0-guide)

A root `deno.json` declares members with `workspace`; members may independently use `deno.json` or `package.json` and have separate dependencies, lint settings, and format settings.

```json
{
  "workspace": ["./add", "./subtract"]
}
```

Running `deno publish` at the workspace publishes its JSR members in dependency order, so their release order does not need to be managed manually.

## Included package assets (2.9.0)

`deno pack` now includes assets matched by `publish.include` in the generated tarball, so explicitly selected non-module files are shipped with the package.

## Interactive dependency updates (2.2-guide)

`deno outdated --update --interactive` allows selecting updates interactively. `--latest` is now valid without `--update`, and `deno outdated` can update dependencies stored in external import maps.

```sh
deno outdated --update --interactive
deno outdated --latest
```

## JSR dependencies in `package.json` (2.7-guide)

`package.json` dependencies can use `jsr:` version specifiers directly, so consuming a JSR package no longer requires `deno.json`.

```json
{ "dependencies": { "@std/path": "jsr:^1.0.9" } }
```

## JSR template initialization (2.7.0)

`deno init --jsr <package>` initializes a project from a JSR template package.

```sh
deno init --jsr @scope/template
```

## Local npm package compatibility (2.3.0)

`patch` entries may use absolute paths, and dependencies in a local `package.json` may use `file:` specifiers, covering local-package layouts that previously failed installation or resolution.

## Local npm package links (2.4-guide)

The `links` setting replaces `patch` for redirecting npm dependencies to local packages. Existing `patch` configuration still works but produces a deprecation warning.

```json
{
  "links": ["../cowsay"]
}
```

## Local npm package overrides (2.3-guide)

A project can redirect an npm dependency to a local package by enabling a local `node_modules` directory and listing the package path under `patch`. The package name must also exist in the npm registry; with `nodeModulesDir: "manual"`, rerun `deno install` after changing the local package.

```json
{
  "nodeModulesDir": "auto",
  "patch": ["../path/to/local_npm_package"]
}
```

## Lockfile and cache changes (2.0.0)

Lockfile v4 is the default and stores normalized version constraints in a terser form. The remote-module cache directory is renamed from `deps` to `remote`.

## Lockfile v5 default (2.3.0)

New lockfiles now default to version 5, so tools that read or transform `deno.lock` must understand the new format.

## Lockfile-only dependency updates (2.8.0)

`deno update --lockfile-only` now leaves dependency constraints in project configuration unchanged and updates only the lockfile.

```sh
deno update --lockfile-only
```

## Lockfile-only installation (2.6-guide)

`deno install --lockfile-only` resolves dependencies and updates `deno.lock` without fetching or installing packages, allowing a later normal install to use the verified lockfile.

## Non-interactive npm initialization (2.6.0)

`deno init --npm` accepts `--yes` to bypass its permission prompt, which allows npm project scaffolding to run unattended.

```sh
deno init --npm vite --yes
```

## npm and JSR project creation (2.7-guide)

`deno create npm:<name>` resolves an npm `create-<name>` package, while a JSR template package must export `./create`.

```sh
deno create npm:vite -- my-project
deno create jsr:@std/http
```

## npm dependency overrides (2.7-guide)

Deno honors npm-style `package.json` `overrides`, including global transitive pins and overrides scoped beneath a particular parent dependency.

```json
{
  "overrides": {
    "cookie": "0.7.0",
    "express": { "qs": "6.13.0" }
  }
}
```

## npm executable and global-install resolution (2.9.0)

Global installs now resolve dependencies declared in the installed package's `package.json`. Deno also stops applying the active import map to an npm executable's main module, avoiding unintended rewrites of package binaries.

## npm package documentation (2.8-guide)

`deno doc` can render npm packages, including packages whose entry points do not ship type declarations.

## npm scaffolding and dependency updates (2.1-guide)

`deno init --npm <name>` runs an npm-style project initializer and prompts before granting its script all permissions. `deno outdated` checks both `deno.json` and `package.json`; `--update` respects declared ranges by default, while `--latest` may cross them, package arguments select versions or filters, and `--recursive` covers a workspace.

```sh
deno init --npm vite
deno outdated --update
deno outdated --recursive --update --latest
deno outdated --update chalk@5.2 @std/async@1.0.6
```

## npm type resolution (2.3.0)

Type checking npm dependencies now understands `types@` export conditions and `typesVersions`, preventing their version-specific declarations from being missed.

## Package binaries with `dx` (2.6-guide)

`dx` is an `npx`-style runner for npm and JSR package binaries; install the alias with `deno x --install-alias`, and unqualified names default to `npm:` while local files are rejected. It grants all permissions unless another permission flag is supplied, prompts before downloading, and runs lifecycle scripts when that prompt is accepted.

```sh
dx cowsay "Hello, Deno!"
```

## Package engine warnings (2.9-guide)

`deno install` reads `package.json`'s `engines` field and warns, but does not fail, when the active Node or Deno version violates a declared constraint.

## Package-command syntax (2.0.0)

JSR packages passed to `deno add` or `deno install` require the `jsr:` prefix, and `deno install --entrypoint` replaces `deno cache` for an explicit entrypoint. Permission flags on `deno install` require `-g`; without `-g`, `deno uninstall` aliases `deno remove`.

```sh
deno add jsr:@scope/pkg
deno install --entrypoint main.ts
```

## Package-manager mode (2.0-guide)

`deno install` creates `node_modules` when a project has `package.json`; without one, dependencies stay in Deno's global cache. `deno add` and `deno remove` can update either `package.json` or `deno.json`, so these commands do not make a manifest mandatory for single-file programs.

## Per-member workspace executables (2.9-guide)

In a workspace, `deno install` now creates `node_modules` in each member and populates its `.bin`, allowing tools launched inside that member to find its local dependencies and executables.

## Persistent `package.json` preference (2.9.0)

Set `preferPackageJson` in `deno.json` to persistently target `package.json` for package-management commands instead of passing `--package-json` to each command.

```json
{
  "preferPackageJson": true
}
```

## Published local-path dependencies (2.8-guide)

When registry metadata contains stray `file:` or `link:` dependencies, Deno now skips those entries instead of failing resolution; the referenced development-only code is expected to be present in the published tarball.

## Registry shortcuts for `deno install` (2.3.0)

The `--npm` and `--jsr` registry flags are accepted by `deno install` as well as `deno add`, so following unqualified package names use the selected registry.

```sh
deno install --npm chalk
```

## Registry-wide `deno add` flags (2.3-guide)

`deno add --npm` and `deno add --jsr` apply a registry to following unqualified package names, making multi-package additions shorter; explicit specifiers may still be mixed into the command.

```sh
deno add --npm chalk react jsr:@std/fs
```

## Targeted and production npm installs (2.8-guide)

`deno install --os=<os> --arch=<arch>` resolves platform-specific optional dependencies for a target other than the host. `deno install --prod` omits both `devDependencies` and `@types/*` packages for deployment installs.

```sh
deno install --os=linux --arch=arm64
deno install --prod
```

## Unprefixed npm package arguments (2.8-guide)

Package arguments to `deno add` and `deno install` now default to npm, while JSR packages still need `jsr:`. The `npm:` prefix remains valid on the CLI and remains required in explicit import specifiers.

```sh
deno add express
```

## Workspace-aware version bumps (2.8-guide)

`deno bump-version patch|minor|major|prerelease` updates a package manifest; at a workspace root it bumps every member and rewrites matching `jsr:` constraints in root configuration and import maps. With no increment it derives per-package changes from Conventional Commits, while `--base`, `--start`, and `--dry-run` control the comparison and preview.

```sh
deno bump-version --base=main --dry-run
```
