---
name: swift-knowledge-patch
description: Swift
license: MIT
version: 6.3.0
metadata:
  author: Nevaberry
---

# Swift 6.1–6.3 Knowledge Patch

Baseline: Swift through 6.0 (typed throws, `~Copyable` generics, data-race safety, Swift Testing, Embedded Swift preview, and 128-bit integers). Covered range: Swift 6.1 through 6.3.0.

## Reference index

| Reference | Topics |
| --- | --- |
| [language-and-library.md](references/language-and-library.md) | Syntax, key paths, memory safety, borrowing, `InlineArray`, `Span`, observation, regex, ABI and optimization controls |
| [concurrency.md](references/concurrency.md) | Approachable Concurrency, actor isolation, executor behavior, task APIs, Objective-C concurrency imports, typed notifications |
| [testing-documentation-and-tools.md](references/testing-documentation-and-tools.md) | Swift Testing, XCTest, DocC, SourceKit-LSP, VS Code, LLDB |
| [packages-builds-and-platforms.md](references/packages-builds-and-platforms.md) | SwiftPM traits, warning policy, subprocesses, SwiftBuild, generated C inputs, macros, WebAssembly, Android |
| [c-family-interop.md](references/c-family-interop.md) | Objective-C implementation, strict C++ lifetime annotations, safe wrappers, `@c`, C modules and API notes |
| [embedded-swift.md](references/embedded-swift.md) | Embedded library coverage, restriction diagnostics, MMIO, debugging, object sections and linkage |

Coverage batches: `6.1-guide`, `6.1`, `6.2-approachable-concurrency`, `6.2-language`, `6.2-interop-and-testing`, `6.2`, `6.3-embedded-and-c`, and `6.3`.

## Breaking changes, migrations, and deprecations

### Choose executor behavior deliberately

Approachable Concurrency can change where async code runs. New Xcode projects enable it, but existing projects opt in. For SwiftPM 6.2, migrate one component at a time if fix-its must preserve current behavior:

```swift
.target(
    name: "AppCore",
    swiftSettings: [
        .enableUpcomingFeature("DisableOutwardActorInference"),
        .enableUpcomingFeature("GlobalActorIsolatedTypesUsability"),
        .enableUpcomingFeature("InferIsolatedConformances"),
        .enableUpcomingFeature("InferSendableFromCaptures"),
        .enableUpcomingFeature("NonisolatedNonsendingByDefault"),
    ]
)
```

With `NonisolatedNonsendingByDefault`, a nonisolated async function stays on the caller's actor. Spell that behavior as `nonisolated(nonsending)` in any language mode. Use `@concurrent` only when the function must switch to the generic executor.

```swift
nonisolated(nonsending) func prepare(_ value: Buffer) async { }

@concurrent
func crunch(_ bytes: [UInt8]) async -> Int {
    bytes.reduce(0) { $0 + Int($1) }
}
```

### Configure default isolation per module

Swift 6.2 supports `MainActor` or `nonisolated` as a module default. No setting means `nonisolated`; imported declarations retain their defining module's choice.

```swift
.target(
    name: "AppCore",
    swiftSettings: [.defaultIsolation(MainActor.self)]
)
```

Explicit isolation wins. Actor members do not gain global-actor isolation, and a primary conformance through `SendableMetatype` suppresses inferred `@MainActor`. Use an explicit `nonisolated` declaration for individual opt-outs.

### Acknowledge unsafe APIs

Strict memory-safety checking is opt-in. Calling an `@unsafe` API without the `unsafe` keyword warns; `@safe` is the default and is mainly useful to override inherited unsafe classification.

```swift
let name: String? = "Blob"
unsafe print(name.unsafelyUnwrapped)
```

Foreign types that lack recognized safety or lifetime annotations also warn under strict checking. Add escapability, lifetime, and bounds contracts instead of suppressing those warnings; see [c-family-interop.md](references/c-family-interop.md).

### Make member imports explicit

The `MemberImportVisibility` upcoming feature stops extension members imported in one source file from leaking into another. Add an explicit `import` to every file that uses the API.

### Update error expectations

`#expect(throws:)` and `#require(throws:)` return the matched error. Validate it after the operation; the second trailing error-checking closure is deprecated.

```swift
let error = #expect(throws: GameError.self) {
    try playGame(at: 22)
}
#expect(error == .disallowedTime)
```

### Recheck imported completion handlers

Imported Objective-C completion-handler parameters are `@Sendable` by default unless Objective-C opts out. Existing callback code can therefore acquire sendability diagnostics.

### Replace underscored ABI attributes

Use `@c(name)` instead of `@_cdecl` for C-compatible functions and enums. Use `@export(implementation)` instead of `@_alwaysEmitIntoClient` when clients need an emitted, specialized, or inlined definition; use `@export(interface)` when clients should see only a callable symbol.

```swift
@c(MyLib_initialize)
public func initialize() { }
```

## High-value language and library features

### Use fixed-size inline storage

Integer generic parameters use `let`. `InlineArray<count, Element>` provides fixed-size contiguous inline storage without its own implicit heap allocation.

```swift
var names: InlineArray<4, String> = ["Moon", "Mercury", "Mars", "Venus"]
names[2] = "Jupiter"
```

The literal needs `InlineArray` context and exactly the static count. `InlineArray` is not `Sequence` or `Collection`; iterate over `indices`. It supports noncopyable elements and is conditionally `Copyable` and `Sendable`.

### Borrow contiguous storage safely

`Span<Element>` is a copyable, non-escapable, read-only borrow of initialized contiguous storage. It prevents mutation or destruction of the owner while live. It is not a `Sequence` or `Collection`, so iterate over `indices`.

```swift
func sum(_ values: Span<Int>) -> Int {
    var result = 0
    for i in values.indices { result += values[i] }
    return result
}
```

Use `RawSpan` for initialized heterogeneous bytes. Checked bounds do not make typed raw loads type-safe; reserve its `unsafeLoad` operations for layouts whose alignment and stored type are known.

### Use method and initializer key paths

Key paths can refer to synchronous, nonthrowing methods and initializers. Include `()` to invoke a zero-argument method, omit it to obtain a bound function, and retain labels to disambiguate overloads.

```swift
let uppercased = ["Hello", "world"].map(\.uppercased())
let prefixThrough = \Array<String>.prefix(through:)
```

Static properties also participate in key paths rooted at a metatype:

```swift
let maximum: KeyPath<WarpDrive.Type, Double> = \.maximumSpeed
```

### Observe transactional changes

`Observations` returns an `AsyncSequence` over reads of `@Observable` state. It emits an initial value, can coalesce simultaneous changes, and stops if an optional observed value becomes `nil`.

```swift
for await score in Observations({ player.score }) {
    print(score)
}
```

## High-value concurrency features

### Start work immediately on the current executor

`Task.immediate` runs synchronously when already on the target executor until the first suspension. Task groups add `addImmediateTask()` and `addImmediateTaskUnlessCancelled()`.

```swift
Task.immediate {
    updateCachedState()
    await refreshFromServer()
}
```

Tasks and task-group children accept `name:`; read the current optional name through `Task.name`. Use `escalatePriority(to:)` to raise, never lower, a task's priority, and observe changes with `withTaskPriorityEscalationHandler`.

### Isolate destruction

An actor-isolated class can declare `isolated deinit`; destruction moves to the actor executor and can access isolated, non-`Sendable` state.

```swift
@MainActor
final class Session {
    let user: User
    init(user: User) { self.user = user }
    isolated deinit { user.isLoggedIn = false }
}
```

### Infer task-group child results

`withTaskGroup` and `withThrowingTaskGroup` can infer `ChildTaskResult` from added tasks, so omit `of:` when all children return one type.

## High-value tooling and package features

### Select SwiftPM traits

Packages using tools version 6.1 can define default and composed traits. Local enabled traits become compilation conditions such as `#if Bar`; mirror a dependency trait into a local trait if consuming code also needs to test it.

```sh
swift build --traits Bar,Baz
swift test --enable-all-traits
swift run --disable-default-traits
swift package show-traits
```

Trait names are package-scoped. Avoid mutually exclusive traits because they can destabilize package-graph resolution.

### Preview SwiftBuild

SwiftPM 6.3 keeps the native build system as the default. Preview the next-generation system without manifest changes:

```sh
swift build --build-system swiftbuild
swift test --build-system swiftbuild
swift run --build-system swiftbuild MyExecutable
```

### Control diagnostic groups

Use `-print-diagnostic-groups`, then `-Werror Group` or `-Wwarning Group`. Flag order relative to `-warnings-as-errors` matters. SwiftPM can also set group severity in a manifest.

### Target newer platforms

Swift 6.2 supports WebAssembly for client and server applications. Swift 6.3 provides the first official Swift SDK for Android; Kotlin and Java applications can integrate Swift with Swift Java and Swift Java JNI Core.

Read the indexed topic reference before implementing an affected API; it contains constraints and secondary features intentionally omitted from this quick reference.
