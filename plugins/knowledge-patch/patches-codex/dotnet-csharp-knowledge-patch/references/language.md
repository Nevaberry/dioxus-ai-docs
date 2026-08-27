# Language and Compiler Features

Guidance in this file is attributed to `10.0-guides` and `10.0`.

## C# Extension Members

C# 14 extension blocks can add instance properties and methods, static properties
and methods, and operators to an extended type. A block with a named receiver
defines instance members; omitting the receiver name permits static members.

```csharp
public static class SequenceExtensions
{
    extension<T>(IEnumerable<T> source)
    {
        public bool IsEmpty => !source.Any();
    }
}
```

## Field-Backed Properties

The contextual `field` token refers to a compiler-synthesized backing field, so
an accessor can validate or transform a value without declaring a separate
field. In a type that already declares an identifier named `field`, use `@field`
or `this.field` to refer to the declared identifier.

```csharp
public string Message
{
    get;
    set => field = value ?? throw new ArgumentNullException(nameof(value));
}
```

## First-Class Span Conversions

C# 14 adds implicit conversions among arrays, `Span<T>`, and `ReadOnlySpan<T>`.
Span types also participate more naturally as extension receivers, in composed
conversions, and in generic type inference. Span-aware overload resolution can
therefore select a different overload after moving code to C# 14; compile and test
ambiguous call sites rather than assuming the previous selection remains.

## Unbound Generic Types in `nameof`

`nameof` accepts an unbound generic type. For example, `nameof(List<>)` evaluates
to `"List"` without a type argument.

## Modifiers on Implicitly Typed Lambda Parameters

Simple lambda parameters may use `scoped`, `ref`, `in`, `out`, or `ref readonly`
without explicit parameter types. `params` still requires an explicitly typed
parameter list.

```csharp
TryParse<int> parse = (text, out result) => int.TryParse(text, out result);
```

## Partial Constructors and Events

Instance constructors and events may be partial. Each has exactly one defining
declaration and one implementing declaration. Only the implementing constructor
may specify `this()` or `base()`. For a partial event, the defining declaration is
field-like and the implementing declaration supplies `add` and `remove`
accessors.

## User-Defined Compound Assignment

C# 14 permits user-defined compound-assignment operators. A type can provide
dedicated compound-assignment behavior instead of relying only on the matching
binary operator.

## Null-Conditional Assignment

`?.` and `?[]` can be used on the left side of simple and compound assignments.
The right side is evaluated only when the receiver is non-null. `++` and `--`
remain unsupported in this form.

```csharp
customer?.Order = GetCurrentOrder();
customer?.Balance += payment;
```

## Visual Basic Runtime-API Compatibility

The Visual Basic compiler enforces `unmanaged` generic constraints and respects
`OverloadResolutionPriorityAttribute`. This enables Span-oriented overload
selection and resolves ambiguities consistently with newer runtime APIs.
