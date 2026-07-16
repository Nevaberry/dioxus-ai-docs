# Erlang/OTP Runtime and Libraries

Batch attribution: `otp-27`, `otp-28`, and `otp-29`.

## Contents

- [Write and document Erlang source](#write-and-document-erlang-source)
- [Use comprehensions deliberately](#use-comprehensions-deliberately)
- [Work with processes and messages](#work-with-processes-and-messages)
- [Build shells and terminal programs](#build-shells-and-terminal-programs)
- [Encode JSON and match regular expressions](#encode-json-and-match-regular-expressions)
- [Use collections and storage](#use-collections-and-storage)
- [Trace, profile, and measure coverage](#trace-profile-and-measure-coverage)
- [Analyze types and unsafe code](#analyze-types-and-unsafe-code)
- [Migrate warnings and code loading](#migrate-warnings-and-code-loading)
- [Use native records](#use-native-records)
- [Harden network and archive operations](#harden-network-and-archive-operations)

## Write and document Erlang source

### Keep Markdown documentation beside code

Store documentation in Markdown through `-doc` next to the spec and implementation. OTP documentation uses ExDoc rather than separate Erl_Docgen XML files:

```erlang
-doc """
Returns `N` copies of `Elem`.
""".
-spec duplicate(N, Elem) -> [Elem].
```

### Use triple-quoted strings

`"""` delimits multiline strings. The indentation before the closing delimiter is removed from every content line, while any deeper indentation remains. Quotes and backslashes in the body are literal rather than escapes:

```erlang
Text = """
       first line
         indented line
       """.
```

### Choose binary and list-string sigils

- `~b` creates a UTF-8 binary with escapes.
- `~B` creates a UTF-8 binary without escapes.
- Bare `~` behaves like `~b` for inline strings and `~B` for triple-quoted strings.
- `~s` and `~S` create list strings with and without escaping.

```erlang
Utf8 = ~B[Greek: Γνῶθι σαυτόν],
Tabbed = ~b"abc\txyz".
```

### Account for `maybe` being enabled

The compiler enables `maybe_expr` by default, so remove the old `-feature(maybe_expr, enable).` requirement. Quote the atom as `'maybe'`. Disable the feature only when required with `erlc -disable-feature maybe_expr` or `-feature(maybe_expr, disable).`.

### Write based floating-point literals

Floating-point literals support arbitrary bases. A second `#` introduces the exponent marker:

```erlang
2#0.011.       %% 0.375
16#0.011#e5.  %% 4352.0
```

## Use comprehensions deliberately

### Fail on generator mismatches

Use `<:-` for strict list and map generators and `<:=` for strict binary generators. A non-matching value fails instead of being silently skipped; keep the relaxed operators when skipping is intended:

```erlang
[X || {ok, X} <:- [{ok, 1}, {ok, 2}]].
```

### Zip generators

Join any number of list, binary, or map generators with `&&` to iterate in parallel rather than taking a Cartesian product. Zipped generators may be combined with ordinary generators and filters:

```erlang
[{X, Y} || X <- [1, 2] && Y <- [a, b]].
%% [{1,a},{2,b}]
```

### Assign within comprehensions

With the experimental `compr_assign` feature enabled, use `Pattern = Expr` as a qualifier that binds a computed value for later filters or output. It has the strict semantics of `Pattern <-:- [Expr]`. Without the feature, OTP 29 rejects matches in qualifiers rather than treating the resulting value as a boolean filter.

```erlang
-feature(compr_assign, enable).

selected(List) ->
    [H || E <- List, H = erlang:phash2(E), H rem 10 =:= 0].
```

### Emit multiple values per iteration

Place multiple expressions before `||` to append several values for each iteration without building temporary lists and flattening:

```erlang
[I, -I || I <- lists:seq(1, 5)].
%% [1,-1,2,-2,3,-3,4,-4,5,-5]
```

## Work with processes and messages

### Send priority signals safely

A receiving process must opt in by creating an alias with `alias([priority])`. Send to that alias with `erlang:send/3` and the `priority` option. Priority messages are inserted before ordinary messages but retain signal ordering among themselves:

```erlang
PrioAlias = alias([priority]),
erlang:send(PrioAlias, urgent, [priority]),
true = unalias(PrioAlias).
```

Use `exit/3` for priority exit signals. Add `priority` to `erlang:link/2` or `erlang:monitor/3` when link- or monitor-generated signals must be prioritized.

### Label unregistered processes

Call `proc_lib:set_label/1` in the current process and retrieve a label with `proc_lib:get_label/1`. Labels appear in shell `i/0`, Observer, and crash dumps, making anonymous processes identifiable.

### Schedule fun-based timers

`timer:apply_after/2,3`, `timer:apply_interval/*`, and `timer:apply_repeatedly/*` accept funs directly. For a timer that may outlive a hot-code upgrade, pass a remote fun and its arguments:

```erlang
timer:apply_after(1000, fun io:put_chars/1, ["done\n"]).
```

### Hibernate without discarding the stack

`erlang:hibernate/0` reduces the calling process's memory while waiting for the next message and preserves the call stack. This differs from `erlang:hibernate/3`:

```erlang
erlang:hibernate().
```

## Build shells and terminal programs

### Rely on lazy standard input

Standard input is read only when an operation such as `io:get_line/2` asks for it. Programs no longer need `-noinput` merely to prevent eager consumption.

### Select raw `noshell` input

`noshell` remains cooked by default. A custom shell can select raw mode to receive keystrokes without Enter and bypass line editing and terminal echo:

```erlang
shell:start_interactive({noshell, raw}),
Chars = io:get_chars("", 1024).
```

### Capture shell-local functions

The shell accepts `fun Name/Arity` for auto-imported BIFs and shell-local functions, including a local function defined after the fun value was created:

```erlang
1> F = fun id/1.
2> id(X) -> X.
3> F(42).
42
```

### Produce ANSI terminal output

Use `io_ansi:format/2` to return a styled binary or `io_ansi:fwrite/2` to write it directly:

```erlang
io_ansi:fwrite([bold, red, "wrong answer: ", "~p\n"], [99]).
```

## Encode JSON and match regular expressions

### Use STDLIB JSON

The `json` module supplies `json:decode/1` and `json:encode/1`. Object keys decode to binaries by default, preventing unbounded atom creation:

```erlang
Map = json:decode(<<"{\"ok\":true}">>),
Json = json:encode(Map).
```

Use `json:decode/3` with decoder callbacks such as `object_push`. Use `json:encode/2` with a recursive custom encoder, delegating ordinary map and value handling to `json:encode_map/2` and `json:encode_value/2`.

### Migrate regex assumptions to PCRE2

The `re` module uses PCRE2. Its stricter parser rejects some previously tolerated invalid escapes; updated Unicode properties and branch-reset behavior can alter matches and splits. Never reuse the internal value from `re:compile/2` on another node or OTP version.

## Use collections and storage

### Compare and transform sets through their APIs

`sets`, `gb_sets`, and `ordsets` each provide `is_equal/2`, `map/2`, and `filtermap/2`. Use `is_equal/2` instead of term equality because equal sets may have different internal representations.

### Traverse ETS while retrieving objects

Use `ets:first_lookup/1`, `next_lookup/2`, `last_lookup/1`, and `prev_lookup/2` to combine key traversal with object lookup. Use the default-object form of `ets:update_element/4` for a missing key:

```erlang
ets:update_element(Tab, Key, {2, Value}, {Key, Default}).
```

### Expand array workflows

The `array` module provides `concat/1,2`, `slice/3`, `shift/2`, fun-driven constructors `from/2,3`, index-bounded traversal such as `foldl/5`, and `mapfold` families including `mapfoldl/3` and `sparse_mapfoldr/5`.

### Treat map traversal as consistently ordered, not sorted

Map key order remains undefined, but every traversal mechanism for a given map now produces the same order. This includes `maps:keys/1`, `maps:to_list/1`, map comprehensions, and iterators. Do not infer a semantic sort order from that consistency.

### Validate ordered tree and set input

`gb_sets:from_ordset/1` and `gb_trees:from_orddict/1` validate ordering and raise `badarg` for invalid input rather than constructing corrupt values. Use `gb_trees:from_list/1` when input is not already ordered.

### Use persistent functional graphs

The immutable `graph` module is the functional counterpart to `digraph` and `digraph_utils`. Every modification returns a new graph and leaves earlier versions usable:

```erlang
G0 = graph:new(),
G1 = graph:add_vertex(G0, a),
G2 = graph:add_vertex(G1, b),
G3 = graph:add_edge(G2, a, b).
```

## Trace, profile, and measure coverage

### Profile through `tprof`

Use one API for call counts, time, and allocation:

```erlang
tprof:profile(M, F, Args,
              #{type => call_count | call_time | call_memory}).
```

Call counting observes all processes. Time and memory profiling observe the caller and processes it spawns.

### Isolate trace sessions

Create independent Kernel `trace` sessions with `trace:session_create/3`, configure them with `trace:process/4` and `trace:function/4`, and release them with `trace:session_destroy/1`. Each session owns its tracer and configuration, so migrated tools do not overwrite one another. Users of `erlang:trace/3` still share a global session.

### Use native coverage

On JIT-capable runtimes, Cover automatically uses low-overhead native coverage. Start coverage before normal module execution with `erl +JPcover function_counters`, and query it with `code:get_coverage(function, Module)`.

## Analyze types and unsafe code

### Declare nominal Dialyzer types

Use `-nominal` when structurally identical types must be incompatible by name in function inputs, outputs, and specifications. A nominal type remains compatible with a structurally identical non-nominal, non-opaque type:

```erlang
-nominal meter() :: integer().
-nominal foot() :: integer().

-spec as_meter(integer()) -> meter().
as_meter(X) -> X.
```

### Find unsafe calls

The compiler warns for calls to functions marked always unsafe. Compile with `erlc +warn_possibly_unsafe_function` to diagnose conditionally dangerous operations such as atom creation. Xref understands `-unsafe` attributes and adds `unsafe_function_calls`, `undocumented_function_calls`, and `private_function_calls` analyses:

```erlang
xref:analyze(S, unsafe_function_calls).
```

### Use bounded integer guards

`is_integer/3` checks both the type and inclusive bounds, avoiding range comparisons that accidentally accept floats:

```erlang
is_digit(C) -> is_integer(C, $0, $9).
```

## Migrate warnings and code loading

### Replace old-style `catch`

OTP 28 offers the opt-in `warn_deprecated_catch` warning for `catch Expr`, with per-module suppression through `-compile(nowarn_deprecated_catch)`. OTP 29 enables the warning by default. Prefer `try ... catch` so only the intended exception class is handled:

```erlang
Result = try work()
         catch
             throw:Reason -> {error, Reason}
         end.
```

### Enable additional construct warnings where useful

Use `warn_obsolete_bool_op` to find `and` and `or`. The compiler also warns when a variable is bound inside a subexpression and used afterward, or when a match confusingly unifies constructors such as `{a,B} = {Y,Z}`. Move the binding outward and write the latter as `{a=Y,B=Z}`.

### Account for safer code-path precedence

The code server places the current working directory last rather than first, preventing a local BEAM file from shadowing an OTP or application module of the same name.

### Avoid deprecated archive loading

Putting application archives on the code path is deprecated, as are archive support in `erl_prim_loader`, archive lookup through `code:lib_dir/2`, and `-code_path_choice`. The default path choice is `strict`; archive users can temporarily request `-code_path_choice relaxed`.

A single archive embedded in an escript remains supported. Access its data files through `escript:extract/2` for future-safe behavior.

## Use native records

The experimental `-record #name{}` form declares a runtime-native record instead of a tuple-backed record. Construction, update, matching, and field access retain familiar record syntax. Definitions are module-private unless exported with `-export_record`; refer to an exported record externally as `#module:name{}`. Expect possible breaking changes while the feature remains experimental.

```erlang
-module(geom).
-export([make_vec/2]).
-export_record([vec]).
-record #vec{x=0.0, y=0.0}.

make_vec(X, Y) -> #vec{x=X, y=Y}.
```

## Harden network and archive operations

### Validate stapled OCSP responses

Enable SSL client validation of a server's stapled OCSP response with `{stapling, staple}`, normally alongside trusted CA certificates:

```erlang
ssl:connect(Host, 443,
            [{cacerts, public_key:cacerts_get()}, {stapling, staple}]).
```

### Bound tar extraction

Pass `{max_size, Size}` to `erl_tar` extraction to cap total extracted data and prevent disk-filling archives.

### Opt into SSH services

SSL and SSH prefer hybrid ML-KEM-768/X25519 key exchange and automatically fall back when a peer lacks support. SSH daemons no longer enable shell, exec, or SFTP services by default; explicitly enable only the services the application needs:

```erlang
ssh:daemon(Port, [{shell, {shell, start, []}},
                  {exec, erlang_eval},
                  {subsystems, [ssh_sftpd:subsystem_spec([])]}
                  | Options]).
```
