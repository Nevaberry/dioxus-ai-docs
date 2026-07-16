# Language and compiler

## Context parameters and resolution

### Declaration constraints

Context parameters can be declared only on functions and whole properties, not constructors or classes. A contextual property has no backing field, so it needs an accessor and cannot have an initializer or delegate; `_` declares a value usable for context resolution but not by name.

```kotlin
context(users: UserRepository)
val firstUser: User? get() = users.getById(1)
```

Context function types contain types but no parameter names. Contextual values in a lambda are anonymous and can be retrieved with `implicit<T>()`:

```kotlin
fun <R> withLogger(logger: Logger, block: context(Logger) () -> R): R =
    block(logger)

val task: context(Logger) () -> Unit = {
    implicit<Logger>().log("ready")
}
```

A call must find exactly one compatible contextual value at the nearest scope level. Same-level matches produce an ambiguity, and `@DslMarker` restrictions apply to context parameters as well as receivers.

A callable reference eagerly resolves and captures its context where the reference is created, so its resulting function type has no context parameters. Reflection identifies context values as `KParameter.Kind.CONTEXT_PARAMETER`. JVM declarations encode them before an extension receiver and ordinary value parameters.

The former Experimental context-receiver feature is no longer supported in 2.3.20; migrate declarations to context parameters. An overload with context parameters is no longer considered more specific than an otherwise matching overload without them. Calls that previously selected the contextual declaration can become ambiguous, and the compiler warns when such a declaration is shadowed.

### Context-sensitive resolution

With `-Xcontext-sensitive-resolution`, enum entries and sealed members can omit their type qualifier when an expected type comes from a `when` subject, declaration, parameter, return type, check, or cast. The initial preview does not resolve functions, properties with parameters, or extension properties this way.

```kotlin
val problem: Problem = CONNECTION
fun label(p: Problem) = when (p) { CONNECTION -> "network"; else -> "other" }
```

The expanded lookup includes sealed and enclosing supertypes of the expected type, but no other supertype scopes. Type operators and equality expressions warn when a clashing declaration makes the result ambiguous.

## Language features and previews

### Stable syntax and control flow

Nested type aliases and data-flow-based exhaustiveness checks for `when` expressions are Stable. `return` statements in expression-bodied functions with an explicit return type are enabled by default:

```kotlin
fun valueOrZero(value: Int?): Int = value ?: return 0
```

The same expression-body construct without an explicit return type is headed for deprecation. Before stabilization, `-Xdata-flow-based-exhaustiveness` allowed prior checks and early returns to satisfy later `when` cases without a redundant `else`.

When choosing between overloads accepting `() -> T` and `suspend () -> T`, an untyped lambda selects the non-suspending overload under the 2.3 semantics. Write `suspend { ... }` to select the suspending overload. Kotlin 2.2.20 can preview the behavior with `-language-version 2.3`.

```kotlin
transform { 42 }
transform(suspend { 42 })
```

### Experimental name-based destructuring

`-Xname-based-destructuring=only-syntax` enables explicit bindings from variables to property names without changing positional destructuring. `name-mismatch` instead warns about mismatched data-class property and variable names. `complete` makes the parenthesized short form name-based and uses square brackets for positional destructuring.

```kotlin
data class User(val username: String, val email: String)
val user = User("alice", "alice@example.com")
(val mail = email, val name = username) = user
val [username, email] = user
```

### Explicit backing fields

With `-Xexplicit-backing-fields`, a public property's storage can have a narrower implementation type without a separate private property. Code in the same private scope sees the implementation type through the property and can smart-cast it automatically.

```kotlin
val city: StateFlow<String>
    field = MutableStateFlow("")

fun updateCity(value: String) { city.value = value }
```

### Reified catches and extended contracts

`-Xallow-reified-type-in-catch` permits an inline function to catch its `reified T : Throwable` directly. It is experimental in 2.2.20 and planned to become default in 2.4.

```kotlin
inline fun <reified T : Throwable> runCatchingOnly(block: () -> Unit) {
    try { block() } catch (error: T) { println(error.message) }
}
```

Experimental contracts can assert generic types and appear in property accessors and selected operators with `-Xallow-contracts-on-more-functions`. `returnsNotNull()` uses `-Xallow-condition-implies-returns-contracts`; `condition holdsIn block` uses `-Xallow-holdsin-contract`. The latter two forms also require `ExperimentalExtendedContracts`.

## Diagnostics and API intent

### Return-value checking

The Experimental checker warns when a non-`Unit`, non-`Nothing` result is discarded. `-Xreturn-value-checker=check` checks marked APIs and scopes, including most standard-library functions, while `full` treats project files as marked. Use `@MustUseReturnValues`, `@IgnorableReturnValue`, or `val _ = call()` to control it.

```kotlin
kotlin {
    compilerOptions { freeCompilerArgs.add("-Xreturn-value-checker=check") }
}
```

Serialization 1.10 marks its APIs for this checker, so ignoring a result such as `Json.encodeToString(...)` can warn.

### Per-diagnostic severity

The Experimental `-Xwarning-level=DIAGNOSTIC_NAME:(error|warning|disabled)` option overrides `-Werror`, `-nowarn`, or `-Wextra` for one warning. For example, use `-Werror -Xwarning-level=DEPRECATION:warning`.

### Java nullability and mutability annotations

JSpecify compiler support is finalized. The JVM compiler also recognizes Vert.x `io.vertx.codegen.annotations.Nullable` and reports mismatches as warnings by default. Promote them to errors with:

```kotlin
freeCompilerArgs.add("-Xnullability-annotations=@io.vertx.codegen.annotations:strict")
```

Java declarations marked `org.jetbrains.annotations.Unmodifiable` or `UnmodifiableView` return read-only Kotlin collection types. Assigning such a result to a mutable collection warns in 2.3.20 and is scheduled to become an error in 2.5.0.

## Annotations and metadata

### Property annotation propagation

`-Xannotation-target-all` enables `@all:Ann`, which propagates to each applicable constructor parameter, Kotlin property, backing field, getter, setter parameter, and JVM record component. Separately, `-Xannotation-default-target=param-property` applies an unqualified annotation to `param` when possible and also to `property`, or to `field` when no property target applies. Use `first-only` to retain the old behavior.

```kotlin
@JvmRecord
data class Person(@all:Positive val age: Int)
```

### Annotations in Kotlin metadata

`-Xannotations-in-metadata` writes declaration, accessor, receiver, backing-field, delegate-field, and enum-entry annotations into Kotlin metadata. Consumers use the Experimental `Km*.annotations` APIs under `@OptIn(ExperimentalAnnotationsInMetadata::class)` and should tolerate the data before metadata annotation writing becomes the default.

Kotlin 2.3.21 adds `CompilerPluginData` to the `kotlinx-metadata` Km API, exposing compiler-plugin data to metadata consumers.

## JVM generation and Java interop

### Interface defaults

The stable `-jvm-default` option replaces `-Xjvm-default` and defaults to `enable`, generating interface defaults plus compatibility bridges and `DefaultImpls`. `no-compatibility` emits only interface defaults, while `disable` restores the old `DefaultImpls`-only scheme.

```kotlin
kotlin { compilerOptions { jvmDefault = JvmDefaultMode.NO_COMPATIBILITY } }
```

### Boxed entry points for inline value classes

`@JvmExposeBoxed` generates Java-callable boxed constructors or boxed variants of annotated functions involving inline value classes; `-Xjvm-expose-boxed` applies it module-wide. It adds Java entry points without changing Kotlin's internal unboxed use.

```kotlin
@JvmExposeBoxed
@JvmInline
value class UserId(val value: Int)
```

Boxed inline value classes no longer incorrectly pass `is` or `as` checks for `java.lang.Number` or `java.lang.Comparable` merely because their underlying primitive does.

### Lambda bytecode and signatures

Annotated JVM lambdas use `invokedynamic` through `LambdaMetafactory` by default, so reflection code cannot rely on annotations living on a generated lambda class. Temporarily restore class-based generation with `-Xindy-allow-annotated-lambdas=false`.

Top-level lambdas now use the same type-checking logic as lambdas passed as call arguments, which can change reflection-visible generic signatures. Applying `@JvmSerializableLambda` to an `inline` or `crossinline` lambda is an error because those lambdas are not serializable.

The compiler can generate Java 25 bytecode. Common `@JvmRecord` declarations compile as metadata again in Kotlin 2.3.21 after `compileCommonMainKotlinMetadata` failed because `java.lang.Record` was inaccessible. That patch also removes a false `SUBCLASS_CANT_CALL_COMPANION_PROTECTED_NON_STATIC` error in multi-module projects.

### JPA openness

`kotlin.plugin.jpa` applies both the existing `no-arg` preset and the `all-open` JPA preset. `javax.persistence` and `jakarta.persistence` entities, embeddables, and mapped superclasses are therefore automatically open for lazy associations. Maven's `kotlin-maven-noarg` dependency includes `kotlin-maven-allopen` implicitly.

## Tightened and removed behavior

### Type aliases and inference

K2 rejects constructor calls and supertypes through aliases whose expansion contains variance such as `out`; use the expanded type directly. It also rejects the ineffective `reified` modifier on type-alias parameters. Inheriting from a nullable type introduced through a type alias is an error, and a reified type parameter may no longer be inferred as an intersection type.

Kotlin 2.3.0 changed an implicitly inferred type argument that violated an upper bound into an error, including inference through aliases. Kotlin 2.3.21 postponed that enforcement, so successful compilation on the patch does not establish future compatibility.

### Visibility and dependency checks

K2 errors when generic expression types expose types available only through indirect dependencies, when a declaration's type-parameter bound is less visible than the declaration, or when a non-private inline function refers to private types or members. Add the direct dependency or align visibility; removing `inline` is a binary-incompatible alternative.

### Corrected callable and delegation behavior

Synthetic property syntax is no longer created from getters declared in Kotlin, including through Java subclasses or mapped types; call the getter explicitly. Callable references to Java synthetic properties are a Revoked feature and should not be used in new code.

Kotlin can no longer delegate a generic interface to a Java class whose implementation supplies a non-generic override. Such delegation fails at compile time instead of risking a runtime `ClassCastException`.

A lambda used as a parameter's default value may not contain a non-local `return`; move the return logic outside the default expression. Kotlin 2.2.21 also corrects erroneous `NON_PUBLIC_CALL_FROM_PUBLIC_INLINE` diagnostics for `@PublishedApi` fun interfaces.

### Language-version support

The compiler rejects `-language-version=1.6` and 1.7 and warns for 1.8 and 1.9 under the earlier transition. Kotlin 2.3 rejects `-language-version=1.8` on every platform and `-language-version=1.9` on non-JVM platforms; JVM compilation retains 1.9 support.

K1 is deprecated. Migrate projects that still select it to K2. IntelliJ IDEA 2025.1 enables K2 analysis by default.

### Scripting changes

The `kotlinc` REPL requires `-Xrepl`. JSR-223 remains available only with language version 1.9 and is not moving to K2, while Maven `KotlinScriptMojo` is deprecated.

Kotlin 2.3.21 repairs the `scriptCompilationClasspathFromContext` behavior change introduced in 2.3.20, JVM backend failures for scratch scripts with anonymous objects, code-generation failures around destructuring declarations, and missing source locations in `ScriptDiagnostic` errors. Kotlin 2.1.21 repairs `main.kts` dependency resolution after a 2.1.20 regression.

## Patch-sensitive compiler and reflection fixes

Kotlin 2.2.10 repairs several 2.2.0 regressions that can require a patch upgrade rather than a source change: Android dexing null-field failures, duplicate `DebugMetadata` on JVM-default suspend interface methods, an Xcode 16.3/iOS 15.5-simulator linker failure, and Apple Watch `SIGABRT` crashes.

Upgrade from Kotlin 2.3.0 when compilation is unstable around enhanced Java nullability or overload resolution, `UInt` constants trigger `ClassCastException`, JSpecify `@NullMarked` causes an `equals(Any?)` override conflict, or `@NoInfer` behaves incorrectly. Kotlin 2.3.10 also fixes a serialization-plugin race around Protobuf extension registration and `NoWhenBranchMatchedException` from a `when` with a `!is` check and a non-sealed intermediate class.

Kotlin 2.3.10 fixes `KotlinReflectionInternalError` involving references to `FunctionN.invoke` and type parameters in generic supertypes, plus incorrect `KType` argument comparisons when a type parameter is `Nothing`.

## Batch attributions

Relevant versioned extraction batches: `2.1.20-guide`, `2.1.20`, `2.2-language-guide`, `2.2-tooling-guide`, `2.2.0`, `2.3-language-guide`, `2.3-tooling-guide`, and `2.3.0`.
