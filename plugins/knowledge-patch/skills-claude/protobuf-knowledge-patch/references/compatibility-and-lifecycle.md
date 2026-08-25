# Compatibility and release lifecycle

## Generated-code/runtime direction (`release-lifecycle`)

Generated code must never run against a runtime older than the `protoc` and
plugin release that produced it, even if the releases differ only at patch
level. For most languages, major V gencode is supported from its own release
through runtime major V+1; runtime V+2 or newer is unsupported. Within one
runtime major, older-minor gencode works on later-minor runtimes.

Security fixes can require a paired runtime update and regeneration despite
these windows. Loading multiple protobuf runtime majors into one process is
unsupported.

Regenerate on every release update. The compatibility window exists to permit
rolling upgrades and existing-project migration, not to make stale gencode the
normal configuration.

## Exact-version languages (`release-lifecycle`)

C++ and Rust require the generated code and runtime release to match exactly.
C++ additionally provides no ABI-stability guarantee across minor or even patch
releases.

## Python's extended window (`release-lifecycle`)

Python generated code from 3.20.0 onward is descriptor-based and is supported
through at least runtime 8.x. If a future major ends that extended window,
poison-pill warnings and errors are expected before the break.

## Poison warnings during staged upgrades (`30.0-migration`)

An older generated file can still operate with a newer runtime under a rolling
upgrade while warning that the next runtime major will reject it. For example,
Python 4.x gencode works with a 5.x runtime but warns about 6.x. Treat the warning
as a requirement to regenerate before the next major upgrade.

## Shared releases and package majors (`release-lifecycle`)

Protobuf publishes a shared `minor.point` release, but each language runtime
prepends its own major. Shared release `34.1`, for example, maps to Java
`4.34.1` and C# `3.34.1`. A shared release can therefore trigger a major change
for one language while remaining within the same major for another.

The provisional `34.0-announcement` plan targeted v34 for Q1 2026. Its package
transition moved C++ and Python from 6.33 to 7.34.0, and PHP and Objective-C from
4.33 to 5.34.0. Java, Ruby, C#, Rust, and JRuby did not take a major bump. Python
gencode itself did not change for 7.34.x, and its poison checks were relaxed so
older generated files did not warn or fail.

## Supported release lines (`release-lifecycle`)

Active lines receive features, compatible changes, and fixes. Maintenance lines
receive only critical and security fixes.

| Component | Active | Maintenance or minimum gencode |
| --- | --- | --- |
| `protoc` | 35.x | 33.x and Java-specific 25.x maintenance |
| C++ | 7.35.x | 6.33.x maintenance; exact-match gencode |
| C# | 3.35.x | minimum gencode 3.0.0 |
| Java | 4.35.x | 3.25.x maintenance; minimum gencode 3.0.0 |
| PHP | 5.35.x | 4.33.x maintenance; minimum gencode 4.26.0 |
| Python | 7.35.x | 6.33.x maintenance; minimum gencode 3.20.0 |
| Ruby | 4.35.x | minimum gencode 3.0.0 |

## Cadence and retirement (`release-lifecycle`)

Updates are quarterly, with breaking releases targeted for Q1. A new minor ends
support for the preceding minor immediately. A new major leaves the previous
major supported for four additional quarters. Java 3.x is an exception with a
36-month maintenance window.

## Editions have independent numbers (`release-lifecycle`)

Edition numbers are not compiler or runtime versions. Edition 2023 requires
`protoc` 27.0 or newer; Edition 2024 requires 32.0 or newer. A current compiler
continues to accept proto2, proto3, Edition 2023, and Edition 2024 schemas.

## Changes allowed outside breaking releases (`release-lifecycle`)

Minor and patch releases may add or deprecate `descriptor.proto` elements,
introduce an Edition, or add/drop operating-system, language, and tooling
support. Enforcing an existing policy, such as removing an end-of-life
platform, is not considered a breaking change and does not require a language
major bump.

## Android and JRuby (`release-lifecycle`)

Android's supported minimum SDK is the lower of the Google Play services
minimum and Jetpack's default. JRuby is best-effort: its target is the newest
JRuby compatible with the minimum supported Ruby version.
