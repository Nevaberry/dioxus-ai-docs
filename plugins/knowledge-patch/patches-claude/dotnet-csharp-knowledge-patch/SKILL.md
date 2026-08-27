---
name: dotnet-csharp-knowledge-patch
description: .NET and C#
version: null
license: MIT
metadata:
  author: Nevaberry
---


# .NET and C# Knowledge Patch

Use this skill when changing, reviewing, or troubleshooting C# language features,
.NET runtime behavior, libraries, SDK commands, packaging, deployment, or servicing.

## Start Here

Before applying guidance:

1. Inspect the project file, `global.json`, `Directory.Build.*`, package references,
   publish properties, and container configuration.
2. Identify the target framework, C# `LangVersion`, installed SDK/runtime, workload,
   operating system, architecture, and publish mode.
3. Treat compiler diagnostics, current API signatures, generated assets, and tests as
   authoritative for the exact project configuration.
4. Read the topic reference containing the affected subsystem; many compatibility
   changes are platform- or mode-specific.
5. When upgrading deployed applications, separate SDK selection from runtime and
   container servicing.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Language](references/language.md) | Extension members, `field`, span conversions, lambdas, partial members, assignments, Visual Basic compatibility |
| [Hosting, Platform, and Interop](references/hosting-platform-interop.md) | Hosting, configuration, logging, native libraries, COM, desktop behavior |
| [Runtime, I/O, and Core Libraries](references/runtime-io.md) | Streams, shutdown, core types, globalization, tensors, intrinsics |
| [SDK, CLI, Packaging, and Testing](references/sdk-cli-packaging.md) | CLI behavior, tools, workloads, NuGet, MSBuild, file-based apps, containers, testing |
| [Security and Networking](references/security-networking.md) | Servicing, certificates, post-quantum APIs, AES-KWP, TLS, HTTP, URI, mail |
| [Serialization, Data, and Diagnostics](references/serialization-data-diagnostics.md) | JSON, XML serialization, telemetry, sampling, EF Core filters |

## Breaking Changes and Migration Checks

### Service the runtime before debugging application symptoms

Deployed .NET 10 applications and container bases need the security fixes carried by
runtime 10.0.11. SDK 10.0.400, 10.0.303, and 10.0.111 install that runtime and its
matching ASP.NET Core runtime. See
[Security and Networking](references/security-networking.md#security-servicing).

### Recheck the container base and output format

Default container images use Ubuntu. Audit distribution-specific packages, paths,
and package-manager commands, or pin an intentional base. For SDK container publish,
set `ContainerImageFormat` to `Docker` or `OCI` when the output contract matters.

### Audit native-library lookup

Single-file applications no longer probe the executable directory for native
libraries. `DllImportSearchPath.AssemblyDirectory` searches only the assembly
directory. Make native deployment paths explicit and test the published artifact.

### Audit CLI automation streams and defaults

Non-command output and `dotnet watch` logging go to standard error. `--interactive`
defaults to true in user scenarios. Scripts should parse the intended stream and set
interaction behavior explicitly when prompts are unacceptable.

### Review solution, package, and tool side effects

`dotnet new sln` creates SLNX by default. `dotnet package list` restores, and
`dotnet tool install --local` creates a missing manifest. Ensure automation either
accepts these effects or passes explicit options.

### Harden restore and package metadata

Restore audits transitive dependencies. Versionless `PackageReference` items and
invalid package IDs are errors; pruning and runtime-asset rules can change generated
assets. Do not suppress NU1510 until confirming whether the direct reference is
actually required.

### Revalidate serialization contracts

`System.Text.Json` detects property-name conflicts. `XmlSerializer` includes obsolete
properties instead of ignoring them. Snapshot wire contracts and generated metadata
when moving existing models.

### Recheck overload resolution and span conversions

C# 14's first-class span conversions can select a different overload and affect
generic inference. Compile ambiguous call sites under the project's actual language
version, especially where array, `Span<T>`, and `ReadOnlySpan<T>` overloads coexist.

### Account for hosting lifecycle changes

All of `BackgroundService.ExecuteAsync` runs as a `Task`; configuration retains null
values. Review startup assumptions, synchronous pre-await work, and providers that
formerly treated null as absent.

### Review runtime I/O and shutdown assumptions

`BufferedStream.WriteByte` does not implicitly flush, and the runtime does not install
default termination-signal handlers. Add explicit flushing and application-owned
signal/lifecycle handling where correctness depends on either behavior.

### Check platform-specific networking behavior

Trimmed publications disable HTTP/3 by default, browser clients stream responses by
default, and `MailAddress` rejects consecutive dots. macOS TLS 1.3 requires an
explicit Network.framework opt-in with additional behavioral tradeoffs.

### Re-test Windows desktop ambiguity and failures

Mixed WPF/Windows Forms projects must qualify `MenuItem` and `ContextMenu`. WPF now
rejects some invalid markup/resource patterns, and some `System.Drawing` failures use
`ExternalException` rather than `OutOfMemoryException`.

## High-Value Language Features

### Use extension blocks for related members

A named receiver defines instance extension properties or methods; omitting its name
permits static members and operators.

```csharp
public static class SequenceExtensions
{
    extension<T>(IEnumerable<T> source)
    {
        public bool IsEmpty => !source.Any();
    }
}
```

### Add validation with `field`

The contextual `field` token accesses a compiler-synthesized backing field. If the
type already has an identifier named `field`, use `@field` or `this.field` for that
existing member.

```csharp
public string Message
{
    get;
    set => field = value ?? throw new ArgumentNullException(nameof(value));
}
```

### Assign through null-conditionals

`?.` and `?[]` can be assignment targets. The right-hand side runs only for a
non-null receiver; `++` and `--` are not supported in this form.

```csharp
customer?.Order = GetCurrentOrder();
customer?.Balance += payment;
```

### Use partial constructors and events deliberately

Provide exactly one defining and one implementing declaration. Only the implementing
constructor may specify `this()` or `base()`; an implementing partial event supplies
`add` and `remove` accessors.

## High-Value Library Features

### Prefer algorithm-specific certificate lookup

Use the `HashAlgorithmName` overload of `FindByThumbprint` to avoid SHA-1-only lookup
and same-length hash ambiguity. Choose PFX export parameters according to the required
compatibility/security tradeoff.

### Enable strict JSON intentionally

Set `AllowDuplicateProperties = false` to reject duplicate names. The
`JsonSerializerOptions.Strict` preset additionally rejects unmapped members, retains
case-sensitive binding, and enforces nullable annotations and required constructor
parameters.

### Preserve references in generated JSON contexts

Set `JsonSourceGenerationOptionsAttribute.ReferenceHandler` to a
`JsonKnownReferenceHandler`, such as `Preserve`, when source-generated serialization
must handle cycles.

### Treat tensor slices as views

Tensor slicing returns a non-copying view whose later reads observe underlying
storage. Copy explicitly when snapshot semantics are required.

### Use named EF Core filters for selective disabling

Define multiple named filters per entity when callers must disable one filter without
turning off all filters for that entity.

## High-Value SDK Workflows

### Run a tool once

`dotnet tool exec` downloads and runs without installing. Pin `package@version` for
repeatability, account for the first-download prompt, and remember that a nearby local
tool manifest can supply the version.

### Publish file-based applications carefully

`dotnet publish app.cs` defaults to native AOT. Add
`#:property PublishAot=false` when dependencies are incompatible. File-based apps can
also use `#:project` and executable extensionless shebang files.

### Generate CLI integration metadata

Pass `--cli-schema` to a CLI command for a JSON description of arguments, options,
and subcommands. Use `dotnet completions script` for native shell completions.

### Select the test runner explicitly

To route `dotnet test` through Microsoft.Testing.Platform, select that runner in
`global.json`; do not infer the runner solely from test package references.
