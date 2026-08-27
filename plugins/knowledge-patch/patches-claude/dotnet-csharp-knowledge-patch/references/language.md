# Language Features and Compiler Compatibility

The items in this reference are attributed to `10.0-guides` unless a different
batch is named.

## Extension Members

C# 14 extension blocks can add instance properties and methods, static properties
and methods, and operators to an extended type. A block with a named receiver
defines instance members; omit the receiver name to define static members.

```csharp
public static class SequenceExtensions
{
    extension<T>(IEnumerable<T> source)
    {
        public bool IsEmpty => !source.Any();
    }
}
```

Keep the receiver form aligned with the kind of member being added; changing from a
named to an unnamed receiver changes the extension surface from instance to static.

## Field-Backed Properties

The contextual `field` token refers to a compiler-synthesized backing field. It lets
an accessor add validation or transformation without declaring a separate field.

```csharp
public string Message
{
    get;
    set => field = value ?? throw new ArgumentNullException(nameof(value));
}
```

If the containing type already declares an identifier named `field`, use `@field` or
`this.field` when referring to that existing member.

## First-Class Span Conversions

C# 14 adds implicit conversions among arrays, `Span<T>`, and `ReadOnlySpan<T>`. Span
types also participate more naturally as extension receivers, in composed
conversions, and in generic type inference.

These rules can cause overload resolution to choose a different candidate after a
language-version upgrade. Recompile and test calls where array, span, and read-only
span overloads coexist; add an explicit conversion when the intended overload must
remain fixed.

## Unbound Generic Types in `nameof`

`nameof` accepts an unbound generic type, so the following expression does not need a
type argument and evaluates to `"List"`:

```csharp
string name = nameof(List<>);
```

## Modifiers on Implicitly Typed Lambda Parameters

Simple lambda parameters can use `scoped`, `ref`, `in`, `out`, or `ref readonly`
without explicit parameter types. `params` still requires an explicitly typed
parameter list.

```csharp
TryParse<int> parse = (text, out result) => int.TryParse(text, out result);
```

## Partial Constructors and Events

Instance constructors and events can be partial. Each member must have exactly one
defining declaration and one implementing declaration.

- Only the implementing constructor may specify a `this()` or `base()` initializer.
- The implementing declaration of a partial event supplies the `add` and `remove`
  accessors for the defining field-like event.

Use these constraints when generating declarations across files; two defining or two
implementing declarations are invalid.

## User-Defined Compound Assignment

C# 14 supports user-defined compound assignment operators. A type can provide
dedicated compound-assignment behavior instead of relying only on the corresponding
binary operator. Review mutation and conversion semantics when both forms exist; the
compound operation need not merely be an expansion to the binary operation.

## Null-Conditional Assignment

The null-conditional operators `?.` and `?[]` can appear on the left side of simple
and compound assignments. The right side is evaluated only when the receiver is
non-null.

```csharp
customer?.Order = GetCurrentOrder();
customer?.Balance += payment;
```

The increment and decrement forms `++` and `--` remain unsupported on a
null-conditional target.

## Visual Basic Runtime-API Compatibility

In batch `10.0`, the Visual Basic compiler interprets and enforces `unmanaged`
generic constraints and respects `OverloadResolutionPriorityAttribute`. This enables
span-oriented overload selection and resolves ambiguities consistently with newer
runtime APIs. Recompile Visual Basic consumers when library overloads depend on these
metadata contracts.
