# State, Import, and Resource Lifecycle

Use this reference for resource safety, replacements, hooks, imports, state repair, checkpoints, direct-resource operations, and Automation API lifecycle controls.

## Inherited safety options (batch `3.145.0-3.159.0`)

An explicit `false` on a child overrides inherited `protect: true` and `retainOnDelete: true`. A protected-delete error no longer stops unrelated deployment operations from continuing.

Autonaming configuration is stable as of 3.146.0. Its strategy applies to custom resources, not component resources.

## Bulk state deletion (batch `3.145.0-3.159.0`)

`pulumi state delete --all` removes every resource entry from stack state in one repair operation. Export and secure a checkpoint first, confirm the backend and stack, and preview afterward.

## Reference validation and state protection (batch `3.160.0-3.181.0`)

Unresolved references are validation errors. Use `--allow-dangling-references` only when intentionally operating on state that contains them. `pulumi state protect <URN>` sets protection directly in state.

## Import and update together (batch `3.160.0-3.181.0`)

A resource with the `import` option can be adopted and updated in one deployment, and its import ID remains through the update. Program generation for .NET, Go, Node.js, and Python emits the resource import option.

## Undecryptable stack references (batch `3.160.0-3.181.0`)

`StackReference` outputs that cannot be decrypted are elided rather than exposed as usable values.

## Resource lifecycle hooks (batch `3.182.0-3.198.0`)

The engine and Go, Node.js, and Python SDKs support resource hooks. Hooks propagate through component `Construct`, resource transforms can set them, and `ResourceHookArgs` includes resource type and name. Destroy operations involving delete hooks must run the program; after-delete hooks also run for component resources.

## Taint and untaint (batch `3.182.0-3.198.0`)

`pulumi state taint <URN>` marks a resource for forced replacement on the next update. `pulumi state untaint <URN>` removes that marker.

## Automation API operation controls (batch `3.182.0-3.198.0`)

Go, Node.js, and Python inline programs can request run-program behavior for refresh and destroy. Node.js adds `previewDestroy` for a dry-run destroy. Python preview exposes its JSON option, and Python command options accept `on_error` callbacks for incremental stderr consumption.

## Checkpoint, removal, and import behavior (batch `3.182.0-3.198.0`)

The CLI reads and writes v4 checkpoints and deployments. On DIY backends, `pulumi stack rm --remove-backups` removes stack backups as well. Imports converted from `--from` state files always generate resource declarations.

## Missing old values in ignoreChanges (batch `3.182.0-3.198.0`)

If an `ignoreChanges` path is absent from old state, the engine uses the new value at that path rather than raising an error.

## Replacement dependencies with replaceWith (batch `replace-with`)

Starting in v3.207.0, a custom resource can set `replaceWith` to other resources. Replacing a referenced target replaces the resource carrying the option even without an ordinary dependency edge. These relationships are transitive and can be mutual to replace a group together.

Go, Python, Node.js, and Java support the option in this release; C# and YAML support was still forthcoming.

## Arbitrary replacement triggers (batch `3.199.0-3.214.0`)

The `replacement_trigger` resource option forces replacement whenever its value changes between runs. Engine and Go support arrived in 3.208.0, followed by Node.js and Python during this batch.

## Stash and non-finite state values (batch `3.199.0-3.214.0`)

The builtin `Stash` resource stores an arbitrary value in state. Resource state can contain floating-point `NaN` and infinity values.

## Hidden diffs (batch `3.199.0-3.214.0`)

Resource options can hide selected diffs: Go `HideDiffs`, Node.js `hideDiffs`, and Python `hide_diffs`.

## Secrets in resource hooks (batch `3.199.0-3.214.0`)

Node.js and Python hooks receive secrets as secret `Output` values rather than an exposed internal representation.

## Imports from transforms (batch `3.199.0-3.214.0`)

The engine honors a resource `import` option set by a resource transform.

## OnError retry hooks (batch `3.214.1-3.228.0`)

The engine and Go, Node.js, and Python SDKs support `OnError` resource hooks for custom retry policies.

## Automation API cancellation (batch `3.214.1-3.228.0`)

The generated low-level Node.js Automation API interface exposes a `cancel` command.

## Dependency-safe bulk state deletion (batch `3.214.1-3.228.0`)

`pulumi state delete` accepts multiple URNs in one invocation and orders their removal safely according to dependencies.

```shell
pulumi state delete '<URN-1>' '<URN-2>'
```

## Direct resources before stateful mode (batch `3.229.0-3.248.0`)

`pulumi do` added `create`, `patch`, and `delete`. In this batch those operations required `--stateless` to use direct-provider behavior because stateful implementation had not yet landed. `--provider` could take provider configuration from existing provider state. Project-scoped PCL inputs received the selected stack's organization and short name.

Later behavior adds stateful operations; do not carry the old `--stateless` requirement into those workflows.

## Snippets and direct-resource state (batch `3.229.0-3.248.0`)

Engine snippets are PCL blocks stored in state to track ad-hoc resources. Deployment tooling can target them separately from ordinary resource URNs.

## Resource hooks and read timeouts (batch `3.229.0-3.248.0`)

PCL declares resource hooks, Python supports decorator-based resource and error hooks, and hook calls receive resource options. A failing after-hook fails the deployment. Provider errors are forwarded to error hooks for retry. `customTimeouts.read` controls resource-read timeouts.

## Imports with providers and rich values (batch `3.229.0-3.248.0`)

Import files can define provider resources alongside imported resources. Generated import programs preserve asset, archive, and resource-reference values inside maps and arrays. Map keys containing template sequences are HCL-escaped.

## Stateful direct-resource operations (batch `3.249.0-3.254.0`)

`pulumi do` supports stateful create and delete, plus `upsert` for stateful create-or-update. Numeric and boolean command inputs may be expressions.

## Automation API import (batch `3.249.0-3.254.0`)

Generated Node.js, Python, and Go Automation APIs expose import operations. Go Automation API preview-refresh and refresh can pass `--import-pending-creates`.

## Importing supplied state directly (batch `3.249.0-3.254.0`)

An import-file resource can include inputs and outputs. When outputs are present, Pulumi imports that state directly and skips the provider read. Converter and import-file workflows support parameterized and extension-parameterized providers.

## State converter hierarchy and providers (batch `3.249.0-3.254.0`)

`ResourceImport` includes parent and properties for hierarchy and filtering. A state converter can return explicit provider resources, associate imports with them, receive a schema-loader target, and request mappings for a named ecosystem.

## Corrected failure, diff, and import semantics (batch `3.249.0-3.254.0`)

Failed resource registrations create faulted outputs rather than unknown outputs. Diffs nested inside `Output` values are no longer ignored. Importing with an ID different from the provider's canonical ID no longer causes deletion on a later update.

## Passphrase-free non-secret reads (batch `3.249.0-3.254.0`)

Reading non-secret stack outputs and running `pulumi about` no longer require the passphrase for a passphrase-encrypted stack. Secret reads still require the relevant decryption capability.

## Existing resources in pulumi do (batch `3.255.0-3.258.0`)

`pulumi do --resources` enables expressions to reference resources already in stack state. Identifiers are assigned automatically, and `pulumi do show-resources` lists them. Stateful operations accept `--provider`; stateful `patch` overlays supplied inputs on the existing snippet.

Outside a project, `pulumi do` falls back to an automatically created project and stack under `PULUMI_HOME`.

## Non-UTF-8 state values (batch `3.255.0-3.258.0`)

Strings containing non-UTF-8 bytes can flow between providers, engine operations, state, and opted-in languages. Go and PCL are the initial language paths. Diffs and JSON render these strings as a base64-tagged `b"..."` representation.

## One-operation protection override (batch `3.255.0-3.258.0`)

`pulumi up`, `preview`, and `destroy` accept `--ignore-protect`. It permits protected resources to be deleted for that operation without first editing protection in state. Treat it as explicit authorization to bypass a durable safety control.

## State-converter and import data (batch `3.255.0-3.258.0`)

State converters can return resource inputs and outputs from `ConvertState` and receive a package resolver through `resolver_target`. Generated import files include explicit provider resources. `pulumi preview --import-file` no longer emits unknown values, and `pulumi import` rejects import files containing unknowns.

## Individual state inspection (batch `3.255.0-3.258.0`)

`pulumi state get <URN>` displays one resource from stack state.
