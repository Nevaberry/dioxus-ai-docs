# Packages, builds, and platforms

Package, build, and platform additions from batches `6.1-guide`, `6.1`, `6.2-language`, `6.2`, `6.3-embedded-and-c`, and `6.3`.

## Contents

- [SwiftPM package traits](#swiftpm-package-traits)
- [Diagnostic severity](#diagnostic-severity)
- [Build systems and generated inputs](#build-systems-and-generated-inputs)
- [Package libraries and macros](#package-libraries-and-macros)
- [Installation and platform SDKs](#installation-and-platform-sdks)

## SwiftPM package traits

With `// swift-tools-version: 6.1`, declare feature-like traits, select defaults, and compose a trait by enabling other local traits. Enabled local traits become compilation conditions such as `#if Bar`.

```swift
let package = Package(
    name: "FooLib",
    traits: [
        .default(enabledTraits: ["Bar"]),
        .init(name: "Bar", description: "Bar support"),
        .init(name: "Baz", enabledTraits: ["Bar"]),
    ],
    targets: [.target(name: "FooLib")]
)

#if Bar
public func bar() -> String { "bar" }
#endif
```

Consumers get default traits when they omit `traits`, can request them explicitly with `.defaults`, or can replace them with named selections. Enable dependency traits conditionally from local traits. A target product dependency can use `.when(platforms:traits:)`.

```swift
.package(path: "../foo-lib", traits: [
    .init(name: "Baz", condition: .when(traits: ["MyBazFlag"]))
])
```

Only a package's own traits can be tested with `#if`. Mirror a dependency trait into a local trait when consuming source also needs conditional compilation. Trait names are namespaced per package. Avoid mutually exclusive traits because they can disrupt package-graph resolution.

Select trait configurations for `swift build`, `swift test`, or `swift run`:

```sh
swift build --traits Bar,Baz
swift test --enable-all-traits
swift run --disable-default-traits
```

Since SwiftPM 6.3, run `swift package show-traits` to list a package's supported traits.

## Diagnostic severity

### Compiler controls

Since 6.1, pass `-print-diagnostic-groups` to display names such as `DeprecatedDeclaration`. Promote one group with `-Werror DeprecatedDeclaration` or retain warning severity with `-Wwarning DeprecatedDeclaration`.

Flag order is significant. Place `-warnings-as-errors` relative to group-specific overrides deliberately. In Xcode custom flags, enter the option and group name as separate arguments.

### SwiftPM controls

Since 6.2, a package manifest can configure diagnostic-group warning and error levels directly rather than relying on raw compiler flags. For example, Embedded Swift restrictions can be checked in a normal build:

```swift
swiftSettings: [
    .treatWarning("EmbeddedRestrictions", as: .warning),
]
```

## Build systems and generated inputs

### SwiftBuild preview

SwiftPM 6.3 can preview its next-generation build system with `--build-system swiftbuild`. The native build system remains the default. The option works with build, test, and run without manifest changes.

```sh
swift build --build-system swiftbuild
swift test --build-system swiftbuild
swift run --build-system swiftbuild MyExecutable
```

### Generated C-module inputs

SwiftPM 6.3 can experimentally accept plugin-generated C sources, module maps, headers, and API notes for a C module target. Opt in on the consuming package's tools-version line. The feature works with the native build system and SwiftBuild.

```swift
// swift-tools-version: 6.3;(experimentalCGen)
```

A target can have only one generated module map and cannot also provide a module map in its public headers path. Headers and API notes referenced by the generated map must share its directory. Generated public headers are found under the fixed `include` directory in the plugin output; that directory is also added for transitive dependents.

## Package libraries and macros

### Concurrency-friendly subprocesses

The `Subprocess` package provides async APIs for launching and managing external processes, including arguments, captured output, and platform-specific configuration. Its initial API is version 0.1 and can change before 1.0.

```swift
import Subprocess

let result = try await run(
    .path(FilePath("/usr/bin/swift")),
    arguments: ["--version"]
)
let swiftVersion = result.standardOutput
```

### Shared macro implementation libraries

Since 6.3, SwiftPM supports factoring common macro implementation code into a library used only by macros. That shared library can use prebuilt `swift-syntax` binaries.

## Installation and platform SDKs

### Swift 6.1 installation

Swift 6.1 ships with Xcode 16.3. For a standalone toolchain on macOS or Linux, use `swiftly`; the Swift installation documentation covers other supported methods, including Windows.

### WebAssembly

Swift 6.2 supports WebAssembly builds for client and server applications targeting browsers or other Wasm runtimes.

### Android

Swift 6.3 ships the first official Swift SDK for Android for native Swift programs and Android-compatible package builds. Existing Kotlin or Java applications can integrate Swift through Swift Java and Swift Java JNI Core.
