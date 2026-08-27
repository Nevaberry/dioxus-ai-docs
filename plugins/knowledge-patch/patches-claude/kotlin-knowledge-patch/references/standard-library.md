# Standard library

## Common atomics

The experimental `kotlin.concurrent.atomics` package provides platform-independent atomics for common code. JVM atomics convert without overhead through `asJavaAtomic()` and `asKotlinAtomic()`.

```kotlin
import kotlin.concurrent.atomics.*

@OptIn(ExperimentalAtomicApi::class)
fun increment() {
    var count = AtomicInt(0)
    count += 1
    println(count.load())
}
```

Functional updates include:

- `update` and `updateAt`, which discard the result.
- `fetchAndUpdate` and `fetchAndUpdateAt`, which return the old value.
- `updateAndFetch` and `updateAndFetchAt`, which return the new value.

All remain under `ExperimentalAtomicApi`.

## Time and instants

`kotlin.time.Clock` and `kotlin.time.Instant` began as experimental timezone-independent time primitives while calendar and timezone operations remained in `kotlinx-datetime`. They are stable in Kotlin 2.3 and no longer require `ExperimentalTime` for their standard APIs.

```kotlin
import kotlin.time.*

val elapsed = Clock.System.now() - Instant.parse("2023-01-01T00:00:00Z")
```

On JVM, use `toKotlinInstant()` and `toJavaInstant()`. JavaScript conversion through `Instant.toJSDate()` loses sub-millisecond precision.

## UUID parsing, ordering, and generation

Experimental `Uuid.parse()` accepts both dashed and plain hexadecimal text. `parseHexDash()` and `toHexDashString()` make the dashed representation explicit. UUIDs are `Comparable` under `ExperimentalUuidApi` and can be sorted directly.

Later experimental APIs add nullable `parseOrNull()`, `parseHexDashOrNull()`, and `parseHexOrNull()`, together with random `generateV4()` and monotonic `generateV7()`.

`generateV7NonMonotonicAt(Instant)` creates a v7 UUID at a supplied timestamp but does not guarantee ordering among UUIDs generated for that same timestamp.

## Arrays and collection equality

Experimental `copyOf(newSize) { initializer }` overloads for generic and primitive arrays fill newly added positions. A generic array remains `Array<T>` instead of widening to `Array<T?>`.

```kotlin
@OptIn(ExperimentalStdlibApi::class)
val expanded: Array<String> = arrayOf("one").copyOf(3) { "default" }
```

`Iterable.intersect()` and `subtract()` now test each receiver element before adding it to the result. Membership therefore uses ordinary `Any.equals` consistently even when the argument comes from a referential-equality collection such as `IdentityHashMap.keys`.

## Removed and renamed APIs

Migrate source away from these removed forms:

- Replace legacy `Char` and numeric conversions with explicit code-point or digit APIs.
- Replace `Number.toChar()` with an explicit numeric conversion followed by `toChar()`, or construct the intended `Char` directly.
- Use the argument names `startIndex` and `endIndex` for `String.subSequence`.
- Replace `kotlin.io.createTempDirectory()` and `createTempFile()` with `kotlin.io.path.createTempDirectory` and `createTempFile`.
- `InputStream.readBytes(Int)` is hidden; use a current read API and explicit sizing behavior.
- Replace `kotlin.native.Throws` with common `kotlin.Throws`.
- Replace `AbstractDoubleTimeSource` with `AbstractLongTimeSource`.
