# Cross-Platform Hosts

## AgValoniaGPS archive boundary

AgValoniaGPS was the C#/.NET 10, Avalonia 12, ReactiveUI, dependency-injection,
and MVVM rewrite targeting Windows, macOS, Linux, Android, and iOS. Its
repository was archived read-only on 2026-06-27 and now points to AgOpenWeb.

Historical releases were automated nightly prereleases. Identify a build by
its exact nightly tag and commit; an internal value such as `26.5.50` need not
identify one artifact uniquely.

The documented development commands are:

```bash
dotnet build Platforms/AgValoniaGPS.Desktop
dotnet run --project Platforms/AgValoniaGPS.Desktop
dotnet test
```

## AgOpenWeb architecture

AgOpenWeb is an independent AgValoniaGPS fork. Its .NET host serves an
HTML/JavaScript guidance UI at:

```text
http://<host>:5174
```

It retains C#/.NET 10, Avalonia 12, dependency injection, MVVM, and shared
cross-platform code, while using CommunityToolkit.Mvvm instead of ReactiveUI.

A reachable browser page proves only that the host is available. Diagnose
GNSS, NTRIP, hardware UDP, and control output as separate paths.

## Execution modes

Choose an artifact that matches the execution mode and platform:

- Desktop mode embeds host and window on Windows x64, Apple-silicon macOS,
  and Linux x64 or ARM64.
- Headless mode runs as a Linux systemd service or Windows service.
- Mobile mode hosts the UI on Android; iOS is recorded as a sideload target.

For headless installations, record the host platform and browser-client
platform separately.

## Channels and runtime dependencies

As of 2026-07-28, `v26.6.74` is the latest stable AgOpenWeb release. A
newer-dated 2026-07-19 nightly exists but is an unversioned and potentially
unstable prerelease.

Bundles are self-contained, with two important launcher dependencies:

- Windows desktop requires WebView2.
- Linux launcher builds require system WebKitGTK.

Desktop, headless-service, and Android artifacts are not interchangeable.
Select by release channel, execution mode, operating system, and architecture.

## Migration boundary

Lineage does not guarantee compatibility between WinForms AgOpenGPS,
AgValoniaGPS, and AgOpenWeb. Revalidate all of the following when crossing a
codebase boundary:

- profile conversion and field files;
- custom PGNs and network ports;
- GNSS sentences;
- board firmware.
