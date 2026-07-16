# Ecosystem libraries

## kotlinx.coroutines

### Flow terminal predicates

Coroutines 1.10 adds terminal `Flow.any`, `Flow.all`, and `Flow.none` operators:

```kotlin
val hasErrors = events.any { it.isError }
```

### Flow chunking

Coroutines 1.9 adds `Flow<T>.chunked(size: Int)`, which emits lists containing consecutive groups of upstream values:

```kotlin
val pages: Flow<List<Record>> = records.chunked(100)
```

### Dispatcher views

In coroutines 1.9, `limitedParallelism` accepts an optional view name for diagnostics, and closeable dispatchers implement `AutoCloseable`.

```kotlin
val parser = Dispatchers.Default.limitedParallelism(2, "parser")
executor.asCoroutineDispatcher().use { dispatcher ->
    runBlocking(dispatcher) { doWork() }
}
```

### Test timeouts

Coroutines 1.8 changes the default whole-test timeout to 60 seconds. Pass `timeout` per test or set the JVM-wide `kotlinx.coroutines.test.default_timeout` system property with a duration such as `10s`.

```kotlin
runTest(timeout = 30.seconds) { exerciseSubject() }
```

### Delay rounding

Starting with coroutines 1.8, `delay(Duration)` rounds positive nanoseconds up to a whole millisecond instead of down, so a sub-millisecond delay no longer becomes zero delay.

### Debug agent package

Coroutines 1.10 moves direct references to `kotlinx.coroutines.debug.AgentPremain` to `kotlinx.coroutines.debug.internal.AgentPremain` while reorganizing debug and core artifacts.

## kotlinx.serialization

### Stable JSON options

Serialization 1.10 stabilizes `decodeEnumsCaseInsensitive`, `allowTrailingComma`, `allowComments`, and `prettyPrintIndent`. It also stabilizes `@EncodeDefault`, `JsonUnquotedLiteral`, unsigned `JsonPrimitive` constructors, and the JSON DSL's `Nothing?` overloads.

Serialization 1.10 marks its APIs for Kotlin's return-value checker. Ignoring a result such as `Json.encodeToString(...)` can warn when the checker is enabled.

### Unknown keys and diagnostics

Serialization 1.8 adds `@JsonIgnoreUnknownKeys`, which permits unknown properties only for annotated classes while others retain the `Json` instance's strict behavior.

```kotlin
@Serializable
@JsonIgnoreUnknownKeys
data class Envelope(val value: String)
```

Serialization 1.10 detects class-discriminator conflicts introduced by naming strategies, `ClassDiscriminatorMode.ALL_JSON_OBJECTS`, or polymorphic default serializers during encoding and throws `SerializationException`. Decoding accepts a colliding payload key for both sealed and open hierarchies. `MissingFieldException.serialName` identifies the class whose required field is absent.

### Time and UUID serializers

Serialization 1.9 requires Kotlin 2.2 and supplies a default string-based `InstantSerializer` for `kotlin.time.Instant` plus `InstantComponentSerializer` for component-based encoding.

```kotlin
@Serializable
data class Event(
    @Serializable(with = InstantComponentSerializer::class)
    val occurredAt: Instant,
)
```

Serialization 1.7.2 provides `Uuid.serializer()` for `kotlin.uuid.Uuid`. With the Kotlin 2.0.20 plugin, mark UUID properties `@Contextual`; Kotlin 2.1 can insert the serializer automatically.

```kotlin
@Serializable
data class Row(@Contextual val id: Uuid)
```

### Polymorphism and sealed hierarchies

Serialization 1.10 adds `subclassesOfSealed` to `SerializersModule`, allowing an abstract or interface root to register all known subclasses of a sealed branch without listing them individually.

Since serialization 1.7, `SerializersModule.serializer<T>()` first uses a contextual serializer registered for a non-sealed interface and falls back to `PolymorphicSerializer` only when none exists. Runtime 1.7 requires a serialization compiler plugin of at least Kotlin 2.0.0-RC1 so runtime and plugin use the same lookup order.

### Descriptor stability

Serialization 1.8 makes `SerialDescriptor`, `SerialKind`, and most related builder APIs stable; `PolymorphicKind` remains experimental. `@SealedSerializationApi` marks the public APIs as safe to consume but requiring opt-in to implement or inherit.

### Nullable serializers and ProtoBuf maps

Serialization 1.8.1 permits nullable type arguments in `JsonTransformingSerializer` and adds ProtoBuf encoding for null map keys and values.

### CBOR and COSE

Serialization 1.7.2 adds `@CborLabel`, key/value tag encoding and verification flags, definite-length encoding, and byte-string preference. Custom `CborEncoder` and `CborDecoder` implementations can inspect the resulting `CborConfiguration`.

`Cbor.CoseCompliant` provides a preset, but canonical key sorting must still be done separately.

```kotlin
val cbor = Cbor {
    preferCborLabelsOverNames = true
    useDefiniteLengthEncoding = true
    alwaysUseByteString = true
}
val cose = Cbor.CoseCompliant
```

### Retaining generated serializers

With serialization 1.7.2 and Kotlin 2.0.20 or newer, Experimental `@KeepGeneratedSerializer` retains the plugin-generated serializer when the class declares a custom one. Retrieve it from the companion with `generatedSerializer()`.

```kotlin
@OptIn(ExperimentalSerializationApi::class)
@KeepGeneratedSerializer
@Serializable(with = PayloadSerializer::class)
data class Payload(val value: String)

val generated = Payload.generatedSerializer()
```

### kotlinx-io integration

Serialization 1.7.1 adds `kotlinx-serialization-json-io` with `encodeToSink`, `decodeFromSource`, and lazy `decodeSourceToSequence` operations for `kotlinx-io` sinks and sources.

### ProtoBuf oneof

Serialization 1.7 adds Experimental `@ProtoOneOf`, representing a Protocol Buffers `oneof` field as a Kotlin sealed-class hierarchy.

## Ktor

Ktor 3 adds server-sent events and WebAssembly support alongside enhanced configuration capabilities.

OpenAPI specification support for Ktor Client and Server applications is delivered. Ktor also has WebRTC client support and completed work to simplify dependency-injection usage.

Ktor 3.4 adds Zstd support to the compression plugin, duplex streaming for OkHttp, and structured-concurrency integrations for the HTTP request lifecycle.

## Exposed

Exposed 1.0.0 is released, allowing projects to target its 1.0 line rather than pre-1.0 artifacts. The 1.0 stable API promises no breaking changes until the next major release.

R2DBC support is delivered, adding reactive database connectivity. The reworked library also has a plugin providing first-class IDE support.

## Koog

Koog is an open-source Kotlin framework for building AI agents from predefined workflows and patterns that can be used directly or combined.

Koog 0.5 adds full Agent2Agent (A2A) protocol support for interconnected agents. Native Agent Client Protocol (ACP) integration lets a custom Koog agent connect to an IDE.

Koog 0.4 adds observability integrations, Ktor integration, native structured-output support, and an iOS target, expanding deployment and monitoring options.

## IDE and editor tooling

IntelliJ IDEA 2025.1 enables K2 mode by default and reuses parts of the K2 compiler for code analysis.

The official Kotlin language server (LSP) and Visual Studio Code extension entered pre-Alpha with basic completion, navigation, inspections, quick fixes, Java interoperability, and project import.

The Kotlin Multiplatform IDE plugin supports Windows and Linux development hosts; Native-specific implications are covered in [multiplatform-and-native.md](multiplatform-and-native.md).

## Release cadence

Since Kotlin 2.0, `2.x.0` language releases arrive about every six months, followed roughly three months later by a `2.x.20` tooling release. Bug-fix `2.x.yz` releases have no fixed schedule, and language and tooling releases receive several EAP builds.
