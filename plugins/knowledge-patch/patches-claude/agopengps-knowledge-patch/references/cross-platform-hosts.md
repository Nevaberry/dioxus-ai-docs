# Cross-Platform Hosts and Migration

## AgValoniaGPS historical status

AgValoniaGPS was the C#/.NET 10, Avalonia 12, ReactiveUI, dependency-injection,
and MVVM rewrite targeting Windows, macOS, Linux, Android, and iOS. Its
repository was archived read-only on 2026-06-27 and now points to AgOpenWeb.

Its releases were automated nightly pre-releases. Identify a historical build
by exact nightly tag and commit because an internal value such as `26.5.50` need
not identify one unique artifact.

```bash
dotnet build Platforms/AgValoniaGPS.Desktop
dotnet run --project Platforms/AgValoniaGPS.Desktop
dotnet test
```

## AgOpenWeb architecture

AgOpenWeb is an independent AgValoniaGPS fork. A .NET host serves its
HTML/JavaScript guidance UI at `http://<host>:5174`. It retains C#/.NET 10,
Avalonia 12, dependency injection, MVVM, and shared cross-platform code, while
using CommunityToolkit.Mvvm instead of ReactiveUI.

A reachable browser proves only that the host is available. Diagnose GNSS,
NTRIP, hardware UDP, and control output independently.

## Execution modes

- Desktop mode embeds the host and window on Windows x64, Apple-silicon macOS,
  and Linux x64 or ARM64.
- Headless mode runs as a Linux systemd service or Windows service.
- Mobile mode hosts the UI on Android; iOS is recorded as a sideload target.

For a headless installation, record both host platform and browser-client
platform so display-side behavior is reproducible.

## Channel, architecture, and prerequisites

As of 2026-07-28, `v26.6.74` is the latest stable AgOpenWeb release. A
newer-dated 2026-07-19 nightly is an unversioned, potentially unstable
pre-release and does not supersede stable merely by date.

Bundles are self-contained, but Windows desktop still needs WebView2 and Linux
launcher builds need system WebKitGTK. Desktop, headless-service, and Android
artifacts are not interchangeable. Select by release channel, execution mode,
and architecture.

## Compatibility boundary

Do not infer file-level or wire-level compatibility from the WinForms to
AgValoniaGPS to AgOpenWeb lineage. Revalidate profile conversion, field files,
custom PGNs, network ports, GNSS sentences, and board firmware at every move
between codebases.

