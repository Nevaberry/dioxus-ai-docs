---
name: kotlin-knowledge-patch
description: "Kotlin ecosystem changes since training cutoff (latest: 2.3.0) — guard conditions, explicit backing fields, multi-dollar interpolation, Compose compiler plugin, Ktor 3.0, Coroutines 1.10, Serialization 1.10, Compose Multiplatform 1.10. Load before working with Kotlin."
license: MIT
version: "2.3.0"
metadata:
  author: Nevaberry
---

# Kotlin 2.0+ Knowledge Patch

Claude's baseline knowledge covers Kotlin through 1.9.x and Compose Multiplatform 1.6. This skill provides changes from Kotlin 2.0 (2024) onwards, plus ecosystem updates for Ktor, Coroutines, Serialization, and Compose Multiplatform.

## Quick Reference

### Kotlin Language Features

| Feature | Version | Status | Enable Flag |
|---------|---------|--------|-------------|
| Guard conditions in `when` | 2.1 | Preview | `-Xwhen-guards` |
| Multi-dollar interpolation | 2.1 | Preview | `-Xmulti-dollar-interpolation` |
| Non-local break/continue | 2.1 | Preview | `-Xnon-local-break-continue` |
| Explicit backing fields | 2.3 | Experimental | `-Xexplicit-backing-fields` |
| Unused return value checker | 2.3 | Experimental | `-Xreturn-value-checker=check\|full` |

See `references/language-features.md` for syntax and examples.

### Standard Library

| API | Version | Status |
|-----|---------|--------|
| `Uuid.generateV4()`, `generateV7()` | 2.3 | Experimental |
| `Uuid.parseOrNull()` | 2.3 | Experimental |
| `kotlin.time.Clock`, `Instant` | 2.3 | Stable |

See `references/language-features.md` for details.

### Build & Tooling

| Change | Version |
|--------|---------|
| Compose compiler merged into Kotlin (`kotlin("plugin.compose")`) | 2.0 |
| Power-assert compiler plugin | 2.0 |
| KMP Android: use `com.android.kotlin.multiplatform.library`, rename `androidTarget` to `android` | 2.3 |

See `references/build-tooling.md` for Gradle configuration.

### Ecosystem Libraries

| Library | Version | Key Changes |
|---------|---------|-------------|
| Ktor | 3.0 | kotlinx-io migration, SSE support, CSRF plugin |
| Coroutines | 1.9–1.10 | `chunked`, `any`/`all`/`none` Flow operators |
| Serialization | 1.10 | Stabilized JSON APIs, `subclassesOfSealed` |
| Compose Multiplatform | 1.8–1.10 | Navigation 3, unified `@Preview`, web Beta |

See `references/ecosystem-updates.md` and `references/compose-multiplatform.md`.

## Reference Files

| File | Contents |
|------|----------|
| `language-features.md` | Guard conditions, multi-dollar interpolation, non-local break/continue, explicit backing fields, return value checker, UUID, Clock/Instant |
| `build-tooling.md` | Compose compiler plugin, power-assert, KMP Android target migration |
| `ecosystem-updates.md` | Ktor 3.0 (kotlinx-io, SSE, CSRF), Coroutines 1.9–1.10, Serialization 1.10 |
| `compose-multiplatform.md` | Navigation SavedState, Navigation 3, unified @Preview, web Beta, deprecated aliases |

## Critical Knowledge

### Compose Compiler Plugin (2.0)

The Compose compiler is now bundled with Kotlin. Replace separate Compose compiler artifacts:

```kotlin
plugins {
    kotlin("multiplatform") version "2.0.0"
    kotlin("plugin.compose") version "2.0.0"  // replaces old compose-compiler
}
```

### Guard Conditions in `when` (2.1, Preview)

Add `if` conditions to `when` branches:

```kotlin
when (animal) {
    is Cat if !animal.mouseHunter -> animal.feedCat()
    is Dog -> animal.feedDog()
    else -> println("Unknown")
}
```

### Explicit Backing Fields (2.3, Experimental)

Eliminates the `_backing` property pattern:

```kotlin
val city: StateFlow<String>
    field = MutableStateFlow("")

fun updateCity(newCity: String) {
    city.value = newCity  // smart cast to MutableStateFlow works
}
```

### Multi-dollar String Interpolation (2.1, Preview)

Use `$$` prefix so single `$` is literal:

```kotlin
val json = $$"""
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "$${simpleName}"
}
"""
```

### Non-local Break and Continue (2.1, Preview)

`break`/`continue` work inside lambdas passed to inline functions:

```kotlin
for (element in elements) {
    val value = element.nullableMethod() ?: run {
        continue  // works in inline lambda
    }
}
```

### Unused Return Value Checker (2.3, Experimental)

```kotlin
@file:MustUseReturnValues  // or annotate class/function
// Suppress: val _ = computeValue()
// Exclude: @IgnorableReturnValue
```

Enable: `-Xreturn-value-checker=check` (annotated scopes) or `=full` (all project functions).

### UUID (2.3, Experimental)

```kotlin
val v4 = Uuid.generateV4()         // explicit v4
val v7 = Uuid.generateV7()         // time-ordered v7
val parsed = Uuid.parseOrNull("…") // null instead of throwing
val atTime = Uuid.generateV7NonMonotonicAt(instant)
```

### `kotlin.time.Clock` and `Instant` are Stable (2.3)

No more `@OptIn(ExperimentalTime::class)` needed:

```kotlin
val now = Clock.System.now()  // returns Instant
```

### Power-assert Plugin (2.0, Experimental)

```kotlin
plugins {
    kotlin("plugin.power-assert") version "2.0.0"
}
powerAssert {
    functions = listOf("kotlin.assert", "kotlin.test.assertTrue")
}
```

### KMP Android Target Migration (2.3)

Use Google's `com.android.kotlin.multiplatform.library` plugin. Rename `androidTarget` to `android`. Old `kotlin-android` plugin deprecated with AGP 9.0+.

### Ktor 3.0 — kotlinx-io Migration

`Input`/`Output`/`ByteReadChannel`/`ByteWriteChannel` are deprecated. Use kotlinx-io `Source`/`Sink` instead.

### Ktor 3.0 — SSE Support

```kotlin
// Server
install(SSE)
routing {
    sse {
        send(ServerSentEvent(data = "Hello"))
        close()
    }
}

// Client
val client = HttpClient(CIO) { install(SSE) }
client.sse(host = "127.0.0.1", port = 8080, path = "/sse") {
    incoming.collect { event -> println(event) }
}
```

### Ktor 3.0 — CSRF Plugin

```kotlin
install(CSRF) {
    allowOrigin("https://example.com")
    originMatchesHost()
    checkHeader("X-CSRF") { csrfHeader -> /* validate */ true }
    onFailure { respondText("Forbidden", status = HttpStatusCode.Forbidden) }
}
```

### Flow Terminal Operators (Coroutines 1.10)

```kotlin
flow.any { it > 0 }   // terminal, returns Boolean
flow.all { it > 0 }   // terminal, returns Boolean
flow.none { it > 0 }  // terminal, returns Boolean
flow.chunked(5)        // Flow<List<T>>, groups emissions (1.9)
```

### Serialization 1.10 — Stabilized APIs

Remove `@OptIn` for: `allowTrailingComma`, `allowComments`, `decodeEnumsCaseInsensitive`, `prettyPrintIndent`, `@EncodeDefault`, `JsonUnquotedLiteral`, `JsonPrimitive` with unsigned types.

### Serialization 1.10 — `subclassesOfSealed`

```kotlin
val module = SerializersModule {
    polymorphic(Base::class) {
        subclassesOfSealed(MySealedClass::class)
    }
}
```

### Compose Multiplatform 1.10 — Navigation 3

`PredictiveBackHandler()` deprecated in favor of `NavigationBackHandler()` from the Navigation Event library.

### Compose Multiplatform 1.10 — Unified `@Preview`

Use `androidx.compose.ui.tooling.preview.Preview` in `commonMain`. Old platform-specific annotations deprecated.

### Compose Multiplatform 1.10 — Deprecated Dependency Aliases

`compose.ui`, `compose.material3` aliases in Gradle plugin are deprecated. Use direct version catalog references instead.
