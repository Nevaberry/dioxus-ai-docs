---
name: ios-sdk-knowledge-patch
description: iOS SDK
version: iOS 26 / Xcode 26
license: MIT
metadata:
  author: Nevaberry
---


# iOS SDK Compatibility Guidance

Use this skill when maintaining, rebuilding, or migrating Apple-platform code
whose behavior depends on recent iOS SDKs or Xcode toolchains. It is especially
useful for SDK-linked behavior changes, Swift concurrency diagnostics, StoreKit,
network security, text and scene behavior, C/C++ interoperability, and test or
distribution failures.

## How to use this skill

1. Identify the Xcode version, SDK used to build, deployment target, and runtime.
2. Separate compile-time or link-time failures from SDK-linked runtime behavior.
3. Check deprecations and removals before applying a compatibility workaround.
4. Open the topic reference that matches the affected subsystem.
5. Test both an existing binary and a fresh rebuild when behavior is SDK-linked.

Do not infer behavior solely from the runtime OS. Several changes below activate
only when an app is linked against a newer SDK, while other fixes belong to a
specific Xcode-bundled Simulator runtime.

## Reference index

| Reference | Topics |
| --- | --- |
| [Commerce, distribution, and services](references/commerce-distribution-and-services.md) | StoreKit, AdAttributionKit, enterprise apps, Background Nearby Interaction, Broadcast Extensions, Push to Talk, App Store uploads |
| [Language, runtime, and interoperability](references/language-runtime-and-interop.md) | Swift concurrency and modules, Objective-C races, C and C++ compatibility, fileports, semaphores, formatting |
| [Networking, data, and security](references/networking-data-and-security.md) | URLSession, TLS, IKEv2, Core Data, libxml2, Metal residency |
| [Toolchain, build, and testing](references/toolchain-build-and-testing.md) | Xcode requirements, device support, linker behavior, Simulator limits, package builds, diagnostics, Swift Testing |
| [UI, text, scenes, and documents](references/ui-text-scenes-and-documents.md) | SwiftUI, UIKit, TextKit, Writing Tools, navigation, gestures, layout and text direction |

## Breaking changes and required migrations

### Remove obsolete Core Data ubiquity options

New SDK builds reject the old `NSPersistentStoreUbiquitous*` options and related
metadata-removal option. Remove them, preserve the local store, and migrate cloud
synchronization to `NSPersistentCloudKitContainer` or SwiftData. See the data
reference for the full key list and build-dependent behavior.

### Keep managed objects within their context

The current Core Data imports expose `NSManagedObject` as nonisolated and
non-`Sendable`, while contexts are `Sendable` and `perform` closures are
`Sendable`. Treat a managed object as context-confined rather than silencing new
concurrency diagnostics. Use `-com.apple.CoreData.ConcurrencyDebug 1` to expose
violations during testing.

### Replace deprecated StoreKit entitlement lookup

Replace `Transaction.currentEntitlement(for:)` with
`Transaction.currentEntitlements(for:)`. The singular API can omit
family-shared transactions. Also do not treat introductory-offer ineligibility
as meaningful when no App Store account is signed in.

### Update localized text construction

When interpolating a nonlocalized value into `LocalizedStringResource`,
`String(localized:)`, or `AttributedString(localized:)`, supply a localized value
or deliberately use `String(describing:)`. Replace `Text` concatenation with
interpolation so translators can reorder the content.

### Replace legacy platform and entitlement APIs

- Replace `UIScreen.mainScreen` with a screen obtained from the relevant scene or
  window context.
- Move apps from the unrestricted VoIP PushKit Push to Talk entitlement to the
  Push to Talk framework.
- Replace libxml2 custom allocation calls and allocator configuration with the
  system allocation functions.

### Audit C++ ABI boundaries

Rebuilding with Xcode 26 can change layouts involving `std::unordered_map`,
`std::unordered_set`, their multi variants, or `std::deque` when empty allocator
or `[[no_unique_address]]` relationships are involved. Do not pass affected
types across binary boundaries without rebuilding and validating both sides.

## SDK-linked behavior checks

### Network security

Apps linked on or after iOS 26 default `URLSession` and Network framework
connections to TLS 1.2. Prefer upgrading legacy endpoints. If transition support
is unavoidable, set the minimum explicitly with
`URLSessionConfiguration.tlsMinimumSupportedProtocolVersion` or
`sec_protocol_options_set_min_tls_protocol_version`.

IKEv2 profiles and servers must also avoid DES, 3DES, SHA1-96, SHA1-160, and
Diffie-Hellman groups below 14.

### Text direction

`Text`, `TextEditor`, and `TextField` infer each paragraph's base writing
direction from its content in new SDK builds. Set
`AttributedString.writingDirection` per paragraph or apply
`.writingDirection(strategy: .layoutBased)` when layout direction should win.

TextKit 2 indentation follows the resolved paragraph direction under the same
SDK-linked behavior; compare old and newly linked binaries before treating a
difference as a regression.

### Picker, navigation, and gesture behavior

- Button-like `Picker` styles use fitted sizing; call `buttonSizing(_:)` when the
  picker should fill its container.
- `NavigationLink` is a single view in list contexts. Put
  `containerValue(_:_:)` outside the link if the value must propagate.
- Use `highPriorityGesture(_:isEnabled:)` to precede a native recognizer and
  `simultaneousGesture(_:isEnabled:)` for equal priority.

## High-value additions

### Opt into the new URL loading mode

The new HTTP loading path is opt-in through the configuration:

```swift
let configuration = URLSessionConfiguration.default
configuration.usesClassicLoadingMode = false
let session = URLSession(configuration: configuration)
```

Exercise representative redirects, authentication, caching, uploads, and proxy
paths before changing an app-wide session factory.

### Apply StoreKit offer controls and metadata

Advanced Commerce purchase support and
`introductoryOfferEligibility(compactJWS:)` allow a server-signed compact JWS to
request or block introductory-offer redemption. Account for the newer
`appTransactionID`, `originalPlatform`, and `period` metadata, and use
`AppStore.Platform`; its platform model combines watchOS with iOS.

### Use section actions and control-size ranges

`sectionActions(content:)` attaches actions to a `Section`. They remain trailing
on macOS but render as individual form rows on iOS and iPadOS. `ControlSize` is
also `Comparable`, and `controlSize(_:)` can clamp the environment to a range.

### Support background UWB ranging

An active Live Activity permits Nearby Interaction Ultra Wideband ranging while
the app is in the background. Design the activity lifecycle and ranging session
together so the background capability is not assumed after the activity ends.

### Exercise Swift Testing termination paths

Swift Testing exit tests cover code that invokes `precondition()`,
`fatalError()`, or otherwise terminates its process. Save attachments to a known
directory with:

```sh
swift test --attachments-path <directory>
```

## Toolchain triage

### Confirm host and device floors first

Before debugging an installation or launch failure, verify the host macOS floor,
the SDK bundled with the selected Xcode, and the minimum OS supported for device
debugging. These constraints changed between Xcode 16.3, 16.4, and 26; the exact
matrix is in the toolchain reference.

### Distinguish known tool failures

- Safari extensions are absent from iOS and visionOS Simulator; use a device.
- The Xcode 16.3 `-stack_size` linker failure can affect app-bundle targets.
- Xcode 16.4 fixes iOS 18.3 Simulator `NSURLSession` requests that always timed
  out.
- `devicectl diagnose` collects from the Mac and every available device by
  default, so plan for broader collection time and output.

### Control explicit modules deliberately

Swift explicit modules are enabled by default for most Swift targets in Xcode
26, except pre-Swift-5 language modes and Swift/C++ interoperability. For a
severe compatibility failure, `SWIFT_ENABLE_EXPLICIT_MODULES=NO` is a temporary
escape hatch; diagnose the incompatible dependency before keeping the opt-out.

### Preview the shared package builder carefully

Enable the preview package build implementation with:

```sh
defaults write com.apple.dt.Xcode IDEEnableNewPackagePIFBuilder -bool YES
```

Keep the setting explicit in reproduction notes because this builder is a
preview and is intended to become the default later.

## Verification checklist

- Rebuild cleanly with the target Xcode and record the SDK actually selected.
- Run concurrency checks around Core Data and nonatomic Objective-C properties.
- Test localized, right-to-left, and mixed-direction text with the rebuilt app.
- Exercise TLS and IKEv2 endpoints against the stronger defaults.
- Validate StoreKit with signed-in, signed-out, and family-sharing scenarios.
- Test Simulator-only failures on a physical device where the limitation says
  the Simulator is insufficient.
- Recheck C++ layouts and linked binary compatibility after a toolchain change.
- Confirm distribution builds meet the current App Store SDK requirement.
