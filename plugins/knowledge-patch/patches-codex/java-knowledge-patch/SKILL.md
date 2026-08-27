---
name: java-knowledge-patch
description: Java
version: "26"
license: MIT
metadata:
  author: Nevaberry
---


# Java Knowledge Patch

Use this skill when upgrading a JDK, reviewing Java launch configuration,
adopting recently finalized or preview APIs, or diagnosing runtime behavior
that changed across current JDK releases.

## Working method

1. Identify the exact JDK used to compile, test, package, and run the
   application; these can differ in CI and production.
2. Audit launch arguments, service definitions, container entrypoints, IDE
   settings, build plugins, and native-image or custom-runtime pipelines.
3. Separate permanent APIs from preview, incubating, and experimental
   features. Apply the flags required by the selected JDK, then recompile.
4. Check removed APIs and tools before debugging secondary linkage, startup,
   monitoring, certificate, or provider failures.
5. Validate runtime and security changes under the deployment's real class
   path, module path, collector, trust store, network policy, and native
   libraries.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration, removals, and deprecations](references/migration-removals.md) | Removed APIs, tools, launcher flags, VM options, platform support, and migration checks |
| [Language, APIs, and concurrency](references/language-apis.md) | Module imports, preview discipline, finalized APIs, compact source files, stable values, and HTTP/3 |
| [Runtime, GC, AOT, and diagnostics](references/runtime-performance.md) | Collector changes, object headers, virtual threads, AOT caches, JFR, and runtime images |
| [Security and cryptography](references/security-cryptography.md) | Security Manager, native access, final fields, KDF, ML-KEM, ML-DSA, PEM, trust roots, and providers |

## Breaking changes: start here

### Removed launcher and VM surfaces

- Remove `-t`, `-tm`, `-Xfuture`, `-checksource`, `-cs`, and
  `-noasyncgc`; the `java` launcher no longer accepts them.
- Replace old aliases such as `-verbosegc`, `-noclassgc`, `-verify`,
  `-verifyremote`, `-ss`, `-ms`, and `-mx` with current long-form VM
  options or unified logging.
- Remove tuning assumptions around `Xmaxjitcodesize`,
  `AlwaysActAsServerClassMachine`, `NeverActAsServerClassMachine`,
  `AggressiveHeap`, and `MaxRAM`; they are removal targets.

### Removed APIs and tools

- The Applet APIs and `javax.swing.JApplet` are gone. Old bytecode can fail
  to link as well as old source failing to compile.
- `Thread.stop()` is gone; use interruption or another cooperative
  cancellation protocol. Existing bytecode may throw `NoSuchMethodError`.
- `jrunscript` is gone, and `jstatd`, `jdk.jsobject`, `ZipError`, legacy
  locking modes, and `jhsdb debugd` are on a removal path.
- `java.net.Socket` constructors cannot create datagram sockets. Use
  `DatagramSocket` or `DatagramChannel`.

### Disabled and restricted behavior

- Enabling the Security Manager is an error. Treat its remaining APIs only
  as temporary migration aids.
- JNI and restricted Foreign Function and Memory use warn without an explicit
  native-access grant. Resolve the warnings before enforcement becomes
  deny-by-default.
- Deep-reflection writes to `final` fields warn. Grant mutation narrowly with
  `--enable-final-field-mutation`, control violations with
  `--illegal-final-field-mutation`, and migrate frameworks toward supported
  construction or serialization.

### Platform and observability removals

- Do not assume a 32-bit x86 JDK. The Windows port was removed first; the
  remaining x86 port and the bundled experimental Graal JIT were subsequently
  removed.
- Old JMX system properties, PerfData sampling, and private
  `sun.rt._sync*` counters are gone. Move agents to supported JFR, JMX, or
  serviceability APIs.
- Linux GTK 2 support, legacy short-zone-ID interpretation, JNDI compatibility
  hooks, remote code downloading, and old JMX serialization compatibility
  have been removed.

See [Migration, removals, and deprecations](references/migration-removals.md)
for exact names and a systematic audit checklist.

## Preview and finalization rules

- Compile and run preview-dependent code with `--enable-preview`; preview
  class files must be recompiled for each JDK release.
- Module imports, compact source files and instance `main` methods, flexible
  constructor bodies, scoped values, and the KDF API are permanent. Remove
  preview flags only when no remaining preview feature requires them.
- Primitive patterns, structured concurrency, lazy constants, and PEM
  encodings still use preview forms; the Vector API remains incubating.
- The Class-File API and Stream Gatherers are final and need no preview flag.

### Module imports

Module imports do not import subpackages or change module readability. A
type-import-on-demand declaration wins over a module import when both expose
the same simple name. Do not generalize the broad reach of
`import module java.se;` to arbitrary modules.

### Compact source files

`IO` is in `java.lang`, but its static methods are not implicitly imported.
Qualify calls such as `IO.println(...)` or add an explicit static import.
Its streams are `System.in` and `System.out`, not `java.io.Console`.

See [Language, APIs, and concurrency](references/language-apis.md) for code
examples, feature states, and migration details.

## Runtime quick reference

### Garbage collectors and headers

- ZGC is generational-only; configurations selecting non-generational ZGC
  must be revised.
- Generational Shenandoah and compact object headers progressed from
  experimental modes to product features. Current startup configuration does
  not need `-XX:+UnlockExperimentalVMOptions` solely for either feature.
- When testing the earlier experimental compact-header form, unlock
  experimental options and enable `UseCompactObjectHeaders` explicitly.

### Virtual threads

Virtual threads blocked in most `synchronized` constructs can unmount from
their carrier. Reassess workarounds built around the former common pinning
behavior, while still measuring the application's actual blocking paths.

### AOT caches

- A training run can record loaded and linked classes for a later startup
  cache; the workflow also supports reuse of method profiles.
- A cache is coupled to its application and runtime inputs. Rebuild it when
  the application, class path, module path, or JDK changes.
- Cached objects can be stored in a collector-neutral representation, so the
  object cache is no longer tied to one garbage collector.

### Diagnostics

Experimental JFR facilities include Linux CPU-time profiling, cooperative
stack sampling, and method timing and tracing. Method tracing instruments
code, so restrict it to the methods needed for the diagnostic session.

See [Runtime, GC, AOT, and diagnostics](references/runtime-performance.md)
for configuration and deployment implications.

## Security and cryptography quick reference

- Standard facilities cover KDFs, ML-KEM key encapsulation, ML-DSA
  signatures, and PEM encoding/decoding of keys, certificates, and revocation
  lists. Check whether the selected API form is permanent or preview.
- Do not assume old roots remain in the default trust store. Test real
  certificate chains after a JDK update.
- Do not infer provider support from older platform requirements. Audit
  SunPKCS11 PBE assumptions and verify PBES2 capabilities explicitly.
- Treat the first warning from terminally deprecated `sun.misc.Unsafe`
  memory-access methods as a dependency migration signal.

See [Security and cryptography](references/security-cryptography.md) for the
specific root and provider changes and the native/reflection migration knobs.

## Upgrade verification checklist

- Search every launch surface for removed and deprecated flags.
- Compile without stale preview flags, then add back only those required by
  features that remain preview.
- Run linkage tests for removed Applet and thread-stopping APIs.
- Exercise custom runtime images, native libraries, agents, and monitoring
  integrations.
- Recreate AOT caches using the deployed application and runtime inputs.
- Test collectors, compact headers, and virtual-thread workloads under load.
- Validate QUIC over UDP, proxy and firewall behavior, HTTP fallback,
  certificates, and telemetry before enabling HTTP/3.
- Validate trust chains and cryptographic provider algorithms in the target
  runtime rather than relying on prior defaults.
