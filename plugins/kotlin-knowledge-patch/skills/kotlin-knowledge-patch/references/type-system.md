# Type System Enhancements

## Nested Type Aliases (2.2.0 Beta, Stable in 2.3.0)

Type aliases can now be declared inside classes/objects. Cannot capture outer type parameters.

```kotlin
class Dijkstra {
    typealias VisitedNodes = Set<Node>
    private fun step(visited: VisitedNodes) = ...
}
```

Enable in 2.2.x: `-Xnested-type-aliases`. Stable in 2.3.0.

## Explicit Backing Fields (2.3.0, Experimental)

Declare a backing field with a different type than the property, eliminating private `_backing` properties.

```kotlin
val city: StateFlow<String>
    field = MutableStateFlow("")

fun updateCity(newCity: String) {
    city.value = newCity  // smart cast to MutableStateFlow within same scope
}
```

Enable: `-Xexplicit-backing-fields`.

## Name-Based Destructuring (2.3.20, Experimental)

Match variables to property names instead of position-based `componentN()` order.

```kotlin
data class User(val username: String, val email: String)

// Explicit form — variables bound by property name
(val mail = email, val name = username) = user

// In complete mode, parentheses use name-based matching:
val (email, username) = user  // matches by name, not position

// Position-based destructuring uses square brackets:
val [username, email] = user  // position-based like before
```

Modes: `-Xname-based-destructuring=only-syntax|name-mismatch|complete`.

## Data-Flow Exhaustiveness for `when` (2.2.20 Experimental, Stable in 2.3.0)

Compiler tracks prior checks and early returns for `when` exhaustiveness.

```kotlin
fun getPermissionLevel(role: UserRole): Int {
    if (role == UserRole.ADMIN) return 99
    return when (role) {
        UserRole.MEMBER -> 10
        UserRole.GUEST -> 1
        // no else needed — ADMIN already handled
    }
}
```

Enable in 2.2.x: `-Xdata-flow-based-exhaustiveness`. Default in 2.3.0.

## Return in Expression Bodies (2.2.20, Default in 2.3.0)

`return` is now allowed in expression bodies when the return type is explicit.

```kotlin
fun getDisplayNameOrDefault(userId: String?): String =
    getDisplayName(userId ?: return "default")
```
