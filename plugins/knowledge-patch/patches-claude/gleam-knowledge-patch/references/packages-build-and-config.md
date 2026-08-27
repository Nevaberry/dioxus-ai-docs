# Packages, build, and configuration

## Hex authentication and ownership

### Authentication lifecycle

Since 1.7.0, the first Hex login creates a long-lived API token stored encrypted
on disk with a local password. Later Hex operations request that local password
instead of the Hex account credentials.

Since 1.15.0, Hex authentication uses OAuth2 exclusively, with MFA for write
operations and short-lived access tokens. The first Hex use with this release
revokes legacy tokens stored by Gleam. The password used to encrypt local tokens
must contain at least eight characters.

Set `GLEAM_CACERTS_PATH` to custom CA certificates that Gleam should trust for
Hex package-manager communication (since 1.9.0).

### Owners

Transfer a Hex package to another account with
`gleam hex owner transfer` (since 1.13.0). Add another owner with
`gleam hex owner add` (since 1.16.0).

### Verified registry metadata

Since 1.18.0, Gleam obtains a downloaded Hex package's checksum and requirements
from verified registry metadata rather than the Hex API response. The registry
signature protects the values used for tarball verification and dependency
resolution.

## Publishing checks

Since 1.7.0, `gleam publish` detects modules outside the package namespace,
explains the collision risk, and asks for confirmation. A package named
`pumpkin` should normally place modules under `src/pumpkin/`.

Publishing an unofficial package with a name beginning with the core team's
`gleam_` prefix requires a longer typed confirmation (since 1.7.0). Publishing
a `0.*` version also requires confirmation because it does not provide normal
semantic-versioning compatibility guarantees.

Since 1.14.0, the compiler warns about a module with no public types or
functions, and `gleam publish` treats it as an error that requires removing the
module from the package.

Since 1.15.0, publishing refuses a package with no README or with the default
README created by `gleam new`.

Since 1.17.0, publishing recognises an enclosing Git repository when the
package is inside a monorepo rather than at its root.

## Dependencies

### Dependency sources

Since 1.9.0, a dependency may come from a Git repository when its Git or HTTP
URL and a tag, branch, or commit SHA are supplied.

```toml
[dependencies]
gleam_stdlib = { git = "https://github.com/gleam-lang/stdlib.git", ref = "957b83b" }
```

Erlang rebar3 and Elixir Mix packages use the same Hex requirement syntax as
Gleam packages under `[dependencies]`; no ecosystem-specific form is needed.

### Dependency tree

Since 1.8.0, `gleam deps tree` prints the resolved tree. `--package` selects one
package's subtree; `--invert` shows every path from a package back to the root.

```sh
gleam deps tree
gleam deps tree --package package_c
gleam deps tree --invert package_b
```

Since 1.14.0, `--package` and `--invert` are mutually exclusive; combining them
fails instead of silently ignoring `--invert`.

### Resolution and updates

Since 1.12.0, resolution failures identify incompatible packages and trace
conflicting constraints through direct and transitive dependencies.

`gleam update` and `gleam deps download` report a dependency whose newest major
version lies outside the project's allowed range (since 1.12.0).

Since 1.13.0, adding, removing, changing, or updating dependencies prints the
affected package names and versions when resolution changes.

Since 1.14.0, `gleam deps outdated` lists each dependency's current version and
latest package-repository version. Since 1.17.0, it also prints a summary count,
including `0 of N packages have newer versions available` when all are current.

## Project creation and source directories

Since 1.8.0, `gleam new` proposes a valid alternative and asks to use it when a
requested name contains an invalid character or a Gleam keyword. Project names
may contain lowercase letters, underscores, and numbers.

Since 1.7.0, Erlang, Elixir, JavaScript, and other external modules may be in
subdirectories of `src/` or `test/`; they are not restricted to the top level.

Since 1.11.0, development-only source may live in `dev/`. It can import `src/`
modules and use development dependencies without entering production output.
Give `<package>_dev` a `main` function and run:

```sh
gleam dev
```

Since 1.17.0, `gleam dev --no-print-progress` suppresses compilation and
execution progress while preserving the program's own output.

## Configuration

### Canonical key names

Since 1.15.0, `dev_dependencies` and `tag_prefix` are canonical. The older
`dev-dependencies` and `tag-prefix` spellings work but are deprecated.

```toml
[dev_dependencies]
gleeunit = ">= 1.0.0 and < 2.0.0"
```

Since 1.12.0, `repository.tag-prefix` can prefix generated release tags so
packages in a monorepo have distinct tags. Use the later canonical spelling
`tag_prefix`.

Since 1.18.0, commands that previously failed on TOML 1.1 syntax accept
`gleam.toml` files using that syntax.

### Internal modules

`internal_modules` is glob-based: it marks matching modules as outside the
public package API but does not prevent imports. Defaults are
`<package>/internal` and `<package>/internal/*`.

```toml
internal_modules = ["my_app/internal", "my_app/internal/*"]
```

### OTP application startup

`erlang.application_start_module` names an OTP application-behaviour module.
In Erlang atom notation, a Gleam module slash becomes `@`.
`erlang.extra_applications` lists OTP applications to start beyond those
provided by dependencies.

```toml
[erlang]
application_start_module = "my_project@application"
extra_applications = ["inets", "ssl"]
```

### JavaScript generation and runtime

`javascript.typescript_declarations` emits `.d.ts` files.
`javascript.runtime` selects `node`, `deno`, or `bun` and defaults to Node.

Deno's `allow_env`, `allow_net`, `allow_read`, `allow_run`, and `allow_write`
accept booleans or allowlists. `allow_all`, `allow_ffi`, `allow_hrtime`, and
`allow_sys` are booleans.

```toml
[javascript]
typescript_declarations = true
runtime = "deno"

[javascript.deno]
allow_env = ["DATABASE_URL"]
allow_net = ["example.com:443"]
allow_read = ["./database.sqlite"]
```

## Build behavior

Since 1.16.0, if a module fails to compile, the build tool prunes modules that
depend on it and continues compiling independent module trees. The language
server diagnoses the import that leads to the failed module.

Use `gleam fix` to rewrite deprecated Gleam syntax to supported replacements
across the project.

## Exports

Since 1.10.0, `gleam export package-information` writes package information as
JSON for other build tools.

`gleam export package-interface --out` writes JSON describing project modules,
functions, and types. Separate commands export JavaScript and TypeScript
prelude modules.

```sh
gleam export package-information
gleam export package-interface --out build/package-interface.json
gleam export javascript-prelude
gleam export typescript-prelude
```

## Documentation and repository metadata

Additional Markdown documentation pages are `documentation.pages` entries with
a display title, output HTML path, and source file.

```toml
[[documentation.pages]]
title = "My Page"
path = "my-page.html"
source = "./guides/my-page.md"
```

Since 1.13.0, repository metadata accepts Tangled as a source forge, allowing
generated documentation to link type and value definitions to source.

```toml
repository = { type = "tangled", user = "me", repo = "my_project" }
```

## Tooling and project safety

The language server type-checks unsaved buffers for the configured target
without generating code or compiling Erlang or Elixir, so merely opening a
project cannot execute foreign code. Only formatting is available for Gleam
files outside a project.

Since 1.10.0, official container images include a software bill of materials
and SLSA provenance information for audits and compliance checks.
