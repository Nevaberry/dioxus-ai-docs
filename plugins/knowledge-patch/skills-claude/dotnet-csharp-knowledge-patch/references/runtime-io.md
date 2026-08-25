# Runtime, I/O, and Core Libraries

Compatibility items are attributed to `10.0-guides`; new API items marked below are
from `10.0`.

## Buffered I/O and Shutdown

`BufferedStream.WriteByte` no longer implicitly flushes. Call `Flush`/`FlushAsync` or
dispose the stream at the point durability or downstream visibility is required.

The runtime no longer installs default termination-signal handlers. Applications that
depend on graceful signal handling must own the lifecycle behavior and verify it in
their deployment environment.

## Tracing, Filesystems, TAR, and LDAP

The default trace-context propagator is the W3C standard. Check interoperability with
systems that expect a different propagation format and configure propagation
explicitly when required.

On Linux, `DriveInfo.DriveFormat` reports filesystem types. Code that assumed a blank
or generic value should accept concrete filesystem names.

`GnuTarEntry` and `PaxTarEntry` omit `atime` and `ctime` by default. Populate those
timestamps explicitly when archive consumers require them.

`ActivitySource.CreateActivity` and `StartActivity` sampling behavior changed. Re-run
sampling tests and avoid assuming that the same listeners or parent context produce
the previous creation/start result.

LDAP `DirectoryControl` parsing is stricter. Reject or repair malformed controls
instead of depending on permissive parsing.

## Core Types and Metadata

Generic-math shift operations now behave consistently. Re-test custom numeric types
whose operators depended on earlier inconsistent shift semantics.

An explicit struct size cannot be combined with `InlineArray`. Remove the explicit
size and let the inline-array layout be defined by its supported contract.

`FilePatternMatch.Stem` is non-nullable. Update nullable annotations and eliminate
branches that exist only for a null stem unless another source can introduce null.

`Type.MakeGenericSignatureType` performs additional argument validation. Pass a valid
generic type definition and suitable signature arguments; expect formerly tolerated
invalid combinations to fail.

`System.Linq.AsyncEnumerable` is part of the core libraries. Check namespace and
package collisions where a separate async-LINQ surface was previously referenced.

Reflection and trimming annotations were tightened or removed on several APIs. Treat
new warnings as migration work: preserve required members, update annotations, and
test trimmed publications instead of suppressing warnings wholesale.

## Numeric String Ordering

In `10.0`, `CompareOptions.NumericOrdering` compares embedded digit sequences
numerically: `"2"` sorts before `"10"`, and `"2"` compares equal to `"02"`.

```csharp
int order = CultureInfo.InvariantCulture.CompareInfo.Compare(
    "2", "10", CompareOptions.NumericOrdering);
```

Do not use `NumericOrdering` with index or prefix operations such as `IndexOf`,
`StartsWith`, or `IsPrefix`; those combinations are unsupported.

## `TimeSpan.FromMilliseconds` Overload

In `10.0`, a real `FromMilliseconds(long)` overload works in expression trees. The
second parameter of the existing two-`long` overload is no longer optional.

```csharp
Expression<Action> expression = () => TimeSpan.FromMilliseconds(1000L);
```

Recompile calls that relied on the optional second parameter so overload binding is
verified under the current API surface.

## Tensor Contracts and Slices

In `10.0`, `System.Numerics.Tensors` is no longer experimental and includes the
nongeneric `IReadOnlyTensor` contract. Slicing returns a non-copying view; access made
after the source storage changes observes those changes. Copy when an independent
snapshot is required.

Tensor arithmetic operators are available only when the element type implements the
corresponding generic-math interfaces. Add suitable constraints to generic code that
uses those operators.

## AVX10.2 Intrinsics

The `10.0` x64 intrinsics are under
`System.Runtime.Intrinsics.X86.Avx10v2`, but JIT support remains disabled by default
because capable hardware was not yet available. Do not make this API's presence a
proxy for executable hardware/JIT support; retain a tested fallback path.
