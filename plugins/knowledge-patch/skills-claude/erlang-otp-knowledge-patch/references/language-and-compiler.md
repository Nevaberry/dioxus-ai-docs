# Language and compiler

## Comprehensions

### Strict generators (since 28.0)

Strict generators fail on a pattern mismatch instead of silently skipping the input. Use `<:-` for list and map generators and `<:=` for binary generators; the older operators remain relaxed.

```erlang
[X || {ok, X} <:- [{ok, 1}, error, {ok, 3}]].
%% ** exception error: no match of right hand side value error
```

### Zip generators (since 28.0)

Join any number of list, binary, or map generators with `&&` to consume them in parallel. Zipped generators can be mixed with ordinary generators and filters and do not produce a Cartesian product.

```erlang
[{X, Y} || X <- [1, 2] && Y <- [a, b]].
%% [{1,a},{2,b}]
```

### Map-comprehension abstract forms (since 28.2)

Syntax Tools 4.0.2 annotates map comprehensions and map generators. Abstract-form consumers must handle them explicitly rather than assuming all comprehension and generator nodes are list or binary forms.

### Assignment qualifiers (since 29.0)

A match used as a comprehension qualifier is a compile error by default. Enable the experimental `compr_assign` feature with `-feature(compr_assign, enable).` or `erl -enable-feature compr_assign`; `P = E` then behaves as the strict generator `P <-:- [E]`.

```erlang
-feature(compr_assign, enable).
hashes(Items) ->
    [H || Item <- Items, H = erlang:phash2(Item), H rem 10 =:= 0].
```

### Multi-valued comprehensions (since 29.0)

A comprehension may emit multiple comma-separated values per iteration.

```erlang
[I, -I || I <- lists:seq(1, 3)].
%% [1,-1,2,-2,3,-3]
```

## Syntax, literals, and types

### Shell-local fun syntax (since 28.0)

The shell accepts normal `fun Name/Arity` syntax for auto-imported BIFs and shell-local functions.

```erlang
F = fun is_atom/1,
true = F(example).
```

### Based floating-point literals (since 28.0)

Floats can use bases other than ten, with an optional based exponent introduced by a second `#`. This can preserve an exact non-decimal or bit-level form.

```erlang
2#0.011.      %% 0.375
16#0.011#e5. %% 4352.0
2#0.10101#e8.
```

### Nominal types (since 28.0)

Dialyzer supports `-nominal` types whose structurally identical representations remain distinct in function inputs and outputs.

```erlang
-nominal meter() :: integer().
-nominal foot() :: integer().
```

`meter()` and `foot()` are incompatible. A nominal type remains compatible with a non-opaque, non-nominal type with the same structure, such as `integer()`.

### Left-associative application (since 29.0)

Function application is left associative: `f(X)(Y)` is accepted as `(f(X))(Y)`.

### Bounded integer guard (since 29.0)

`is_integer(Term, LowerBound, UpperBound)` returns `true` only when all three arguments are integers and `LowerBound =< Term =< UpperBound`. It avoids range guards that accidentally accept floats.

```erlang
is_digit(C) -> is_integer(C, $0, $9).
```

## Native records

### Definition and visibility (since 29.0)

Experimental native records are runtime types, not tagged tuples. Declare them with `-record #name{...}.`; construction, update, match, and field syntax resemble existing records, while printed values include the defining module.

```erlang
-record #vec{x = 0.0, y = 0.0}.
-export_record([vec]).

make_vec(X, Y) -> #vec{x = X, y = Y}.
```

Definitions are private by default. Another module may make a field-free match such as `#geom:vec{}`, but construction and field-aware matching require `-export_record([vec])` in the defining module. The feature remains experimental and can change incompatibly.

### Compiler and runtime corrections (since 29.0.1)

This patch fixes native-record programs that could crash the compiler and comparisons that could return the wrong result or crash ERTS. It also fixes a rare compiler optimization that could invert a Boolean result. Treat this patch as the minimum for deployments using experimental native records.

### Analysis and formatting corrections (since 29.0.2)

Further fixes cover Dialyzer analysis, `io_lib:bformat/2`, and a crash involving a tuple-record operation inside a native-record anonymous update. Update the full OTP installation rather than selectively patching one affected application.

## Warnings, deprecations, and diagnostics

### Old-style `catch` migration (since 28.0)

Enable `warn_deprecated_catch` to locate `catch Expr` before migration. A module can suppress a project-wide setting with `-compile(nowarn_deprecated_catch).`; targeted `try ... catch` clauses reduce the chance of swallowing unrelated runtime errors.

The warning is enabled by default in 29.0. Use the suppression only as a temporary migration escape hatch.

### New default and opt-in warnings (since 29.0)

The compiler warns by default when a variable is exported from a subexpression or a match aliases patterns that unify constructors. The corresponding escape hatches are `nowarn_export_var_subexpr` and `nowarn_match_alias_pats`.

Enable `warn_obsolete_bool_op` to find eager `and` and `or` expressions that should generally use `andalso` and `orelse`, or `,` and `;` in guards.

### Scheduled removals (since 29.0)

Old-style guard type tests such as `integer` and `atom` are deprecated for removal in OTP 30. The `odbc` application and the `ftp` and `ct_ftp` modules have the same planned removal release.

### Unsafe-function and `xref` analyses (since 29.0)

Functions can carry `-unsafe` attributes. Calls to OTP functions classified as always unsafe warn by default; `warn_possibly_unsafe_function` also reports conditionally unsafe operations such as atom-creating functions.

`xref:analyze/2` adds `unsafe_function_calls`, `undocumented_function_calls`, and `private_function_calls`. `xref` applies `ignore_xref` declarations as a post-analysis filter instead of relying on individual build tools to do so.

## Abstract output

### Documentation-preserving `.abstr` files (since 29.0)

The `to_abstr` compiler option preserves source `-doc` attributes in the generated `.abstr` file. BEAM-targeting languages and abstract-form tools can retain documentation metadata instead of reconstructing it.
