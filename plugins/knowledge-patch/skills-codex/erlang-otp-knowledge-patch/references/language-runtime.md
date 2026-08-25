# Language and Runtime

## Write strict and parallel comprehensions

### Strict generators

Since 28.0, use `<:-` for strict list and map generators and `<:=` for strict
binary generators. A value that does not match the generator pattern raises
instead of being silently skipped:

```erlang
[X || {ok, X} <:- [{ok, 1}, error, {ok, 3}]].
%% ** exception error: no match of right hand side value error
```

The existing generator operators remain relaxed.

### Zip generators

Join generators with `&&` to consume them in parallel rather than forming a
Cartesian product:

```erlang
[{X, Y} || X <- [1, 2] && Y <- [a, b]].
%% [{1,a},{2,b}]
```

Any number of list, binary, or map generators can be zipped and mixed with
other generators and filters.

### Assignment qualifiers

Since 29.0, using a match as a comprehension qualifier is a compile error by
default instead of compiling and later failing as a non-boolean filter. Enable
the experimental feature with `-feature(compr_assign, enable).` or
`erl -enable-feature compr_assign`. Then `P = E` behaves like the strict
generator `P <-:- [E]`:

```erlang
-feature(compr_assign, enable).
hashes(Items) ->
    [H || Item <- Items, H = erlang:phash2(Item), H rem 10 =:= 0].
```

### Multiple emitted values

Since 29.0, a comprehension may emit multiple comma-separated values for each
iteration:

```erlang
[I, -I || I <- lists:seq(1, 3)].
%% [1,-1,2,-2,3,-3]
```

## Use new expression and guard forms

### Left-associative calls

Since 29.0, function application is left associative. `f(X)(Y)` is accepted
and means `(f(X))(Y)`.

### Bounded integer checks

Since 29.0, `is_integer(Term, LowerBound, UpperBound)` returns true only when
all three arguments are integers and
`LowerBound =< Term =< UpperBound`. Prefer it to range guards that can
accidentally accept floats:

```erlang
is_digit(C) -> is_integer(C, $0, $9).
```

### Based floating-point literals

Since 28.0, floating-point literals support bases other than ten, including a
based exponent introduced by a second `#`:

```erlang
2#0.011.       %% 0.375
16#0.011#e5.  %% 4352.0
```

This syntax can preserve an exact non-decimal or bit-level representation, as
in `2#0.10101#e8`.

## Represent domain types

### Nominal Dialyzer types

Since 28.0, declare types with `-nominal` when identical representations must
remain distinct:

```erlang
-nominal meter() :: integer().
-nominal foot() :: integer().
```

`meter()` and `foot()` are incompatible in input and output specifications. A
nominal type is still compatible with a non-opaque, non-nominal type of the
same structure, such as `integer()`.

### Experimental native records

OTP 29.0 introduces experimental native records as runtime types rather than
tagged tuples:

```erlang
-record #vec{x = 0.0, y = 0.0}.
-export_record([vec]).

make_vec(X, Y) -> #vec{x = X, y = Y}.
```

They use familiar record construction, update, match, and field syntax and
print with their defining module, such as `#geom:vec{...}`. Definitions are
private by default. Another module may make a field-free match such as
`#geom:vec{}`, but construction and field-aware matching require
`-export_record([vec])` in the defining module. The feature may still change
incompatibly.

OTP 29.0.1 fixes a rare optimization that could invert a Boolean result,
native-record programs that could crash the compiler, and comparisons that
could return a wrong result or crash ERTS. Treat that patch as the minimum for
native-record experiments.

OTP 29.0.2 additionally fixes native-record Dialyzer analysis,
`io_lib:bformat/2` formatting, and a crash caused by a tuple-record operation
inside a native-record anonymous update. Update the complete OTP installation
rather than selectively patching an application.

## Apply compiler diagnostics

### Old-style `catch`

Since 29.0, the old-style `catch Expr` warning is enabled by default. In 28.0
it was available through `warn_deprecated_catch`, with
`-compile(nowarn_deprecated_catch).` as a module-level override. Migrate to
targeted `try ... catch` clauses to avoid swallowing unrelated runtime errors.

### Exported variables, match aliases, and Boolean operators

Since 29.0, the compiler warns by default when a variable escapes a
subexpression and when a match aliases patterns that unify constructors.
Temporary migration escape hatches are `nowarn_export_var_subexpr` and
`nowarn_match_alias_pats`.

Enable `warn_obsolete_bool_op` to find eager `and` and `or` operations that
should generally become `andalso` and `orelse`, or `,` and `;` in guards.

### Deprecations planned for OTP 30

Since 29.0, old-style guard type tests such as `integer` and `atom` are
deprecated and scheduled for removal in OTP 30. The `odbc` application and the
`ftp` and `ct_ftp` modules have the same status. Remove dependencies rather
than suppressing the migration work.

### Unsafe functions and `xref`

Since 29.0, functions can carry `-unsafe` attributes, and the compiler warns by
default about calls to OTP functions classified as always unsafe. Enable
`warn_possibly_unsafe_function` for conditional cases, including atom-creating
functions.

`xref:analyze/2` provides `unsafe_function_calls`,
`undocumented_function_calls`, and `private_function_calls`. `xref` now
applies `ignore_xref` declarations after analysis instead of requiring each
build tool to implement that filter.

Since 29.0.2, analyzing a BEAM file without debug information and with
`moduledoc(false)` returns an error rather than crashing. Callers must handle
the error result.

## Manage processes and signals

### Priority messages and signals

Since 28.0, a receiver opts in by creating `alias([priority])`. A sender uses
the alias with the `priority` option to place a message ahead of ordinary
messages while preserving signal order:

```erlang
PrioAlias = alias([priority]),
erlang:send(PrioAlias, Message, [priority]).
```

Sending through the alias without the option is ordinary, and `unalias/1`
revokes the capability. Use `exit(PrioAlias, Reason, [priority])` for a
priority exit signal. For event-generated link and monitor signals, pass
`priority` to `erlang:link/2` or `erlang:monitor/3`.

### Stack-preserving hibernation

Since 28.0, `erlang:hibernate/0` minimizes the calling process's memory while
waiting for its next message. Unlike `erlang:hibernate/3`, it does not discard
the call stack.

### Idempotent persistent-term insertion

Since 28.4, `persistent_term:put_new/2` returns quickly when the same key and
value are already present. It raises `badarg` when the key exists with a
different value:

```erlang
persistent_term:put_new(config, Config).
```

## Work with collections

### Expanded `array` API and serialization boundary

Since 29.0, `array` adds:

- `prepend/2`, `append/2`, and `concat/1,2`;
- `slice/3`, `shift/2`, and `from/2,3`;
- index-bounded traversals such as `foldl/5`; and
- map-fold families such as `mapfoldl/3` and `sparse_mapfoldr/5`.

Its internal representation changed. Array terms serialized with
`term_to_binary/1` on earlier releases are incompatible and must be rebuilt
rather than carried through the upgrade unchanged.

### Consistent but undefined map iteration

Since 29.0, `maps:keys/1`, `maps:values/1`, `maps:to_list/1`, default
iterators, and map comprehensions produce a given map's elements in the same
order. The order remains undefined: it is neither sorted nor a stability
guarantee.

### Checked ordered construction

Since 29.0, `gb_sets:from_ordset/1` and `gb_trees:from_orddict/1` reject
unordered input instead of creating invalid structures. For example,
`gb_sets:from_ordset([3,2,1])` raises `badarg` with reason `not_ordset`.

### Persistent functional graphs

Since 29.0, `graph` is a persistent functional counterpart to `digraph` and
`digraph_utils`. A modification returns a new graph while prior values remain
usable:

```erlang
G0 = graph:new(),
G1 = graph:add_vertex(G0, a),
G2 = graph:add_vertex(G1, b),
G3 = graph:add_edge(G2, a, b).
```

## Compile and transfer regular expressions

Since 28.0, `re` uses PCRE2. Pattern validation is stricter: invalid escapes
such as `\M`, `\i`, `\B`, or `\8` can raise `badarg`. Unicode property
results can change with updated property data, and branch-reset groups can
change `re:split/3` output. Retest stored patterns and result assumptions.

The internal value returned by `re:compile/2` is not safe to reuse across
nodes or OTP versions. Since 28.1, use the supported export/import path for
compiled regular expressions when transferring them between Erlang node
instances; never transfer the internal value directly.

## Reject malformed External Term Format

Since 29.0.4, `binary_to_term` no longer corrupts the heap when an invalid
tuple declares an arity of 2^31 or larger, and crafted ETF payloads no longer
crash ERTS. Continue treating untrusted term decoding as a security boundary
and do not depend on former crash behavior.
