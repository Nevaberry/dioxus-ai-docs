# Compiler Features

## Unused Return Value Checker (2.3.0, Experimental)

Warns when expressions return non-Unit/Nothing values that are silently dropped.

```kotlin
@MustUseReturnValues          // mark class or @file:MustUseReturnValues for whole file
class Greeter {
    fun greet(name: String): String = "Hello, $name"
}

@IgnorableReturnValue         // suppress on specific functions
fun <T> MutableList<T>.addSafe(element: T): Boolean = add(element)

val _ = computeValue()        // suppress at call site with unnamed variable
```

Enable: `-Xreturn-value-checker=check` (only marked scopes) or `=full` (entire project).

## Suspend Overload Resolution (2.2.20, Default in 2.3.0)

When both regular and suspend overloads exist, a lambda now resolves to the regular overload. Use `suspend { }` for the suspend overload.

```kotlin
fun transform(block: () -> Int) {}
fun transform(block: suspend () -> Int) {}

transform({ 42 })          // resolves to () -> Int
transform(suspend { 42 })  // resolves to suspend () -> Int
```

## Reified Types in Catch (2.2.20 Experimental, Default in 2.4.0)

Reified generic type parameters now work in `catch` clauses of inline functions.

```kotlin
inline fun <reified E : Throwable> handleException(block: () -> Unit) {
    try { block() }
    catch (e: E) { println("Caught: ${e::class.simpleName}") }
}
handleException<IOException> { throw IOException("fail") }
```

Enable: `-Xallow-reified-type-in-catch`.

## Contract Improvements (2.2.20, Experimental)

### returnsNotNull()

Guarantees non-null return when condition is met:

```kotlin
@OptIn(ExperimentalContracts::class, ExperimentalExtendedContracts::class)
fun decode(encoded: String?): String? {
    contract { (encoded != null) implies (returnsNotNull()) }
    return encoded?.let { java.net.URLDecoder.decode(it, "UTF-8") }
}
// After null check: decode(s).length — no safe call needed
```

Enable: `-Xallow-condition-implies-returns-contracts`.

### holdsIn

Condition assumed true inside lambda:

```kotlin
@OptIn(ExperimentalContracts::class, ExperimentalExtendedContracts::class)
fun <T> T.alsoIf(condition: Boolean, block: (T) -> Unit): T {
    contract {
        callsInPlace(block, InvocationKind.AT_MOST_ONCE)
        condition holdsIn block  // smart cast available inside block
    }
    if (condition) block(this)
    return this
}
```

Enable: `-Xallow-holdsin-contract`.

### Contracts in Property Accessors and Operator Functions

Contracts now work in property accessors and operator functions (invoke, contains, componentN, iterator, etc.).

Enable: `-Xallow-contracts-on-more-functions`.

## -Xwarning-level (2.2.0, Experimental)

Fine-grained per-diagnostic warning control:

```
-Xwarning-level=DIAGNOSTIC_NAME:(error|warning|disabled)
```
