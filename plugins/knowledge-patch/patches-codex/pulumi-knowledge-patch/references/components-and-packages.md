# Components and Packages

## Cross-language component packages

A component source directory becomes a cross-language package when it contains
`PulumiPlugin.yaml`; same-language-only components do not need the file. Pulumi
analyzes exposed components, derives a schema, and generates consumer SDKs,
including Pulumi YAML (batch `components-2025`).

TypeScript exposes every exported component class and YAML needs no entrypoint.
Other runtimes start a provider host:

- Python uses `_main_.py` and passes classes to
  `pulumi.provider.experimental.component_provider_host`.
- Go builds with `infer.NewProviderBuilder().WithNamespace(...).WithComponents`
  from `pulumi-go-provider` v1, then calls `provider.Run`.
- .NET returns `Pulumi.Experimental.Provider.ComponentProviderHost.Serve(args)`
  from `Program.Main`.
- Java starts `com.pulumi.provider.internal.ComponentProviderHost` with the
  package to scan.

## YAML-authored components

Pulumi YAML defines reusable components under top-level `components`; each
component declares inputs, child resources, and outputs. Use another language
for logic such as conditionals or map merges.

```yaml
runtime: yaml
components:
  SecureBucket:
    inputs:
      bucketName: { type: string }
    resources:
      bucket:
        type: aws:s3/bucketV2:BucketV2
        properties: { bucket: "${bucketName}" }
    outputs:
      bucketName: "${bucket.id}"
```

## Installing and restoring components

`pulumi package add` accepts Git sources pinned to tags and relative or absolute
component directories. Private repositories use tokens from the environment.
The command records the source under `packages` in `Pulumi.yaml`; `pulumi
install` restores all declarations and generates local SDKs. Commit those SDKs
or require every checkout to restore them.

Local paths must keep `./` or `../`; unprefixed sources are no longer assumed to
be paths. `pulumi install` recurses into local packages. Multiple components in
one Git repository can be referenced together. Git plugins accept HTTPS,
subdirectories, and short commits; an unversioned source chooses its latest
version. `GITHUB_TOKEN` and `GITLAB_TOKEN` are recognized. Plugin namespaces are
inferred and cannot be overridden through `PulumiPlugin.yaml` as of 3.159.0.

## Registries and templates

`pulumi package add` accepts registry identifiers. `pulumi new` accepts qualified
registry template names and lists published templates; private Registry template
resolution does not require `PULUMI_EXPERIMENTAL`, though it can be disabled by
`PULUMI_DISABLE_REGISTRY_RESOLVE=true`. Unqualified package names resolve through
the Pulumi Cloud Registry by default.

Pulumi Cloud templates are valid `pulumi new` sources. `pulumi package publish`
was experimental in 3.158.0 and became stable in 3.166.0; `pulumi template
publish`, added in 3.180.0, remained experimental. `pulumi package delete`
removes Registry versions. Package references may appear in plugins.

Private packages can be local dependencies. Publishing accepts Azure DevOps Git
URLs. Source-based packages work with `pulumi schema check`, and package add/get
schema install package dependencies. `pulumi package new` bootstraps from a
template. `pulumi package add --language` works outside a project or plugin.

## Extension packages and direct servers

Package commands accept `--extension`; declarations written to `Pulumi.yaml`
are restored by `pulumi install`. Generated tokens use the extension's package
name, not the base provider name. SDK and program generation supports
extension-parameterized packages.

`--server <URL>` on package add, publish, get-schema, get-mapping, gen-sdk, info,
and schema check bypasses package resolution and treats the URL as the plugin
download URL. Package add persists that server in `Pulumi.yaml` (batch
`3.255.0-3.258.0`).

The default package-registry source is private. Plugin download URLs may resolve
through the Registry; `pulumi install --file` bypasses it. Go's direct-repository
installer supports private GitHub and GitLab instances. `pulumi plugin run`
executes a local plugin binary; source debugging uses the exact form
`--attach-debugger plugin=<name>`.

## Component metadata and state

Local Node.js components use the version from `package.json`, not `0.0.0`.
Python component providers can set their version. Node.js component
`initialize` receives resource options, name, and type.

Go and Node.js components send inputs to the engine for state and diffs, matching
Python; set `PULUMI_NODEJS_SKIP_COMPONENT_INPUTS` to opt Node.js out. Node.js
schema inference understands enums, `Partial<T>`, and `Required<T>`.
Replacement triggers pass through remote `Construct` calls.

Component provider invokes inherit a provider from the parent's `providers`
option. PCL applies component providers to both resources and invokes, and
generated Node.js, Go, and Python code parents invokes accordingly.
