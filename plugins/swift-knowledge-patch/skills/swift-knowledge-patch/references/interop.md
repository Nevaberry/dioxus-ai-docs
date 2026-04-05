# C and Objective-C Interop (Swift 6.1–6.3)

## @c Attribute (6.3)

Expose Swift functions and enums to C code via generated headers:

```swift
@c func processData(_ ptr: UnsafePointer<UInt8>, count: Int) -> Int32 { ... }
// Generated C header: int32_t processData(const uint8_t *, int);
```

### Custom C names

Use `@c(name)` to specify the generated C function name:

```swift
@c(MyLib_processData)
func processData(_ ptr: UnsafePointer<UInt8>, count: Int) -> Int32 { ... }
// Generated C header: int32_t MyLib_processData(const uint8_t *, int);
```

### Providing Swift implementations for existing C headers

Combine `@c` with `@implementation` to provide Swift bodies for functions declared in existing C headers:

```swift
@c @implementation
func existingCFunction() { /* Swift body */ }
```

This allows incremental migration of C codebases to Swift — implement one function at a time without changing the C header interface.

## @objc @implementation (6.1)

Replace Objective-C `@implementation` blocks with Swift extensions. Enables incremental migration of ObjC classes to Swift, one category at a time:

```swift
@objc @implementation extension MyObjCClass {
  func viewDidLoad() { /* Swift implementation */ }
}
```

This allows you to:
- Keep the ObjC `@interface` in the header file
- Replace the ObjC `@implementation` with a Swift extension
- Migrate one category/method group at a time
- Maintain full binary compatibility with existing ObjC consumers

## Module Selectors (6.3)

Disambiguate APIs from different modules using `::` syntax:

```swift
import ModuleA
import ModuleB

let x = ModuleA::getValue()
let y = ModuleB::getValue()

// Access Swift concurrency types unambiguously
let task = Swift::Task { await doWork() }
```

This replaces workarounds like type aliases or fully qualified names when two imported modules export the same symbol.
