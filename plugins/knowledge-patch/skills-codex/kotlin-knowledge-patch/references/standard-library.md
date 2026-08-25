# Standard library

## Common atomics

The experimental `kotlin.concurrent.atomics` package provides platform-independent atomics for common code. JVM values convert without overhead through `asJavaAtomic()` and `asKotlinAtomic()`.

```kotlin
import kotlin.concurrent.atomics.*

@OptIn(ExperimentalAtomicApi::class)
fun increment() {
    var count = AtomicInt(0)
    count += 1
    println(count.load())
}
```

Functional updates cover values and array elements:

- `update` / `updateAt` discard the result.
- `fetchAndUpdate` / `fetchAndUpdateAt` return the old value.
- `updateAndFetch` / `updateAndFetchAt` return the new value.

These operations also require `ExperimentalAtomicApi`.

## UUIDs

Experimental `Uuid.parse()` accepts dashed and plain hexadecimal input. `parseHexDash()` and `toHexDashString()` explicitly select the dashed form. UUIDs implement `Comparable` under `ExperimentalUuidApi`.

Newer experimental operations add nullable `parseOrNull()`, `parseHexDashOrNull()`, and `parseHexOrNull()`, along with random `generateV4()` and monotonic `generateV7()`. `generateV7NonMonotonicAt(Instant)` uses a supplied timestamp without ordering guarantees among values at that same instant.

## Time

`kotlin.time.Clock` and `kotlin.time.Instant` began as experimental timezone-independent time primitives while calendar/timezone work remained in `kotlinx-datetime`. They are stable in Kotlin 2.3 and no longer require the `ExperimentalTime` opt-in.

JVM conversion uses `toKotlinInstant()` and `toJavaInstant()`. `Instant.toJSDate()` loses sub-millisecond precision.

```kotlin
import kotlin.time.*

val elapsed = Clock.System.now() - Instant.parse("2023-01-01T00:00:00Z")
```

## Arrays and collections

Experimental `copyOf(newSize) { initializer }` overloads for generic and primitive arrays initialize new slots. For generic arrays they preserve `Array<T>` rather than widening to `Array<T?>`.

```kotlin
@OptIn(ExperimentalStdlibApi::class)
val expanded: Array<String> = arrayOf("one").copyOf(3) { "default" }
```

`Iterable.intersect()` and `subtract()` now test each receiver element before adding it to the result. Membership therefore uses ordinary `Any.equals` consistently even if the argument is backed by referential equality, such as `IdentityHashMap.keys`.

## Removed and renamed APIs

Kotlin 2.2 makes `kotlin.native.Throws` and `AbstractDoubleTimeSource` source errors; use common `kotlin.Throws` and `AbstractLongTimeSource`.

Kotlin 2.3 removes old character/number conversions, `Number.toChar()`, old `String.subSequence(start, end)` parameter names, and `kotlin.io.createTempDirectory()` / `createTempFile()` from source use. Use explicit code/digit APIs, `toInt().toChar()` or `Char`, `startIndex`/`endIndex`, and the `kotlin.io.path` replacements. `InputStream.readBytes(Int)` is hidden.
