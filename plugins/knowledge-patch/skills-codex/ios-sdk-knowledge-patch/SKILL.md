---
name: ios-sdk-knowledge-patch
description: iOS SDK
version: iOS 26 / Xcode 26
license: MIT
metadata:
  author: Nevaberry
---


# iOS SDK Knowledge Patch

Use this skill when building, reviewing, testing, or upgrading applications
against recent iOS SDKs and Xcode toolchains. Start with the compatibility
checks below, then open the topic reference that matches the affected code.

## How to Apply This Patch

1. Inspect the Xcode version, base SDK, deployment target, linked-on SDK, Swift
   language mode, and device OS before changing code.
2. Distinguish an SDK-linked behavior change from a runtime change. Several
   behaviors below affect only binaries rebuilt with a newer SDK.
3. Audit removals and deprecations before adopting new APIs or build defaults.
4. Reproduce issues with the same SDK and toolchain used by CI and distribution.
5. Prefer the project's manifests, compiler diagnostics, tests, and observed
   behavior if they conflict with this guidance.

## Reference Index

| Reference | Topics |
| --- | --- |
| [C++, Swift interop, and language runtime](references/cpp-and-language-interop.md) | C and C++ compatibility, libxml2 allocators, Swift interop, spans, ABI changes, and Objective-C race detection |
| [Graphics, media, and spatial APIs](references/graphics-media-and-spatial.md) | Nearby Interaction, broadcast extensions, and Metal residency |
| [Networking, security, and distribution](references/networking-security-and-distribution.md) | HTTP loading, TLS and VPN policy, entitlements, enterprise recovery, Safari extensions, attribution, and App Store uploads |
| [Persistence, Foundation, and commerce](references/persistence-foundation-and-commerce.md) | Core Data, StoreKit, ISO-8601 parsing, fileports, and named semaphores |
| [SwiftUI, UIKit, and text](references/swiftui-uikit-and-documents.md) | Localization, navigation, gestures, text direction, Writing Tools, picker sizing, and screen APIs |
| [Toolchain, build, and testing](references/toolchain-build-and-testing.md) | Xcode host and device requirements, explicit modules, linking, package builds, diagnostics, Simulator fixes, and Swift Testing |

## Breaking Changes and Required Migrations

### Remove Core Data Ubiquity Options

When building with the newer SDK, the legacy Core Data ubiquity option keys are
errors rather than warnings. Remove those keys and migrate synchronization to
`NSPersistentCloudKitContainer` or SwiftData. Removing the keys preserves the
local store but stops its synchronization.

See [Persistence, Foundation, and commerce](references/persistence-foundation-and-commerce.md)
for the complete key list and concurrency-import changes.

### Replace the Legacy Push to Talk Entitlement

Applications built with the newer SDK cannot use
`com.apple.developer.pushkit.unrestricted-voip.ptt`. Migrate to the Push to Talk
framework rather than carrying the entitlement forward.

### Raise Legacy Network Security Floors

Newly linked applications default to TLS 1.2 for `URLSession` and Network
framework connections. IKEv2 also drops DES, 3DES, SHA1-96, SHA1-160, and
Diffie-Hellman groups below 14. Update endpoints, VPN profiles, and VPN servers;
use an explicit minimum protocol only when a legacy endpoint cannot yet move.

### Stop Using libxml2 Custom Allocators

Replace libxml2 allocation functions with the system `malloc`, `realloc`,
`free`, and `strdup` family. Remove `xmlMemSetup`, `xmlMemGet`, `xmlGcMemSetup`,
`xmlGcMemGet`, and related allocator globals because libxml2 and libxslt now use
the system allocator internally.

### Use the Plural StoreKit Entitlement API

Replace `Transaction.currentEntitlement(for:)` with
`Transaction.currentEntitlements(for:)`. The singular API can omit
family-shared transactions. Also require an App Store sign-in before treating
`isEligibleForIntroOffer(for:)` as a meaningful eligibility result.

### Fix Localization-Sensitive Text Construction

Do not interpolate a nonlocalized value directly into `LocalizedStringResource`,
`String(localized:)`, or `AttributedString(localized:)`. Supply a localized value
or explicitly use `String(describing:)` for an intentional description. Replace
SwiftUI `Text` concatenation with interpolation so translations can reorder
content.

### Audit SDK-Linked SwiftUI Behavior

For rebuilt applications, paragraph direction is content-based, button-like
pickers use fitted sizing, and a `NavigationLink` produces one view instead of a
view list in list contexts. Explicitly configure writing direction or button
sizing where required, and move escaping `containerValue(_:_:)` modifiers
outside the link.

### Keep Indirect Metal Pipelines Resident

With Metal 4 command encoders, add render and compute pipelines that support
indirect command buffers to the residency set. Do this even when the current
driver appears to tolerate a missing residency declaration.

## Build and Runtime Compatibility

### Match Xcode to Its Host

Xcode 16.3 requires macOS Sequoia 15.2 or later. Xcode 16.4 requires macOS
Sequoia 15.3 through macOS Tahoe 26.1. Xcode 26 requires macOS Sequoia 15.6 or
later. Keep local and CI hosts within the selected Xcode release's supported
range.

### Respect Device Debugging Floors

Xcode 16.3 supports on-device debugging for iOS and tvOS 15 or later, watchOS 7
or later, and visionOS. Xcode 26 raises the watchOS floor to 8 while retaining
the iOS and tvOS 15 floors.

### Account for Explicit Swift Modules

Swift explicit modules are enabled by default for Swift targets, except for
targets using a pre-Swift-5 language version or Swift/C++ interoperability. If a
severe compatibility issue blocks a build, use
`SWIFT_ENABLE_EXPLICIT_MODULES=NO` as a temporary opt-out while fixing it.

### Treat C++ Container Layout as ABI-Sensitive

The toolchain can change the layout of `std::unordered_map`,
`std::unordered_set`, their multi variants, and `std::deque` when rebound
allocators share an empty base. Enclosing layouts can also change when an empty
allocator, comparator, or hasher is reused through `[[no_unique_address]]` or
empty inheritance. Rebuild ABI boundaries together and avoid persisting such
layouts.

### Diagnose Core Data Concurrency

The imported concurrency annotations make `NSManagedObject` non-`Sendable` and
`NSManagedObjectContext` `Sendable`; context `perform` closures are also
`Sendable`. Keep managed objects inside their context's scope, and launch with
`-com.apple.CoreData.ConcurrencyDebug 1` to catch violations.

### Recognize Nonatomic Property Races

A synthesized Objective-C nonatomic setter may temporarily store the sentinel
`0x400000000000bad0` (`0xbad0` on 32-bit watchOS). A concurrent read that crashes
on this value points to unsafe simultaneous property access.

## High-Value API Changes

### Opt In to the New HTTP Loading Mode

Set `usesClassicLoadingMode` to `false` on a `URLSessionConfiguration` to test
the new HTTP loader before it becomes the default:

```swift
let configuration = URLSessionConfiguration.default
configuration.usesClassicLoadingMode = false
let session = URLSession(configuration: configuration)
```

### Use StoreKit's Expanded Commerce Metadata

Advanced Commerce purchases and
`introductoryOfferEligibility(compactJWS:)` are available. New transaction data
includes `appTransactionID`, `originalPlatform`, and `period`; the platform type
is `AppStore.Platform`, and the former `watchOS` case is folded into `iOS`.

### Use SwiftUI Control and Section APIs

`ControlSize` is comparable, and `controlSize(_:)` accepts a range that clamps
the environment value. `sectionActions(content:)` adds section actions; they
remain trailing on macOS and become individual form rows on iOS and iPadOS.

### Select Gesture Priority Explicitly

Use `highPriorityGesture(_:isEnabled:)` when a SwiftUI gesture must precede a
native UIKit or AppKit recognizer. Use `simultaneousGesture(_:isEnabled:)` when
both should receive equal priority.

### Exercise Swift Testing Exit Paths

Swift Testing can test code paths that terminate through `precondition()`,
`fatalError()`, or another process exit. Use
`swift test --attachments-path <directory>` to control attachment output.

### Use Background Nearby Interaction Deliberately

An application with an active Live Activity can perform Ultra Wideband ranging
through Nearby Interaction while backgrounded. Tie background ranging to the
Live Activity's active lifetime.

## Common Diagnostic Traps

- Safari extensions are absent from iOS and visionOS Simulator; test them on a
  device.
- An iOS 18.3 Simulator runtime used with Xcode 16.4 includes the fix for
  `NSURLSession` requests that otherwise always timed out.
- `isEligibleForIntroOffer(for:)` returns `false` when no App Store account is
  signed in.
- `ISO8601FormatStyle` accepts fractional seconds regardless of the
  `includingFractionalSeconds` setting.
- `UIScreen.mainScreen` is deprecated; audit existing uses and avoid adding new
  dependencies on it.
- The generic `std::char_traits` base template is temporarily restored but
  remains deprecated and should not anchor new code.
- `devicectl diagnose` collects a sysdiagnose from the Mac and every available
  device by default; account for the broader collection scope.

## Distribution Check

Before uploading, verify that the archive was produced with an accepted Xcode
and platform SDK. Current App Store submission requirements are detailed in
[Networking, security, and distribution](references/networking-security-and-distribution.md).
