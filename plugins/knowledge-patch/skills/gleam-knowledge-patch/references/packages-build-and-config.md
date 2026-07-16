# Packages, build, and configuration

## Contents

- [Project layout and scaffolding](#project-layout-and-scaffolding)
- [Dependencies](#dependencies)
- [Build, development, CI, and exports](#build-development-ci-and-exports)
- [Package configuration](#package-configuration)
- [Publishing validation and authentication](#publishing-validation-and-authentication)
- [Hex ownership and release lifecycle](#hex-ownership-and-release-lifecycle)
- [Documentation and repository links](#documentation-and-repository-links)

## Project layout and scaffolding

### Development-only source

Since 1.11.0, put development-only modules in `dev/`. They may import `src/` and use development dependencies but are not shipped in production. Define `main` in `<package>_dev` and run it with `gleam dev`.

See [conventions-and-patterns.md](conventions-and-patterns.md) for the complete `src/`, `dev/`, and `test/` import boundaries.

### New-project controls

`gleam new` can select an Erlang or JavaScript template, override the package name, and omit Git or only GitHub-specific files.

```sh
gleam new --template javascript --skip-git web_app
```

`--skip-git` skips repository initialisation plus `.gitignore`, `.git/*`, and `.github/*`. `--skip-github` omits only `.github/*`.

Since 1.8.0, an invalid or reserved project name prompts with a valid replacement rather than only failing; for example, `type` can become `type_app` after confirmation.

### Internal-module globs

`internal_modules` contains module-name glob patterns and defaults to `<package>/internal` and its descendants. Matching modules are omitted from generated documentation, but their public definitions remain importable and carry no public stability guarantee.

```toml
internal_modules = ["my_app/internal", "my_app/internal/*"]
```

## Dependencies

### Git, path, Hex, rebar3, and Mix dependencies

Since 1.9.0, a dependency may point at a Git or HTTP repository and a `ref` naming a tag, branch, or commit SHA. The build tool downloads the repository and treats it as a normal Gleam package.

```toml
[dependencies]
gleam_stdlib = { git = "https://github.com/gleam-lang/stdlib.git", ref = "957b83b" }
shared = { path = "../shared" }
```

Regular dependency entries may also name Gleam packages, Erlang rebar3 packages, or Elixir Mix packages with the same Hex-requirement syntax. Development dependencies are omitted from published packages and cannot duplicate a regular dependency.

```toml
[dev_dependencies]
gleeunit = ">= 1.0.0 and < 2.0.0"
```

### Inspect dependency trees

Since 1.8.0, display the whole dependency tree, one package's subtree, or all paths from a package back to the root:

```sh
gleam deps tree
gleam deps tree --package package_c
gleam deps tree --invert package_b
```

Since 1.14.0, combining `--invert` with `--package` fails instead of silently ignoring `--invert`.

### Resolution diagnostics and change reports

Since 1.12.0, a dependency-resolution failure identifies the incompatible packages and traces the requirement chains imposing conflicting ranges.

`gleam update` and `gleam deps download` report dependencies with newer major releases, showing the selected and newest versions without automatically choosing a potentially breaking major. Since 1.13.0, resolution after commands such as `gleam add` or `gleam update` prints each added, removed, or changed package and version for auditing.

### Outdated dependencies

Since 1.14.0, `gleam deps outdated` lists packages with repository updates and shows current and latest versions, including newer majors.

```sh
gleam deps outdated
```

Since 1.17.0, the summary states how many packages are outdated out of the total checked, including an explicit zero when all are current.

### Custom certificate authorities

Since 1.9.0, set `GLEAM_CACERTS_PATH` to a CA certificate path when requests to Hex must trust a custom authority, such as on a TLS-intercepting network.

## Build, development, CI, and exports

### Warning and formatting gates

Promote compiler warnings to failures and check formatting without rewriting files:

```sh
gleam build --warnings-as-errors
gleam format --check src/main.gleam test/main_test.gleam
```

### Development output

Since 1.17.0, suppress compilation and launch progress while retaining the program's output:

```sh
gleam dev --no-print-progress
```

### Fault-tolerant compilation

Since 1.16.0, when a module fails to compile, the build tool prunes its dependent subtree and continues compiling independent modules. This preserves as much current language-server information as possible. An opened module that could not compile receives a diagnostic on the import leading to the failure.

### Machine-readable and packaging exports

Since 1.10.0, `gleam export package-information` writes package information as JSON for other build tools.

`package-interface` exports JSON describing modules, functions, and types to a required output path. Other exports provide JavaScript and TypeScript prelude modules or construct the publishable Hex tarball.

```sh
gleam export package-information
gleam export package-interface --out build/package-interface.json
gleam export javascript-prelude
gleam export typescript-prelude
gleam export hex-tarball
```

Target-specific shipment and escript exports are covered in [targets-and-ffi.md](targets-and-ffi.md).

### Release artefacts

Since 1.10.0, official container images include Software Bill of Materials and SLSA provenance data for security auditing and compliance.

Since 1.11.0, releases include a precompiled ARM64 Windows executable, avoiding a source build on Windows-on-ARM.

## Package configuration

### TOML and compiler constraints

Project configuration uses TOML 1.1. `name` and `version` are required. An optional `gleam` requirement makes compilation fail when the active compiler does not satisfy the range.

```toml
name = "my_package"
version = "1.0.0"
gleam = ">= 1.15.0"
```

### Snake-case keys

Since 1.15.0, the canonical keys are `dev_dependencies` and `tag_prefix`. The hyphenated `dev-dependencies` and `tag-prefix` forms remain accepted but are deprecated.

Development-tool configuration conventions are documented in [conventions-and-patterns.md](conventions-and-patterns.md). Target-specific `[erlang]` and `[javascript]` settings are documented in [targets-and-ffi.md](targets-and-ffi.md).

## Publishing validation and authentication

### Namespace and version confirmations

Since 1.7.0, `gleam publish` detects modules that pollute the VM's top-level namespace and asks for confirmation. Package modules should normally live below `src/<package-name>/`.

Publishing a package whose name uses the core-team `gleam_` prefix requires typing a longer confirmation. Publishing a `0.*` version also requires confirmation, encouraging packages intended for use to adopt stable semantic versions.

### Required package content

Since 1.14.0, the compiler warns about a module with no public types or functions, and publishing treats that redundant module as an error until it is removed.

Since 1.15.0, publishing refuses a package with no README or with the unchanged default README generated by `gleam new`.

Since 1.17.0, publishing detects a containing Git repository when the Gleam package lives in a monorepo subdirectory instead of at the repository root.

### Hex credentials and OAuth2

The 1.7.0 credential workflow exchanged supplied Hex credentials for a long-lived API token and stored it encrypted with a local password, prompting for that local password on later operations.

Since 1.15.0, Gleam uses Hex's short-lived OAuth2 flow exclusively. First use revokes any stored legacy token. Hex write operations require multi-factor authentication, and a password used to encrypt local tokens must contain at least eight characters.

## Hex ownership and release lifecycle

Since 1.13.0, transfer an existing package to another account:

```sh
gleam hex owner transfer
```

Since 1.16.0, add another owner to an existing package:

```sh
gleam hex owner add
```

Retire a package version with a reason and optional message, or restore it:

```sh
gleam hex retire <PACKAGE> <VERSION> <REASON> [MESSAGE]
gleam hex unretire <PACKAGE> <VERSION>
```

## Documentation and repository links

### Documentation lifecycle

Build local HTML documentation and optionally open it, publish it to HexDocs, or remove the documentation for a specific package version:

```sh
gleam docs build --open
gleam docs publish
gleam docs remove --package my_package --version 1.2.0
```

Since 1.11.0, generated documentation preserves source type-variable names, keeps imported types qualified, shows full modules on hover, and links to imported type documentation.

### Publishing metadata and additional pages

`licences`, `description`, and `repository` are optional locally but required for Hex publishing. Licences use SPDX identifiers. Top-level `links` appear in generated docs and on Hex; each `[[documentation.pages]]` entry adds a Markdown source page to generated HTML.

```toml
licences = ["Apache-2.0"]
description = "A useful package"
links = [{ title = "Home", href = "https://example.com" }]

[repository]
type = "github"
user = "my-user"
repo = "my-package"

[[documentation.pages]]
title = "Guide"
path = "guide.html"
source = "./docs/guide.md"
```

### Monorepo and Tangled links

Since 1.12.0, repository configuration accepts `tag-prefix`; it is prepended to the default release tag so packages in a monorepo can use distinct tags while retaining correct documentation source links.

Since 1.13.0, set repository type `tangled` to link generated HTML type and value definitions to source hosted on Tangled.

```toml
repository = { type = "tangled", user = "me", repo = "my_project" }
```
