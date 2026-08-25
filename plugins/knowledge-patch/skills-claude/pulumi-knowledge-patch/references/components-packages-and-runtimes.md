# Components, Packages, and Runtimes

Use this reference when authoring reusable components, managing packages and templates, selecting language runtimes, generating SDKs, or testing Pulumi programs.

## Cross-language component packages (batch `components-2025`)

A component directory becomes a cross-language package when it contains `PulumiPlugin.yaml`; the file is unnecessary for a same-language-only component. Pulumi analyzes exposed components, derives a schema, and generates consumer-language SDKs, including Pulumi YAML SDKs.

The plugin manifest names the authoring runtime, such as `python`, `nodejs`, `dotnet`, `go`, `java`, or `yaml`.

## Runtime-specific component exposure (batch `components-2025`)

- TypeScript exposes every exported component class and needs no separate entry point.
- YAML needs no provider-host entry point.
- Python uses `_main_.py` and passes the exposed classes to `pulumi.provider.experimental.component_provider_host(name=..., components=[...])`.
- Go uses the `pulumi-go-provider` v1 builder, such as `infer.NewProviderBuilder().WithNamespace(...).WithComponents(infer.ComponentF(NewComponent)).Build()`, then calls `provider.Run(...)`.
- .NET returns `Pulumi.Experimental.Provider.ComponentProviderHost.Serve(args)` from `Program.Main`.
- Java starts `com.pulumi.provider.internal.ComponentProviderHost` with a package to scan.

## YAML-authored components (batch `components-2025`)

Pulumi YAML defines reusable components under top-level `components`. Each definition can declare inputs, child resources, and outputs, and consumers reference the resulting component type. YAML fits straightforward component definitions; conditionals, map merges, and similar logic still require another authoring language.

## Installing component sources (batch `components-2025`)

`pulumi package add` accepts a Git source, optionally pinned to a release tag, or a relative or absolute component directory. It retrieves or inspects the source and generates a local SDK for the consuming language. Private Git repositories work when access tokens are supplied through the environment.

```shell
pulumi package add github.com/myorg/secure-s3-component@v1.0.0
pulumi package add ./components/secure-s3-component
```

## Restoring declared packages (batch `components-2025`)

`pulumi install` processes every `packages` entry in `Pulumi.yaml` and generates local SDKs. Generated SDKs can be committed for reproducibility; if ignored, every fresh checkout must run `pulumi install`. Pulumi YAML consumes a component through the package name and exposed component type.

## Git package resolution (batch `3.145.0-3.159.0`)

Git plugins accept HTTPS URLs, repository subdirectories, and short commit hashes. An unversioned source resolves its latest version. `GITHUB_TOKEN` and `GITLAB_TOKEN` are recognized. A Git plugin's namespace is inferred and, as of 3.159.0, cannot be overridden in `PulumiPlugin.yaml`.

## SDK project and resource introspection (batch `3.145.0-3.159.0`)

The .NET, Go, Java, Node.js, Python, and YAML SDKs can locate the project root. Go and Python expose `pulumiResourceName` and `pulumiResourceType` for a resource's runtime name and type token.

## Python toolchains and deferred Go outputs (batch `3.145.0-3.159.0`)

Python dynamic providers work with Poetry and uv. Pulumi supports uv-based plugin and package discovery, and `RunPlugin` defaults to a virtual environment.

The Go SDK and Go program generation support deferred outputs, so code can create an output handle before establishing the value that resolves it.

## Package publication and cloud templates (batch `3.145.0-3.159.0`)

`pulumi new` can use Pulumi Cloud templates. Package publishing first appeared experimentally in 3.158.0; use the later stable `pulumi package publish` behavior for current workflows.

## Java SDK 1.0 (batch `release-notes-117`)

The Java SDK reached general availability at 1.0 with the full Pulumi programming model, parity with other supported languages, stronger type safety, and support for the Java LTS versions current at launch.

## Autonaming for components (batch `release-notes-117`)

Autonaming configuration is available in CLI 3.91.1 and later. It can disable generated names globally or configure autonaming per component without program-code changes. Engine autonaming strategies apply to custom resources rather than component resources themselves.

## Package publication lifecycle (batch `3.160.0-3.181.0`)

`pulumi package publish` became non-experimental in 3.166.0. `pulumi template publish` was added in 3.180.0 and remained experimental in this batch.

## Package and plugin source resolution (batch `3.160.0-3.181.0`)

`pulumi package add` records its source under `packages` in `Pulumi.yaml`. An unprefixed source is no longer assumed to be a file path, so keep `./` or `../` on local paths. The default Registry package source is private. Plugin download URLs can resolve through the Pulumi Registry, while `pulumi install --file` bypasses Registry resolution. The Go direct-repository plugin installer supports private GitHub and GitLab instances.

## Node.js and Go baselines (batch `3.160.0-3.181.0`)

At this point the Node.js SDK required Node.js 20, supported Node.js 24, and targeted ES2020 instead of ES2016. Later guidance raises the minimum to Node.js 22. Generated Go programs and the Go SDK targeted Go 1.23 in this batch; later generation targets Go 1.25.

## Go property and workspace APIs (batch `3.160.0-3.181.0`)

Go `property.Value` is immutable. `property.Path` and `property.Map.Delete` support structured access and removal. `workspace.GetPluginInfo`, `workspace.GetPluginPath`, and APIs that create `plugin.Context` accept `context.Context`.

## Python component provider namespaces (batch `3.160.0-3.181.0`)

Experimental component-provider helpers moved from `pulumi.provider.experimental.provider` to `pulumi.provider.experimental.component`. A new general provider interface occupies the former `provider` namespace. Python component providers also support a bootstrap-less mode.

## Python component types and references (batch `3.160.0-3.181.0`)

Python component providers support resource references, enum inference, and enum references. `@pulumi.type_token` and the static `pulumi_type` resource-class property expose the type token to provider and component code.

## Go policy authoring (batch `3.160.0-3.181.0`)

Go introduced an experimental Policy as Code SDK. Go Automation API preview and update options can carry policy packs.

## Registry packages and templates (batch `3.182.0-3.198.0`)

`pulumi package add` accepts Registry identifiers. `pulumi new` accepts qualified Registry template names and lists published templates. Private Registry publishing and resolution do not require `PULUMI_EXPERIMENTAL`; `PULUMI_DISABLE_REGISTRY_RESOLVE=true` disables Registry resolution for project creation.

## Node.js package handling (batch `3.182.0-3.198.0`)

The Node.js SDK can use Bun as its package manager and configures ESM automatically unless `--import` or `--require` is supplied explicitly. Entrypoint discovery respects `package.exports`.

## Mock-based SDK testing (batch `3.182.0-3.198.0`)

Go and Python tests can retrieve registered resources from the mock monitor for assertions. Go tests can inspect the current stack export map with `GetCurrentExportMap`.

## Go policy context (batch `3.182.0-3.198.0`)

The Go Policy SDK exposes a Pulumi `Context` to policy code.

## Recursive installation and Registry deletion (batch `3.199.0-3.214.0`)

`pulumi install` recurses into local packages. Multiple Git components from one repository can be referenced together. `pulumi package delete` removes package versions from the Pulumi Registry, and install/package workflows understand package references in plugins.

## Component versions and initialization (batch `3.199.0-3.214.0`)

Local Node.js components use the version from `package.json` instead of `0.0.0`. Python component providers can set their version. A Node.js component resource's `initialize` method receives resource options, name, and type.

## Component inputs in state (batch `3.199.0-3.214.0`)

Go and Node.js components send their inputs to the engine for diffing and state storage, matching Python. Node.js can opt out with `PULUMI_NODEJS_SKIP_COMPONENT_INPUTS`.

## Python 3.14 and generated project manifests (batch `3.199.0-3.214.0`)

The Python SDK supports Python 3.14 and requires `grpcio>=1.75.1` on that runtime. For uv and Poetry projects, `pulumi new --generate-only` creates `pyproject.toml`.

Looking up a missing `StackReference` output in Python returns missing-output behavior without raising the former exception.

## Output-only generated functions (batch `3.199.0-3.214.0`)

Schema functions can set `OutputStyleOnly` to generate only the output-form function and suppress the corresponding plain function.

## CLI and plugin version contracts (batch `3.214.1-3.228.0`)

Projects declare `requiredPulumiVersion` in `Pulumi.yaml`, with language-specific runtime checks. Plugins can declare their supported CLI range. In `PulumiPlugin.yaml`, `pulumiVersionRange` was renamed to `requiredPulumiVersion`; `ProviderHandshakeResponse.pulumi_version_range` was removed.

## Bun native runtime (batch `3.214.1-3.228.0`)

The bundled `pulumi-language-bun` plugin runs Pulumi programs, plugins, debuggers, and policy packs natively under Bun. Do not confuse this with selecting Bun as a Node.js package manager.

## Package and Registry workflows (batch `3.214.1-3.228.0`)

Unqualified package names resolve through the Pulumi Cloud Registry by default. Component workflows support private packages as local dependencies. Publishing accepts Azure DevOps Git URLs. `pulumi schema check` accepts source-based packages, and `package add`/`package get-schema` install dependencies needed by source packages.

## Component schema inference and option propagation (batch `3.214.1-3.228.0`)

Node.js component schema inference understands enums, `Partial<T>`, and `Required<T>`. Replacement triggers pass through remote-component `Construct` calls.

## .NET codegen package migration (batch `3.214.1-3.228.0`)

Provider tooling must migrate from `github.com/pulumi/pulumi/pkg/v3/codegen/dotnet` to `github.com/pulumi/pulumi-dotnet/pulumi-language-dotnet/v3/codegen`. The old package is deprecated and scheduled for removal.

## Lockfile-aware Python and Go targets (batch `3.214.1-3.228.0`)

Python toolchain selection detects lockfiles and reads Poetry and uv lockfiles when calculating program dependencies. Generated Go programs and SDK modules target Go 1.25; Automation API supports Go 1.26.

## Runtime-free bootstrapping (batch `3.229.0-3.248.0`)

Pulumi projects can omit a runtime. `pulumi project new -y` writes a minimal project without a template, `pulumi new` aliases it, and Node.js consumers can run the CLI through `npx pulumi`.

## Recovering failed outputs (batch `3.229.0-3.248.0`)

Node.js and Python provide `Output.recover` for catching and recovering from exceptions raised during output resolution.

## Node.js and TypeScript compatibility (batch `3.229.0-3.248.0`)

The Node.js SDK test matrix includes Node.js 26 and drops Node.js 20. TypeScript 6 is accepted as a peer dependency. Newly generated TypeScript projects set both `module` and `moduleResolution` to `nodenext`.

## Package bootstrapping (batch `3.229.0-3.248.0`)

`pulumi package new` bootstraps a package from a template. `pulumi package add --language` works outside a Pulumi project or plugin. Third-party conversion resolves provider plugins through the Pulumi Registry.

## Native async Python entrypoints (batch `3.249.0-3.254.0`)

The Python SDK provides `pulumi.run` for natively awaited program entrypoints. The async entrypoint may return stack outputs.

## Current Node.js installation controls (batch `3.249.0-3.254.0`)

The Node.js SDK requires Node.js 22 or later and supports pnpm 11. Set the Node.js runtime option `production` in `Pulumi.yaml` to make `pulumi install` use the package manager's production mode and skip `devDependencies`.

## Extension package generation (batch `3.249.0-3.254.0`)

SDK and program generation supports extension-parameterized packages. The HCL runtime exists, but converting a Terraform program to the `hcl` target is rejected.

## Extension package installation and names (batch `3.255.0-3.258.0`)

Package commands accept `--extension` for extension-parameterized packages. Entries recorded this way in `Pulumi.yaml` are restored by `pulumi install`. Generated resources and functions use the extension package's own package name rather than the base provider's name.

## Component providers for invokes (batch `3.255.0-3.258.0`)

An invoke parented to a component resolves its provider from the parent's `providers` option. PCL applies a component block's providers to its resources and invokes, and generated Node.js, Go, and Python code parents component invokes accordingly.

## Go output invokes (batch `3.255.0-3.258.0`)

Generated Go output-form invokes pass unresolved arguments into the core SDK for dependency inference. SDKs generated with this contract require Pulumi SDK v3.255.0 or later.

## Python toolchain and Automation API (batch `3.255.0-3.258.0`)

For uv projects, `UV_PROJECT_ENVIRONMENT` overrides the virtual-environment path used by Pulumi. Python Automation API `preview_refresh` and `preview_destroy` methods accept a `program` argument.
