# Language and compiler

## Context parameters and resolution (`2.2-language-guide`, `2.3-tooling-guide`)

### Declaration constraints

Context parameters may appear only on functions and whole properties, not classes or constructors. A contextual property cannot have a backing field, initializer, or delegate and therefore needs an accessor. Name a value `_` when it should participate in context lookup without being referenced directly.

```kotlin
context(users: UserRepository)
val firstUser: User? get() = users.getById(1)
```

Context function types contain types but not parameter names. Values inside their lambdas are anonymous and retrievable with `implicit<T>()`:

```kotlin
fun <R> withLogger(logger: Logger, block: context(Logger) () -> R): R = block(logger)
val task: context(Logger) () -> Unit = { implicit<Logger>().log("ready") }
```

Lookup must find exactly one compatible value at the nearest scope level. Same-level matches are ambiguous, and `@DslMarker` restrictions apply to context parameters. A contextual overload is no longer considered more specific than an otherwise matching non-contextual overload; a call can become ambiguous and shadowed declarations receive warnings.

A callable reference resolves and captures its context at creation, so its resulting function type has no context parameters. Reflection exposes captured declaration parameters as `KParameter.Kind.CONTEXT_PARAMETER`; on the JVM they precede an extension receiver and ordinary parameters.

### Context-sensitive resolution

With `-Xcontext-sensitive-resolution`, enum entries and sealed members may omit their qualifier where an expected type comes from a `when` subject, declaration, argument, return, type check, or cast. The lookup does not cover functions, parameterized properties, or extension properties. Its expanded form considers sealed and enclosing supertypes, but no unrelated supertype scopes, and warns when a clashing declaration makes a type operator or equality expression ambiguous.

### Remove context receivers

Context receivers are unsupported from Kotlin 2.3.20. Migrate declarations to context parameters rather than retaining their former experimental syntax.

## Language behavior and opt-ins (`2.2-tooling-guide`, `2.3-language-guide`)

### Suspend overloads and expression-bodied returns

With language version 2.3, an untyped lambda chooses `() -> T` over a competing `suspend () -> T`; use `suspend { ... }` to select the suspend overload. Kotlin 2.2.20 can preview this with `-language-version 2.3`.

An expression-bodied function may contain `return` when it has an explicit return type; omitting the explicit type is headed for deprecation. A lambda used as a parameter's default value still may not perform a non-local `return`.

### Exhaustiveness, catches, and contracts

Data-flow-based `when` exhaustiveness is stable: prior checks and early returns can eliminate cases without a redundant `else`. On the earlier preview, enable it with `-Xdata-flow-based-exhaustiveness`.

`-Xallow-reified-type-in-catch` permits `catch (error: T)` for `reified T : Throwable`; it was experimental in Kotlin 2.2.20 and planned as a default for 2.4.

Experimental extended contracts can assert generic types and appear in property accessors and selected operators with `-Xallow-contracts-on-more-functions`. `returnsNotNull()` uses `-Xallow-condition-implies-returns-contracts`; `condition holdsIn block` uses `-Xallow-holdsin-contract`; the latter two also require `ExperimentalExtendedContracts`.

### Unused return values and backing fields

`-Xreturn-value-checker=check` warns for discarded non-`Unit`, non-`Nothing` results in marked APIs and scopes; `full` treats project files as marked. Express intent with `@MustUseReturnValues`, `@IgnorableReturnValue`, or `val _ = call()`.

With `-Xexplicit-backing-fields`, a public property can expose an interface while its backing field keeps a narrower implementation type. Code in the same private scope sees and can smart-cast to the implementation type.

### Name-based destructuring

`-Xname-based-destructuring=only-syntax` enables explicit variable-to-property bindings while retaining ordinary positional destructuring. `name-mismatch` warns when data-class property and variable names differ. `complete` makes the parenthesized short form name-based and reserves square brackets for positional destructuring.

### Stable and supported language versions

Nested type aliases, data-flow exhaustiveness, and explicit-type expression-bodied returns are stable/default. Kotlin 2.2 rejects language versions 1.6 and 1.7 and warns for 1.8 and 1.9. Kotlin 2.3 rejects 1.8 everywhere and 1.9 on non-JVM targets, while JVM compilation retains 1.9 support.

The K1 compiler is deprecated; treat it only as migration infrastructure and move projects to K2. The compiler rejects `-language-version=1.6`; later compatibility changes also affect `-language-version=1.8` and `-language-version=1.9` as described above. Kotlin-to-Java direct actualization in multiplatform projects remains experimental even though it has been available since 2.1.0.

## Diagnostics and type-system corrections

### Warning control

Use `-Xwarning-level=DIAGNOSTIC_NAME:(error|warning|disabled)` to override `-Werror`, `-nowarn`, or `-Wextra` for one diagnostic—for example, `-Werror -Xwarning-level=DEPRECATION:warning`. KGP diagnostics also follow Gradle `--warning-mode`: `fail` promotes warnings and `none` hides them; use `kotlin.internal.diagnostics.ignoreWarningMode=true` only for a deliberate exception.

### Visibility and type aliases

K2 rejects expression types that expose types available only through indirect dependencies, declaration bounds less visible than their declarations, and non-private inline functions referring to private types or members. Add the direct dependency or align visibility; removing `inline` changes binary compatibility.

Constructor calls and supertypes through aliases whose expansion contains variance such as `out` are rejected; use the expanded type. `reified` on a type-alias parameter is also rejected. Nullable supertypes introduced through aliases and inference of reified parameters as intersection types are errors.

### Inference and generic correctness

Kotlin 2.3.0 changed inferred type arguments that violate upper bounds from warnings to errors, including through type aliases. Kotlin 2.3.21 rolled that enforcement back, so code compiling there may still violate the future rule.

Top-level lambdas now share call-argument lambda type checking, which can change reflection-visible generic signatures. Generic delegation to a Java implementation with a non-generic override is rejected instead of risking `ClassCastException`.

`@JvmSerializableLambda` on `inline` or `crossinline` lambdas is an error because those lambdas are not serializable. Kotlin 2.2.21 also fixes false `NON_PUBLIC_CALL_FROM_PUBLIC_INLINE` diagnostics for `@PublishedApi` fun interfaces.

## JVM interop, annotations, and reflection

### Interface defaults and inline value classes

Stable `-jvm-default` replaces `-Xjvm-default` and defaults to `enable`, emitting interface defaults, compatibility bridges, and `DefaultImpls`. `no-compatibility` emits only interface defaults; `disable` restores the old `DefaultImpls`-only layout.

`@JvmExposeBoxed` creates Java-callable boxed constructors or function variants involving inline value classes; `-Xjvm-expose-boxed` applies module-wide. Boxed value classes no longer pass `is`/`as` checks for `java.lang.Number` or `java.lang.Comparable` solely because the underlying primitive does.

Java 25 classfile output is supported. The compiler recognizes Vert.x `io.vertx.codegen.annotations.Nullable` as warning-level nullness; use `-Xnullability-annotations=@io.vertx.codegen.annotations:strict` to make mismatches errors. JSpecify compiler support is finalized.

### Annotation propagation and metadata

`-Xannotation-target-all` enables `@all:Ann`, propagating an annotation to every applicable constructor parameter, property, field, accessor parameter, and JVM record component. `-Xannotation-default-target=param-property` targets `param` plus `property`, or `field` when no property target applies; select `first-only` for old behavior.

`-Xannotations-in-metadata` records declaration, accessor, receiver, backing/delegate field, and enum-entry annotations. Consumers use `Km*.annotations` with `@OptIn(ExperimentalAnnotationsInMetadata::class)` and should already tolerate the data.

Annotated JVM lambdas now use `invokedynamic` through `LambdaMetafactory`, so reflection must not assume annotations live on a generated class. `-Xindy-allow-annotated-lambdas=false` temporarily restores class generation.

### Corrected Java-facing behavior

Kotlin getters, including those surfaced through Java subclasses or mapped types, no longer create Kotlin synthetic-property syntax; call the getter. Callable references to Java synthetic properties are revoked and should not be used.

`kotlin.plugin.jpa` now combines `no-arg` and `all-open`, automatically opening `javax.persistence` and `jakarta.persistence` entities, embeddables, and mapped superclasses. Maven's `kotlin-maven-noarg` dependency also includes `kotlin-maven-allopen`.

Java declarations annotated `org.jetbrains.annotations.Unmodifiable` or `UnmodifiableView` yield read-only Kotlin collection types. Assigning them to mutable types warns in 2.3.20 and is scheduled to become an error in 2.5.0.

## Scripting, compiler metadata, and patch repairs (`2.3.0`, `2.4.10`)

The `kotlinc` REPL requires `-Xrepl`. JSR-223 remains tied to language version 1.9 and is not moving to K2; Maven `KotlinScriptMojo` and Ant support are deprecated. Kotlin 2.1.21 also restores dependency declarations in `.main.kts` after the 2.1.20 resolution regression.

Kotlin 2.3.21 repairs `scriptCompilationClasspathFromContext`, scratch scripts with anonymous objects, destructuring code generation, and missing `ScriptDiagnostic` locations. It also adds `CompilerPluginData` to the `kotlinx-metadata` Km API.

Kotlin 2.3.10 repairs compiler instability around enhanced Java nullability, overload resolution, `UInt` constants, JSpecify `@NullMarked` causing an `equals(Any?)` override conflict, `@NoInfer`, a Protobuf extension-registration race, and `NoWhenBranchMatchedException` from a `when` with a `!is` check and non-sealed intermediate class. Reflection fixes cover `KotlinReflectionInternalError` for `FunctionN.invoke` references or generic-supertype parameters and incorrect `KType` comparisons involving `Nothing`.

Kotlin 2.4.10 fixes `IllegalStateException: No value for annotation parameter` for `const val` inside nested Java annotation-array arguments and propagates expected types into reified inline calls nested in lambda Elvis expressions. In `.main.kts`, it restores `@file:CompilerOptions("-jvm-target", ...)` and fixes imported-script extension resolution failures involving `FirResolvedTypeRef`.

## Release practice

Since Kotlin 2.0, language releases conventionally use `2.x.0` about every six months and tooling releases `2.x.20` roughly three months later; bug-fix `2.x.yz` releases have no fixed schedule, and both release types may have several EAPs. Pin and inspect the actual project version rather than inferring behavior from cadence.
