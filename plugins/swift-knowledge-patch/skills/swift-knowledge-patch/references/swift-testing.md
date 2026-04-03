# Swift Testing (6.2–6.3)

## Exit Tests (6.2)

Test code that crashes/exits. Runs in a subprocess. macOS/Linux/Windows only.

```swift
@Test func preconditionFires() async {
    await #expect(processExitsWith: .failure) {
        precondition(false)
    }
}
```

## Attachments (6.2)

```swift
Attachment.record("debug info")                    // String
Attachment.record(myEncodable, named: "snapshot")  // Codable types
```

## Warning Issues and Test Cancellation (6.3)

```swift
Issue.record("Suspicious but not fatal", severity: .warning)
try Test.cancel() // cancel current test and its task hierarchy
```
