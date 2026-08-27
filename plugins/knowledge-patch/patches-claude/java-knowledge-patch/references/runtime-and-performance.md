# Runtime, Performance, and Diagnostics

Use this reference for runtime images, garbage collectors, object layout,
ahead-of-time caches, virtual-thread behavior, and JFR diagnostics.

## Runtime images

Custom-image pipelines can use `jlink` without relying on installed JMOD files
(24-migration). Retest custom plugins and reproducibility checks; the relaxed
JMOD dependency does not prove that an existing image pipeline produces the
same output.

## Garbage collectors

### ZGC

Non-generational ZGC is removed in JDK 24 (24). Generational ZGC is the only
ZGC mode, so remove configuration that attempts to select or preserve the old
non-generational mode.

### Generational Shenandoah

Generational Shenandoah is experimental in JDK 24 (24). Opt in deliberately
and evaluate it as an experimental collector mode.

It becomes a product feature in JDK 25 (25-migration). Startup configuration
no longer needs `-XX:+UnlockExperimentalVMOptions` solely to select
generational Shenandoah.

## Compact object headers

Compact object headers can experimentally reduce object headers to 64 bits on
64-bit platforms in JDK 24 (24). The experimental form is enabled with:

```text
-XX:+UnlockExperimentalVMOptions -XX:+UseCompactObjectHeaders
```

Compact object headers become a product feature in JDK 25 (25-migration).
Remove `-XX:+UnlockExperimentalVMOptions` when its only purpose was enabling
compact object headers. Revalidate layout-sensitive tooling and performance
assumptions on the actual platform.

## Ahead-of-time caches

### Class loading and linking

JDK 24 can record loaded and linked classes during a training run and store
them in an AOT cache (24). Later runs can use the cache to improve startup.

### Input compatibility

The JDK 25 workflow is simplified and can reuse method profiles (25,
25-migration). An AOT cache remains coupled to the application and runtime
inputs that created it.

Rebuild the cache whenever any of these changes:

- application content
- class path
- module path
- JDK

Treat caches as derived artifacts tied to a particular deployment input set,
not as generally reusable binaries.

### Collector-neutral object caches

AOT object caches can work with any garbage collector in JDK 26 because cached
objects load from a GC-neutral representation (26-migration). This removes the
collector coupling; it does not remove the application, path, or JDK coupling.

## Virtual-thread synchronization

HotSpot allows a virtual thread blocked in most `synchronized` constructs to
unmount from its carrier thread (24). This removes a common source of carrier
pinning.

Do not assume all pinning is gone. Diagnose the actual blocking path and
runtime behavior rather than mechanically replacing every synchronized block.

## Experimental JFR diagnostics

JFR adds experimental diagnostics in JDK 25 (25-migration):

- Linux CPU-time profiling
- cooperative stack sampling
- method timing
- method tracing

Method tracing instruments code. Restrict it to the methods needed for the
diagnostic session, measure its effect, and avoid treating an instrumented run
as an unbiased performance baseline.

## Runtime validation checklist

1. Build the runtime image without assuming installed JMOD files, then verify
   plugins and reproducibility.
2. Remove any non-generational ZGC selection.
3. Align experimental-unlock flags with the selected JDK and feature status.
4. Benchmark compact object headers on the deployed architecture.
5. Generate AOT caches from the same inputs used by the deployment.
6. Invalidate AOT caches whenever application or runtime inputs drift.
7. Measure virtual-thread pinning on the actual workload.
8. Scope experimental JFR instrumentation to the diagnostic question.
