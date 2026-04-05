# JVM Interop & Multiplatform

## @JvmExposeBoxed (2.2.0, Experimental)

Makes inline value classes usable from Java by generating a public boxed constructor.

```kotlin
@JvmExposeBoxed
@JvmInline
value class PositiveInt(val number: Int)

@JvmExposeBoxed
fun PositiveInt.timesTwo(): PositiveInt = PositiveInt(this.number * 2)
// Java: new PositiveInt(5)  — now works
```

## -jvm-default Mode Change (2.2.0)

Interface functions now compile to JVM default methods by default. New stable `-jvm-default` option replaces `-Xjvm-default`.

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        jvmDefault = JvmDefaultMode.NO_COMPATIBILITY  // or ENABLE (default), DISABLE
    }
}
```

## Swift Export Enabled by Default (2.2.20)

KMP Swift export is now enabled by default — no manual opt-in needed.

## withJava() Deprecated (2.1.20)

Java source sets are now created by default in KMP. `withJava()` is being phased out.

## @JsExport.Default (2.3.0)

Generate JavaScript default exports from Kotlin declarations.

```kotlin
@JsExport.Default
class HelloWorker  // generates: export default HelloWorker;
```
