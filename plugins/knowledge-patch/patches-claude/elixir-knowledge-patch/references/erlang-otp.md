# Erlang/OTP Runtime and Libraries

## Language and source forms

### Markdown source documentation (`otp-27`)

OTP documentation is Markdown beside the spec and implementation. Use `-doc`
attributes and ExDoc instead of separate Erl_Docgen XML files:

```erlang
-doc """
Returns `N` copies of `Elem`.
""".
-spec duplicate(N, Elem) -> [Elem].
```

### Triple-quoted strings (`otp-27`)

`"""` delimits multiline strings. Indentation before the closing delimiter is
removed from each content line; deeper indentation remains. Quotes and
backslashes in the body are literal rather than escapes.

```erlang
Text = """
       first line
         indented line
       """.
```

### String sigils (`otp-27`)

`~b` creates a UTF-8 binary with escapes and `~B` one without escapes. Bare `~`
behaves like `~b` for inline strings and `~B` for triple-quoted strings. `~s` and
`~S` create list strings with and without escaping.

```erlang
Utf8 = ~B[Greek: Γνῶθι σαυτόν],
Tabbed = ~b"abc\txyz".
```

### `maybe` is enabled by default (`otp-27`)

The compiler enables `maybe_expr` without a feature declaration, so the atom is
written `'maybe'`. Disable the feature with `erlc -disable-feature maybe_expr` or
`-feature(maybe_expr, disable).` when necessary.

### Strict and zipped generators (`otp-28`)

Use `<:-` for strict list or map generators and `<:=` for strict binary
generators. A strict generator fails on a pattern mismatch instead of skipping
it. Keep relaxed generators when non-matches are intentional.

Join generators with `&&` to zip them in parallel rather than form a Cartesian
product. Any number of list, binary, or map generators may be zipped and mixed
with other generators and filters.

```erlang
[X || {ok, X} <:- [{ok, 1}, {ok, 2}]].
[{X, Y} || X <- [1, 2] && Y <- [a, b]].
%% [{1,a},{2,b}]
```

### Based floating-point literals (`otp-28`)

Floating-point literals support arbitrary bases. A second `#` introduces the
exponent marker, enabling exact non-decimal forms without decimal conversion:

```erlang
2#0.011.       %% 0.375
16#0.011#e5.  %% 4352.0
```

### Experimental native records (`otp-29`)

`-record #name{}` declares a runtime-native record rather than a tuple-backed
record. Construction, update, matching, and access otherwise use familiar
record syntax. Records are module-private unless exported with `-export_record`;
external references use `#module:name{}`. The feature is experimental and may
change incompatibly.

```erlang
-module(geom).
-export([make_vec/2]).
-export_record([vec]).
-record #vec{x=0.0, y=0.0}.

make_vec(X, Y) -> #vec{x=X, y=Y}.
```

### Assignment and multiple values in comprehensions (`otp-29`)

With experimental `compr_assign` enabled, `Pattern = Expr` is a comprehension
qualifier binding a computed value for later filters or output. Its semantics are
as strict as `Pattern <-:- [Expr]`. Without the feature, matches in qualifiers
are rejected rather than treated as boolean filters.

```erlang
-feature(compr_assign, enable).

selected(List) ->
    [H || E <- List, H = erlang:phash2(E), H rem 10 =:= 0].
```

A list comprehension may emit multiple values per iteration by placing multiple
expressions before `||`:

```erlang
[I, -I || I <- lists:seq(1, 5)].
%% [1,-1,2,-2,3,-3,4,-4,5,-5]
```

## Processes, shells, and messaging

### Labels for unregistered processes (`otp-27`)

`proc_lib:set_label/1` attaches a term to the current process, and
`proc_lib:get_label/1` retrieves a process label. Labels appear in shell `i/0`,
Observer, and crash dumps, making anonymous processes identifiable.

### Fun-based timers (`otp-27`)

`timer:apply_after/2,3`, `apply_interval/*`, and `apply_repeatedly/*` accept funs
directly. When a timer may survive hot-code upgrade, pass a remote fun and its
arguments:

```erlang
timer:apply_after(1000, fun io:put_chars/1, ["done\n"]).
```

### Priority signals (`otp-28`)

A process opts in with `alias([priority])`. Send to that alias through
`erlang:send/3` with the `priority` option; priority messages move ahead of
ordinary messages while retaining signal ordering. Use `exit/3` for priority
exit signals and the `priority` option to `erlang:link/2` or `erlang:monitor/3`
for link- or monitor-generated signals.

```erlang
PrioAlias = alias([priority]),
erlang:send(PrioAlias, urgent, [priority]),
true = unalias(PrioAlias).
```

### Lazy input and raw `noshell` (`otp-28`)

Standard input is read only when an operation such as `io:get_line/2` requests
it, so `-noinput` is no longer needed merely to prevent eager reads. `noshell`
remains cooked by default, but a custom shell may select raw mode to receive
keystrokes without Enter, line editing, or echo:

```erlang
shell:start_interactive({noshell, raw}),
Chars = io:get_chars("", 1024).
```

### Local funs in the shell (`otp-28`)

The shell accepts `fun Name/Arity` for auto-imported BIFs and shell-local
functions, even when the local function is defined after the fun:

```erlang
1> F = fun id/1.
2> id(X) -> X.
3> F(42).
42
```

### Stack-preserving hibernation (`otp-28`)

`erlang:hibernate/0` reduces the calling process's memory while waiting for its
next message but, unlike `erlang:hibernate/3`, preserves the existing call stack.

## Standard library and storage

### Built-in JSON (`otp-27`)

STDLIB's `json` module supplies `json:decode/1` and `json:encode/1`. Decoding
uses binary object keys by default, avoiding creation of unbounded atoms.
`json:decode/3` accepts callbacks such as `object_push`; `json:encode/2` accepts
a recursive encoder that may delegate to `json:encode_map/2` and
`json:encode_value/2`.

```erlang
Map = json:decode(<<"{\"ok\":true}">>),
Json = json:encode(Map).
```

### Set utilities (`otp-27`)

`sets`, `gb_sets`, and `ordsets` each provide `is_equal/2`, `map/2`, and
`filtermap/2`. Prefer `is_equal/2` over term equality because equal sets may have
different internal representations.

### ETS lookup traversal and default updates (`otp-27`)

`ets:first_lookup/1`, `next_lookup/2`, `last_lookup/1`, and `prev_lookup/2`
combine key traversal with object lookup. `ets:update_element/4` accepts a
default object for a missing key:

```erlang
ets:update_element(Tab, Key, {2, Value}, {Key, Default}).
```

### Expanded arrays (`otp-29`)

`array` adds `concat/1,2`, `slice/3`, `shift/2`, fun-based `from/2,3`, bounded
traversal variants such as `foldl/5`, and map-fold families including
`mapfoldl/3` and `sparse_mapfoldr/5`.

### Consistent map traversal order (`otp-29`)

Map key order remains undefined, but all traversal mechanisms for a given map now
produce that same order, including `maps:keys/1`, `maps:to_list/1`, map
comprehensions, and iterators.

### Checked ordered structures (`otp-29`)

`gb_sets:from_ordset/1` and `gb_trees:from_orddict/1` validate input ordering and
raise `badarg` rather than silently creating corrupt structures. Use
`gb_trees:from_list/1` when input is not already ordered.

### Immutable graphs (`otp-29`)

`graph` is the functional counterpart to `digraph` and `digraph_utils`. Every
mutation returns a new graph and leaves earlier versions usable:

```erlang
G0 = graph:new(),
G1 = graph:add_vertex(G0, a),
G2 = graph:add_vertex(G1, b),
G3 = graph:add_edge(G2, a, b).
```

### ANSI terminal output (`otp-29`)

`io_ansi:format/2` returns a binary containing ANSI styling sequences, while
`io_ansi:fwrite/2` writes the styled result:

```erlang
io_ansi:fwrite([bold, red, "wrong answer: ", "~p\n"], [99]).
```

## Diagnostics, tracing, and coverage

### Unified `tprof` (`otp-27`)

Use one profiling API for call counts, time, and allocation:

```erlang
tprof:profile(M, F, Args, #{type => call_count | call_time | call_memory}).
```

Call counting covers all processes. Time and memory measurement covers the
caller and processes it spawns.

### Independent trace sessions (`otp-27`)

Kernel's `trace` module gives each session its own tracer and process/function
configuration. Use `trace:session_create/3`, `trace:process/4`,
`trace:function/4`, and `trace:session_destroy/1`. Legacy `erlang:trace/3` users
still share one global session.

### Native coverage (`otp-27`)

On JIT-capable runtimes, Cover automatically uses low-overhead native coverage.
Start coverage before normal module execution with
`erl +JPcover function_counters`, then query it through
`code:get_coverage(function, Module)`.

### Unsafe-call checks (`otp-29`)

The compiler warns for functions marked always unsafe. Add
`erlc +warn_possibly_unsafe_function` to diagnose conditionally dangerous calls
such as atom creation. Xref understands `-unsafe` attributes and provides
`unsafe_function_calls`, `undocumented_function_calls`, and
`private_function_calls` analyses.

```erlang
xref:analyze(S, unsafe_function_calls).
```

### Obsolete or confusing constructs (`otp-28`, `otp-29`)

In OTP 28, opt into old-style `catch Expr` warnings with
`warn_deprecated_catch`; suppress a project-level setting per module with
`-compile(nowarn_deprecated_catch)`. Prefer `try ... catch` so unrelated runtime
errors are not swallowed. OTP 29 enables the old-style catch warning by default.

OTP 29's `warn_obsolete_bool_op` opts into warnings for `and` and `or`. The
compiler also warns when a variable is bound in a subexpression and used later,
or a match implicitly unifies constructors such as `{a,B} = {Y,Z}`. Move the
binding outward and spell the latter `{a=Y,B=Z}`.

### Integer range guard (`otp-29`)

`is_integer/3` verifies both integer type and inclusive bounds, avoiding range
tests that accidentally accept floats:

```erlang
is_digit(C) -> is_integer(C, $0, $9).
```

## Code loading and regular expressions

### Archive loading deprecations (`otp-27`)

Putting application archives on the code path is deprecated, as are archive
handling in `erl_prim_loader`, `code:lib_dir/2` archive lookup, and
`-code_path_choice`. The default is `strict`; archive users can temporarily use
`-code_path_choice relaxed`.

A single archive embedded in an escript remains supported. Access its data files
through `escript:extract/2` for forward compatibility.

### PCRE2 migration (`otp-28`)

`re` uses PCRE2. Its stricter parser rejects previously tolerated invalid
escapes, and new Unicode property data or branch-reset behavior may change
matches and splits. The value from `re:compile/2` changed and must not be reused
across nodes or OTP versions.

### Safer default code path (`otp-29`)

The code server places the current working directory last instead of first, so a
local BEAM file cannot shadow an OTP or application module of the same name.

## Transport and archive security

### Client OCSP stapling (`otp-27`)

Enable validation of a server's stapled OCSP response with `{stapling, staple}`
in `ssl:connect/3`, normally alongside trusted CAs:

```erlang
ssl:connect(Host, 443,
            [{cacerts, public_key:cacerts_get()}, {stapling, staple}]).
```

### Bounded tar extraction (`otp-29`)

Pass `{max_size, Size}` to `erl_tar` extraction to cap total extracted data and
protect the destination from disk-filling archives.

### SSL and SSH defaults (`otp-29`)

SSL and SSH prefer hybrid ML-KEM-768/X25519 key exchange and fall back when the
peer lacks it. SSH daemons no longer enable shell, exec, or SFTP by default; opt
into only needed services:

```erlang
ssh:daemon(Port, [{shell, {shell, start, []}},
                  {exec, erlang_eval},
                  {subsystems, [ssh_sftpd:subsystem_spec([])]}
                  | Options]).
```
