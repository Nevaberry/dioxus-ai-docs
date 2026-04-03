# Concurrency (Swift 5.10–6.2)

## Approachable Concurrency

`-default-isolation MainActor` makes all code MainActor-isolated by default per module. Nonisolated async functions now run on the caller's actor by default (SE-0461). Use `@concurrent` to explicitly opt into the concurrent thread pool.

```swift
// With -default-isolation MainActor, no annotations needed:
struct ImageCache {
    static var cache: [URL: Image] = [:]

    static func load(from url: URL) async throws -> Image {
        if let img = cache[url] { return img }
        let img = try await fetchImage(at: url) // stays on MainActor
        cache[url] = img
        return img
    }

    @concurrent // explicitly run off MainActor
    static func fetchImage(at url: URL) async throws -> Image {
        let (data, _) = try await URLSession.shared.data(from: url)
        return decode(data)
    }
}
```

Enable per-feature in packages:

```swift
// swift-tools-version: 6.2
.target(name: "MyTarget", swiftSettings: [
    .enableUpcomingFeature("NonisolatedNonsendingByDefault"),
    .enableUpcomingFeature("InferIsolatedConformances"),
])
```

## Task.immediate

Starts executing synchronously on caller's executor until first suspension point.

```swift
Task.immediate { print("runs before next line") }
// In task groups:
group.addImmediateTask { /* starts immediately */ }
```

## isolated deinit

Runs deinit on the actor's executor, allowing safe access to actor-isolated state.

```swift
@MainActor class Session {
    let user: User
    isolated deinit { user.isLoggedIn = false }
}
```

## weak let

Immutable weak reference — enables Sendable conformance on types with weak refs.

```swift
final class Session: Sendable {
    weak let user: User? // can't reassign, but can be deallocated
    init(user: User?) { self.user = user }
}
```

## Global-Actor Isolated Conformances

Restrict protocol conformances to a specific actor context.

```swift
@MainActor class User: @MainActor Equatable {
    static func ==(lhs: User, rhs: User) -> Bool { lhs.id == rhs.id }
}
```

## Task Naming

```swift
let t = Task(name: "FetchNews") { /* ... */ }
print(Task.name ?? "unnamed")
group.addTask(name: "Subtask \(i)") { /* ... */ }
```
