# Kotlin Language Features (2.1–2.3)

## Guard Conditions in `when` (2.1, Preview)

Add secondary conditions to `when` branches with `if`. Enables pattern matching with additional constraints without nesting.

```kotlin
when (animal) {
    is Cat if !animal.mouseHunter -> animal.feedCat()
    is Dog -> animal.feedDog()
    else -> println("Unknown")
}
```

Enable: `-Xwhen-guards`

## Multi-dollar String Interpolation (2.1, Preview)

Use `$$` prefix so single `$` is literal text; `$$` triggers interpolation. Useful for JSON schemas, template engines, and other dollar-heavy formats.

```kotlin
val json = $$"""
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "$${simpleName}"
}
"""
```

Enable: `-Xmulti-dollar-interpolation`

## Non-local Break and Continue (2.1, Preview)

`break` and `continue` now work inside lambdas passed to inline functions:

```kotlin
for (element in elements) {
    val value = element.nullableMethod() ?: run {
        continue  // works in inline lambda
    }
}
```

Enable: `-Xnon-local-break-continue`

## Explicit Backing Fields (2.3, Experimental)

Eliminates the common `_backing` property pattern. The `field` keyword declares the backing field type directly, allowing the property to expose a wider type while the backing field holds a narrower mutable type.

```kotlin
val city: StateFlow<String>
    field = MutableStateFlow("")

fun updateCity(newCity: String) {
    city.value = newCity  // smart cast to MutableStateFlow works
}
```

Enable: `-Xexplicit-backing-fields`

## Unused Return Value Checker (2.3, Experimental)

Warns when function results are silently dropped. Helps catch bugs where important return values (error codes, new collections, etc.) are accidentally ignored.

```kotlin
@file:MustUseReturnValues  // apply to entire file
// Or annotate individual classes/functions

// Suppress for intentional drops:
val _ = computeValue()

// Exclude functions that are safe to ignore:
@IgnorableReturnValue
fun log(message: String): Boolean { /* ... */ }
```

Enable modes:
- `-Xreturn-value-checker=check` — only checks annotated scopes (`@MustUseReturnValues`)
- `-Xreturn-value-checker=full` — checks all project functions

## UUID Improvements (2.3, Experimental)

```kotlin
val v4 = Uuid.generateV4()         // explicit v4 generation
val v7 = Uuid.generateV7()         // time-ordered v7 (sortable)
val parsed = Uuid.parseOrNull("…") // returns null instead of throwing
val atTime = Uuid.generateV7NonMonotonicAt(instant) // v7 at specific timestamp
```

## `kotlin.time.Clock` and `kotlin.time.Instant` are Stable (2.3)

Time tracking APIs promoted from experimental. Use for cross-platform time handling:

```kotlin
val now = Clock.System.now()  // returns Instant
```

No more `@OptIn(ExperimentalTime::class)` needed.
