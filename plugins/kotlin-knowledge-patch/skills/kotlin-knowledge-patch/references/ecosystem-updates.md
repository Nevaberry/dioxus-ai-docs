# Kotlin Ecosystem Updates

## Ktor 3.0 (2024-10-10)

### Migrated to kotlinx-io

Low-level IO APIs (`Input`, `Output`, `ByteReadChannel`, `ByteWriteChannel`) are deprecated. Use kotlinx-io `Source`/`Sink` instead. Old APIs remain supported until Ktor 4.0.

### SSE Support (Server-Sent Events)

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

### CSRF Plugin

```kotlin
install(CSRF) {
    allowOrigin("https://example.com")
    originMatchesHost()
    checkHeader("X-CSRF") { csrfHeader -> /* validate */ true }
    onFailure { respondText("Forbidden", status = HttpStatusCode.Forbidden) }
}
```

## Coroutines 1.9–1.10

### New Flow Operators

```kotlin
flow.chunked(5)      // Flow<List<T>>, groups emissions into lists (1.9)
flow.any { it > 0 }  // terminal operator, returns Boolean (1.10)
flow.all { it > 0 }  // terminal operator, returns Boolean (1.10)
flow.none { it > 0 } // terminal operator, returns Boolean (1.10)
```

## Serialization 1.10 (2026-01-21)

### Stabilized JSON APIs

These are no longer experimental — remove `@OptIn` annotations:
- `allowTrailingComma`, `allowComments`, `decodeEnumsCaseInsensitive`, `prettyPrintIndent`
- `@EncodeDefault` annotation
- `JsonUnquotedLiteral`, `JsonPrimitive` with unsigned types

### `subclassesOfSealed` Utility

Auto-registers all sealed subclass serializers in polymorphic modules, eliminating manual registration:

```kotlin
val module = SerializersModule {
    polymorphic(Base::class) {
        subclassesOfSealed(MySealedClass::class)
    }
}
```
