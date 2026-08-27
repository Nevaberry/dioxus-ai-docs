# Android Gradle Plugin and Build Toolchain

## Compatibility and toolchain selection

The `agp-9-toolchain` guidance spans the AGP 9.x build stack. AGP 9.0 supports
through API 36.1 and requires Gradle 9.1.0; AGP 9.2 supports API 37.0 and
requires Gradle 9.4.1; AGP 9.3 supports API 37 and requires Gradle 9.5.0. All
three require JDK 17, use Build Tools 36.0.0, and default to NDK
28.2.13676358 (`r28c`). AGP 9.0 also makes a library's compile SDK the default
minimum compile SDK for consumers unless its publisher explicitly sets
`AarMetadata.minCompileSdk`.

## Public DSL and Variant API migration

AGP 9.0 hides legacy DSL implementations and variant entry points. Replace:

- `applicationVariants` and sibling collections with
  `androidComponents.onVariants`;
- `variantFilter` with `androidComponents.beforeVariants`;
- SDK-path getters with `androidComponents.sdkComponents`; and
- custom test providers with Gradle-managed devices.

```kotlin
androidComponents {
    beforeVariants(selector().withBuildType("debug")) { it.enable = false }
}
```

`android.newDsl=false` temporarily restores the old implementation for an
incompatible plugin, but this switch is removed in AGP 10.

### Plugin API replacements

Move bytecode transformation and ASM frame configuration from `Component` to
`Instrumentation`. Replace `ComponentBuilder.enabled` with `enable`,
`VariantOutput.enable` with `enabled`, and the old `*SdkVersion` variant
properties with `minSdk`, `maxSdk`, or `targetSdk`. Unit-test members are only
available on `HasUnitTest` and `HasUnitTestBuilder` subtypes. The old
`BaseExtension.registerTransform` API is removed.

### DSL type and setter changes

`CommonExtension` is no longer parameterized. Invoke its block methods on a
concrete extension or through properties such as `defaultConfig.apply`.
Replace `DependencyVariantSelection` with `DependencySelection` at
`kotlin.android.localDependencySelection`, `Installation.installOptions(String)`
with the mutable `installOptions` property, and `ProductFlavor.setDimension`
with `dimension`. `DensitySplit`, `LanguageSplitOptions`, and the experimental
`PostProcessing` block are gone.

## Kotlin and KMP integration

AGP 9.0 enables built-in Kotlin. Android modules must stop applying
`org.jetbrains.kotlin.android` or `kotlin-android`. AGP carries KGP 2.2.10 and
upgrades lower KGP versions; it also upgrades KSP versions below
2.2.10-2.0.2. Supply a higher KGP version as a top-level `buildscript`
classpath dependency. Using a lower strictly constrained KGP, with 2.0.0 as
the minimum, requires opting out of built-in Kotlin.

The new DSL cannot combine `org.jetbrains.kotlin.multiplatform` with
`com.android.application` or `com.android.library` in one subproject. Use the
Android Gradle Library Plugin for a KMP library, and put the Android application
in a separate subproject because the KMP module cannot use the application
plugin.

## Changed Android defaults

AGP 9.0 changes several project assumptions:

- library package names must be unique;
- AndroidX is the default dependency family;
- application code compiles against a non-final `R`;
- an unset target SDK defaults to the compile SDK, not the minimum SDK;
- `resValues` is disabled unless enabled per module; and
- generated-source providers must use the `androidComponents` Sources API,
  not `AndroidSourceSet`.

On-device tests default to `AndroidJUnitRunner`. Only the tested build type,
normally debug, receives a unit-test component by default. The
`android.dependency.useConstraints` default is `false`, restricting dependency
constraints to application device tests unless the old behavior is restored.

The global `android.defaults.buildfeatures.aidl` and
`android.defaults.buildfeatures.renderscript` properties are removed. Enable
`aidl` and `renderScript` in only the modules that need them. Remove
`android.r8.integratedResourceShrinking` and
`android.enableNewResourceShrinker.preciseShrinking`: AGP 9.0 rejects both
because integrated precise resource shrinking is mandatory.

## Shrinking and keep rules

### Strict defaults

Missing keep files fail the build, optimized resource shrinking is enabled,
and strict full-mode semantics mean `-keep class A` does not retain the
default constructor. Keep it explicitly when needed:

```proguard
-keep class A { <init>(); }
```

Library and feature publication rejects global options such as
`-dontoptimize` and `-dontobfuscate` in consumer rules. When those options
occur in precompiled dependency rules, an app build silently ignores them.

### Kotlin null checks

`-processkotlinnullchecks` accepts `keep`, `remove_message`, or `remove`. The
default is `remove_message`; if it occurs more than once, the strongest value
wins.

```proguard
-processkotlinnullchecks keep
```

### Desugaring keep behavior

Keep information on interface methods no longer propagates to synthesized
companion methods. A separately desugared `minSdk < 24` library that formerly
depended on `-applymapping` must keep companion methods explicitly. Direct
D8/R8 integrations must replace removed L8 keep-rule generation APIs and
`--desugared-lib-pg-conf-output` with TraceReferences.
`-addconfigurationdebugging` is unsupported.

### Mapping IDs

R8 writes `r8-map-id-<MAP_ID>`, using the full mapping hash, into `SourceFile`
for retracing. A custom `-renamesourcefileattribute` takes precedence. In
ProGuard compatibility mode, do not keep `SourceFile` when the mapping ID is
required, or the ID will be absent.

### AGP 9.2 rule syntax and attributes

Wildcard `-keepattributes` patterns no longer match runtime-invisible
annotation attributes. Name all three when they must survive:

```proguard
-keepattributes RuntimeInvisibleAnnotations,
                RuntimeInvisibleParameterAnnotations,
                RuntimeInvisibleTypeAnnotations
```

Negated member-name patterns are accepted, including in `-if` preconditions.
Wildcards in a negated precondition cannot be back-referenced in the
consequent.

```proguard
-keepclassmembers class com.example.MyClass { *** !*ForTesting(...); }
```

### AGP 9.3 analysis and source sets

Run `./gradlew :app:analyzeReleaseR8Config` to generate an R8 Configuration
Analyzer report without building an APK or bundle.

AGP 9.3 adds an `optimization` block inside app build types. Enabling it turns
on code optimization and optimized resource shrinking without the default
Android keep-rules file; the legacy DSL remains supported. `.keep` files under
`src/<variant>/keepRules/` work with either DSL for apps and libraries and can
define KMP consumer rules.

## Build and packaging features

When shader compilation is enabled, put
`glslc.dir=/path/to/shader-tools` in `local.properties`. During migration only,
opting out of `android.custom.shader.path.required` restores implicit lookup.

AGP 9.0 removes embedded Wear OS apps and the `wearApp` configuration,
density-split APKs, and the `androidDependencies` and `sourceSets` report
tasks. Publish the Wear app separately and use app bundles for density
delivery.

The preview Fused Library Plugin can publish several Android libraries as one
Android Library AAR.

AGP 9.2 can aggregate test and coverage dashboards across modules and variants.
Enable the experimental HTML dashboards with:

```properties
android.experimental.reportAggregationSupport=true
```

## Staging the AGP 10 build model

The planned AGP 10 lazy build model removes `android.newDsl`,
`android.builtInKotlin`, all legacy extension and Variant APIs, direct task
access, eager generated-source registration, and the Transform API. Build
logic must use `Variant.artifacts`,
`variant.sources.*.addGeneratedSourceDirectory`,
`variant.instrumentation.transformClassesWith`, and lazy properties. Plugins
must compile against `gradle-api`; the `gradle` artifact will no longer expose
internal AGP classes.

Stage strict behavior on AGP 9.x with both flags:

```properties
android.newDsl=true
android.builtInKotlin=true
```

Starting in AGP 9.4.0-alpha04,
`android.newDsl.optOut=:lib` can temporarily exempt named modules, but the
exemption disappears in AGP 10. A module without Kotlin can use
`android { enableKotlin = false }` to omit its Kotlin compiler task and
standard-library dependency.
