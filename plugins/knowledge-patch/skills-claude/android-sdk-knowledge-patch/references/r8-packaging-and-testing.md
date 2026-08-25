# R8, Packaging, and Test Infrastructure

## Strict shrinking defaults

### Missing files and constructors

AGP 9.0 fails the build when a referenced keep file is missing and enables
optimized resource shrinking. Strict full-mode keep semantics mean that:

```proguard
-keep class A
```

does not retain `A`'s default constructor. Name it when construction is
required:

```proguard
-keep class A { <init>(); }
```

Library and feature publication rejects global options such as
`-dontoptimize` and `-dontobfuscate` in consumer rules. If precompiled
dependency rules contain those global options, application builds silently
ignore them.

### Kotlin null-check rewriting

R8's `-processkotlinnullchecks` accepts `keep`, `remove_message`, or `remove`.
The default is `remove_message`. If the option appears more than once, the
strongest value wins.

```proguard
-processkotlinnullchecks keep
```

Choose `keep` when stack traces or diagnostics must retain Kotlin-generated
null-check messages.

### Runtime-invisible annotations

In AGP 9.2, wildcard `-keepattributes` patterns no longer match
runtime-invisible annotation attributes. Preserve all required forms by naming
them explicitly:

```proguard
-keepattributes RuntimeInvisibleAnnotations,
                RuntimeInvisibleParameterAnnotations,
                RuntimeInvisibleTypeAnnotations
```

### Negated member-name patterns

AGP 9.2 allows negated member names, including in `-if` preconditions:

```proguard
-keepclassmembers class com.example.MyClass { *** !*ForTesting(...); }
```

Wildcards inside a negated `-if` precondition cannot be back-referenced in its
consequent.

## Desugaring and keep propagation

Keep information on interface methods is no longer propagated to synthesized
companion methods. This breaks a former `minSdk < 24` library workflow that
depended on `-applymapping`; explicitly keep companion methods in the artifact
that is desugared separately.

Direct D8/R8 integrations must replace removed L8 keep-rule generation APIs and
`--desugared-lib-pg-conf-output` with `TraceReferences`.
`-addconfigurationdebugging` is no longer supported.

## Mapping and retracing

When retracing is needed, R8 puts `r8-map-id-<MAP_ID>` in `SourceFile`, using
the full mapping hash. A custom `-renamesourcefileattribute` takes precedence.

In ProGuard compatibility mode, do not keep `SourceFile` if the embedded
mapping ID is required; retaining it prevents the ID from being written.

## Optimization DSL and source-set rules

AGP 9.3 adds an `optimization` block to application build types. Enabling the
block turns on both code optimization and optimized resource shrinking without
requiring the default Android keep-rules file. The legacy DSL remains valid.

Place `.keep` files under `src/<variant>/keepRules/` for variant-specific app
and library rules. These files work with either DSL and can also define KMP
consumer rules.

## Configuration analysis and reports

### Analyze without assembling

On AGP 9.3, run:

```shell
./gradlew :app:analyzeReleaseR8Config
```

The task creates an R8 Configuration Analyzer report without completing an APK
or app bundle build.

### Aggregate tests and coverage

On AGP 9.2, set:

```properties
android.experimental.reportAggregationSupport=true
```

This enables experimental HTML dashboards that combine unit-test,
instrumentation-test, and coverage results across modules and variants.

On-device tests default to `AndroidJUnitRunner` under AGP 9.0. Only the tested
build type receives a unit-test component by default, normally debug rather
than debug and release. Test any build logic that assumed both components.

## Native and APK compatibility

### Build native libraries for 16 KB pages

On Android 16, some 4 KB-aligned apps can run in 16 KB page-size compatibility
mode. Compiling with API 36 and enabling the manifest property below suppresses
the user dialog, but it is not a substitute for rebuilding native code with
16 KB alignment.

```xml
<property android:name="android:pageSizeCompat" android:value="true" />
```

This behavior comes from batch `api-36`.

### Make dynamically loaded native code read-only

For API 37 targets, dynamic-code-loading protection includes native libraries.
Make a file read-only before passing it to `System.load()` or loading fails with
`UnsatisfiedLinkError`. This behavior comes from batch `api-37`.

### Hybrid post-quantum APK signing

Android 17 adds APK Signature Scheme v3.2, combining RSA or elliptic-curve
signatures with ML-DSA signatures. Validate that signing, verification,
distribution, and rollback tooling all preserve the hybrid signature.

## Profiling and notification tests

Android 17 adds `ProfilingManager` triggers for `COLD_START`, `OOM`, and
`KILL_EXCESSIVE_CPU_USAGE`. Use the relevant trigger when investigating startup,
memory, or CPU termination behavior.

Android 17 also strictly limits custom notification-view sizes. Test each
custom layout at runtime rather than relying only on resource previews.
