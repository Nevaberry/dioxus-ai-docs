# Standard library

## Time and instants

Experimental `kotlin.time.Clock` and `kotlin.time.Instant` introduced timezone-independent moments in the standard library while calendar and timezone functionality remains in `kotlinx-datetime`:

```kotlin
import kotlin.time.*

@OptIn(ExperimentalTime::class)
val elapsed = Clock.System.now() - Instant.parse("2023-01-01T00:00:00Z")
```

JVM converters are `toKotlinInstant()` and `toJavaInstant()`. `Instant.toJSDate()` loses sub-millisecond precision.

`Clock` and `Instant` are now Stable, so standard time-tracking APIs no longer require `ExperimentalTime` opt-in.

## UUIDs

Experimental `Uuid.parse()` accepts dashed and plain hexadecimal forms. `parseHexDash()` and `toHexDashString()` make the dashed form explicit. After opting in with `ExperimentalUuidApi`, UUIDs are `Comparable` and can be sorted directly.

The still-Experimental API adds `parseOrNull()`, `parseHexDashOrNull()`, and `parseHexOrNull()`, plus `generateV4()` and monotonic `generateV7()`. `generateV7NonMonotonicAt(Instant)` creates a v7 UUID for a supplied timestamp without guaranteeing ordering among UUIDs at that timestamp.

Serialization support for common UUID values is covered in [ecosystem-libraries.md](ecosystem-libraries.md).

## Common atomics

The Experimental `kotlin.concurrent.atomics` package provides platform-independent atomics for common code. JVM types convert without overhead through `asJavaAtomic()` and `asKotlinAtomic()`:

```kotlin
import kotlin.concurrent.atomics.*

@OptIn(ExperimentalAtomicApi::class)
fun increment() {
    var count = AtomicInt(0)
    count += 1
    println(count.load())
}
```

Functional operations include:

- `update` and `updateAt`, which discard the result.
- `fetchAndUpdate` and `fetchAndUpdateAt`, which return the old value.
- `updateAndFetch` and `updateAndFetchAt`, which return the new value.

All require `ExperimentalAtomicApi`.

## Arrays

Experimental `copyOf(newSize) { initializer }` overloads for generic and primitive arrays initialize added slots and preserve `Array<T>` rather than widening a generic result to `Array<T?>`.

```kotlin
@OptIn(ExperimentalStdlibApi::class)
val expanded: Array<String> = arrayOf("one").copyOf(3) { "default" }
```

## Collection equality

`Iterable.intersect()` and `subtract()` test each receiver element before adding it to the result set. Membership therefore uses `Any.equals` consistently even when the argument is backed by referential equality, such as `IdentityHashMap.keys`.

## Removed and renamed APIs

The following old APIs now produce source errors:

- Old `Char` and numeric conversion functions: use explicit code or digit APIs.
- `Number.toChar()`: convert with `toInt().toChar()` or construct the intended `Char` explicitly.
- `String.subSequence(start, end)` with the old named arguments: use `startIndex` and `endIndex`.
- `kotlin.io.createTempDirectory()` and `createTempFile()`: use the `kotlin.io.path` replacements.

`InputStream.readBytes(Int)` is hidden.

Use common `kotlin.Throws` instead of `kotlin.native.Throws`, and `AbstractLongTimeSource` instead of `AbstractDoubleTimeSource`.
