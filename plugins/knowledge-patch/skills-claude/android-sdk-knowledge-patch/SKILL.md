---
name: android-sdk-knowledge-patch
description: Android SDK
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Android SDK Knowledge Patch

Use this skill when updating Android applications, libraries, build logic, or
Play delivery settings where recent platform and Android Gradle Plugin behavior
can affect compatibility. Check the project's `compileSdk`, `targetSdk`,
`minSdk`, AGP, Gradle, JDK, Kotlin, KSP, NDK, and form factors before applying
target-gated guidance.

Prefer the project's manifests, build files, tests, and observed runtime
behavior when they differ from general guidance. Distinguish changes affecting
all apps on a platform release from changes gated by `targetSdk`.

## Reference index

| Reference | Topics |
| --- | --- |
| [AGP toolchain and APIs](references/agp-toolchain-and-apis.md) | Toolchain floors, Kotlin, public DSL, Variant API, removed APIs, migration staging |
| [Bluetooth, media, and devices](references/bluetooth-media-and-devices.md) | Bluetooth, companions, health, camera, codecs, alarms, widgets, device integration |
| [Google Play target API policy](references/play-target-api-policy.md) | Submission floors, existing-app availability, extensions, exemptions |
| [R8, packaging, and testing](references/r8-packaging-and-testing.md) | Shrinking, keep rules, packaging, native compatibility, reports, profiling |
| [Runtime, UI, and scheduling](references/runtime-ui-and-scheduling.md) | Jobs, concurrency, back, edge-to-edge, large screens, IME, audio, desktop UI |
| [Security, networking, and data](references/security-networking-and-data.md) | Intents, LAN access, TLS, SMS, contacts, URI grants, Keystore, media access |

## Start with the compatibility gates

1. Read `compileSdk`, `targetSdk`, `minSdk`, AGP, Gradle, and JDK from the
   project rather than assuming they move together.
2. Identify device and form-factor scope: phone, tablet, desktop windowing,
   Wear OS, Android Auto, Automotive OS, TV, or XR.
3. Separate platform-wide behavior from target-gated behavior in tests.
4. Exercise compatibility flags only as temporary diagnostics; implement the
   durable behavior before raising the target SDK.
5. For build plugins, migrate to lazy public APIs before enabling stricter AGP
   behavior.

## Breaking platform behavior

### Scheduling and concurrency

- Android 16 expands job runtime quotas to visible-to-background work, active
  standby apps, and work beside foreground services. Inspect stop reasons and
  use user-initiated data-transfer jobs when appropriate.
- Keep `JobParameters` alive until `jobFinished()`. Abandoned timeouts report
  `STOP_REASON_TIMEOUT_ABANDONED` and repeated abandonment can reduce job
  frequency.
- API 36 targets receive at most one missed `scheduleAtFixedRate` invocation
  when returning to a valid lifecycle; do not expect a burst of catch-up runs.
- Android 17 can memory-limit apps on some devices, and API 37 targets receive
  a lock-free `MessageQueue`. Remove reflection over queue internals.
- API 37 targets cannot mutate `static final` fields through reflection or JNI.

### Navigation, windows, and configuration

- API 36 targets cannot disable edge-to-edge on Android 16. Remove
  `windowOptOutEdgeToEdgeEnforcement` and handle insets.
- Predictive back is the default for API 36 targets. Migrate legacy
  `onBackPressed` and `KEYCODE_BACK` handling to supported back APIs.
- On `sw600dp` and larger displays, API 36 targets generally lose orientation,
  resizeability, and aspect-ratio restrictions. The temporary opt-out ceases to
  work when targeting API 37.
- Android 17 no longer recreates activities by default for several input and
  desktop-related configuration changes. Opt in with
  `android:recreateOnConfigChanges` when resource reload depends on recreation.
- Android 17 does not restore prior IME visibility after recreation. Request it
  explicitly or use `windowSoftInputMode="stateAlwaysVisible"` when required.

### Permissions and protected data

- API 36 targets must replace broad body-sensor permissions with granular
  health permissions and provide the required privacy-rationale activity.
- API 37 targets must declare and request `ACCESS_LOCAL_NETWORK` for LAN
  discovery and connections, unless using the system-mediated picker.
- WebOTP messages are delayed from non-recipient apps on Android 17, and
  ordinary OTP-bearing SMS is also delayed for API 37 targets. Prefer SMS
  Retriever or SMS User Consent.
- API 37 targets must make native dynamic-code files read-only before
  `System.load()`.
- API 37 targets cannot read contact account columns directly from
  `ContactsContract.Data`; join through `RawContacts`.
- Detect and replace implicit URI grants before Android 18. Send intents need
  read grants; image capture needs both read and write grants.

## Breaking build behavior

### Align the AGP toolchain

- AGP 9.x requires JDK 17. Match each AGP release to its required Gradle,
  supported SDK, Build Tools, and NDK combination before changing build logic.
- AGP 9.0 enables built-in Kotlin. Stop applying
  `org.jetbrains.kotlin.android` or `kotlin-android` in Android modules and
  account for AGP-controlled KGP and KSP versions.
- KMP modules cannot combine the new Android DSL with the traditional Android
  application or library plugins. Use the KMP Android library integration and
  place Android applications in a separate subproject.

### Leave legacy DSL and Variant APIs

- Replace `applicationVariants` and sibling collections with
  `androidComponents.onVariants`.
- Replace `variantFilter` with `androidComponents.beforeVariants`.
- Obtain SDK paths from `androidComponents.sdkComponents`.
- Register generated sources through the `androidComponents` Sources API.
- Replace Transform API and direct task access with artifacts,
  instrumentation, sources, and lazy properties.
- Treat `android.newDsl=false` and built-in-Kotlin opt-outs as temporary AGP 9
  migration aids; AGP 10 removes the legacy escape hatches.

### Audit defaults and removed features

- Libraries require unique package names; AndroidX is the default dependency
  family; app code uses non-final `R`; and an unset target SDK defaults to the
  compile SDK.
- Enable `resValues`, AIDL, and RenderScript per module when needed.
- Missing keep files fail builds, optimized resource shrinking is enabled, and
  strict full-mode keep semantics do not preserve a default constructor unless
  the rule names it.
- Remove embedded Wear packaging, density splits, removed report tasks, and
  global resource-shrinker flags.
- Configure `glslc.dir` when shader compilation is enabled.

## High-value migration patterns

### Safe nested intent launch

Android 16 protects nested intent launches by default. Preserve that protection
unless a verified legitimate flow breaks. Only code compiled against API 36 can
call `removeLaunchSecurityProtection()`, and doing so restores the redirection
risk. Consider strict incoming matching:

```xml
<application android:intentMatchingFlags="enforceIntentFilter" />
```

Use a component-level `none` override only where necessary, or
`allowNullAction` when an absent action is intentionally accepted.

### Local-network migration

On Android 16, test LAN denial before enforcement:

```shell
adb shell am compat enable RESTRICT_LOCAL_NETWORK com.example.app
```

Reboot, then test TCP, UDP, multicast, broadcast, native sockets, denial, and
revocation. `NEARBY_WIFI_DEVICES` restores gated access during this test phase.
For API 37 targets, declare the dedicated permission:

```xml
<uses-permission android:name="android.permission.ACCESS_LOCAL_NETWORK" />
```

### R8 keep rules

Under strict full mode, retain required constructors explicitly:

```proguard
-keep class A { <init>(); }
```

When runtime-invisible annotations are required, name all three attributes
instead of using a wildcard:

```proguard
-keepattributes RuntimeInvisibleAnnotations,
                RuntimeInvisibleParameterAnnotations,
                RuntimeInvisibleTypeAnnotations
```

Use `.keep` files in `src/<variant>/keepRules/` for source-set-specific app,
library, or KMP consumer rules. Run `:app:analyzeReleaseR8Config` to inspect an
AGP 9.3 release configuration without producing an APK or bundle.

### Bluetooth read loops

API 37 RFCOMM input streams return `-1` on socket closure or connection loss.
Handle EOF explicitly:

```kotlin
while (true) {
    val count = input.read(buffer)
    if (count == -1) break
    consume(buffer, count)
}
```

Do not depend solely on `IOException` for disconnect detection.

## New capabilities worth adopting

- Use `PhotoPickerUiCustomizationParams` for a portrait photo-picker grid and
  remember that limited media access can revoke app-owned items immediately.
- Use `CameraCaptureSession.updateOutputConfigurations()` for live camera
  output-use-case changes; inspect RAW14, extension, and device-type APIs.
- Use the listener overload of `setExactAndAllowWhileIdle()` for in-process
  callbacks without a `PendingIntent`-associated long partial wakelock.
- Use complex IME text-change metadata for composition and candidate events;
  standard `TextView` handling is automatic for API 37 targets.
- Use `OPTION_APPWIDGET_DISPLAY_ID` and complex DP/SP padding for widgets on
  external displays.
- Consider companion Handoff, Medical Device and Fitness Tracker profiles,
  association-time extra permissions, and the session-scoped system location
  button where they fit the product.
- Use APK Signature Scheme v3.2 for hybrid classical and ML-DSA signing where
  the signing pipeline supports it.

## Verification checklist

- Test both old and raised target SDK behavior on representative platform
  releases and large-screen/device form factors.
- Exercise background jobs, audio, activity launches, alarms, and memory-limit
  exit diagnostics.
- Test accessibility, predictive back, insets, IME composition and visibility,
  physical-keyboard password entry, pointer capture, and custom notifications.
- Test LAN denial/revocation, ECH and certificate transparency, cleartext domain
  exceptions, contact queries, OTP flows, URI sharing, and key-limit failures.
- Build release variants with shrinking, retrace through the embedded mapping
  ID, and verify annotation retention and desugared-library keep behavior.
- Validate Play submission and availability requirements independently for each
  packaged form factor.
