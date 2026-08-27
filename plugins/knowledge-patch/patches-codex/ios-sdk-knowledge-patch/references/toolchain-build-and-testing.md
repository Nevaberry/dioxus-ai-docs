# Toolchain, Build, and Testing

## Xcode, SDK, and Host Compatibility

### Xcode 16.3

Xcode 16.3 bundles the iOS and iPadOS 18.4 SDKs and requires macOS Sequoia
15.2 or later. On-device debugging supports iOS and tvOS 15 or later, watchOS 7
or later, and visionOS.

### Xcode 16.4

Xcode 16.4 bundles the iOS and iPadOS 18.5 SDKs and requires macOS Sequoia
15.3 through macOS Tahoe 26.1.

### Xcode 26

Xcode 26 bundles Swift 6.2 and the iOS, iPadOS, tvOS, watchOS, macOS Tahoe, and
visionOS 26.0 SDKs. It requires macOS Sequoia 15.6 or later. On-device debugging
supports iOS and tvOS 15 or later, watchOS 8 or later, and visionOS.

## Compiler and Build Defaults

### Swift Explicit Modules Are Enabled by Default

Xcode 26 enables Swift explicit modules by default for Swift targets. Targets
using a pre-Swift-5 language version or Swift/C++ interoperability are exempt.
For a severe compatibility failure, temporarily set:

```text
SWIFT_ENABLE_EXPLICIT_MODULES=NO
```

Use the opt-out to unblock diagnosis, then address the incompatible dependency
or build assumption.

### Preview the Shared Swift Package Builder

Xcode 26 includes a preview package builder shared with Swift Package Manager;
it is planned to become the default later. Enable it with:

```sh
defaults write com.apple.dt.Xcode IDEEnableNewPackagePIFBuilder -bool YES
```

Exercise package builds in CI-like conditions before adopting the preview for
critical workflows.

## Linking and Runtime Loading

### Drop the Obsolete Debug-Dylib Workaround

With Xcode 16.3, using `LD_CLIENT_NAME` no longer requires
`ENABLE_DEBUG_DYLIB=NO` to avoid the missing debug-dylib runtime crash. Remove
the workaround when it exists only for that defect.

The `-stack_size` linker flag can still fail for an app-bundle target in Xcode
16.3; do not assume the same release resolves that separate linker issue.

## Diagnostics and Simulator Behavior

### Expect `devicectl diagnose` to Collect Every Device

In Xcode 16.4, running the command below obtains a sysdiagnose from the Mac and
all available devices by default:

```sh
devicectl diagnose
```

Account for collection time, output volume, and the broader device scope.

### Use the Correct Runtime for the URLSession Fix

Xcode 16.4 fixes the iOS 18.3 Simulator defect in which `NSURLSession` requests
always timed out and failed. Confirm the failing test actually uses the fixed
runtime.

## Swift Testing

### Test Exiting Code Paths

Swift Testing in Xcode 26 adds exit tests for code that invokes
`precondition()`, `fatalError()`, or otherwise terminates the test process.

### Choose the Attachment Directory

Pass an explicit output directory when running Swift tests:

```sh
swift test --attachments-path <directory>
```

This selects where Swift Testing attachments are saved.
