# Concurrency Changes (Swift 6.1–6.2)

## Overview

Swift 6.1–6.2 significantly refine the concurrency model introduced in Swift 6.0. The key theme is making `@MainActor` the natural default for app code, with explicit opt-outs for concurrent work.

## Default MainActor Isolation (6.2)

New compiler flag `-default-isolation MainActor` makes all unannotated code `@MainActor` by default. This is the recommended approach for apps, scripts, and UI-heavy code:

```swift
// Package.swift
.target(name: "MyApp", swiftSettings: [
  .defaultIsolation(MainActor.self),
])
```

- All unannotated declarations become `@MainActor`
- Use `nonisolated` to opt specific declarations out
- Use `@concurrent` to explicitly run on the concurrent thread pool
- Ideal for app targets; library targets should generally not use this

## @concurrent Attribute (6.2)

Explicitly marks async functions to run on the concurrent thread pool (off-actor). This is the replacement for the old implicit behavior where nonisolated async functions would hop to the global executor:

```swift
@concurrent
static func fetchImage(at url: URL) async throws -> Image {
  let (data, _) = try await URLSession.shared.data(from: url)
  return await decode(data: data)
}
```

Use `@concurrent` when:
- You have CPU-bound work that should not block the main actor
- You explicitly want off-actor execution
- You're writing library code that should not inherit the caller's isolation

## nonisolated Async Runs on Caller's Actor (6.2)

Under the `NonisolatedNonsendingByDefault` upcoming feature flag (default in 6.2), nonisolated async functions run on the caller's actor instead of switching to the global executor. This eliminates the confusing difference between sync and async nonisolated behavior.

**Before (Swift 6.1 and earlier):**
- `nonisolated func sync()` — runs wherever called
- `nonisolated func async()` — hops to global executor

**After (Swift 6.2):**
- `nonisolated func sync()` — runs wherever called
- `nonisolated func async()` — runs wherever called (same as sync)
- `@concurrent func async()` — hops to global executor (explicit opt-in)

## nonisolated on Types and Extensions (6.1)

`nonisolated` can now be applied to types and extensions to prevent `@MainActor` inference. This is especially useful for protocol conformances that don't need main-actor isolation:

```swift
@MainActor struct S {
  let id: Int
}

nonisolated extension S: Equatable {
  static func ==(lhs: S, rhs: S) -> Bool { lhs.id == rhs.id }
}
```

Without `nonisolated`, the extension would inherit `@MainActor` from the type, which could cause issues with protocol conformance requirements.

## Task Group Type Inference (6.1)

`withTaskGroup` and `withThrowingTaskGroup` no longer require the `of:` parameter — the child task result type is inferred from context:

```swift
// Before (6.0)
let results = await withTaskGroup(of: String.self) { group in
  for id in ids {
    group.addTask { await fetch(id) }
  }
  return await group.reduce(into: []) { $0.append($1) }
}

// After (6.1+)
let results = await withTaskGroup { group in
  for id in ids {
    group.addTask { await fetch(id) }
  }
  return await group.reduce(into: []) { $0.append($1) }
}
```

## Observations Async Sequence (6.2)

Stream transactional state changes from `@Observable` types:

```swift
for await changes in Observations(of: model) {
  // All synchronous mutations batched into one update
  updateUI(with: changes)
}
```

This provides an async-sequence-based alternative to the closure-based `withObservationTracking`, making it natural to use in structured concurrency contexts.
