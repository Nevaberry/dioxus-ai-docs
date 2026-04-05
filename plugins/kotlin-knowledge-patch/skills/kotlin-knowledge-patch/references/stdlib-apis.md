# Stdlib API Additions

## Common Atomic Types (2.1.20, Experimental)

`kotlin.concurrent.atomics` package provides platform-independent thread-safe operations.

```kotlin
@OptIn(ExperimentalAtomicApi::class)
val counter = AtomicInt(0)
counter += 1
println(counter.load()) // 1

// JVM interop
val javaAtomic: java.util.concurrent.atomic.AtomicInteger = counter.asJavaAtomic()
val kotlinAtomic: AtomicInt = javaAtomic.asKotlinAtomic()
```

## kotlin.time.Instant and Clock (2.1.20 Experimental, Stable in 2.3.0)

`Instant` and `Clock` moved from `kotlinx-datetime` to stdlib `kotlin.time`.

```kotlin
@OptIn(ExperimentalTime::class)
val now = Clock.System.now()
val past = Instant.parse("2023-01-01T00:00:00Z")
val duration = now - past
// JVM interop: .toJavaInstant() / .toKotlinInstant()
```

## UUID Improvements

### Parsing enhancements (2.1.20, Experimental)

`Uuid.parse()` now accepts both hex-and-dash and plain hex. New `parseHexDash()`/`toHexDashString()`. `Uuid` is now `Comparable`.

### V4/V7 Generation and Null-Safe Parsing (2.3.0, Experimental)

```kotlin
@OptIn(ExperimentalUuidApi::class)
val v4 = Uuid.generateV4()   // same as Uuid.random()
val v7 = Uuid.generateV7()   // time-ordered

val parsed = Uuid.parseOrNull("not-a-uuid")  // returns null instead of throwing
// Also: parseHexDashOrNull(), parseHexOrNull()

// v7 for specific timestamp
@OptIn(ExperimentalTime::class)
val atTime = Uuid.generateV7NonMonotonicAt(Instant.fromEpochMilliseconds(1577836800000))
```

## Map.Entry.copy() (2.3.20, Experimental)

Create immutable copies of map entries for safe manipulation.

```kotlin
@OptIn(ExperimentalStdlibApi::class)
val toRemove = map.entries.filter { it.key % 2 == 0 }.map { it.copy() }
map.entries.removeAll(toRemove)
```
