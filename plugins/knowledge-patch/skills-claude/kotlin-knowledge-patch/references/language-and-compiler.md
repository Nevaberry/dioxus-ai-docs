# Language and compiler

The guidance from `2.2-language-guide`, `2.2-tooling-guide`, `2.3-language-guide`, and `2.3-tooling-guide` is organized here by migration task. Patch-specific compiler, reflection, metadata, and scripting repairs from `2.3.0` and `2.4.10` are included where they affect diagnosis.

## Context parameters

### Declarations and function types

Context receivers are no longer supported as of Kotlin 2.3.20. Rewrite them as context parameters. They can appear only on functions and whole properties, not constructors or classes. A contextual property has no backing field, initializer, or delegate and therefore needs an accessor. Use `_` when a value participates in resolution but must not be available by name.

```kotlin
context(users: UserRepository)
val firstUser: User? get() = users.getById(1)
```

Context function types contain only types, not parameter names. Retrieve an anonymous contextual value inside a lambda with `implicit<T>()`:

```kotlin
fun <R> withLogger(logger: Logger, block: context(Logger) () -> R): R =
    block(logger)

val task: context(Logger) () -> Unit = {
    implicit<Logger>().log("ready")
}
```

Resolution selects exactly one compatible contextual value at the nearest scope level. Multiple same-level candidates are ambiguous, and `@DslMarker` restrictions apply to context parameters as well as receivers. Since 2.3.20, an otherwise matching contextual overload is not more specific than a non-contextual overload; a call can become ambiguous, and a shadowed contextual declaration produces a warning.

Callable references eagerly resolve and capture their context at creation, so the resulting function type has no context parameters. Reflection exposes each context parameter as `KParameter.Kind.CONTEXT_PARAMETER`. On the JVM, context parameters precede the extension receiver and ordinary parameters in the method ABI.

## Context-sensitive resolution and destructuring

With `-Xcontext-sensitive-resolution`, enum entries and sealed members may omit their type qualifier when an expected type comes from a `when` subject, declaration, parameter, return type, type check, or cast. Functions, parameterized properties, and extension properties are not resolved this way. The later preview also looks in sealed and enclosing supertypes of the expected type, but not arbitrary supertype scopes; type operators and equality expressions warn when clashing declarations make lookup ambiguous.

```kotlin
val problem: Problem = CONNECTION
fun label(p: Problem) = when (p) {
    CONNECTION -> "network"
    else -> "other"
}
```

Name-based destructuring remains experimental. `-Xname-based-destructuring=only-syntax` enables explicit variable-to-property bindings while retaining existing positional destructuring. `name-mismatch` warns when data-class property and variable names differ. `complete` makes the short parenthesized form name-based and reserves square brackets for positional destructuring.

```kotlin
data class User(val username: String, val email: String)
val user = User("alice", "alice@example.com")
(val mail = email, val name = username) = user
val [username, email] = user
```

## Function bodies, overloads, catches, and contracts

With language version 2.3, an untyped lambda passed to overloads accepting `() -> T` and `suspend () -> T` selects the non-suspending overload. Use `suspend { ... }` to select the suspending overload. Kotlin 2.2.20 can preview this with `-language-version 2.3`.

```kotlin
transform { 42 }
transform(suspend { 42 })
```

Returns inside expression-bodied functions are stable when the function declares its return type. The same construct without an explicit return type is headed for deprecation.

```kotlin
fun valueOrZero(value: Int?): Int = value ?: return 0
```

Data-flow-based exhaustiveness for `when` is stable. Earlier builds need `-Xdata-flow-based-exhaustiveness`; the compiler can then use prior checks and early returns instead of demanding a redundant `else`.

`-Xallow-reified-type-in-catch` permits an inline function to catch `reified T : Throwable`; it was experimental in 2.2.20 and planned as a default for 2.4.

Extended contracts can assert generic types and appear in accessors and selected operators with `-Xallow-contracts-on-more-functions`. `returnsNotNull()` requires `-Xallow-condition-implies-returns-contracts`; `condition holdsIn block` requires `-Xallow-holdsin-contract`. The latter two also require `ExperimentalExtendedContracts`.

A lambda used as a parameter's default value cannot contain a non-local `return`. Move that return logic outside the default expression.

## Annotation targets, metadata, and JVM exposure

`-Xannotation-target-all` enables `@all:Ann`, propagating an annotation to each applicable constructor parameter, Kotlin property, backing field, getter, setter parameter, and JVM record component. Independently, `-Xannotation-default-target=param-property` applies an unqualified annotation to `param` where possible and also to `property`, or to `field` when no property target applies. Use `first-only` for the old behavior.

```kotlin
@JvmRecord
data class Person(@all:Positive val age: Int)
```

`-Xannotations-in-metadata` stores declaration, accessor, receiver, backing-field, delegate-field, and enum-entry annotations in Kotlin metadata. Consumers read them through experimental `Km*.annotations` APIs and should tolerate annotation data before writing becomes the default. Kotlin 2.3.21 also exposes compiler-plugin metadata through `CompilerPluginData` in the `kotlinx-metadata` Km API.

Use `@JvmExposeBoxed` for Java-callable boxed constructors or function variants involving inline value classes; `-Xjvm-expose-boxed` applies it to a whole module without changing Kotlin's internal unboxed use.

Annotated JVM lambdas now use `LambdaMetafactory` by default. Reflection cannot assume annotations live on a generated lambda class; `-Xindy-allow-annotated-lambdas=false` temporarily restores class-based generation.

The stable `-jvm-default` option replaces `-Xjvm-default`. Its `enable` default emits interface defaults with compatibility bridges and `DefaultImpls`; `no-compatibility` emits only interface defaults, while `disable` restores `DefaultImpls`-only output.

Top-level lambdas now share the type-checking rules used for call-argument lambdas, which can change reflection-visible generic signatures.

## Source checks and removed forms

K2 reports errors when:

- An inferred generic expression type exposes a type available only through an indirect dependency. Add the direct dependency.
- A declaration's type-parameter bound is less visible than the declaration.
- A non-private inline declaration refers to private types or members. Align visibility; simply removing `inline` changes the binary API.
- A type alias with variance such as `out` is used for a constructor call or supertype. Use the expanded type. `reified` on a type-alias parameter is also rejected.
- A nullable type introduced through a type alias is used as a supertype.
- A reified parameter is inferred as an intersection type.
- `@JvmSerializableLambda` is applied to an `inline` or `crossinline` lambda.
- A generic Kotlin interface is delegated to a Java implementation whose override is non-generic.

Kotlin 2.3.0 promoted inferred type arguments violating upper bounds from warning to error, including inference involving aliases. Kotlin 2.3.21 rolled that check back temporarily, so successful compilation there is not a final migration check.

Synthetic property syntax is not created for getters declared in Kotlin, including through Java subclasses or mapped types; call the getter. Callable references to Java synthetic properties are a revoked language feature and must not be used in new code.

Boxed inline value classes no longer pass `is` or `as` checks for `java.lang.Number` or `java.lang.Comparable` solely because the underlying primitive does.

The compiler rejects `-language-version=1.6` and `1.7`; 2.2 warns for 1.8 and 1.9. Kotlin 2.3 rejects 1.8 everywhere and 1.9 on non-JVM platforms, while JVM compilation retains 1.9 support. K1 is deprecated; migrate remaining K1 selections to K2.

JSpecify nullness support is finalized. When an upgrade changes enhanced Java nullability behavior, verify whether a patch release repairs a compiler regression before weakening annotations.

## Return-value checking and explicit backing fields

`-Xreturn-value-checker=check` warns for discarded non-`Unit`, non-`Nothing` results from marked APIs and scopes, including most standard-library functions. `full` treats project files as marked. Express policy with `@MustUseReturnValues` or `@IgnorableReturnValue`; write `val _ = call()` for an intentional discard.

```kotlin
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xreturn-value-checker=check")
    }
}
```

With `-Xexplicit-backing-fields`, a public property can expose a stable interface while storing a narrower type. Code in the same private scope sees the implementation type and can smart-cast it.

```kotlin
val city: StateFlow<String>
    field = MutableStateFlow("")

fun updateCity(value: String) { city.value = value }
```

Use experimental per-diagnostic control as `-Xwarning-level=DIAGNOSTIC_NAME:error|warning|disabled`. It overrides global `-Werror`, `-nowarn`, or `-Wextra` for that diagnostic.

## JVM interop diagnostics

Kotlin can target Java 25 bytecode. The JPA plugin now combines `no-arg` and `all-open`, opening `javax.persistence` and `jakarta.persistence` entities, embeddables, and mapped superclasses; Maven's `kotlin-maven-noarg` also brings in `kotlin-maven-allopen`.

Vert.x `io.vertx.codegen.annotations.Nullable` is recognized, with mismatches warned by default. Promote it to strict with `-Xnullability-annotations=@io.vertx.codegen.annotations:strict`.

Java APIs annotated `org.jetbrains.annotations.Unmodifiable` or `UnmodifiableView` map to read-only Kotlin collection types. Assignment to a mutable collection warns in 2.3.20 and is planned to become an error in 2.5.0.

## Scripting and command-line behavior

The `kotlinc` REPL requires `-Xrepl`. JSR-223 remains restricted to language version 1.9 and is not migrating to K2. Maven `KotlinScriptMojo` is deprecated.

Kotlin 2.1.21 restores dependency resolution in `main.kts` after the 2.1.20 regression. Kotlin 2.3.21 corrects `scriptCompilationClasspathFromContext`, anonymous-object scratch-script backend failures, destructuring code generation, and missing `ScriptDiagnostic` source locations.

Kotlin 2.4.10 restores `@file:CompilerOptions("-jvm-target", ...)` in `.main.kts` instead of silently using JVM 1.8, and fixes K2 `FirResolvedTypeRef` failures for extension functions imported from other scripts.

The Kotlin distribution includes the `kotlinr` command starting in 2.4.10.

## Patch-upgrade diagnostics

Prefer an upgrade to Kotlin 2.3.10 over source workarounds for instability involving enhanced Java nullability, overload resolution, `UInt` constants throwing `ClassCastException`, JSpecify `@NullMarked` conflicts on `equals(Any?)`, incorrect `@NoInfer`, a serialization-plugin race registering Protobuf extensions, or `NoWhenBranchMatchedException` after a `!is` check through a non-sealed intermediate type.

Kotlin 2.3.10 also repairs `KotlinReflectionInternalError` for references to `FunctionN.invoke` and type parameters in generic supertypes, plus incorrect `KType` argument comparisons when a type parameter is `Nothing`.

Kotlin 2.3.21 fixes common `@JvmRecord` metadata compilation when `java.lang.Record` is inaccessible and removes a false `SUBCLASS_CANT_CALL_COMPANION_PROTECTED_NON_STATIC` diagnostic in multi-module projects.

Kotlin 2.4.10 fixes a JVM backend `IllegalStateException` when a nested Java annotation-array argument uses a `const val`, and restores expected-type propagation into reified inline calls inside a lambda with an Elvis expression.
