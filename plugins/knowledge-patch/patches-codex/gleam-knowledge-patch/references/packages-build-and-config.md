# Packages, build, and configuration

## Project layout and development

### Development-only modules

Put development tooling in `dev/` (since 1.11.0). These modules may import
`src/` and development dependencies but are excluded from production. Give
the `<package>_dev` module a `main` function and run it with:

```sh
gleam dev
gleam dev --no-print-progress
```

The quiet flag, added in 1.17.0, suppresses compilation and execution progress
while preserving the program's own output.

Production `src/` modules may import only regular dependencies and other
`src/` modules. `dev/` and `test/` may import every dependency scope and source
directory.

### Valid project names

Project names may contain lowercase letters, underscores, and numbers. If
`gleam new` receives invalid characters or a Gleam keyword, it proposes a valid
alternative and asks whether to use it (since 1.8.0).

### Continue independent compilation

When a module fails, the compiler prunes its dependent modules and continues
compiling independent module trees (since 1.16.0). The language server marks
the import that leads to the failed module.

### Platform binaries

Precompiled Gleam executables include Windows ARM64 builds (since 1.11.0).
Official container images include a software bill of materials and SLSA
provenance metadata for audits and compliance (since 1.10.0).

## Dependencies

### Git dependencies

Declare a Git or HTTP URL and an explicit tag, branch, or commit SHA using
`ref` (since 1.9.0):

```toml
[dependencies]
gleam_stdlib = { git = "https://github.com/gleam-lang/stdlib.git", ref = "957b83b" }
```

### Mix and rebar3 packages

Erlang rebar3 and Elixir Mix packages use the same Hex requirement syntax as
Gleam packages under `[dependencies]`; there is no ecosystem-specific form.

### Inspect the resolved tree

`gleam deps tree` prints the resolved dependency graph (since 1.8.0):

```sh
gleam deps tree
gleam deps tree --package package_c
gleam deps tree --invert package_b
```

`--package` selects one subtree, while `--invert` shows every path from a
package back to the project. These options are mutually exclusive (since
1.14.0); combining them is an error.

### Understand resolution and update changes

Dependency-resolution errors trace incompatible constraints through direct and
transitive dependencies (since 1.12.0). Adding, removing, changing, or updating
dependencies prints affected package names and versions (since 1.13.0).

`gleam update` and `gleam deps download` report available major versions that
fall outside the project's permitted range (since 1.12.0).

### Inspect outdated packages

`gleam deps outdated` lists current and latest repository versions (since
1.14.0). It prints a summary count since 1.17.0, including
`0 of N packages have newer versions available` when everything is current.

## Hex authentication and integrity

### OAuth2, MFA, and local token storage

Hex authentication uses OAuth2 exclusively (since 1.15.0). Write operations
require MFA and use short-lived access tokens. On first Hex use, legacy tokens
stored by Gleam are revoked. The local password used to encrypt credentials
must be at least eight characters.

The persistent flow initially creates a long-lived API token and stores it
encrypted on disk (since 1.7.0); later package operations prompt for the local
encryption password instead of Hex account credentials. Apply the current
OAuth2 and short-lived-token behavior for current clients.

### Custom certificate authorities

Set `GLEAM_CACERTS_PATH` to custom CA certificates trusted for communication
with Hex package-manager servers (since 1.9.0).

### Verified registry metadata

In 1.18.0, downloaded Hex packages take their checksum and requirements from
verified registry metadata instead of the Hex API response. The registry
signature therefore protects both tarball verification and dependency
resolution inputs.

## Publishing

### Keep modules in the package namespace

`gleam publish` detects modules outside the package namespace, explains the
collision risk, and requests confirmation (since 1.7.0). A package named
`pumpkin` should normally keep its modules below `src/pumpkin/`.

### Reserved-looking and pre-1.0 names

Publishing an unofficial package beginning with the core team's `gleam_`
prefix requires a longer typed confirmation (since 1.7.0). Publishing a `0.*`
version also requires confirmation because it does not carry normal semantic
version compatibility guarantees (since 1.7.0).

### README and public-definition gates

Publishing refuses a package with no README or the untouched README created by
`gleam new` (since 1.15.0).

The compiler warns when a module has no public types or functions, and
publishing treats that module as an error requiring removal (since 1.14.0).

### Monorepos and source forges

Publishing recognises an enclosing Git repository when a package is nested in
a monorepo rather than at the repository root (since 1.17.0).

The repository configuration accepts a tag prefix for distinct monorepo
release tags (since 1.12.0). Use the canonical snake-case spelling:

```toml
[repository]
tag_prefix = "my_package-v"
```

Tangled is supported as a source forge (since 1.13.0), allowing generated
documentation to link definitions to source:

```toml
repository = { type = "tangled", user = "me", repo = "my_project" }
```

### Manage package owners

Transfer an existing Hex package to another account with
`gleam hex owner transfer` (since 1.13.0). Add another owner with
`gleam hex owner add` (since 1.16.0).

## Configuration

### Canonical snake-case keys

Use `dev_dependencies` and `tag_prefix` (since 1.15.0). The older
`dev-dependencies` and `tag-prefix` spellings still work but are deprecated.
Other settings use snake case as well.

### TOML 1.1 syntax

Gleam 1.18.0 accepts project files using TOML 1.1 syntax in commands that had
previously rejected them.

### Tool configuration

Put static settings for additional tools under `tools.<tool-name>` in
`gleam.toml` instead of separate configuration files. Dynamic settings may
still come from environment variables or CLI arguments.

```toml
[tools.lustre.build]
minify = true
outdir = "../server/priv/static"
```

### Internal module globs

`internal_modules` marks glob-matched modules as outside the package's public
API; it does not enforce import access. The defaults are
`<package>/internal` and `<package>/internal/*`.

```toml
internal_modules = ["my_app/internal", "my_app/internal/*"]
```

## Documentation and metadata exports

### Additional documentation pages

Configure extra Markdown pages as `documentation.pages` entries with a display
title, output HTML path, and source path:

```toml
[[documentation.pages]]
title = "My Page"
path = "my-page.html"
source = "./guides/my-page.md"
```

### Generated documentation precision

Generated package documentation preserves source type-variable names (since
1.11.0). Imported types retain their qualifier, link to their own docs, and
show the full module name on hover. Public type aliases are preferred over
exposing aliased internal types (since 1.13.0).

### Export package information and interfaces

`gleam export package-information` writes package metadata as JSON for other
build tools (since 1.10.0).

`gleam export package-interface --out` writes JSON describing project modules,
functions, and types. Dedicated commands export the JavaScript and TypeScript
prelude modules:

```sh
gleam export package-interface --out build/package-interface.json
gleam export javascript-prelude
gleam export typescript-prelude
```

### Rewrite deprecated syntax

Run `gleam fix` to rewrite deprecated Gleam syntax across the project:

```sh
gleam fix
```
