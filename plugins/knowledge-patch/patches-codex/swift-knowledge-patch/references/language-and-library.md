# Language and standard library

Language, library, memory-model, and ABI additions from batches `6.1-guide`, `6.2-language`, and `6.3`.

## Contents

- [Syntax and lookup](#syntax-and-lookup)
- [Key paths](#key-paths)
- [Memory safety and ownership](#memory-safety-and-ownership)
- [Fixed-size and borrowed storage](#fixed-size-and-borrowed-storage)
- [Observation, runtime, and utility APIs](#observation-runtime-and-utility-apis)
- [ABI and optimization](#abi-and-optimization)

## Syntax and lookup

### Trailing commas in delimited lists

Since 6.1, accept trailing commas in any comma-separated list enclosed by `()`, `[]`, or `<>`, including calls, tuples, generic parameters, and string interpolation. Do not use them in undelimited lists such as enum cases.

```swift
func add<T: Numeric,>(_ a: T, _ b: T,) -> T { a + b }
let result = add(1, 5,)
```

### File-scoped member imports

When the `MemberImportVisibility` upcoming feature is enabled, an extension member imported in one source file no longer leaks into other files. Import the defining module explicitly in every file that uses that API.

### Raw identifiers

Since 6.2, a backtick-escaped identifier can contain spaces, start with digits, or contain operator characters. It cannot consist only of operator characters.

```swift
@Test func `Strip HTML tags from string`() { }
enum HTTPError { case `401`, `404` }
let error = HTTPError.`404`
```

### Default values in string interpolation

Use `default:` to render a fallback for a `nil` optional. Unlike `??`, the fallback does not need the wrapped value's type.

```swift
let age: Int? = nil
print("Age: \(age, default: "Unknown")")
```

### `enumerated()` is a collection

The result of `enumerated()` now conforms to `Collection` whenever its base does. Pass it directly to collection-requiring APIs and slice it efficiently without first creating an `Array`.

```swift
let latterHalf = (1000..<2000).enumerated().dropFirst(500)
```

### Module name selectors

Since 6.3, disambiguate same-named declarations with `ModuleName::member`. The `Swift` module can qualify concurrency and string-processing APIs too.

```swift
let a = ModuleA::getValue()
let b = ModuleB::getValue()
let task = Swift::Task { await doWork() }
```

## Key paths

### Metatype roots

Since 6.1, static properties participate in key paths rooted at the metatype.

```swift
struct WarpDrive { static let maximumSpeed = 9.975 }
let maximum: KeyPath<WarpDrive.Type, Double> = \.maximumSpeed
```

### Methods and initializers

Since 6.2, key paths can refer to methods and initializers as well as properties and subscripts. Include `()` to invoke a zero-argument method through the key path; omit it to retrieve a bound function. Preserve argument labels to disambiguate overloads. Async and throwing methods are not supported.

```swift
let values = ["Hello", "world"]
let uppercaseValues = values.map(\.uppercased())
let prefixThrough = \Array<String>.prefix(through:)
```

## Memory safety and ownership

### Strict memory-safety checking

Opt-in strict memory safety introduces `@unsafe` and `@safe`. A call to an `@unsafe` API must be acknowledged with the `unsafe` keyword or it produces a warning. `@safe` is the default; write it mainly to override inherited unsafe classification.

```swift
let name: String? = "Blob"
unsafe print(name.unsafelyUnwrapped)
```

Foreign types have additional strict-mode rules; see [c-family-interop.md](c-family-interop.md).

### Immutable weak references

Declare a stored property as `weak let` to fix the reference after initialization while still allowing it to become `nil` after object destruction. Unlike a mutable weak property, this can allow an otherwise suitable class to conform to `Sendable`.

```swift
final class Session: Sendable {
    weak let user: User?
    init(user: User?) { self.user = user }
}
```

### Non-escapable types

Declare a type `~Escapable` when it must not outlive the scope that provides its storage. The restriction prevents storage-dependent values from being retained or returned beyond a valid lifetime and underpins borrowed views such as `Span`.

### Yielding accessors

Use yielding accessors to provide read or write access to stored values without copying. They are particularly useful for noncopyable values and borrowed container views.

## Fixed-size and borrowed storage

### Integer generic parameters and `InlineArray`

Integer generic parameters use `let` in a generic signature. `InlineArray<count, Element>` uses a static integer parameter for fixed-size, contiguous inline storage without its own implicit heap allocation.

```swift
var names: InlineArray<4, String> = ["Moon", "Mercury", "Mars", "Venus"]
names[2] = "Jupiter"

let inferred: InlineArray = [1, 2, 3] // InlineArray<3, Int>
```

An inline-array literal needs `InlineArray` context, must have exactly the static element count, and does not use `ExpressibleByArrayLiteral`; an unconstrained literal remains `Array`. `InlineArray` is neither `Sequence` nor `Collection`, so iterate with `indices`. It supplies checked and `unchecked:` subscripts, `count`, `isEmpty`, `swapAt`, closure-based initialization, and `init(repeating:)` for copyable elements. It can contain noncopyable elements and is conditionally `Copyable` and `Sendable` according to its element.

### `Span`

`Span<Element>` is a copyable but non-escapable, read-only borrow of initialized contiguous storage. It does not copy elements, always bounds-checks its normal integer subscript, and keeps the owner from being mutated or destroyed while the view is live.

```swift
func sum(_ values: Span<Int>) -> Int {
    var result = 0
    for i in values.indices { result += values[i] }
    return result
}
```

`Span` is neither `Sequence` nor `Collection`; use `indices`. Use `subscript(unchecked:)` only when bounds are already proved. `isIdentical(to:)` and `indices(of:)` compare storage regions. `withUnsafeBufferPointer` and, for `BitwiseCopyable` elements, `withUnsafeBytes` provide scoped unsafe interoperation. The initial 6.2 API has no public initializer; obtain spans from storage-owning APIs.

### `RawSpan`

`RawSpan` is a non-escapable view over initialized heterogeneous bytes. Obtain one from storage of `BitwiseCopyable` elements or from a corresponding `Span`. It exposes `byteCount`, `byteOffsets`, identity and subrange tests, and scoped `withUnsafeBytes` access.

Use `unsafeLoad(fromByteOffset:as:)` for an aligned typed load and `unsafeLoadUnaligned(fromByteOffset:as:)` for an unaligned `BitwiseCopyable` load. The `fromUncheckedByteOffset:` variants also omit bounds checks. All these loads remain type-unsafe even when bounds are checked.

## Observation, runtime, and utility APIs

### Transactional observation

`Observations` creates an `AsyncSequence` from a closure that reads `@Observable` state. It emits the initial value and subsequent transactional changes, and can coalesce simultaneous changes. If the observed value is optional, becoming `nil` can end iteration.

```swift
@Observable final class Player { var score = 0 }
let player = Player()

for await score in Observations({ player.score }) {
    print(score)
}
```

### Runtime backtraces

Import the new `Runtime` module and call `Backtrace.capture()`. A capture is unsymbolicated by default; call `symbolicated()` for frames with function, file, and line data.

```swift
import Runtime
let frames = try? Backtrace.capture().symbolicated()?.frames
```

### Regex lookbehind

Swift regex literals support lookbehind assertions. The preceding context is required for the match but excluded from the result.

```swift
let prices = "Coat $100, shoes $59.99"
let amounts = prices.matches(of: /(?<=\$)\d+(?:\.\d{2})?/)
```

### Exact duration totals and clock epochs

`Duration` exposes its total attoseconds as `Int128`, avoiding 64-bit range limits during exact conversion. `SuspendingClock` and `ContinuousClock` expose the exact instant each treats as zero, allowing their instants to be related to a defined epoch instead of only measuring relative durations.

## ABI and optimization

### ABI-only declarations

Use `@abi` in ABI-stable libraries to retain an existing binary-facing declaration while presenting a changed source API. Compatible uses include renaming a poor API or changing `rethrows` to typed throws without breaking already-compiled clients.

### Client optimization controls

Since 6.3, use `@specialize` to provide pre-specialized implementations of generic APIs and `@inline(always)` to guarantee inlining of direct calls. Reserve guaranteed inlining for cases where the benefit justifies increased code size.
