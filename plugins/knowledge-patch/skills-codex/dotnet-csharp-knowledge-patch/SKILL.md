---
name: dotnet-csharp-knowledge-patch
description: .NET and C#
version: null
license: MIT
metadata:
  author: Nevaberry
---


# .NET and C# Knowledge Patch

Use this skill when writing, reviewing, upgrading, building, testing, publishing,
or operating .NET and C# projects. It is especially useful when an apparently
minor SDK or runtime change alters defaults, overload resolution, serialization,
native loading, CLI output, restore behavior, or container output.

## How to Apply This Patch

1. Inspect the project files, `global.json`, target frameworks, language version,
   package references, runtime identifiers, container bases, and test runner.
2. Treat this as multi-product coverage: match guidance to the actual C# language,
   SDK, runtime, ASP.NET Core, EF Core, desktop, or tooling component in use.
3. Read the relevant reference file before changing code or configuration.
4. Prefer the repository's manifests, tests, and observed behavior if they differ
   from this guidance.
5. For upgrades, audit changed defaults before adopting new APIs.

## Reference Index

| Reference | Topics |
| --- | --- |
| [language.md](references/language.md) | C# language syntax, overload resolution, partial members, and compiler compatibility |
| [runtime-and-io.md](references/runtime-and-io.md) | Core libraries, I/O, diagnostics, tensors, globalization, and intrinsics |
| [sdk-cli-build-and-test.md](references/sdk-cli-build-and-test.md) | SDK and CLI defaults, NuGet, workloads, tools, MSBuild, testing, and servicing |
| [security-networking-and-interop.md](references/security-networking-and-interop.md) | Cryptography, TLS, HTTP, certificates, native libraries, and COM |
| [serialization-hosting-and-data.md](references/serialization-hosting-and-data.md) | JSON, XML, hosting, configuration, logging, and EF Core |
| [deployment-and-ui.md](references/deployment-and-ui.md) | Containers, Native AOT, file-based apps, WPF, Windows Forms, and drawing |

## Upgrade Priorities

### Apply the Security Servicing Release

Update deployed .NET runtimes and refresh container images to receive the current
security fixes. Installing SDK `10.0.400`, `10.0.303`, or `10.0.111` also installs
the matching updated .NET and ASP.NET Core runtimes. See
[sdk-cli-build-and-test.md](references/sdk-cli-build-and-test.md) for the affected
CVE inventory and exact servicing guidance.

### Recheck Container Bases

Default .NET 10 container images use Ubuntu. Do not assume that package names,
filesystem paths, or the package manager match an older base distribution. Pin
the required base image or adapt installation steps. When publishing a console
project, set `ContainerImageFormat` explicitly if downstream tooling requires
Docker or OCI rather than an inferred format.

### Audit Restore and Package Assumptions

Restore audits transitive packages. A versionless `PackageReference` is an error,
direct references removed by pruning raise NU1510, and `PrunePackageReference`
makes direct prunable references private. Also account for stricter package IDs,
HTTP failures, runtime-asset omission from `deps.json`, and removal of the enhanced
HTTP retry environment switch.

### Separate Data from CLI Diagnostics

Non-command-relevant CLI output, including `dotnet watch` logging, goes to standard
error. Scripts must capture stdout and stderr deliberately. Also expect
`--interactive` to default to true in user scenarios and `dotnet package list` to
restore before listing.

### Review Native Loading

Single-file applications no longer probe the executable directory for native
libraries. `DllImportSearchPath.AssemblyDirectory` searches only the assembly
directory. Package native assets or configure an explicit, secure search path
instead of relying on the executable location.

### Revalidate Serialization Contracts

`System.Text.Json` detects property-name conflicts. `XmlSerializer` includes
properties marked `ObsoleteAttribute` instead of ignoring them. Run contract and
round-trip tests before deploying an upgrade, especially when reflection,
inheritance, or generated contexts affect the shape.

## C# 14 Quick Reference

### Extension Blocks

A named receiver defines instance extension members; omit the receiver name for
static extension members. Extension blocks can provide properties, methods, and
operators.

```csharp
public static class SequenceExtensions
{
    extension<T>(IEnumerable<T> source)
    {
        public bool IsEmpty => !source.Any();
    }
}
```

### Field-Backed Properties

Use the contextual `field` token to access a compiler-synthesized backing field
from an accessor. If the type already declares an identifier named `field`, use
`@field` or `this.field` for that existing identifier.

```csharp
public string Message
{
    get;
    set => field = value ?? throw new ArgumentNullException(nameof(value));
}
```

### Null-Conditional Assignment

`?.` and `?[]` may appear on the left of simple or compound assignment. The
right-hand side runs only when the receiver is non-null. This form does not
support `++` or `--`.

```csharp
customer?.Order = GetCurrentOrder();
customer?.Balance += payment;
```

### Span Overload Changes

Implicit conversions among arrays, `Span<T>`, and `ReadOnlySpan<T>` now compose
more naturally and participate in generic inference. After changing language
version, verify calls with span-aware overloads because a different overload may
be selected.

### Other Language Changes

- `nameof(List<>)` returns `"List"` without a type argument.
- Implicitly typed lambda parameters may use `scoped`, `ref`, `in`, `out`, or
  `ref readonly`; `params` still requires explicit parameter types.
- Instance constructors and events may be partial, with one defining declaration
  and one implementing declaration.
- A type may implement a dedicated compound-assignment operator.

See [language.md](references/language.md) for defining/implementing declaration
rules and compiler compatibility details.

## Runtime and Library Quick Reference

### Cryptography

- Use the hash-algorithm-specific `FindByThumbprint` overload for non-SHA-1
  certificate thumbprints and to avoid same-length hash ambiguity.
- Use `ExportPkcs12` with a compatibility preset or custom PBE parameters to
  choose the PFX protection scheme explicitly.
- Check `IsSupported` before using `MLKem`, `MLDsa`, or `SlhDsa`; availability is
  platform dependent and some APIs remain experimental.
- `Aes` exposes RFC 5649 padded key-wrap operations.

### Strict JSON

Set `AllowDuplicateProperties = false` to reject duplicate names. The
`JsonSerializerOptions.Strict` preset also rejects unmapped members, retains
case-sensitive binding, and enforces nullable annotations and required
constructor parameters. Generated contexts can preserve reference cycles with
`JsonKnownReferenceHandler.Preserve`.

### Diagnostics and Hosting

Telemetry sources and meters may carry schema URLs, activity serialization now
includes events and links, and trace aggregation supports root-activity rate
limits. Review sampling after an upgrade because `ActivitySource.CreateActivity`
and `StartActivity` behavior changed. All of `BackgroundService.ExecuteAsync` now
runs as a `Task`, which changes where synchronous startup work executes.

## SDK and Deployment Quick Reference

### One-Shot Tools and CLI Introspection

`dotnet tool exec package@version` downloads and runs a tool without installing
it. Omit `@version` for the latest version; expect confirmation before a new
download. Any CLI command can emit its machine-readable command schema with
`--cli-schema`.

### File-Based Apps

`dotnet publish app.cs` uses Native AOT by default. Add
`#:property PublishAot=false` when dependencies are incompatible. File-based apps
also support `#:project` references and executable extensionless shebang files.

### Test Runner Selection

Select Microsoft.Testing.Platform under `test.runner` in `global.json` when
`dotnet test` should use it. Keep runner selection explicit in shared repositories
so local and CI behavior agree.

### Named EF Core Filters

Define multiple named query filters for an entity when policies such as tenancy
and soft deletion must be independently disabled. Disable only the named filter
needed for a query instead of removing all filters for the entity.

## Upgrade Validation Checklist

- Build with the pinned SDK and inspect warnings as well as errors.
- Run restore explicitly and review audit and pruning diagnostics.
- Test scripts that parse CLI stdout or assume old solution or tool defaults.
- Exercise native-library loading in single-file deployments.
- Rebuild and scan container images after changing the base distribution.
- Round-trip representative JSON and XML payloads.
- Verify browser streaming, HTTP/3, mail-address validation, and macOS TLS where
  those paths are used.
- Run background-service startup, cancellation, and shutdown tests.
- Recheck WPF, Windows Forms, and `System.Drawing` exception handling.
- Validate cryptographic capability with runtime support checks on every target
  platform.
