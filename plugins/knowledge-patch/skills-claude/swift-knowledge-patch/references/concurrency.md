# Concurrency and isolation

Concurrency behavior and APIs from batches `6.1-guide`, `6.2-approachable-concurrency`, `6.2-language`, and `6.2`.

## Contents

- [Approachable Concurrency migration](#approachable-concurrency-migration)
- [Isolation defaults and opt-outs](#isolation-defaults-and-opt-outs)
- [Async executor semantics](#async-executor-semantics)
- [Isolation-aware function values and tasks](#isolation-aware-function-values-and-tasks)
- [Conformances and imported APIs](#conformances-and-imported-apis)
- [Task APIs](#task-apis)
- [Actor-isolated destruction](#actor-isolated-destruction)
- [Typed Foundation notifications](#typed-foundation-notifications)

## Approachable Concurrency migration

Xcode enables Approachable Concurrency for new projects. Existing projects must opt in because executor behavior can change. For a package, set tools version 6.2 and enable the component upcoming features per target. Enable them individually when migration fix-its must preserve old behavior before the complete bundle is active.

```swift
// swift-tools-version: 6.2
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

## Isolation defaults and opt-outs

### Per-module default actor isolation

Swift 6.2 can infer `@MainActor` for otherwise unannotated declarations throughout a module. Pass `-default-isolation MainActor` or configure each SwiftPM target. With no setting, the default remains `nonisolated`; an imported module preserves the isolation chosen by its defining module.

```swift
.target(
    name: "AppCore",
    swiftSettings: [.defaultIsolation(MainActor.self)]
)
```

Only `MainActor` and `nonisolated` are valid defaults. Explicit or previously inferred isolation wins. Actor members do not gain global-actor isolation. A primary conformance to a protocol inheriting `SendableMetatype` suppresses default `@MainActor` inference.

### Declaration-level `nonisolated`

Since 6.1, put `nonisolated` on a protocol, struct, class, or enum to cut off global-actor isolation inferred through a conformance or inheritance chain. Cross into any actor-isolated members asynchronously as usual.

```swift
nonisolated struct App: DataStoring {
    let controller = DataController()
    init() async { await controller.load() }
}
```

Use the same explicit declaration-level opt-out for individual types in a module whose default is `MainActor`.

## Async executor semantics

### Caller-actor execution

With `NonisolatedNonsendingByDefault`, a nonisolated async function runs on the caller's actor rather than switching automatically to the generic executor. `nonisolated(nonsending)` explicitly requests this behavior in any language mode. Non-`Sendable` arguments and results therefore do not cross an isolation boundary by default.

```swift
final class Buffer { }

nonisolated(nonsending)
func prepare(_ buffer: Buffer) async { }
```

### Explicit concurrent execution

Annotate an async function `@concurrent` when it must always switch off an actor to the generic executor. The annotation implies `nonisolated`. It is limited to async functions and cannot be combined with global-actor isolation, isolated parameters, or `@isolated(any)`. Arguments and results that cross from an actor must be `Sendable` or reside in a disconnected region.

```swift
@concurrent
func crunch(_ bytes: [UInt8]) async -> Int {
    bytes.reduce(0) { $0 + Int($1) }
}
```

## Isolation-aware function values and tasks

### Async function types

`nonisolated(nonsending)` and `@concurrent` are part of an async function's type. Higher-order APIs preserve whether a call remains on the caller's actor or switches away. A function conversion that crosses an isolation boundary needs an async destination and `Sendable` argument and result types. Converting a `nonisolated(nonsending)` function to an actor-isolated function does not cross a boundary; it simply runs on that actor.

### `#isolation`

Inside a `nonisolated(nonsending)` async function, `#isolation` expands to the implicit optional actor inherited from the caller. Forward it to an `isolated (any Actor)?` parameter. It expands to `nil` inside `@concurrent` functions and synchronous nonisolated functions.

### Unstructured tasks in nonisolated functions

An unstructured `Task` created inside any nonisolated function does not inherit that function's implicit caller actor. Isolate the task explicitly when it must run on a particular actor; otherwise, capturing caller-isolated non-`Sendable` state is rejected.

```swift
nonisolated(nonsending) func schedule() async {
    let caller = #isolation
    Task { @MainActor in
        // Explicitly main-actor isolated.
    }
}
```

## Conformances and imported APIs

### Global-actor-isolated conformances

With `InferIsolatedConformances`, a global-actor-isolated type can satisfy a normally nonisolated protocol through an inferred isolated conformance. Use that conformance only where the actor's isolation is available; it cannot escape across concurrency boundaries.

```swift
@MainActor
final class Model: Equatable {
    let id: Int
    init(id: Int) { self.id = id }
    static func == (lhs: Model, rhs: Model) -> Bool { lhs.id == rhs.id }
}
```

### Objective-C async imports

Objective-C methods transformed by the import-as-async heuristic import as `nonisolated(nonsending)` even when the upcoming feature is disabled. This preserves their existing caller-actor behavior and avoids spurious sendability diagnostics.

Imported Objective-C completion-handler parameters are considered `@Sendable` by default unless the Objective-C declaration requests otherwise. Revisit captures in existing callbacks when new sendability diagnostics appear.

### Actor assertions in async contexts

Nonisolated async code can now execute on an actor. Accordingly, `Actor` and `MainActor` APIs including `assertIsolated`, `assumeIsolated`, and `preconditionIsolated` are available from async contexts.

## Task APIs

### Task-group result inference

Since 6.1, `withTaskGroup` and `withThrowingTaskGroup` infer `ChildTaskResult` from added tasks. Omit `of:` when all child tasks return the same type.

```swift
let words = await withTaskGroup { group in
    group.addTask { "Hello" }
    group.addTask { "world" }
    return await group.reduce(into: [String]()) { $0.append($1) }
}
```

### Immediately started tasks

`Task.immediate` starts synchronously when already on the target executor and continues until its first suspension. Task groups provide `addImmediateTask()` and `addImmediateTaskUnlessCancelled()`.

```swift
Task.immediate {
    updateCachedState()
    await refreshFromServer()
}
```

### Names

`Task.init`, `Task.detached`, task-group `addTask`, and `addTaskUnlessCancelled` accept `name:`. Read the current optional name through `Task.name` for logging and debugging.

```swift
Task(name: "Thumbnail loader") {
    print(Task.name ?? "unnamed")
}
```

### Priority escalation

`withTaskPriorityEscalationHandler` reports old and new priorities whenever the current task is escalated. A task handle's `escalatePriority(to:)` can explicitly raise, but never lower, its priority.

```swift
let worker = Task(priority: .medium) {
    await withTaskPriorityEscalationHandler {
        await doWork()
    } onPriorityEscalated: { old, new in
        print("\(old) -> \(new)")
    }
}
worker.escalatePriority(to: .high)
```

## Actor-isolated destruction

An actor-isolated class can declare `isolated deinit`. Destruction moves to the actor's executor, so the deinitializer can access isolated and potentially non-`Sendable` state.

```swift
@MainActor
final class Session {
    let user: User
    init(user: User) { self.user = user }
    isolated deinit { user.isLoggedIn = false }
}
```

## Typed Foundation notifications

Foundation's modern `NotificationCenter` API uses concrete message structs with stored payload properties instead of string names and untyped dictionaries. Conform a message to `MainActorMessage` for synchronous main-actor delivery or `AsyncMessage` for asynchronous delivery; isolation behavior becomes part of its type.
