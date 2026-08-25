# Language, APIs, and Concurrency

Use this reference when compiling source that adopts module imports, compact
source files, newly permanent APIs, or features that still require preview or
incubator flags.

## Preview compilation discipline

Preview-dependent source must be compiled and run with `--enable-preview` and
recompiled for every JDK release. Do not carry preview class files forward and
assume that unchanged source syntax implies binary compatibility.

When a formerly preview feature becomes permanent, remove
`--enable-preview` only if no other source in the compilation uses a preview
feature. Incubating modules retain their own module-resolution requirements.

## Module import declarations

Module imports are preview syntax in 24-migration. They neither import
subpackages nor alter module readability. A type-import-on-demand declaration
takes precedence over a module import, so `List` resolves to
`java.util.List` here rather than `java.awt.List`:

```java
import module java.desktop;
import java.util.*;

class Example {
    List<String> values = new ArrayList<>();
}
```

`import module java.se;` has unusually broad reach in JDK 24 because
`java.se` transitively requires `java.base`. Do not generalize that reach to
arbitrary modules.

Module import declarations become permanent in 25-migration, together with
compact source files and instance `main` methods, flexible constructor bodies,
scoped values, and the KDF API. Recompile without preview enablement when these
are the only formerly preview features in use.

## Compact source files and `IO`

During 25-migration, `IO` moves into `java.lang`, but its static methods are
not implicitly imported. Qualify the call or add an explicit static import:

```java
void main() {
    IO.println("Hello");
}
```

`IO` uses `System.in` and `System.out`, not `java.io.Console`. Test code that
depended on console-specific input or output behavior.

## Final APIs available without preview

The Class-File API is final in 24. It can parse, generate, and transform Java
class files without preview enablement.

The Stream Gatherers API is also final in 24. Custom intermediate stream
operations built with gatherers no longer require preview enablement.

The standard KDF API is still a preview in 24, so code using that revision
must retain preview compilation and runtime flags. It becomes permanent in
25-migration.

## Feature states that still require care

In 25-migration, primitive patterns, structured concurrency, stable values,
and PEM encodings remain preview features. The Vector API remains incubating.
Keep the corresponding preview or module flags rather than removing them just
because other features in the same source tree became permanent.

The 25 batch introduces the following APIs and workflows:

- PEM encoding and decoding for keys, certificates, and revocation lists.
- Stable values for lazily initialized immutable values that the JVM can
  optimize as constants.
- A simplified command-line workflow for creating and using AOT caches; see
  [Runtime, GC, AOT, and Diagnostics](runtime-performance.md).

## Updating preview source for the next release

The 26-migration changes the preview landscape:

- Stable values evolve into the lazy-constants second preview. Update source
  written against the earlier preview rather than only changing a flag.
- Structured concurrency reaches a sixth preview.
- Primitive patterns reach a fourth preview.
- PEM encoding reaches a second preview.
- The Vector API remains incubating.

Code using the JDK 25 forms must be updated and recompiled for JDK 26. Treat
each preview revision as an API migration, even when the feature's overall
purpose has not changed.

## Virtual-thread synchronization

As of 24, HotSpot allows a virtual thread blocked in most `synchronized`
constructs to unmount from its carrier. This removes a common source of
carrier pinning. Revisit workarounds based on the older behavior, but profile
the application's actual synchronization and native-call paths rather than
assuming all blocking is unpinned.

## HTTP/3 client deployments

The standard HTTP Client can use HTTP/3 in 26-migration. Adoption affects more
than Java source because QUIC uses UDP. Before enabling it, test:

- UDP traversal through proxies, firewalls, and network policy.
- Fallback paths when HTTP/3 cannot be established.
- Certificate handling under the target runtime and network path.
- Metrics, traces, logs, packet visibility, and other observability needed to
  diagnose negotiation and fallback.

Retain an exercised fallback until the production path has proven that QUIC
traffic and diagnostics work end to end.
