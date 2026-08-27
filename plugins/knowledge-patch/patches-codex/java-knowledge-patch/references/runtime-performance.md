# Runtime, GC, AOT, and Diagnostics

Use this reference for garbage-collector configuration, compact headers,
virtual-thread runtime behavior, ahead-of-time caches, JFR diagnostics, and
custom runtime images.

## Garbage-collector changes

### ZGC

Non-generational ZGC is removed in 24. Generational ZGC is the only ZGC mode.
Remove configuration that explicitly selects the former non-generational mode
and verify startup plus memory behavior with the remaining collector.

### Generational Shenandoah

Generational Shenandoah is experimental in 24. Deployments must opt in and
evaluate it as an experimental collector mode rather than treating it as a
drop-in production default.

It becomes a product feature in 25-migration. Startup configuration no longer
needs `-XX:+UnlockExperimentalVMOptions` solely to select generational
Shenandoah. Remove only the unlock flag that was needed for this feature;
retain it if another selected experimental feature still requires it.

## Compact object headers

HotSpot can experimentally reduce object headers to 64 bits on 64-bit
platforms in 24. The experimental form must be enabled explicitly:

```text
-XX:+UnlockExperimentalVMOptions -XX:+UseCompactObjectHeaders
```

Compact object headers become a product feature in 25-migration. Current
startup configuration no longer needs `-XX:+UnlockExperimentalVMOptions`
solely to enable the header mode. Re-run footprint, allocation, GC, and
compatibility testing when moving from the experimental form.

## Ahead-of-time class loading and linking

The 24 runtime can record loaded and linked classes during a training run and
store them in an AOT cache. Later runs can consume the cache to improve
startup.

The 25 batch simplifies the command-line workflow for creating and using AOT
caches. The 25-migration also permits reuse of method profiles, but the cache
remains coupled to the inputs used to create it.

Rebuild the cache whenever any of these changes:

- The application.
- The class path.
- The module path.
- The JDK.

Do not promote a cache independently of the application and runtime inputs it
was trained against.

In 26-migration, AOT object caches can work with any garbage collector because
cached objects are loaded from a GC-neutral representation. This removes the
collector coupling of the object representation, not the application, path,
or JDK coupling of the cache as a whole.

## Virtual threads and synchronization

HotSpot in 24 allows a virtual thread blocked in most `synchronized`
constructs to unmount from its carrier. This eliminates a common pinning
source, but the statement is deliberately not universal. Measure native calls
and other blocking paths before sizing carrier pools or deleting operational
alerts.

## JFR experimental diagnostics

The 25-migration adds experimental JFR facilities for:

- Linux CPU-time profiling.
- Cooperative stack sampling.
- Method timing.
- Method tracing.

Method tracing instruments application code. Restrict it to the methods
needed for the current diagnostic session, measure its overhead, and avoid
turning a focused experiment into an unbounded production configuration.

## Runtime images

The 24-migration permits `jlink` custom-image pipelines to operate without
relying on installed JMOD files. Retest custom plugins and reproducibility;
the changed input arrangement can expose assumptions in wrappers or image
comparison tooling.

Platform packaging must also stop assuming a 32-bit x86 JDK. Windows x86 is
removed and Linux x86 is on a removal path during 24-migration; the remaining
32-bit x86 port is removed in 25-migration.

## Deployment validation

1. Start every supported collector configuration and reject obsolete ZGC
   selectors.
2. Remove experimental unlocking only after accounting for every experimental
   option in the same launch command.
3. Benchmark compact headers and generational Shenandoah independently so
   regressions have an attributable cause.
4. Train AOT caches with production-equivalent class and module paths.
5. Invalidate and rebuild caches as one release artifact whenever application
   or runtime inputs change.
6. Scope experimental JFR instrumentation to the diagnostic question and
   record overhead.
7. Rebuild custom runtime images and compare module content and reproducible
   output.
