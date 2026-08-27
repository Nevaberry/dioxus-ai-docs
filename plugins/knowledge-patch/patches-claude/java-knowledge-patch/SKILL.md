---
name: java-knowledge-patch
description: Java
version: "26"
license: MIT
metadata:
  author: Nevaberry
---


# Java Compatibility Guide

Use this skill when writing, reviewing, or migrating Java applications, build
logic, launch scripts, runtime images, or operational tooling whose behavior
depends on recent JDK changes.

Prefer the project's declared toolchain and the runtime actually used in
production. Check build files, CI images, container bases, service definitions,
IDE launchers, and native packaging before recommending a migration.

## How to use this skill

1. Identify the compile JDK, runtime JDK, and whether preview features are
   enabled.
2. Search every launch surface for removed, deprecated, or experimental VM
   options.
3. Check source and bytecode for removed APIs before investigating secondary
   failures.
4. Rebuild preview-dependent code for the exact JDK release that will run it.
5. Rebuild AOT caches when the application or any runtime input changes.
6. Validate trust stores, providers, proxies, firewalls, and monitoring agents
   as deployment inputs rather than treating the source tree as the whole
   migration surface.
7. Open the topic reference that matches the work; do not infer old behavior
   from a similarly named replacement.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration and removals](references/migration-and-removals.md) | Removed APIs, tools, launcher flags, platform support, deprecations |
| [Language and APIs](references/language-and-apis.md) | Module imports, compact source files, finalized APIs, previews |
| [Runtime and performance](references/runtime-and-performance.md) | Garbage collectors, object headers, AOT caches, virtual threads, JFR |
| [Security and networking](references/security-and-networking.md) | Native access, cryptography, trust stores, JNDI, HTTP/3 |

## Breaking-change quick reference

### Treat source, bytecode, and launch configuration separately

- Source compilation can fail after removal of Applet types.
- Existing bytecode can fail to link when it reaches a removed member such as
  `Thread.stop()`.
- A service can fail before application startup because the launcher rejects a
  removed option.
- A running application can still be incorrect because a trust root, provider
  algorithm, monitoring interface, or platform compatibility property changed.

### High-risk removed surfaces

- Security Manager enablement is an error; legacy permission types are
  migration-only surfaces and are themselves removal targets.
- Non-generational ZGC is gone. Configure ZGC without assuming the old mode
  remains selectable.
- `java.net.Socket` constructors no longer provide datagram sockets. Use
  `DatagramSocket` or `DatagramChannel`.
- Applet APIs and `Thread.stop()` are gone. Replace them at source and account
  for linkage errors from old bytecode.
- `jrunscript` is gone after first being deprecated for removal.
- The bundled experimental Graal JIT and 32-bit x86 JDK ports are not portable
  migration assumptions.

### Launcher and VM option audit

Search service units, shell scripts, container commands, build plugins, test
harnesses, and IDE metadata for:

- Removed launcher options: `-t`, `-tm`, `-Xfuture`, `-checksource`, `-cs`, and
  `-noasyncgc`.
- Removal-target aliases: `-verbosegc`, `-noclassgc`, `-verify`,
  `-verifyremote`, `-ss`, `-ms`, and `-mx`.
- Removal-target tuning options: `Xmaxjitcodesize`,
  `AlwaysActAsServerClassMachine`, `NeverActAsServerClassMachine`,
  `AggressiveHeap`, and `MaxRAM`.
- Explicit `UseCompressedClassPointers` tuning. The underlying feature remains;
  the explicit option is the compatibility risk.

Move logging to unified logging and use supported long-form VM options.

## Deprecation quick reference

Plan removal work for these categories before they become startup or linkage
failures:

- `ZipError`, old Security Manager permission classes, and XML interchange in
  JMX `DescriptorSupport`.
- `jstatd`, `jhsdb debugd`, and the already removed `jrunscript`.
- `jdk.jsobject` and legacy HotSpot locking modes.
- Linux `VFORK`, `java.locale.useOldISOCodes`, and explicit compressed-class-
  pointer tuning.
- 32-bit Linux x86 distributions and native artifacts.

Do not interpret deprecation of an option as removal of the feature it used to
tune. Verify the documented replacement or VM-selected behavior.

## Preview and language quick reference

### Preview discipline

- Compile and run preview code with `--enable-preview`.
- Recompile preview-dependent code for every JDK release.
- Remove preview enablement only when no remaining source or dependency needs
  it.
- Update source when a preview evolves; recompilation alone may not be enough.
- Keep module flags for incubating APIs such as the Vector API.

### Module imports

A module import does not import subpackages and does not change module
readability. A type-import-on-demand declaration wins over a module import when
both expose the same simple name.

Do not generalize the broad reach of `import module java.se;` to arbitrary
modules; its reach follows `java.se`'s transitive requirements.

### Compact source files

`IO` is in `java.lang`, but its static methods are not implicitly imported.
Call `IO.println(...)` or add an explicit static import. Its I/O is backed by
`System.in` and `System.out`, not `java.io.Console`.

### API status checks

- Class-file parsing, generation, and transformation are available through the
  final Class-File API.
- Stream gatherers are final for custom intermediate stream operations.
- Module imports, compact source files and instance `main` methods, flexible
  constructor bodies, scoped values, and KDF are permanent features.
- Primitive patterns, structured concurrency, lazy constants, and PEM
  encodings require release-specific preview checks.

## Runtime quick reference

### Garbage collection and object layout

- Generational ZGC is the only ZGC mode.
- Generational Shenandoah and compact object headers moved from experimental to
  product status; do not retain the experimental unlock solely for them.
- Compact object headers use 64-bit headers on supported 64-bit platforms.
- AOT object caches are collector-neutral, but their other application and
  runtime compatibility constraints still apply.

### AOT cache safety

Treat an AOT cache as derived deployment output. Rebuild it when the
application, class path, module path, or JDK changes. A cache may reuse method
profiles, but it remains coupled to the inputs used to create it.

### Threads and diagnostics

Most virtual threads blocked in `synchronized` code can unmount from carrier
threads, so do not diagnose every synchronized block as carrier pinning.

JFR CPU-time profiling, cooperative stack sampling, and method timing or
tracing are experimental diagnostics. Method tracing instruments code; scope
it narrowly.

## Security and networking quick reference

- Treat native-access and `sun.misc.Unsafe` warnings as migration work, not
  harmless noise.
- Validate ML-KEM, ML-DSA, KDF, and PEM needs against API status for the
  selected toolchain.
- Audit trust chains after default-root removals; do not assume a certificate
  remains trusted because an older JDK trusted it.
- Audit provider algorithms when relying on SunPKCS11 PBE factories or older
  DESede and PKCS1Padding requirements.
- For HTTP/3, test QUIC over UDP through network policy, proxies, firewalls,
  fallback paths, certificate handling, and observability.
- Do not attempt to restore JNDI remote code downloading; it is permanently
  disabled.

## Symptom-driven lookup

| Symptom | First checks |
| --- | --- |
| Launcher exits before `main` | Removed and deprecated launcher or VM options |
| `NoSuchMethodError` around thread stopping | Old bytecode calling removed `Thread.stop()` |
| Applet imports do not compile | Removed `java.applet` or `JApplet` APIs |
| Final-field mutation warning | Mutation grant scope and illegal-mutation policy |
| AOT cache behaves inconsistently | Application, class path, module path, or JDK drift |
| TLS chain stops validating | Removed default trust roots |
| Provider algorithm disappears | SunPKCS11 and security-requirement changes |
| UDP path fails only with HTTP/3 | QUIC reachability and fallback behavior |
| Monitoring agent loses data | Removed PerfData, JMX properties, or private counters |
| Preview class will not load | Matching compile/run flags and exact-release rebuild |

## Review checklist

- Confirm compile and runtime JDKs.
- Identify every preview and incubator dependency.
- Scan all launcher surfaces, not only the main build file.
- Search source and packaged bytecode for removed APIs.
- Review GC, object-header, and AOT settings together.
- Review native access and final-field mutation grants for minimum scope.
- Validate trust roots and provider algorithms in a production-like image.
- Exercise HTTP/3 fallback and UDP network policy where applicable.
- Replace unsupported monitoring inputs with JFR, JMX, or supported
  serviceability APIs.
- Record which caches, images, native artifacts, and installers must be rebuilt.
