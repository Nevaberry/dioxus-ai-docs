# Swift Testing Updates (6.1–6.3)

## TestScoping for Setup/Teardown (6.1)

Custom traits can implement `TestScoping` to provide setup and teardown logic — a structured replacement for `setUp`/`tearDown` in XCTest:

```swift
struct MockDB: TestTrait, TestScoping {
  func provideScope(for test: Test, testCase: Test.Case?,
    performing function: @Sendable () async throws -> Void) async throws {
    try await DB.$current.withValue(MockDB()) { try await function() }
  }
}

@Test(.mockDB) func testQuery() { ... }
```

The scope wraps each test execution, so resources are set up before and torn down after each test automatically.

## Error Return from #expect(throws:) (6.1)

`#expect(throws:)` and `#require(throws:)` now return the caught error, enabling detailed inspection:

```swift
let error = #expect(throws: ValidationError.self) { try validate(input) }
#expect(error?.field == "email")
```

## Exit Tests (6.2)

Verify that code terminates under specific conditions. Runs in a subprocess so the test process itself is not affected:

```swift
@Test func preconditionFires() async {
  await #expect(processExitsWith: .failure) {
    preconditionFailure("boom")
  }
}
```

Use for testing:
- `preconditionFailure` / `fatalError` calls
- `exit()` calls
- Signal-based termination

## Attachments (6.2)

Add context to test results — images, strings, logs, or any data:

```swift
@Test func renderTest() throws {
  let image = render()
  Test.Attachment(image, named: "render-output.png").attach()
}
```

Attachments appear in test reports and CI artifacts, making it easier to diagnose failures.

## Raw Identifier Test Names (6.2)

Use backtick-quoted raw identifiers for human-readable test names:

```swift
@Test func `square() returns x * x`() {
  #expect(square(4) == 16)
}
```

## Warning Issues (6.3)

Record non-failing warnings that appear in test reports:

```swift
Issue.record("Slow response", severity: .warning)
```

Warnings don't fail the test but are surfaced in reports for investigation.

## Test Cancellation (6.3)

Cancel a running test programmatically:

```swift
try Test.cancel()
```
