# SDK, CLI, Build, Restore, and Test

Compatibility changes are attributed to `10.0-guides`, feature additions to
`10.0`, and servicing guidance to `10.0.11`.

## Security Servicing

.NET 10.0.11 fixes these vulnerabilities:

- Remote code execution: CVE-2026-70354 and CVE-2026-62897.
- Elevation of privilege: CVE-2026-62886, CVE-2026-62871, and CVE-2026-62909.
- Information disclosure: CVE-2026-62898, CVE-2026-62900, and CVE-2026-62902.
- Security feature bypass: CVE-2026-62899.
- Denial of service: CVE-2026-62901.

Update deployed runtimes and refresh .NET 10 container images. Runtime 10.0.11 is
included in SDK 10.0.400, 10.0.303, and 10.0.111. Installing one of those SDKs
also installs its matching updated .NET and ASP.NET Core runtimes, so separate
runtime packages are unnecessary.

## CLI Defaults and Streams

- `--interactive` defaults to `true` in user scenarios.
- Output unrelated to a command's primary result goes to standard error.
  `dotnet watch` logging also goes to standard error.
- `dotnet new sln` creates SLNX by default.
- `dotnet package list` performs a restore.
- `dotnet tool install --local` creates a tool manifest if none exists.

Update scripts that parse stdout, assume a traditional solution file, avoid
restore during listing, or expect local tool installation to fail without a
manifest.

## SDK, Workloads, and Tool Packaging

- .NET tool packaging creates runtime-identifier-specific packages.
- Workload management defaults to workload-set mode instead of loose manifests.
- Target-framework `DefineConstants` are unavailable during evaluation.
- Dynamic native code-coverage instrumentation defaults to false.
- Double quotes in file-level directives are rejected.
- `dnx` scripts bypass `global.json` SDK selection.
- `dnx.ps1` is no longer included.

## NuGet Restore, Audit, and Pruning

- `dotnet restore` audits transitive packages.
- A versionless `PackageReference` is an error.
- Direct references pruned by NuGet produce NU1510.
- `PrunePackageReference` makes direct prunable references private.
- Packages without runtime assets are omitted from `deps.json`.
- HTTP warnings in package list and search operations are errors.
- Invalid package IDs are errors.
- SHA-1 signing fingerprints are deprecated.
- `NUGET_ENABLE_ENHANCED_HTTP_RETRY` has been removed.

## One-Shot Tool Execution

`dotnet tool exec` downloads and runs a tool without installing it. It uses the
latest version unless the package is written as `package@version`, prompts before
a new download, and honors the version in a nearby local tool manifest.

```bash
dotnet tool exec --source ./artifacts/package dotnetsay@0.1.0 "Hello"
```

## Portable Tool Fallback

Add the `any` RID beside platform RIDs to create a framework-dependent,
platform-agnostic fallback package for systems without a matching native tool
binary.

```xml
<RuntimeIdentifiers>linux-x64;win-x64;any</RuntimeIdentifiers>
```

## Machine-Readable CLI Schema

Every CLI command accepts `--cli-schema` and emits a JSON description of its
arguments, options, and subcommands for shell integration and other tooling.

```bash
dotnet clean --cli-schema
```

## .NET Tasks in .NET Framework MSBuild

Visual Studio 2026 and `msbuild.exe` can execute .NET-built MSBuild tasks through
`TaskHostFactory`. Execution is out of process and does not support task Host
Objects. A conditional second `UsingTask` without the factory can retain
in-process execution under Core MSBuild.

```xml
<UsingTask TaskName="MyTask"
           AssemblyFile="path\to\MyTask.dll"
           Runtime="NET"
           TaskFactory="TaskHostFactory" />
```

## Noun-First Commands and Completions

`dotnet package add|list|remove` and `dotnet reference add|list|remove` coexist
with the older verb-first forms. Generate native completion scripts for Bash,
Fish, Nushell, PowerShell, or Zsh with `dotnet completions script`.

```bash
dotnet completions script bash
```

## Microsoft.Testing.Platform

`dotnet test` can use Microsoft.Testing.Platform when `global.json` selects the
runner:

```json
{
  "test": {
    "runner": "Microsoft.Testing.Platform"
  }
}
```
