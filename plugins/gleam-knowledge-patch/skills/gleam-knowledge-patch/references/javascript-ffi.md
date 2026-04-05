# JavaScript FFI

## External API for Gleam data (1.13)

A dedicated API is now provided for JavaScript FFI code to construct, inspect, and check Gleam custom types. Each Gleam type generates `$`-prefixed functions in its compiled `.mjs` module.

```gleam
// src/person.gleam
pub type Person {
  Teacher(name: String, subject: String)
  Student(name: String)
}
```

```javascript
// src/my_ffi.mjs
import { ... } from "./person.mjs";

// Construct variants
let teacher = Person$Teacher("Joe", "CS");
let student = Person$Student("Louis");

// Check variant
Person$isTeacher(teacher); // true

// Access variant-specific fields
Person$Teacher$subject(teacher); // "CS"

// Access shared fields (works on any variant)
Person$name(teacher); // "Joe"
```

This replaces direct access to internal representations. Existing JS externals should migrate to this API.

## BitArray JavaScript FFI functions (1.15)

The JS external API now includes `BitArray$isBitArray` and `BitArray$BitArray$data` for working with Gleam bit arrays in JavaScript FFI code. TypeScript type guards are generated for the check functions.

```javascript
import { BitArray$isBitArray, BitArray$BitArray$data } from "../gleam.mjs";

export function writeFile(path, data) {
  if (BitArray$isBitArray(data)) {
    const buffer = BitArray$BitArray$data(data);
    return fs.write(path, buffer);
  }
}
```

## `@external` annotations for external types (1.14)

The `@external` annotation can now be applied to external type declarations (not just functions), specifying the corresponding Erlang or TypeScript type for generated type specs/declarations.

```gleam
@external(erlang, "erlang", "map")
@external(javascript, "../dict.d.mts", "Dict")
pub type Dict(key, value)
```

This produces precise Erlang type specs and TypeScript declarations instead of falling back to `any`.

## CommonJS FFI modules (1.12)

FFI JavaScript modules can now use the `.cjs` extension for CommonJS imports.
