# Providers, Schemas, PCL, and Protocols

Use this reference for provider and plugin authors, schema maintainers, code generators, PCL tooling, invokes, component provider behavior, and language/provider protocol clients.

## Conversion and parameterized imports (batch `3.145.0-3.159.0`)

`pulumi convert --from=<plugin>@<version>` pins the converter plugin. Conversion can bridge Terraform providers automatically, and PCL generation understands `try` and `can`. `pulumi import` accepts resources supplied by parameterized packages and providers.

## Provider-schema alias shorthand (batch `3.145.0-3.159.0`)

A provider schema can express aliases directly as an array of type-token strings instead of alias objects:

```json
{"aliases": ["pkg:index:OldResource"]}
```

## Provider, analyzer, and transform context (batch `3.145.0-3.159.0`)

Provider `Configure` receives the provider resource's URN and ID. Explicit providers receive `DiffConfig` for replacement decisions, matching default providers. Go `AnalyzerResourceOptions` includes `Parent`, and resource transforms receive the parent URN.

## Invoke dependency behavior (batch `3.145.0-3.159.0`)

Go, Node.js, and Python avoid provider invokes while resource dependencies are unknown. Node.js and Python also wait for dependencies carried in input properties. Plain Node.js and Python invokes continue accepting output arguments for backward compatibility.

## Git plugin sources (batch `3.145.0-3.159.0`)

Git plugins accept HTTPS, repository subdirectories, and short commit hashes. An unversioned source resolves the latest version. `GITHUB_TOKEN` and `GITLAB_TOKEN` are recognized. Namespace inference is authoritative; as of 3.159.0, `PulumiPlugin.yaml` cannot override a Git plugin's inferred namespace.

## Local plugin development (batch `3.160.0-3.181.0`)

`pulumi plugin run` executes a local binary plugin. Debug a source-based plugin with the exact flag form `--attach-debugger plugin=<name>`.

## Provider-directed recovery refreshes (batch `3.160.0-3.181.0`)

The provider protocol can ask the engine to refresh affected resources by default after a partial failure. Engine support for honoring the request arrived in 3.178.0.

## Scalar provider method returns (batch `3.160.0-3.181.0`)

Provider methods can return scalar rather than object values. Go, Python SDK generation, and Node.js program generation support the shape; Node.js uses the `callSingle` SDK path.

## Removed streaming invoke RPC (batch `3.160.0-3.181.0`)

`StreamInvoke` was removed from the Provider service in 3.161.0. Provider implementations, host adapters, and protocol clients must remove dependencies on that RPC.

## Node.js provider resource options (batch `3.160.0-3.181.0`)

Node.js provider constructors receive `ignoreChanges`, `replaceOnChanges`, `customTimeouts`, `retainOnDelete`, and `deletedWith` instead of silently dropping them.

## Views enabled by default (batch `3.160.0-3.181.0`)

Engine support for views is enabled by default as of 3.176.0. Pulumi YAML enables views by default as of 3.177.0.

## Python provider namespaces and types (batch `3.160.0-3.181.0`)

Component-provider helpers moved to `pulumi.provider.experimental.component`; a general provider interface now occupies `pulumi.provider.experimental.provider`. Component providers can run bootstrap-less and support resource references, enum inference, and enum references. `@pulumi.type_token` and `pulumi_type` expose resource type tokens.

## Resource hooks in Construct and transforms (batch `3.182.0-3.198.0`)

Go, Node.js, and Python resource hooks pass through component `Construct` calls and can be set by resource transforms. `ResourceHookArgs` includes resource type and name. Delete hooks require the program during destroy, and after-delete hooks run for components.

## Provider invokes in preview (batch `3.199.0-3.214.0`)

Provider invokes receive a `preview` flag so implementations can distinguish preview calls. The language protocol also adds a `Language.Template` RPC.

## Output-only schema functions (batch `3.199.0-3.214.0`)

An `OutputStyleOnly` function suppresses generation of the plain function and emits only its output-form variant.

## Plugin CLI version contracts (batch `3.214.1-3.228.0`)

Plugins can declare a supported CLI version range. The `PulumiPlugin.yaml` key is `requiredPulumiVersion`, renamed from `pulumiVersionRange`. `ProviderHandshakeResponse.pulumi_version_range` has been removed.

## Secret invoke propagation (batch `3.214.1-3.228.0`)

If an invoke has a secret input but the provider does not support secrets, the engine marks the invoke outputs secret. The general CLI secrets filter no longer interprets case-insensitive `true` and `false` literals as filter values.

## Provider inheritance and environment remapping (batch `3.214.1-3.228.0`)

Resource registration inherits the `provider` option without incorrectly carrying default providers across packages. Provider resources accept `EnvVarMappings` to remap environment variables before forwarding them to the provider.

## Dynamic-provider inputs after refresh (batch `3.214.1-3.228.0`)

Node.js and Python dynamic-provider `read()` methods can return inputs so refreshed state preserves the input set required for later diffs.

## Component schema and replacement propagation (batch `3.214.1-3.228.0`)

Node.js component inference understands enums, `Partial<T>`, and `Required<T>`. Replacement triggers propagate through remote-component `Construct` calls.

## PCL secrets, ranges, and package labels (batch `3.214.1-3.228.0`)

PCL represents configuration values that must be read as secrets, supports resource ranges, and typechecks component inputs. Labels on `package` blocks are deprecated.

## Cross-package code generation and references (batch `3.214.1-3.228.0`)

SDK generation supports type references into parameterized and third-party packages. Go program generation can emit provider `Call` requests. The engine populates `Name` and `Type` in wire-level `ResourceReference` values and honors provider references passed through a call's `__self__` argument.

## .NET codegen module migration (batch `3.214.1-3.228.0`)

Move provider tools from `github.com/pulumi/pulumi/pkg/v3/codegen/dotnet` to `github.com/pulumi/pulumi-dotnet/pulumi-language-dotnet/v3/codegen`; the former package is deprecated and scheduled for removal.

## New PCL resource forms (batch `3.229.0-3.248.0`)

PCL supports parameterized providers and `read` blocks. A read block finds a resource by ID and queries it without registering it. Engine snippets are PCL blocks retained in state to track ad-hoc resources.

## PCL typing and evaluation (batch `3.229.0-3.248.0`)

Integer literals, list and tuple indices, and the `element` and `range` builtins use integer types rather than number types. Maps of resources created with `range` can be indexed by key.

PCL applies resource-schema defaults, resolves invoke-derived config defaults to the invoke result, and populates schema-declared nested output fields so optional objects can be traversed safely.

## On-demand HCL (batch `3.229.0-3.248.0`)

The HCL language runtime is downloaded on demand instead of bundled. `pulumi convert --from hcl` installs its converter automatically.

## Hooks and read timeouts (batch `3.229.0-3.248.0`)

PCL declares resource hooks, and Python has function-decorator forms for resource and error hooks. Hook calls receive resource options. A failing after-hook fails the deployment. Every provider error is forwarded to error hooks for retry. `customTimeouts` includes `read` for resource-read deadlines.

## Provider and language protocol additions (batch `3.229.0-3.248.0`)

The provider protocol and schema add streaming `ResourceProvider.List`, exposed by Go `plugin.Provider`. `LanguageRuntime` adds the bidirectional-streaming `RunPlugin2` RPC. Node.js and Python providers add cancel handlers; Bun, Go, Node.js, and Python propagate cancellation to language-host runs, and hosts send `Cancel` while closing plugins.

## Provider host and handshake changes (batch `3.229.0-3.248.0`)

Provider handshakes can supply schema-loader, package-resolver, and mapper service addresses. CLI-launched providers receive the active login through `PULUMI_API` and `PULUMI_ACCESS_TOKEN`.

Go `plugin.Host` is workspace-stateless; boot and resolution methods take `plugin.Context`. Plugin-loading functions dropped `name`. `Configure` and `DiffConfig` require `Type`, while PCL/schema binding requires an explicit schema loader.

## Provider schema contracts (batch `3.229.0-3.248.0`)

Schema names cannot contain whitespace or control characters, conflict with module paths, or use reserved package names `pulumi` and `input`. A module nested beneath the index module is a strict bind error.

Schemas support extension parameterization and string-enum provider outputs. Go and Python SDK and program generation support functions with `multiArgumentInputs`.

## Package conversion and Registry resolution (batch `3.229.0-3.248.0`)

`pulumi package new` bootstraps a provider package, and `pulumi package add --language` works without a Pulumi project or plugin. Third-party converters resolve provider plugins through the Pulumi Registry.

## Imports with rich values (batch `3.229.0-3.248.0`)

Import files can declare provider resources and link imports to them. Generated programs preserve assets, archives, and resource references nested in maps and arrays, and HCL-escape map keys containing template sequences.

## PCL hooks, functions, and snippets (batch `3.249.0-3.254.0`)

PCL binds `onError` hooks and generates them into Go, Node.js, and Python. A successful hook command retries the failed resource operation. PCL calls `multiArgumentInputs` functions positionally. Engine deployment options target persisted snippets by UUID through `TargetSnippets`.

## Extension packages and HCL conversion (batch `3.249.0-3.254.0`)

SDK and program generators support extension-parameterized packages. The HCL runtime is usable, but conversion from a Terraform program to the `hcl` target is rejected.

## Rich state-converter protocol (batch `3.249.0-3.254.0`)

`ResourceImport` carries parent and properties for hierarchy and property filtering. State converters can return explicit provider resources and associate imported resources with them, receive a schema-loader target, and request mappings for a named ecosystem rather than only their own converter name.

## Extension installation and token namespaces (batch `3.255.0-3.258.0`)

Package commands accept `--extension`, and `pulumi install` restores extension dependencies recorded in `Pulumi.yaml`. Generated resource and function tokens use the extension's package name rather than the base provider's package name.

## Component provider inheritance for invokes (batch `3.255.0-3.258.0`)

An invoke parented to a component selects its provider from the component's `providers` option. PCL applies component providers to resources and invokes. Generated Node.js, Go, and Python code parents component invokes to preserve this inheritance.

## Direct package plugin servers (batch `3.255.0-3.258.0`)

`--server <URL>` bypasses package resolution and uses the URL as the plugin download location for `pulumi package add`, `publish`, `get-schema`, `get-mapping`, `gen-sdk`, `info`, and `pulumi schema check`. When `package add` writes `Pulumi.yaml`, it preserves the server setting.

## Invoke dependency gating (batch `3.255.0-3.258.0`)

Output-form invokes in Go, Node.js, Python, and PCL declare dependencies so the engine can defer invokes that rely on resources or remote-component children still being created. During preview the deferred invoke resolves as unknown. Go also infers dependencies from invoke arguments.

Generated Go output invokes pass unresolved arguments to the core SDK; generated SDKs using this behavior require Pulumi SDK v3.255.0 or later.

## State-converter inputs and outputs (batch `3.255.0-3.258.0`)

`ConvertState` responses can include resource inputs and outputs. Converters receive a package resolver through `resolver_target`. Generated import files include explicit provider resources, `pulumi preview --import-file` no longer emits unknown values, and `pulumi import` rejects import files that contain unknowns.

## Non-UTF-8 protocol values (batch `3.255.0-3.258.0`)

Strings containing non-UTF-8 bytes can pass between providers, the engine, state, and opted-in languages. Go and PCL are the initial supported language paths.
