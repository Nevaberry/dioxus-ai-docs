# New APIs (Swift 6.2)

## Observations Async Sequence

Streams transactional changes from `@Observable` types. Coalesces synchronous changes into single emissions.

```swift
@Observable class Store { var items: [String] = []; var loading = false }
let store = Store()

let stream = Observations {
    (items: store.items, loading: store.loading) // tracks both properties
}
for await snapshot in stream {
    render(snapshot.items, snapshot.loading)
}
```

## Subprocess Package

```swift
import Subprocess
let result = try await run(.path("/usr/bin/swift"), arguments: ["--version"])
let output = result.standardOutput
```

## Typed NotificationCenter

```swift
// Define typed notification:
struct UserDidLogin: NotificationCenter.MainActorMessage {
    let userId: String
}
// Post and observe with type safety — no string names or untyped dictionaries
```
