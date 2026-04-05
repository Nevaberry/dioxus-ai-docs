# Context Parameters & Resolution

## Context Parameters (2.2.0, Preview)

Replaces context receivers. Key difference: parameters accessed by name, not as implicit receivers.

```kotlin
context(users: UserService)
fun outputMessage(message: String) {
    users.log("Log: $message")  // access via name
}

// Anonymous context parameter — available for resolution but not by name
context(_: UserService)
fun logWelcome() {
    outputMessage("Welcome!")  // resolved from context
}

// Property with context parameter
context(users: UserService)
val firstUser: String
    get() = users.findUserById(1)
```

Enable: `-Xcontext-parameters`. Cannot use with `-Xcontext-receivers`.

## Context-Sensitive Resolution (2.2.0, Preview)

Omit type qualifier for enum entries/sealed class members when type is known from context.

```kotlin
fun message(problem: Problem): String = when (problem) {
    CONNECTION -> "connection"         // not Problem.CONNECTION
    AUTHENTICATION -> "authentication"
    DATABASE -> "database"
    UNKNOWN -> "unknown"
}

val role: UserRole = ADMIN  // not UserRole.ADMIN
```

Works in `when` subjects, explicit return types, declared variable types, `is`/`as` checks, parameter types.

Enable: `-Xcontext-sensitive-resolution`.

## @all Annotation Meta-Target (2.2.0, Preview)

Applies annotation to all relevant property targets (param, property, field, get, setparam).

```kotlin
data class User(
    @all:Email val email: String,  // applies to param, property, field, get
)
```

Enable: `-Xannotation-target-all`.
