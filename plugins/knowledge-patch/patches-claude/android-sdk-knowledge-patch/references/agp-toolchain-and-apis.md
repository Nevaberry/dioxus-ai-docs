# AGP Toolchain and Public APIs

Source batch: `agp-9-toolchain`.

## Toolchain compatibility

### Match AGP, Gradle, SDK, JDK, Build Tools, and NDK

AGP 9.0 supports through API 36.1 and requires Gradle 9.1.0. AGP 9.2
supports API 37.0 and requires Gradle 9.4.1. AGP 9.3 supports API 37 and
requires Gradle 9.5.0. All require JDK 17, use Build Tools 36.0.0, and default
to NDK 28.2.13676358 (`r28c`).

AGP 9.0 also makes a library's compile SDK the default minimum compile SDK for
consumers unless the publisher explicitly sets `AarMetadata.minCompileSdk`.

### Built-in Kotlin owns compiler integration

AGP 9.0 enables built-in Kotlin. Android modules must stop applying
`org.jetbrains.kotlin.android` or `kotlin-android`. AGP carries KGP 2.2.10 and
upgrades lower KGP versions and KSP versions below 2.2.10-2.0.2.

Supply a newer KGP as a top-level `buildscript` classpath dependency. A lower,
strictly constrained KGP—no lower than 2.0.0—requires opting out of built-in
Kotlin.

### KMP requires the dedicated Android integration

The new DSL cannot combine `org.jetbrains.kotlin.multiplatform` with
`com.android.application` or `com.android.library` in one subproject. Use the
Android Gradle Library Plugin for KMP. Move an Android application into a
separate subproject because the new KMP integration does not support the
application plugin in the KMP module.

### Shader compilation needs an explicit path

When shader compilation is enabled, set `glslc.dir=/path/to/shader-tools` in
`local.properties`. The old implicit lookup is available only by opting out of
`android.custom.shader.path.required` during migration.

## Public DSL and Variant API migration

### Replace legacy entry points

AGP 9.0 hides legacy DSL implementations and Variant API entry points. Use:

| Legacy API | Public replacement |
| --- | --- |
| `applicationVariants` and siblings | `androidComponents.onVariants` |
| `variantFilter` | `androidComponents.beforeVariants` |
| SDK path getters | `androidComponents.sdkComponents` |
| Custom test providers | Gradle-managed devices |

For example:

```kotlin
androidComponents {
    beforeVariants(selector().withBuildType("debug")) { it.enable = false }
}
```

`android.newDsl=false` can temporarily restore the old implementation for an
incompatible plugin, but AGP 10 removes this switch.

### Register sources lazily

Generated-source providers must use the `androidComponents` Sources API rather
than `AndroidSourceSet`. Build logic preparing for AGP 10 should use
`variant.sources.*.addGeneratedSourceDirectory` and avoid eager task or source
registration.

### Update reshaped DSL types and setters

`CommonExtension` is no longer parameterized. Invoke its block methods on a
concrete extension or through properties such as `defaultConfig.apply`.

Other required replacements are:

- `DependencyVariantSelection` becomes `DependencySelection` at
  `kotlin.android.localDependencySelection`.
- `Installation.installOptions(String)` becomes the mutable `installOptions`
  property.
- `ProductFlavor.setDimension` becomes the `dimension` property.
- `DensitySplit`, `LanguageSplitOptions`, and the experimental
  `PostProcessing` block are removed.

### Update plugin APIs

Bytecode transformation and ASM frame configuration moved from `Component` to
`Instrumentation`. `ComponentBuilder.enabled` became `enable`, while
`VariantOutput.enable` became `enabled`. The old `*SdkVersion` variant
properties became `minSdk`, `maxSdk`, or `targetSdk`.

Unit-test members are available only on `HasUnitTest` or
`HasUnitTestBuilder` subtypes. `BaseExtension.registerTransform` is removed;
use instrumentation transforms.

## Changed Android defaults

### Core module defaults

AGP 9.0 makes these changes:

- Library package names must be unique.
- AndroidX is the default dependency family.
- Application code compiles against a non-final `R`.
- An unset target SDK defaults to the compile SDK, not the minimum SDK.
- `resValues` is disabled unless enabled per module.

Audit implicit behavior before upgrading, especially target SDK and generated
resource assumptions.

### Test and dependency defaults

On-device tests default to `AndroidJUnitRunner`. Only the tested build type gets
a unit-test component by default—normally debug, not both debug and release.

`android.dependency.useConstraints` defaults to `false`, restricting dependency
constraints to application device tests unless the old behavior is explicitly
restored.

### Module-level feature flags

The global `android.defaults.buildfeatures.aidl` and
`android.defaults.buildfeatures.renderscript` properties are removed. Enable
`aidl` or `renderScript` only in modules that need them.

AGP 9.0 rejects `android.r8.integratedResourceShrinking` and
`android.enableNewResourceShrinker.preciseShrinking`; integrated, precise
resource shrinking is mandatory.

## Packaging and publication

### Removed packaging and report features

AGP 9.0 removes embedded Wear OS apps and the `wearApp` configuration,
density-split APKs, and the `androidDependencies` and `sourceSets` report tasks.
Publish Wear apps separately and use app bundles for density delivery.

### Fuse libraries into one AAR

The preview Fused Library Plugin can package several Android libraries into one
published Android Library AAR. Treat it as a preview capability when deciding
whether to use it in a stable publication pipeline.

## Preparing build logic for AGP 10

### Remove all legacy coupling

AGP 10's planned lazy build system removes `android.newDsl`,
`android.builtInKotlin`, legacy extensions and Variant APIs, direct task access,
eager generated-source registration, and the Transform API.

Use `Variant.artifacts`, `variant.sources.*.addGeneratedSourceDirectory`,
`variant.instrumentation.transformClassesWith`, and lazy properties. Compile
plugins against `gradle-api`; the `gradle` artifact will no longer expose
internal AGP classes.

### Stage strict behavior on AGP 9.x

Enable both modern-mode flags to test stricter behavior:

```properties
android.newDsl=true
android.builtInKotlin=true
```

Beginning with AGP 9.4.0-alpha04,
`android.newDsl.optOut=:lib` can temporarily exempt named modules, but the
option disappears in AGP 10. A module without Kotlin can use
`android { enableKotlin = false }` to avoid creating the Kotlin compiler task
and adding the standard-library dependency.
