# Testing, documentation, and developer tools

Testing and tooling additions from batches `6.1-guide`, `6.1`, `6.2-language`, `6.2-interop-and-testing`, `6.2`, and `6.3`.

## Contents

- [Swift Testing assertions and control flow](#swift-testing-assertions-and-control-flow)
- [Swift Testing traits and artifacts](#swift-testing-traits-and-artifacts)
- [XCTest and test plans](#xctest-and-test-plans)
- [Swift-DocC](#swift-docc)
- [Editor, indexer, and debugger](#editor-indexer-and-debugger)

## Swift Testing assertions and control flow

### Range-based confirmations

Since 6.1, `confirmation(expectedCount:)` accepts closed and lower-bounded ranges. It does not accept a range without a lower bound.

```swift
await confirmation(expectedCount: 5...10) { confirm in
    for await _ in loader { confirm() }
}

await confirmation(expectedCount: 5...) { confirm in
    // Exercise an open-ended number of events.
}
```

### Throwing expectations return the error

`#expect(throws:)` and `#require(throws:)` return the matched error, allowing error validation to follow the operation. The older form with a second trailing error-checking closure is deprecated.

```swift
let error = #expect(throws: GameError.self) {
    try playGame(at: 22)
}
#expect(error == .disallowedTime)
```

### Exit tests

Since 6.2, `#expect(processExitsWith:)` runs its body in a separate process and asynchronously verifies termination such as a precondition failure or `fatalError`. It does not crash the test process.

```swift
await #expect(processExitsWith: .failure) {
    preconditionFailure("expected")
}
```

### Runtime cancellation

Since 6.3, call `try Test.cancel()` after a test starts to cancel that test and its task hierarchy. In a parameterized test, use it to skip one argument when a runtime condition makes that case inapplicable.

## Swift Testing traits and artifacts

### Scoping traits

A custom trait can conform to `TestTrait` and `TestScoping`. Implement `provideScope(for:testCase:performing:)`, install task-local or other scoped configuration, and invoke the supplied test function inside the scope.

```swift
struct DefaultPlayerTrait: TestTrait, TestScoping {
    func provideScope(
        for test: Test,
        testCase: Test.Case?,
        performing function: () async throws -> Void
    ) async throws {
        try await Player.$current.withValue(Player(name: "Natsuki Subaru")) {
            try await function()
        }
    }
}

extension Trait where Self == DefaultPlayerTrait {
    static var defaultPlayer: Self { Self() }
}
```

List multiple scoping traits on a test or suite when needed. They apply in list order, so a later scope can override a value installed by an earlier one.

### Evaluating condition traits

`ConditionTrait.evaluate()` lets ordinary async code evaluate the same disabled or enabled condition used on a test declaration.

```swift
let condition = ConditionTrait.disabled(if: TestManager.inSmokeTestMode)
if try await condition.evaluate() {
    // The disabled condition applies.
}
```

### Attachments

Since 6.2, record diagnostic artifacts with `Attachment.record(_:named:)`. Swift Testing directly supports `String`, `Data`, and encodable values. A custom type can conform to `Attachable` and `Codable` for automatic encoding. The Swift 6.2 attachment API has no lifetime controls.

```swift
let diagnostics = "Unexpected response: \(response)"
Attachment.record(diagnostics, named: "Failure details")
```

Since 6.3, cross-import overlays with UI frameworks such as UIKit allow common platform image types to be attached on Apple platforms and Windows, extending the platform-neutral formats.

### Warning-severity issues

Since 6.3, `Issue.record` accepts `severity:`. Use `.warning` to include an issue in test results without failing the test.

```swift
Issue.record("Something suspicious happened", severity: .warning)
```

## XCTest and test plans

### Non-failing XCTest issues

XCTest can record warning-severity issues without failing the suite. This is useful for diagnostics such as near-threshold snapshot comparisons.

```swift
record(XCTIssue(
    type: .assertionFailure,
    compactDescription: "Images differ slightly",
    severity: .warning
))
```

### Runtime issue detection

Xcode test plans can surface Main Thread Checker, Thread Performance Checker, and framework-reported runtime issues while tests run. These default to warnings so an existing suite continues to pass; the test-plan editor can disable them or promote them to failures.

### UI hitch measurements

`XCTHitchMetric` measures UI responsiveness and animation fluidity for an `XCUIApplication` during a performance measurement.

```swift
measure(metrics: [XCTHitchMetric(application: app)]) {
    app.scrollViews.firstMatch.swipeUp(velocity: .fast)
}
```

## Swift-DocC

### Type-based link disambiguation

Since 6.1, ambiguous symbol links can use readable parameter- and return-type suffixes rather than opaque symbol-identifier hashes. Follow Swift-DocC's ambiguity warning, which reports the minimal suffix needed, such as `-(String,_)`, `->Float`, or `-(String?,_)->Double`.

### Inherited documentation in symbol graphs

Since 6.3, SwiftPM command plugins that generate symbol graphs can control whether inherited documentation is included in the output.

### Experimental Markdown output

Run `docc convert --enable-experimental-markdown-output` to emit Markdown versions of symbol, article, and tutorial pages alongside the usual rendered JSON.

### Static HTML summaries

Pass both `--transform-for-static-hosting` and `--experimental-transform-for-static-hosting-with-content` to `docc convert`. Each page's title, description, availability, declarations, and discussion are then embedded in a `<noscript>` block in `index.html`.

### Code-block annotations

With `--enable-experimental-code-block-annotations`, append `nocopy`, `highlight=[...]`, `showLineNumbers`, or `wrap=<column>` to a code fence after its language. DocC validates highlighted line numbers and warns about unknown options.

````markdown
```swift, highlight=[1, 3], showLineNumbers, wrap=80
let name = "World"
let greeting = "Hello"
print("\(greeting), \(name)!")
```
````

## Editor, indexer, and debugger

### SourceKit-LSP background indexing

Since Swift 6.1, SourceKit-LSP enables background indexing by default for SwiftPM projects. Cross-module and global editor operations such as jump-to-definition can reflect library changes without waiting for a project build.

### Official VS Code extension

The Swift extension is verified and distributed by Swift.org. It includes LLDB debugging, an Explorer panel for package targets, dependencies, and tasks, and a live side-by-side Swift-DocC preview.

### Async LLDB debugging

LLDB can step reliably into async functions even when a call changes threads. Breakpoint stops and thread backtraces expose the current Swift task context.

Embedded-specific LLDB inspection is documented in [embedded-swift.md](embedded-swift.md).
