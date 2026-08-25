# Ecosystem libraries and tooling

## Coroutines and Flow

Coroutines 1.10 adds the terminal predicates `Flow.any`, `Flow.all`, and `Flow.none`.

```kotlin
val hasErrors = events.any { it.isError }
```

Coroutines 1.9 adds `Flow<T>.chunked(size: Int)`, emitting lists of consecutive upstream values.

```kotlin
val pages: Flow<List<Record>> = records.chunked(100)
```

`limitedParallelism` accepts an optional view name for diagnostics, and closeable dispatchers implement `AutoCloseable`. Close a view with `use` when its backing dispatcher is closeable.

```kotlin
val parser = Dispatchers.Default.limitedParallelism(2, "parser")
executor.asCoroutineDispatcher().use { dispatcher ->
    runBlocking(dispatcher) { doWork() }
}
```

Coroutines 1.8 changes `runTest`'s default whole-test timeout to 60 seconds. Pass `timeout` on a test or set the JVM-wide `kotlinx.coroutines.test.default_timeout` system property to a duration such as `10s`.

```kotlin
runTest(timeout = 30.seconds) { exerciseSubject() }
```

Starting with 1.8, `delay(Duration)` rounds positive sub-millisecond values up to one millisecond instead of down to zero.

Coroutines 1.10 moves direct debug-agent references from `kotlinx.coroutines.debug.AgentPremain` to `kotlinx.coroutines.debug.internal.AgentPremain` while reorganizing debug and core artifacts.

## Serialization JSON behavior

Serialization 1.10 stabilizes `decodeEnumsCaseInsensitive`, `allowTrailingComma`, `allowComments`, and `prettyPrintIndent`; `@EncodeDefault`, `JsonUnquotedLiteral`, unsigned `JsonPrimitive` constructors, and JSON DSL `Nothing?` overloads are also stable.

Serialization APIs are marked for Kotlin 2.3's return-value checker. When enabled, discarding results such as `Json.encodeToString(...)` can warn.

Serialization 1.8 adds `@JsonIgnoreUnknownKeys`, allowing unknown keys only for an annotated class while leaving the containing `Json` instance's policy unchanged.

```kotlin
@Serializable
@JsonIgnoreUnknownKeys
data class Envelope(val value: String)
```

Serialization 1.10 detects class-discriminator conflicts caused by naming strategies, `ClassDiscriminatorMode.ALL_JSON_OBJECTS`, or polymorphic default serializers and throws `SerializationException` during encoding. Decoding accepts a payload key that collides with the discriminator for sealed and open hierarchies. `MissingFieldException.serialName` reports the class whose required field was missing.

`SerialDescriptor`, `SerialKind`, and most descriptor builders are stable as of serialization 1.8; `PolymorphicKind` remains experimental. `@SealedSerializationApi` marks public descriptor APIs that are stable to consume but still require opt-in to implement or inherit.

Serialization 1.8.1 permits nullable type arguments in `JsonTransformingSerializer`.

## Serialization time, UUID, and I/O

Serialization 1.9 requires Kotlin 2.2 and provides a default string `InstantSerializer` for `kotlin.time.Instant` plus component-form `InstantComponentSerializer`.

```kotlin
@Serializable
data class Event(
    @Serializable(with = InstantComponentSerializer::class)
    val occurredAt: Instant,
)
```

Serialization 1.7.2 supplies `Uuid.serializer()` for common `kotlin.uuid.Uuid`. With the Kotlin 2.0.20 compiler plugin, annotate UUID properties with `@Contextual`; Kotlin 2.1 can supply the serializer automatically.

```kotlin
@Serializable
data class Row(@Contextual val id: Uuid)
```

The `kotlinx-serialization-json-io` artifact added in 1.7.1 integrates `kotlinx-io` through `encodeToSink`, `decodeFromSource`, and lazy `decodeSourceToSequence`.

## Serialization polymorphism and generated serializers

Serialization 1.10 adds `subclassesOfSealed` to `SerializersModule`, allowing an abstract or interface root to register all known subclasses of a sealed branch at once.

For a non-sealed interface, `SerializersModule.serializer<T>()` chooses a registered contextual serializer before falling back to `PolymorphicSerializer`. Runtime 1.7 requires a serialization compiler plugin of at least Kotlin 2.0.0-RC1 so runtime and generated code use the same lookup order.

With serialization 1.7.2 and Kotlin 2.0.20 or newer, experimental `@KeepGeneratedSerializer` retains the plugin-generated serializer even when a custom serializer is declared. Retrieve it from the companion with `generatedSerializer()`.

```kotlin
@OptIn(ExperimentalSerializationApi::class)
@KeepGeneratedSerializer
@Serializable(with = PayloadSerializer::class)
data class Payload(val value: String)

val generated = Payload.generatedSerializer()
```

## Serialization CBOR and ProtoBuf

Serialization 1.7.2 adds `@CborLabel`, key/value tag encoding and verification, definite-length encoding, and byte-string preference. Custom `CborEncoder` and `CborDecoder` implementations can read the active `CborConfiguration`. `Cbor.CoseCompliant` supplies a COSE preset, but canonical key sorting remains a separate responsibility.

```kotlin
val cbor = Cbor {
    preferCborLabelsOverNames = true
    useDefiniteLengthEncoding = true
    alwaysUseByteString = true
}
val cose = Cbor.CoseCompliant
```

Serialization 1.8.1 encodes null keys and values in ProtoBuf maps. Serialization 1.7 adds experimental `@ProtoOneOf`, representing a Protocol Buffers `oneof` as a Kotlin sealed hierarchy.

## Ktor

Ktor 3 adds server-sent events, WebAssembly support, and expanded configuration capabilities.

OpenAPI support for Ktor Client and Server, a WebRTC client, and simplified dependency-injection usage are delivered capabilities rather than pending roadmap items.

Ktor 3.4 adds Zstd to the compression plugin, duplex streaming for OkHttp, and structured-concurrency integration across the HTTP request lifecycle.

## Exposed

Exposed 1.0.0 is released. Its stable 1.x API promises no breaking changes until the next major version.

R2DBC support is complete, providing reactive database connectivity. The reworked library also has a plugin for first-class IDE support.

## Koog

Koog is an open-source Kotlin framework for agent systems built from predefined, reusable workflows and patterns.

Koog 0.5 supports the Agent2Agent protocol and native ACP integration, allowing a custom Koog agent to connect to an IDE.

Koog 0.4 adds observability integrations, Ktor integration, native structured outputs, and an iOS target.

## IDE and editor tooling

IntelliJ IDEA 2025.1 enables K2 analysis by default and reuses parts of the K2 compiler for code analysis.

The official Kotlin language server and Visual Studio Code extension are pre-Alpha. Their initial capabilities include completion, navigation, inspections, quick fixes, Java interop, and project import.

## Release planning

Since Kotlin 2.0, `2.x.0` language releases arrive about every six months and `2.x.20` tooling releases roughly three months later. Bug-fix `2.x.yz` releases have no fixed schedule, and language and tooling releases receive EAP builds. Plan version constraints around actual compatibility requirements rather than assuming every minor or patch release follows the same timing.
