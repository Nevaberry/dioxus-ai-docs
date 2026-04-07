# Language Features (Swift 6.2–6.3)

## InlineArray (6.2)

Fixed-size array with inline storage (stack-allocated). Does NOT conform to Sequence or Collection.

```swift
var bricks: InlineArray<40, Sprite> = .init(repeating: defaultSprite)
// Shorthand:
var bricks2: [40 of Sprite] = .init(repeating: defaultSprite)

bricks[0] = specialSprite
for i in bricks.indices { print(bricks[i]) } // use indices, not for-in
```

## Method and Initializer Key Paths (6.2)

```swift
let caps = strings.map(\.uppercased()) // invokes method
let fns = strings.map(\.uppercased)    // returns unapplied functions
```

## Default Value in String Interpolation (6.2)

Works across types (unlike `??`).

```swift
var age: Int? = nil
print("Age: \(age, default: "Unknown")") // Int? with String default — OK
```

## enumerated() Conforms to Collection (6.2)

```swift
List(names.enumerated(), id: \.offset) { val in
    Text("User \(val.offset + 1): \(val.element)")
}
```

## @c Attribute for C Interop (6.3)

Expose Swift functions/enums directly to C. Generates C header declarations.

```swift
@c func mySwiftFunction() { /* ... */ }
// Generated header: void mySwiftFunction(void);

@c(MyLib_doWork) func doWork() { /* ... */ }
// Generated header: void MyLib_doWork(void);

@c @implementation func existingCFunction() { /* ... */ }
// Validates against pre-existing C header declaration
```

## Module Selectors (6.3)

Disambiguate identically-named APIs from different modules.

```swift
import ModuleA
import ModuleB
let x = ModuleA::getValue()
let y = ModuleB::getValue()

// Access Swift concurrency types without ambiguity:
let task = Swift::Task { await doWork() }
```
