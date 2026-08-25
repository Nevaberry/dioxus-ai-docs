# Runtime, Core Libraries, Diagnostics, and I/O

Compatibility guidance is attributed to `10.0-guides`; new APIs and behavior are
attributed to `10.0`.

## I/O, Diagnostics, and Shutdown Compatibility

- `BufferedStream.WriteByte` no longer flushes implicitly. Flush explicitly when
  subsequent consumers must observe the byte immediately.
- The default trace-context propagator is the W3C standard.
- On Linux, `DriveInfo.DriveFormat` reports filesystem types.
- `GnuTarEntry` and `PaxTarEntry` omit `atime` and `ctime` by default.
- Sampling behavior changed for `ActivitySource.CreateActivity` and
  `ActivitySource.StartActivity`; validate custom listeners and samplers.
- LDAP `DirectoryControl` parsing is stricter, so malformed controls may now fail.
- The runtime no longer installs default termination-signal handlers. Applications
  that need graceful signal behavior must arrange it explicitly.

## Core Types and Metadata Compatibility

- Generic-math shift operations now behave consistently; test code that depended
  on the older inconsistency.
- An explicit struct size cannot be combined with `InlineArray`.
- `FilePatternMatch.Stem` is non-nullable.
- `Type.MakeGenericSignatureType` performs additional argument validation.
- `System.Linq.AsyncEnumerable` is part of the core libraries.
- Reflection and trimming annotations were tightened or removed on several APIs,
  which can surface source or binary incompatibilities. Re-run trim analysis and
  exercise reflection-heavy paths after upgrading.

## Numeric String Ordering

`CompareOptions.NumericOrdering` compares embedded digit sequences numerically:
`"2"` sorts before `"10"`, and `"2"` compares equal to `"02"`. Do not combine
the option with index or prefix operations such as `IndexOf`, `StartsWith`, or
`IsPrefix`.

```csharp
int order = CultureInfo.InvariantCulture.CompareInfo.Compare(
    "2", "10", CompareOptions.NumericOrdering);
```

## `TimeSpan.FromMilliseconds` and Expression Trees

A real `TimeSpan.FromMilliseconds(long)` overload works in expression trees. The
second parameter of the existing two-`long` overload is no longer optional.

```csharp
Expression<Action> expression = () => TimeSpan.FromMilliseconds(1000L);
```

## Tensor Contracts and Views

`System.Numerics.Tensors` is stable rather than experimental and includes the
nongeneric `IReadOnlyTensor`. Slicing returns a non-copying view, so later reads
observe changes to underlying storage. Tensor arithmetic operators are available
only when the element type implements the corresponding generic-math interfaces.

## Telemetry Schemas and Sampling

`ActivitySource` and `Meter` can carry a telemetry schema URL.
`ActivitySourceOptions` supplies the multi-option constructor path. Out-of-process
`Activity` serialization includes events and links. EventSource trace aggregators
can cap root activities per second with a filter such as:

```text
[AS]*/-ParentRateLimitingSampler(100)
```

## AVX10.2 Intrinsics

The x64 intrinsics are exposed under
`System.Runtime.Intrinsics.X86.Avx10v2`, but JIT support remains disabled by
default because capable hardware was not yet available. Do not make their mere
API presence a runtime capability check.
