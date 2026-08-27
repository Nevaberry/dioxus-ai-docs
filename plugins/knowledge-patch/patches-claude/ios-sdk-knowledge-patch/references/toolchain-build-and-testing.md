# Toolchain, Build, and Testing

## Xcode compatibility and device support

### Xcode 16.3 requirements (18.4)

Xcode 16.3 bundles the iOS and iPadOS 18.4 SDKs and requires macOS Sequoia 15.2
or later. On-device debugging supports iOS and tvOS 15 or later, watchOS 7 or
later, and visionOS.

### Xcode 16.4 requirements (18.5)

Xcode 16.4 bundles the iOS and iPadOS 18.5 SDKs. Its supported host range is
macOS Sequoia 15.3 through macOS Tahoe 26.1.

### Xcode 26 requirements (26.0)

Xcode 26 bundles Swift 6.2 and the iOS, iPadOS, tvOS, watchOS, macOS Tahoe, and
visionOS 26 SDKs. It requires macOS Sequoia 15.6 or later. On-device debugging
supports iOS and tvOS 15 or later, watchOS 8 or later, and visionOS.

Check this matrix before diagnosing unavailable runtimes, unsupported devices,
or a host installation failure.

## Linking and module builds

### Debug dylib and `LD_CLIENT_NAME` (18.4)

Using `LD_CLIENT_NAME` no longer needs the `ENABLE_DEBUG_DYLIB=NO` workaround
for the missing debug-dylib runtime crash. Remove the workaround unless another
independent issue requires it.

### App-bundle stack size failure (18.4)

The `-stack_size` linker flag can still fail for an app-bundle target in Xcode
16.3. Treat this as a toolchain-specific linker limitation when it reproduces
only for that target and version.

### Swift explicit modules (26.0)

Xcode 26 enables Swift explicit modules by default except for targets using a
pre-Swift-5 language version or Swift/C++ interoperability. For a severe
compatibility issue, temporarily set `SWIFT_ENABLE_EXPLICIT_MODULES=NO` while
isolating the incompatible module.

## Package builds

### Preview shared package builder (26.0)

Xcode 26 previews a package builder shared with Swift Package Manager. It is
planned to become the default later. Enable the preview with:

```sh
defaults write com.apple.dt.Xcode IDEEnableNewPackagePIFBuilder -bool YES
```

Record this user default in bug reports and build reproductions because it
changes the selected implementation.

## Simulator and device testing

### Safari extensions require a device (18.4)

Safari extensions do not appear in the iOS or visionOS Simulator. Test the
extension on a physical device for those platforms.

### URLSession timeout fix (18.5)

Xcode 16.4 fixes the iOS 18.3 Simulator runtime defect that made
`NSURLSession` requests always time out and fail. Upgrade the toolchain/runtime
before debugging application networking for this exact symptom.

## Diagnostics

### Broad `devicectl diagnose` collection (18.5)

`devicectl diagnose` now collects a sysdiagnose from the Mac and all available
devices by default:

```sh
devicectl diagnose
```

Expect broader output and collection scope even when no device arguments are
supplied.

### Core Data concurrency checks (26.0)

Pass `-com.apple.CoreData.ConcurrencyDebug 1` when testing managed-object access.
The iOS 26 SDK's concurrency annotations can expose warnings during rebuilds,
and the runtime diagnostic helps distinguish real context violations.

## Swift Testing

### Exit tests and attachment output (26.0)

Swift Testing supports exit tests for code that invokes `precondition()`,
`fatalError()`, or otherwise terminates the test process. Use
`--attachments-path` to select the attachment output directory:

```sh
swift test --attachments-path <directory>
```
