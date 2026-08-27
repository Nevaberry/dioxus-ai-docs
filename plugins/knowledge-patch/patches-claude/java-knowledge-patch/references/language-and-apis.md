# Language Features and Standard APIs

Use this reference to decide whether source requires preview enablement, a
release-specific rewrite, an incubator module, or no special flags.

## Module import declarations

Module imports in their preview form have two important boundaries
(24-migration):

- They do not import subpackages.
- They do not alter module readability.

A type-import-on-demand declaration takes precedence over a module import. In
this example, `List` resolves to `java.util.List`, not `java.awt.List`:

```java
import module java.desktop;
import java.util.*;

class Example {
    List<String> values = new ArrayList<>();
}
```

Compile and run preview-dependent code with `--enable-preview`, and recompile
it for every JDK release.

`import module java.se;` has unusually broad reach in JDK 24 because `java.se`
transitively requires `java.base` (24-migration). Do not generalize that reach
to arbitrary modules.

Module import declarations become permanent in JDK 25 (25-migration). Remove
`--enable-preview` only if no other source in the build needs preview
enablement, then recompile.

## Final APIs and language features

### Class-File API

The Class-File API is final in JDK 24 (24). Use it to parse, generate, and
transform Java class files without preview enablement.

### Stream gatherers

Stream gatherers are final in JDK 24 (24). They support custom intermediate
operations in stream pipelines without preview enablement.

### Features finalized in JDK 25

The following former previews are permanent in JDK 25 (25-migration):

- module import declarations
- compact source files and instance `main` methods
- flexible constructor bodies
- scoped values
- the Key Derivation Function API

When these are the only preview features in a project, remove
`--enable-preview` and recompile.

## Compact source files and `IO`

`IO` is in `java.lang`, but its static methods are not implicitly imported
(25-migration). Qualify the call:

```java
void main() {
    IO.println("Hello");
}
```

Alternatively, add an explicit static import. `IO` uses `System.in` and
`System.out`, not `java.io.Console`; account for this in input handling,
captured output, and tests.

## Preview and incubator lifecycle

### JDK 24 preview API

The standard Key Derivation Function API is previewed in JDK 24 (24). Compile
and run callers with `--enable-preview`, and recompile for each JDK release.

### JDK 25 non-final features

These features remain preview in JDK 25 (25-migration):

- primitive patterns
- structured concurrency
- stable values
- PEM encodings

The Vector API remains incubating (25-migration), so retain the applicable
module configuration in addition to any preview flags used elsewhere.

### Stable values and PEM in JDK 25

Stable values provide lazily initialized immutable values that the JVM can
optimize as constants (25).

The PEM API encodes and decodes keys, certificates, and revocation lists
(25). It remains a preview feature at this point; do not treat availability as
finalization.

### JDK 26 source migration

Preview forms evolve again in JDK 26 (26-migration):

- stable values evolve into the lazy-constants second preview
- structured concurrency reaches a sixth preview
- primitive patterns reach a fourth preview
- PEM encoding reaches a second preview
- the Vector API remains incubating

Update code written for the JDK 25 preview forms and recompile it for JDK 26.
Do not expect preview bytecode or source details to carry forward unchanged.

## Final-field mutation policy

Deep reflection that mutates a `final` field warns in JDK 26
(26-migration).

`--enable-final-field-mutation` grants mutation capability to selected modules
or scopes. `--illegal-final-field-mutation` controls the response when code
mutates a final field without the grant.

Use the narrowest possible grant while migrating frameworks and libraries to
supported construction or serialization mechanisms. Treat a broad grant as a
temporary compatibility measure, not the default fix.

## Feature-status decision procedure

1. Identify every language and API feature the source actually uses.
2. Classify each as final, preview, or incubating for the selected JDK.
3. Add `--enable-preview` to both compilation and execution when any preview
   feature remains.
4. Add required incubator modules independently of preview enablement.
5. Rewrite source for evolved preview forms.
6. Recompile every preview-dependent module and downstream artifact for the
   exact JDK release.
7. Remove preview flags only after the entire build graph no longer needs them.
