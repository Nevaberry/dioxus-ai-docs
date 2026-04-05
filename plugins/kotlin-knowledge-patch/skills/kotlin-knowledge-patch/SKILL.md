---
name: kotlin-knowledge-patch
description: Kotlin 2.1.20–2.3.20 features — context parameters, name-based destructuring, explicit backing fields, stdlib atomics/UUID/Instant, Compose Multiplatform 1.7–1.10. Load before writing Kotlin 2.2+ code.
version: "2.3.20"
license: MIT
metadata:
  author: Nevaberry
---

# Kotlin 2.1.20+ Knowledge Patch

Claude's baseline knowledge covers Kotlin through 2.1.0 (K2 compiler stable, guard conditions/non-local break-continue in preview), KMP stable, Compose Multiplatform through 1.6.x. This skill provides features from 2.1.20 (2025-03-20) onwards.

## Quick Reference

### Language Features

| Feature | Flag / Status | Version |
|---------|--------------|---------|
| Context parameters | `-Xcontext-parameters` (preview) | 2.2.0 |
| Context-sensitive resolution | `-Xcontext-sensitive-resolution` (preview) | 2.2.0 |
| `@all` annotation target | `-Xannotation-target-all` (preview) | 2.2.0 |
| Nested type aliases | `-Xnested-type-aliases` (beta 2.2, stable 2.3) | 2.2.0 |
| Explicit backing fields | `-Xexplicit-backing-fields` (experimental) | 2.3.0 |
| Name-based destructuring | `-Xname-based-destructuring=MODE` (experimental) | 2.3.20 |
| Return in expression bodies | Default since 2.3.0 | 2.2.20 |
| Data-flow exhaustiveness | Stable since 2.3.0 | 2.2.20 |

See `references/context-parameters.md` and `references/type-system.md` for details.

### Stdlib APIs

| API | Status | Version |
|-----|--------|---------|
| `kotlin.concurrent.atomics` | Experimental | 2.1.20 |
| `kotlin.time.Instant` / `Clock` | Experimental → stable 2.3.0 | 2.1.20 |
| `Uuid.generateV4()` / `generateV7()` | Experimental | 2.3.0 |
| `Uuid.parseOrNull()` / `parseHexDashOrNull()` | Experimental | 2.3.0 |
| `Map.Entry.copy()` | Experimental | 2.3.20 |

See `references/stdlib-apis.md` for code examples.

### JVM & Multiplatform

| Feature | Status | Version |
|---------|--------|---------|
| `@JvmExposeBoxed` | Experimental | 2.2.0 |
| `-jvm-default` (stable option) | Default: `ENABLE` | 2.2.0 |
| Swift export enabled by default | Stable | 2.2.20 |
| `withJava()` deprecated | — | 2.1.20 |
| `-Xwarning-level` per-diagnostic | Experimental | 2.2.0 |

See `references/jvm-interop.md` for details.

### Compose Multiplatform

| Version | Highlights |
|---------|-----------|
| 1.7 | Type-safe Navigation, shared element transitions |
| 1.8 | Variable fonts, drag-and-drop on iOS, deep linking on iOS |
| 1.9 | Compose for web Beta, customizable shadows, Material 3 Expressive, `@Preview` parameters |
| 1.10 | Navigation 3 (Alpha), unified `@Preview`, Compose Hot Reload |

See `references/compose-multiplatform.md` for migration notes and Navigation 3 setup.

---

## Key Features

### Context Parameters (2.2.0, Preview)

Replaces context receivers. Parameters accessed by name, not as implicit receivers.

```kotlin
context(users: UserService)
fun outputMessage(message: String) {
    users.log("Log: $message")  // access via name
}

// Anonymous — available for resolution but not by name
context(_: UserService)
fun logWelcome() {
    outputMessage("Welcome!")  // resolved from context
}
```

Enable: `-Xcontext-parameters`. Cannot use with `-Xcontext-receivers`.

### Name-Based Destructuring (2.3.20, Experimental)

Match variables to property names instead of position-based `componentN()`.

```kotlin
data class User(val username: String, val email: String)

// Name-based — variables bound by property name
(val mail = email, val name = username) = user

// In complete mode, parentheses use name-based matching:
val (email, username) = user  // matches by name, not position

// Position-based uses square brackets:
val [username, email] = user  // position-based like before
```

Modes: `-Xname-based-destructuring=only-syntax|name-mismatch|complete`.

### Explicit Backing Fields (2.3.0, Experimental)

Declare a backing field with a different type than the property.

```kotlin
val city: StateFlow<String>
    field = MutableStateFlow("")

fun updateCity(newCity: String) {
    city.value = newCity  // smart cast to MutableStateFlow within same scope
}
```

Enable: `-Xexplicit-backing-fields`.

### Common Atomics (2.1.20, Experimental)

```kotlin
@OptIn(ExperimentalAtomicApi::class)
val counter = AtomicInt(0)
counter += 1
println(counter.load()) // 1

// JVM interop
val javaAtomic: java.util.concurrent.atomic.AtomicInteger = counter.asJavaAtomic()
val kotlinAtomic: AtomicInt = javaAtomic.asKotlinAtomic()
```

### UUID v4/v7 (2.3.0, Experimental)

```kotlin
@OptIn(ExperimentalUuidApi::class)
val v4 = Uuid.generateV4()   // same as Uuid.random()
val v7 = Uuid.generateV7()   // time-ordered
val parsed = Uuid.parseOrNull("not-a-uuid")  // null instead of throwing
```

### Unused Return Value Checker (2.3.0, Experimental)

```kotlin
@MustUseReturnValues          // mark class or @file:MustUseReturnValues
class Greeter {
    fun greet(name: String): String = "Hello, $name"
}

@IgnorableReturnValue         // suppress on specific functions
fun <T> MutableList<T>.addSafe(element: T): Boolean = add(element)

val _ = computeValue()        // suppress at call site with unnamed variable
```

Enable: `-Xreturn-value-checker=check` (marked scopes) or `=full` (entire project).

### Context-Sensitive Resolution (2.2.0, Preview)

Omit type qualifier for enum entries/sealed class members when type is known from context.

```kotlin
fun message(problem: Problem): String = when (problem) {
    CONNECTION -> "connection"         // not Problem.CONNECTION
    AUTHENTICATION -> "authentication"
    DATABASE -> "database"
    UNKNOWN -> "unknown"
}

val role: UserRole = ADMIN  // not UserRole.ADMIN
```

Works in `when` subjects, explicit return types, declared variable types, `is`/`as` checks, parameter types.
Enable: `-Xcontext-sensitive-resolution`.

### Nested Type Aliases (2.2.0 Beta, Stable in 2.3.0)

```kotlin
class Dijkstra {
    typealias VisitedNodes = Set<Node>
    private fun step(visited: VisitedNodes) = ...
}
```

Enable in 2.2.x: `-Xnested-type-aliases`. Stable in 2.3.0.

### kotlin.time.Instant and Clock (2.1.20, Stable in 2.3.0)

```kotlin
@OptIn(ExperimentalTime::class)
val now = Clock.System.now()
val past = Instant.parse("2023-01-01T00:00:00Z")
val duration = now - past
// JVM interop: .toJavaInstant() / .toKotlinInstant()
```

### Suspend Overload Resolution (2.2.20, Default in 2.3.0)

When both regular and suspend overloads exist, a lambda resolves to the regular overload. Use `suspend { }` for the suspend overload.

```kotlin
fun transform(block: () -> Int) {}
fun transform(block: suspend () -> Int) {}

transform({ 42 })          // resolves to () -> Int
transform(suspend { 42 })  // resolves to suspend () -> Int
```

### @JvmExposeBoxed (2.2.0, Experimental)

Makes inline value classes usable from Java by generating a public boxed constructor.

```kotlin
@JvmExposeBoxed
@JvmInline
value class PositiveInt(val number: Int)
// Java: new PositiveInt(5)  — now works
```

### Navigation 3 (Compose 1.10, Alpha)

```kotlin
// build.gradle.kts
implementation("org.jetbrains.androidx.navigation3:navigation3-ui:$version")
implementation("org.jetbrains.androidx.lifecycle:lifecycle-viewmodel-navigation3:$version")
implementation("org.jetbrains.compose.material3.adaptive:adaptive-navigation3:$version")
```

`PredictiveBackHandler()` deprecated — use `NavigationBackHandler()` from Navigation Event library.
Compose dependency aliases (`compose.ui`, etc.) deprecated in 1.10 — use direct library references.

---

## Reference Files

| File | Contents |
|------|----------|
| [context-parameters.md](references/context-parameters.md) | Context parameters, context-sensitive resolution, `@all` annotation target |
| [type-system.md](references/type-system.md) | Nested type aliases, explicit backing fields, name-based destructuring, data-flow exhaustiveness, return in expression bodies |
| [stdlib-apis.md](references/stdlib-apis.md) | Atomics, Instant/Clock, UUID v4/v7, Map.Entry.copy() |
| [compiler-features.md](references/compiler-features.md) | Unused return value checker, suspend overload resolution, reified types in catch, contracts, `-Xwarning-level` |
| [jvm-interop.md](references/jvm-interop.md) | `@JvmExposeBoxed`, `-jvm-default`, Swift export, `withJava()` deprecated |
| [compose-multiplatform.md](references/compose-multiplatform.md) | Compose 1.7–1.10, Navigation 3, deprecations |
