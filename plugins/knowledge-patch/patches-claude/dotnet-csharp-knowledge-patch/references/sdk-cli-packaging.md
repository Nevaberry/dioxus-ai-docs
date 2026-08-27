# SDK, CLI, Packaging, Testing, and Containers

Compatibility sections are attributed to `10.0-guides`; new workflows are attributed
to `10.0`, and servicing SDK details to `10.0.11`.

## Container Base Distribution

Default .NET 10 container images use Ubuntu. If a build depends on the previous
distribution's packages, paths, library versions, or package manager, either adapt the
build or pin an intentional base image. Rebuild and scan the resulting image rather
than assuming a tag change preserves the old userspace.

## CLI Defaults and Output Streams

The CLI's `--interactive` option defaults to `true` in user scenarios. Pass an
explicit value in unattended automation where restore or authentication prompts would
hang or violate policy.

Non-command-relevant CLI output is written to standard error. `dotnet watch` also
logs to standard error. Capture stdout for command data and stderr for diagnostics;
do not treat any stderr output by itself as command failure.

`dotnet new sln` creates SLNX by default. Request another format explicitly when
downstream tools cannot consume SLNX.

`dotnet package list` performs a restore. Account for network access, authentication,
audit policy, and changes to generated restore assets.

`dotnet tool install --local` creates a tool manifest if none exists. Run it from the
intended directory and decide whether the new manifest belongs in source control.

## SDK Evaluation, Workloads, and Tool Packaging

.NET tool packaging creates runtime-identifier-specific packages. Validate the
published package set for every supported RID rather than assuming one portable
artifact.

Workload management defaults to workload-set mode rather than loose manifests. Pin
and update workload sets deliberately in reproducible environments.

Target-framework `DefineConstants` values are unavailable during evaluation. Do not
use them to steer evaluation-time imports or properties; use an evaluation-time
property designed for that purpose.

Dynamic native code-coverage instrumentation defaults to false. Opt in explicitly
when a test pipeline requires it.

Double quotes in file-level directives are rejected. Update directive syntax rather
than depending on permissive parsing.

`dnx` scripts bypass `global.json` SDK selection, and `dnx.ps1` is no longer
included. Do not infer the selected SDK from a nearby `global.json` for these scripts,
and remove deployment assumptions about the PowerShell wrapper.

## NuGet Restore, Audit, and Pruning

`dotnet restore` audits transitive packages. Establish audit policy for CI and make
the required advisory/network inputs available.

A versionless `PackageReference` is an error. Supply the version directly or through
a supported central package-management mechanism.

When NuGet prunes a direct reference it emits NU1510. Determine whether the reference
is genuinely required before suppressing the diagnostic. `PrunePackageReference`
makes direct prunable references private, which can change what flows transitively to
consumers.

Packages without runtime assets are omitted from `deps.json`. Tools that inspect that
file must not assume every restored package appears there.

HTTP warnings from package list/search operations are errors. Correct the source URL
or transport configuration rather than treating them as warnings.

Invalid package IDs are errors. Validate generated IDs before pack/restore.

SHA-1 signing fingerprints are deprecated. Move signing verification and policy to a
supported stronger fingerprint algorithm.

`NUGET_ENABLE_ENHANCED_HTTP_RETRY` was removed. Delete dependencies on that switch
and use currently supported retry/configuration behavior.

## One-Shot Tool Execution

In `10.0`, `dotnet tool exec` downloads and runs a tool without installing it. It
selects the latest version unless the package is written as `package@version`, asks
before a new download, and honors the version in a nearby local tool manifest.

```bash
dotnet tool exec --source ./artifacts/package dotnetsay@0.1.0 "Hello"
```

Pin versions for automation and account for the download prompt and manifest lookup.

## Portable Tool Fallback

For `10.0` tool packaging, include the `any` RID alongside platform RIDs to add a
framework-dependent, platform-agnostic fallback for systems without a matching native
tool binary.

```xml
<RuntimeIdentifiers>linux-x64;win-x64;any</RuntimeIdentifiers>
```

## Machine-Readable CLI Schema

Every `10.0` CLI command accepts `--cli-schema`, which emits JSON describing its
arguments, options, and subcommands for integrations and tooling.

```bash
dotnet clean --cli-schema
```

Treat the emitted schema as command metadata rather than human-formatted help.

## .NET Tasks in .NET Framework MSBuild

With `10.0`, Visual Studio 2026 and `msbuild.exe` can run .NET-built MSBuild tasks
through `TaskHostFactory`. Execution is out of process and does not support task Host
Objects.

```xml
<UsingTask TaskName="MyTask"
           AssemblyFile="path\to\MyTask.dll"
           Runtime="NET"
           TaskFactory="TaskHostFactory" />
```

Where Core MSBuild should keep the task in process, add a conditional second
`UsingTask` without the factory. Keep conditions mutually appropriate for the host.

## Published File-Based Applications

In `10.0`, `dotnet publish app.cs` produces a native executable because file-based
applications publish with native AOT by default. Disable AOT for incompatible
dependencies with `#:property PublishAot=false`.

File-based applications also accept `#:project` references and support executable,
extensionless shebang files.

```csharp
#!/usr/bin/env dotnet
#:project ../ClassLib/ClassLib.csproj
#:property PublishAot=false
Console.WriteLine(new ClassLib.Greeter().Greet());
```

Test reflection, dynamic loading, and native dependencies under the actual publish
mode.

## Noun-First Commands and Completions

The `10.0` aliases `dotnet package add|list|remove` and
`dotnet reference add|list|remove` coexist with the older verb-first forms. Scripts
may migrate gradually, but should use one form consistently in examples and output
matching.

`dotnet completions script` generates native completion scripts for Bash, Fish,
Nushell, PowerShell, and Zsh.

```bash
dotnet completions script bash
```

## Console Container Publishing and Image Format

In `10.0`, console projects can run
`dotnet publish /t:PublishContainer` without setting `EnableSdkContainerSupport`.

Set `ContainerImageFormat` to `Docker` or `OCI` when the format is part of the
delivery contract. Otherwise it can follow defaults influenced by the base image and
multi-architecture publishing.

```xml
<PropertyGroup>
  <ContainerImageFormat>OCI</ContainerImageFormat>
</PropertyGroup>
```

## Microsoft.Testing.Platform in `dotnet test`

In `10.0`, select Microsoft.Testing.Platform as the `dotnet test` runner in
`global.json`:

```json
{
  "test": {
    "runner": "Microsoft.Testing.Platform"
  }
}
```

Make runner selection explicit in repositories where test orchestration behavior is
part of the build contract.

## SDK Builds Carrying the Serviced Runtime

Batch `10.0.11` is carried by SDK 10.0.400, 10.0.303, and 10.0.111. Installing any of
these SDKs also installs its matching updated .NET and ASP.NET Core runtimes; separate
runtime packages are not needed for that installation. Deployment images and hosts
still need to be rebuilt or updated so they actually consume the serviced runtime.
