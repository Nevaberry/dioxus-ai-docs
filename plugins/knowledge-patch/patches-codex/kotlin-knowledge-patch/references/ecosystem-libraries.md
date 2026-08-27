# Ecosystem libraries

## kotlinx.coroutines

Coroutines 1.10 adds terminal `Flow.any`, `Flow.all`, and `Flow.none`; coroutines 1.9 adds `Flow<T>.chunked(size: Int)` for consecutive groups.

```kotlin
val hasErrors = events.any { it.isError }
val pages: Flow<List<Record>> = records.chunked(100)
```

From 1.9, `limitedParallelism` accepts an optional diagnostic name and closeable dispatchers implement `AutoCloseable`. Close them with `use` when the backing dispatcher owns resources.

```kotlin
val parser = Dispatchers.Default.limitedParallelism(2, "parser")
executor.asCoroutineDispatcher().use { dispatcher ->
    runBlocking(dispatcher) { doWork() }
}
```

Coroutines 1.8 gives `runTest` a 60-second whole-test timeout. Override per test with `timeout` or globally on JVM with `kotlinx.coroutines.test.default_timeout` and a duration such as `10s`.

Positive sub-millisecond `delay(Duration)` values round up to a whole millisecond instead of becoming zero. Coroutines 1.10 moves direct debug-agent references from `kotlinx.coroutines.debug.AgentPremain` to `kotlinx.coroutines.debug.internal.AgentPremain` while reorganizing debug/core artifacts.

## kotlinx.serialization

### JSON and return-value checking

Serialization 1.10 stabilizes `decodeEnumsCaseInsensitive`, `allowTrailingComma`, `allowComments`, `prettyPrintIndent`, `@EncodeDefault`, `JsonUnquotedLiteral`, unsigned `JsonPrimitive` constructors, and JSON DSL `Nothing?` overloads.

Its APIs participate in Kotlin 2.3 return-value checking, so ignoring a result such as `Json.encodeToString(...)` can warn. Serialization 1.8 adds `@JsonIgnoreUnknownKeys` for per-class leniency without weakening other classes in the same `Json` configuration.

Discriminator conflicts caused by naming strategies, `ClassDiscriminatorMode.ALL_JSON_OBJECTS`, or default polymorphic serializers now throw `SerializationException` on encode. Decode accepts a colliding payload key for sealed/open hierarchies. `MissingFieldException.serialName` identifies the class missing a required field.

### Time and UUID serializers

Serialization 1.9 requires Kotlin 2.2 and supplies default string `InstantSerializer` plus component-oriented `InstantComponentSerializer` for `kotlin.time.Instant`.

Serialization 1.7.2 provides `Uuid.serializer()` for `kotlin.uuid.Uuid`. With the Kotlin 2.0.20 plugin mark UUID properties `@Contextual`; Kotlin 2.1 can insert the serializer automatically.

### Modules, descriptors, and generated serializers

Serialization 1.10 adds `subclassesOfSealed` so a module can register all known subclasses of a sealed branch under an abstract/interface root.

Serialization 1.8 stabilizes `SerialDescriptor`, `SerialKind`, and most builder APIs; `PolymorphicKind` remains experimental. `@SealedSerializationApi` marks APIs safe to consume but requiring opt-in to implement or inherit.

Since 1.7, `SerializersModule.serializer<T>()` prefers a contextual serializer registered for a non-sealed interface and falls back to `PolymorphicSerializer`. Runtime 1.7 requires a compiler plugin of at least Kotlin 2.0.0-RC1 so lookup order matches.

With serialization 1.7.2 and Kotlin 2.0.20+, experimental `@KeepGeneratedSerializer` retains the generated serializer even when a custom serializer is declared; retrieve it with `generatedSerializer()`.

### ProtoBuf and CBOR

Serialization 1.8.1 allows nullable `JsonTransformingSerializer` type arguments and ProtoBuf null map keys/values. Experimental `@ProtoOneOf` maps a Protobuf `oneof` to a sealed Kotlin hierarchy.

Serialization 1.7.2 adds `@CborLabel`, key/value tag encoding and verification, definite lengths, byte-string preference, and readable `CborConfiguration` for custom `CborEncoder` / `CborDecoder` implementations. `Cbor.CoseCompliant` is a preset, but canonical key sorting remains separate.

### kotlinx-io

The `kotlinx-serialization-json-io` artifact provides `encodeToSink`, `decodeFromSource`, and lazy `decodeSourceToSequence` for `kotlinx-io` sinks and sources.

## Ktor

Ktor 3 provides server-sent events and Wasm plus enhanced configuration. Delivered ecosystem capabilities include Client/Server OpenAPI support, a WebRTC client, and simpler dependency injection.

Ktor 3.4 adds Zstd compression, duplex OkHttp streaming, and structured-concurrency integration for the HTTP request lifecycle.

## Exposed

Exposed 1.0.0 is released with a stable API and a promise of no breaking changes until the next major release. R2DBC support is available for reactive database connectivity, and the reworked library has a first-class IDE plugin.

## Koog

Koog is an open-source Kotlin framework for agents built from predefined/composable workflows and patterns. Koog 0.5 adds Agent2Agent protocol support and native ACP integration for connecting custom agents to an IDE.

Koog 0.4 adds observability and Ktor integrations, native structured outputs, and an iOS target.

## IDE and editor tooling

IntelliJ IDEA 2025.1 uses K2 analysis by default. The official Kotlin language server and Visual Studio Code extension are pre-Alpha, with basic completion, navigation, inspections, quick fixes, Java interop, and project import.
