# Provider and Protocol Development

## Configuration and context

Provider `Configure` receives the provider resource URN and ID. Explicit
providers receive `DiffConfig` for replacement decisions just as default
providers do. Go `AnalyzerResourceOptions` has `Parent`, and resource transforms
receive the parent URN (batch `3.145.0-3.159.0`).

Node.js provider constructors receive `ignoreChanges`, `replaceOnChanges`,
`customTimeouts`, `retainOnDelete`, and `deletedWith`. Provider resources support
`EnvVarMappings` to rewrite environment variables before forwarding them.

## Invokes and calls

Go, Node.js, and Python do not invoke a provider while resource dependencies are
unknown. Node.js and Python wait for resource dependencies in inputs; their plain
invoke APIs keep accepting output arguments for compatibility.

Output-form invokes in Go, Node.js, Python, and PCL explicitly declare resource
dependencies, including remote-component children, so preview yields unknown
until creation completes. Go infers dependencies from arguments. A component's
`providers` option applies to its parented invokes as well as its resources.

Provider invokes receive a `preview` flag. Methods may return scalar values;
Go/Python generation supports them and Node.js generation uses `callSingle`.
Go program generation can emit `Call`, and provider references for calls are
carried through `__self__`.

## Recovery and hooks

Providers can request a default refresh of affected resources after a partial
failure; engine support arrived in 3.178.0. All provider errors are forwarded to
error hooks for retry. Provider implementations in Node.js and Python have
cancel handlers.

## RPC changes

`StreamInvoke` was removed from the Provider service in 3.161.0. Do not retain
it in providers or protocol clients.

The provider protocol and schema add streaming `ResourceProvider.List`, exposed
through Go's `plugin.Provider`. `LanguageRuntime.RunPlugin2` is bidirectional
streaming. Bun, Go, Node.js, and Python connect cancellation to language-host
runs, and hosts send `Cancel` while closing plugins. `Language.Template` is
available for language hosts.

## Handshake and host contracts

Provider handshakes may advertise schema-loader, package-resolver, and mapper
service addresses. CLI-launched providers receive the active login in
`PULUMI_API` and `PULUMI_ACCESS_TOKEN`.

Go `plugin.Host` is workspace-stateless. Boot and resolution APIs accept
`plugin.Context`; plugin-loading functions dropped the `name` argument.
`Configure` and `DiffConfig` require a resource `Type`, and PCL/schema binding
requires an explicit schema loader (batch `3.229.0-3.248.0`).

Projects declare `requiredPulumiVersion` in `Pulumi.yaml`; Node.js exposes
`requirePulumiVersion`, Python `require_pulumi_version`, Go
`CheckPulumiVersion`, and generated .NET `RequirePulumiVersion`. Plugins declare
their CLI range with `requiredPulumiVersion` in `PulumiPlugin.yaml`; the old
`pulumiVersionRange` key and `ProviderHandshakeResponse.pulumi_version_range`
field are removed.

## Schema authoring

Provider aliases may be written as type-token strings:

```json
{ "aliases": ["pkg:index:OldResource"] }
```

Schema names cannot contain whitespace/control characters or conflict with
module paths. `pulumi` and `input` are reserved package names, and a module below
the index module is a strict binding error. Schemas support extension
parameterization, string-enum provider outputs, and functions with
`multiArgumentInputs` in Go/Python generation.

SDK generation supports references into parameterized and third-party packages.
On the wire, `ResourceReference` includes `Name` and `Type`. State converters
receive schema-loader and package-resolver targets and can request named-
ecosystem mappings.

## Source and plugin development

Plugin URLs can resolve through the Registry, while `pulumi install --file`
bypasses registry resolution. `pulumi plugin run` starts a local binary. Attach a
debugger to a source plugin with exactly `--attach-debugger plugin=<name>`.
Package commands can use `--server <URL>` to address a plugin server directly.
