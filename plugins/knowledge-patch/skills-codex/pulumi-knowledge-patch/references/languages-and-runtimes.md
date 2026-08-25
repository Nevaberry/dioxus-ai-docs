# Languages and Runtimes

## Runtime baselines

The Node.js SDK raised its floor to Node.js 20 in batch `3.160.0-3.181.0`, then
to Node.js 22 in `3.249.0-3.254.0`. The current test matrix includes Node.js 26
and no longer includes Node.js 20. TypeScript 6 is accepted as a peer dependency,
and newly generated TypeScript projects use `nodenext` for both `module` and
`moduleResolution`. Node.js supports pnpm 11.

Generated Go programs and the Go SDK first moved to Go 1.23, then to Go 1.25;
Automation API supports Go 1.26. Generated Go output-form invokes that delegate
unresolved inputs to the core SDK require Pulumi SDK v3.255.0 or later.

Python supports Python 3.14 and needs `grpcio>=1.75.1` there. `pulumi new
--generate-only` creates `pyproject.toml` for uv and Poetry projects. Java SDK
1.0 provides the full programming model, type safety, and the Java LTS releases
supported at its launch (batch `release-notes-117`).

## Node.js and Bun

The Node.js SDK can use Bun as a package manager and configures ESM automatically
unless `--import` or `--require` is explicit. Entrypoint lookup respects
`package.exports`. The `production` runtime option in `Pulumi.yaml` causes
`pulumi install` to skip `devDependencies` using the package manager's production
mode.

Bun is also a distinct native Pulumi runtime through bundled
`pulumi-language-bun`; it runs programs, plugins, debuggers, and policy packs.
Do not confuse the runtime with choosing Bun only as Node's package manager.

## Python toolchains and entrypoints

Dynamic providers work with Poetry and uv. Plugin/package discovery supports uv,
and `RunPlugin` uses a virtual environment by default. Lockfile detection chooses
the Python toolchain and reads Poetry and uv locks for program dependencies.
`UV_PROJECT_ENVIRONMENT` overrides the virtual-environment path Pulumi uses.

`pulumi.run` accepts a natively awaited Python entrypoint and may receive its
stack outputs as the return value. Python Automation API `preview_refresh` and
`preview_destroy` accept a `program` argument.

Experimental component helpers moved from
`pulumi.provider.experimental.provider` to
`pulumi.provider.experimental.component`; a new general provider interface now
uses the old provider namespace. Python component providers can run without a
bootstrap. They support resource references, enum inference and references,
`@pulumi.type_token`, and the static `pulumi_type` property.

Missing Python `StackReference` outputs no longer raise. Undecryptable
stack-reference outputs are elided. Python dynamic-provider `read()` may return
inputs so refresh preserves them for subsequent diffs.

## Go APIs

Go has deferred outputs, so code can create an output handle before setting the
value that resolves it. `property.Value` is immutable; `property.Path` and
`property.Map.Delete` provide structured access and removal. Workspace plugin
lookup/path and APIs that create `plugin.Context` accept `context.Context`.

Go and Python tests can query resources registered with their mock monitor; Go
tests can inspect the current stack export map through `GetCurrentExportMap`.
Go's Policy SDK gives policy code a Pulumi `Context` and supports full-stack
validation through `policyx.NewStackValidationPolicy` and `AnalyzeStack`.

## Cross-language runtime introspection

.NET, Go, Java, Node.js, Python, and YAML can locate the project root. Go and
Python expose `pulumiResourceName` and `pulumiResourceType` for a resource's
runtime name and token.

Provider methods may return scalars instead of objects. Go and Python code
generation support this, while Node.js generation uses `callSingle`. Node.js
provider constructors receive `ignoreChanges`, `replaceOnChanges`,
`customTimeouts`, `retainOnDelete`, and `deletedWith` rather than dropping them.

## Outputs, invokes, and hooks

Node.js and Python provide `Output.recover` to handle exceptions during output
resolution. Resource hook secrets arrive as `Output` values in both languages.
Python offers decorator forms of resource and error hooks. Output-form invokes
in Go, Node.js, Python, and PCL declare dependencies; Go also infers them from
arguments, and its generated SDK passes unresolved arguments to the core SDK.

Plain Node.js and Python invokes retain compatibility with output arguments.
Invokes wait for resource dependencies found in inputs; Go, Node.js, and Python
avoid provider calls while those dependencies are unknown.

## YAML behavior

Pulumi YAML enables views by default. It accepts `object` configuration and
parses the value as an object. YAML `null` read as an empty string produces a
warning; the temporary typed-config behavior introduced in 3.170.0 was reverted
in 3.174.0.
