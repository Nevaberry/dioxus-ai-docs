---
name: android-sdk-knowledge-patch
description: Android SDK
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Android SDK Knowledge Patch

Use this skill when upgrading an Android app's target SDK, adopting Android
Gradle Plugin 9.x, preparing for the next Android platform behavior changes,
or checking Google Play target-API requirements. Inspect the app manifest,
module build files, Gradle wrapper, JDK, NDK, native libraries, and affected
runtime flows before changing code.

## Reference index

| Reference | Topics |
| --- | --- |
| [AGP build toolchain](references/agp-build-toolchain.md) | Toolchain floors, public DSL and Variant API, built-in Kotlin, KMP, defaults, R8, packaging, and staged future migration |
| [Background work and lifecycle](references/background-work-and-lifecycle.md) | Job quotas, abandoned jobs, periodic scheduling, broadcasts, activity recreation, background launches and audio, alarms, and profiling |
| [Devices, Bluetooth, camera, and media](references/devices-bluetooth-camera-and-media.md) | Companion devices, Bluetooth, photo picker UI, camera, codecs, Handoff, time-zone events, and NPU access |
| [Networking, security, and native code](references/networking-security-and-native-code.md) | Intent hardening, LAN access, ECH, certificate transparency, cleartext, native loading, Keystore, signing, and HPKE |
| [Platform, UI, and runtime](references/platform-ui-and-runtime.md) | Edge-to-edge, back navigation, large screens, text and IME behavior, runtime internals, touch input, notifications, and desktop windows |
| [Play publishing policy](references/play-publishing-policy.md) | Submission floors, existing-app availability, extensions, and exemptions |
| [Privacy, permissions, and app data](references/privacy-permissions-and-data.md) | Health and location permissions, SMS OTP, contacts, MediaStore, URI grants, and limited photo access |

## Breaking migration checks

### Target-SDK behavior

- Treat edge-to-edge as mandatory at the newer target: remove the ignored
  opt-out and make every screen consume or draw behind insets deliberately.
- Replace legacy back dispatch with supported back APIs. Keep the manifest
  opt-out only as a short migration aid.
- Do not depend on orientation, aspect-ratio, or resizability restrictions on
  large screens. Test at `sw600dp` and in multi-window and desktop modes.
- Audit reflection and JNI: private `MessageQueue` access is unsupported, and
  mutation of `static final` fields fails.
- Decide explicitly whether affected configuration changes should recreate an
  activity. Keyboard visibility is no longer restored automatically after a
  recreation.
- Make files read-only before passing native dynamic code to `System.load()`.
- Update RFCOMM read loops to treat `-1` as end-of-stream.

### Permissions, privacy, and data

- Replace broad body-sensor permissions with granular health permissions and
  provide the required in-app privacy-policy rationale.
- Declare and request the LAN runtime permission for direct local-network
  discovery and connections; offer a system-mediated picker where suitable.
- Move OTP sign-in to SMS Retriever or SMS User Consent rather than depending
  on immediate broadcast or provider access.
- Join contact data to `RawContacts` for account columns, and make provider
  queries conform to strict column and grammar validation.
- Add explicit URI read flags for send intents and both read and write flags
  for image capture before implicit grants disappear.
- Treat app-owned photos as revocable when the user grants limited media
  access, and treat the MediaStore version only as an opaque change token.

### Background execution and lifecycle

- Re-evaluate jobs that begin while visible, run with a foreground service, or
  occupy the active standby bucket; runtime quotas cover these cases.
- Retain `JobParameters` until `jobFinished()` and inspect timeout stop reasons
  so abandoned work does not reduce future scheduling frequency.
- Do not expect fixed-rate scheduling to replay every missed invocation.
- Replace cross-process ordered-broadcast priority assumptions with an
  explicit coordination mechanism.
- Use granular background-activity launch modes for `IntentSender` flows.
- Start background playback only from an eligible lifecycle state and, where
  required, a while-in-use-capable foreground service.

## AGP 9.x migration

### Align the toolchain first

- Match the plugin to its required Gradle version and use JDK 17. Confirm the
  compile SDK, Build Tools, and NDK before diagnosing DSL or task failures.
- Remove `org.jetbrains.kotlin.android` or `kotlin-android` from Android
  modules that use built-in Kotlin. Account for AGP's KGP and KSP floors.
- Separate a KMP Android application into its own subproject and use the
  Android Gradle Library Plugin for the KMP library module.

### Replace legacy build APIs

- Replace `applicationVariants` and sibling collections with
  `androidComponents.onVariants`, and replace `variantFilter` with
  `beforeVariants`.
- Obtain SDK paths through `androidComponents.sdkComponents`; register
  generated sources through the Sources API; use Gradle-managed devices for
  custom test-device provisioning.
- Move bytecode transformations and frame configuration to
  `Instrumentation`, use lazy artifact and property APIs, and access unit-test
  members only through their unit-test-capable variant subtypes.
- Use the old-DSL switch only to unblock a plugin while migrating it. The
  legacy DSL, Variant APIs, direct task access, Transform API, and both major
  escape hatches are removed by the planned lazy build model.

### Recheck changed defaults

- Give every library a unique package namespace and review non-final `R`
  assumptions. An unset target SDK follows the compile SDK.
- Enable `resValues`, AIDL, or RenderScript per module when needed.
- Verify the default instrumentation runner, which build types receive unit
  tests, and the narrower dependency-constraint behavior.
- Supply every referenced keep file. Optimized resource shrinking and strict
  full-mode keep semantics are active; keep constructors explicitly when
  reflection requires them.
- Remove prohibited global optimizer options from published consumer rules,
  and remove invalid legacy resource-shrinker properties.
- Set `glslc.dir` explicitly when compiling shaders.
- Replace density splits with app bundles, publish Wear OS apps separately,
  and remove calls to deleted report tasks.

## R8 and keep-rule checks

- Select the Kotlin null-check policy deliberately with
  `-processkotlinnullchecks`; the strongest repeated setting wins.
- Keep desugared companion methods explicitly instead of relying on interface
  method propagation, and use TraceReferences for direct-tooling keep-rule
  analysis.
- Preserve retrace mapping IDs: a custom source-file rename takes precedence,
  and compatibility mode must not retain `SourceFile` if the embedded mapping
  ID is needed.
- Name runtime-invisible annotation attributes explicitly; wildcards do not
  retain them.
- Use negated R8 member patterns where appropriate, but do not back-reference
  wildcards from a negated `-if` precondition.
- Run the configuration-analyzer task for a report without producing an APK or
  bundle. Consider variant `.keep` source sets and the optimization DSL for
  app and library rules.

## Networking and security checks

- Keep nested-intent launch protection enabled. Remove it only on the exact
  nested intent in a legitimate flow that cannot otherwise work.
- Consider strict incoming-intent matching and explicitly opt components into
  null-action acceptance only where required.
- Test LAN denial and permission revocation, including native sockets. Do not
  confuse permissionless system-mediated discovery with direct socket access.
- Configure ECH and cleartext exceptions with Network Security Configuration.
  Retain the manifest cleartext flag only for the older minimum-SDK case.
- Expect certificate transparency at the newer target and test private or
  enterprise trust configurations.
- Inventory Keystore entries and handle the too-many-keys numeric error.
- Do not use loopback to communicate across profiles.
- Rebuild native libraries for 16 KB alignment even when compatibility mode
  can run an older binary.

## UI, input, and device checks

- Replace accessibility announcements with pane titles, live regions, and
  error-specific events.
- Recheck multilingual text layouts because elegant font height no longer
  selects compact font variants.
- Add an adaptive-icon monochrome layer to control synthesized themed icons.
- For custom password fields, observe the setting that distinguishes physical
  input from touchscreen input.
- Use the richer IME text metadata for custom composition flows; standard
  `TextView` handling is automatic.
- Request absolute pointer capture when raw touchpad finger positions matter.
- Test custom notification views against strict size constraints.
- Test camera live reconfiguration, newer image and extension formats, media
  codecs, BLE hearing-aid routing, display-aware widgets, and desktop pinned
  windows only on devices that advertise the relevant capability.

## Publishing check

Before release, classify each artifact by form factor and whether it is a new
submission, update, or existing listing. Check the corresponding target floor,
then use the Play Console warning flow if a temporary extension is needed.
Private organisational apps and bundled automotive form-factor apps have
specific exemptions; do not generalize those exemptions to public listings.
