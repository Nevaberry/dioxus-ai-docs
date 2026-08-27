# Erlang/OTP Runtime and Libraries

## Write Erlang source

### Keep documentation beside code

OTP source documentation uses Markdown in `-doc` attributes beside the spec
and implementation, rendered by ExDoc rather than maintained as separate
Erl_Docgen XML (`otp-27`):

```erlang
-doc """
Returns `N` copies of `Elem`.
""".
-spec duplicate(N, Elem) -> [Elem].
```

### Use multiline strings and sigils

Triple quotes delimit multiline strings. The indentation before the closing
delimiter is removed from every content line, deeper indentation is preserved,
and quotes and backslashes inside are literal (`otp-27`):

```erlang
Text = """
       first line
         indented line
       """.
```

String sigils choose representation and escaping:

- `~b` is an escaped UTF-8 binary; `~B` is an unescaped UTF-8 binary.
- Bare `~` behaves like `~b` inline and `~B` with triple quotes.
- `~s` and `~S` produce list strings with and without escaping.

```erlang
Utf8 = ~B[Greek: Γνῶθι σαυτόν],
Tabbed = ~b"abc\txyz".
```

### Account for language feature changes

The `maybe_expr` feature is enabled by default in `otp-27`; write the atom as
`'maybe'`. Disable the feature only when necessary with
`erlc -disable-feature maybe_expr` or `-feature(maybe_expr, disable)`.

OTP `otp-28` adds arbitrary-base floating-point literals. A second `#`
introduces the exponent marker:

```erlang
2#0.011.       %% 0.375
16#0.011#e5.  %% 4352.0
```

## Build comprehensions

Strict generators from `otp-28` fail on an input that does not match their
pattern instead of silently skipping it. Use `<:-` for list and map generators
and `<:=` for binary generators; keep the relaxed operators when skipping is
intentional.

```erlang
[X || {ok, X} <:- [{ok, 1}, {ok, 2}]].
```

Join generators with `&&` to zip them in parallel rather than form a Cartesian
product. List, binary, and map generators may be combined with other
generators and filters:

```erlang
[{X, Y} || X <- [1, 2] && Y <- [a, b]].
%% [{1,a},{2,b}]
```

OTP `otp-29` adds two more forms:

- A list comprehension may place multiple expressions before `||`, emitting
  several values per iteration without temporary lists and flattening:

  ```erlang
  [I, -I || I <- lists:seq(1, 5)].
  %% [1,-1,2,-2,3,-3,4,-4,5,-5]
  ```

- With experimental `compr_assign` enabled, `Pattern = Expr` in the qualifier
  list binds a computed value for later filters or output. It has the strict
  semantics of `Pattern <-:- [Expr]`. Without the feature, a match in a
  qualifier is rejected instead of treated as a Boolean filter.

  ```erlang
  -feature(compr_assign, enable).

  selected(List) ->
      [H || E <- List, H = erlang:phash2(E), H rem 10 =:= 0].
  ```

## Work with processes and messages

### Label unregistered processes

`proc_lib:set_label/1` assigns an arbitrary term to the current process, and
`proc_lib:get_label/1` reads a process label. Labels appear in shell `i/0`,
Observer, and crash dumps (`otp-27`).

### Send priority signals

A receiving process must opt in by creating a priority alias. Send to that
alias with `erlang:send/3` and the `priority` option. Priority messages move
ahead of ordinary messages while preserving signal ordering (`otp-28`):

```erlang
PrioAlias = alias([priority]),
erlang:send(PrioAlias, urgent, [priority]),
true = unalias(PrioAlias).
```

Use `exit/3` for priority exit signals. Pass `priority` to `erlang:link/2` or
`erlang:monitor/3` to prioritize link- or monitor-generated signals.

### Hibernate without unwinding

`erlang:hibernate/0` reduces the current process's memory while it waits for
the next message and preserves the current call stack. This differs from
`erlang:hibernate/3`, which starts from a specified MFA (`otp-28`).

```erlang
erlang:hibernate().
```

## Use the shell and standard input

Standard input is lazy in `otp-28`: it is read only when an operation such as
`io:get_line/2` asks for it. Programs no longer need `-noinput` merely to stop
eager consumption.

`noshell` mode remains cooked by default, but a custom shell can select raw
mode for keystrokes without Enter, line editing, or terminal echo:

```erlang
shell:start_interactive({noshell, raw}),
Chars = io:get_chars("", 1024).
```

The shell accepts `fun Name/Arity` for auto-imported BIFs and shell-local
functions, including a local function defined after the fun value was made:

```erlang
1> F = fun id/1.
2> id(X) -> X.
3> F(42).
42
```

## Encode JSON

STDLIB's `json` module provides `json:decode/1` and `json:encode/1` (`otp-27`).
Decoded object keys are binaries by default, avoiding unbounded atom creation.

```erlang
Map = json:decode(<<"{\"ok\":true}">>),
Json = json:encode(Map).
```

For custom behavior, `json:decode/3` accepts callbacks such as `object_push`.
`json:encode/2` accepts a recursive custom encoder that can delegate to
`json:encode_map/2` and `json:encode_value/2`.

## Schedule work

The `timer` fun APIs accept funs directly: `timer:apply_after/2,3`, the
`apply_interval/*` family, and the `apply_repeatedly/*` family (`otp-27`). For
timers that may survive hot-code upgrades, pass a remote fun and its arguments:

```erlang
timer:apply_after(1000, fun io:put_chars/1, ["done\n"]).
```

## Work with collections and storage

### Sets, trees, arrays, and maps

In `otp-27`, `sets`, `gb_sets`, and `ordsets` each add `is_equal/2`, `map/2`,
and `filtermap/2`. Compare sets with `is_equal/2`, not term equality, because
equal sets may have different internal representations.

OTP `otp-29` validates the ordering passed to `gb_sets:from_ordset/1` and
`gb_trees:from_orddict/1`, raising `badarg` rather than constructing corrupt
data. Use `gb_trees:from_list/1` when input is not already ordered.

The `array` module adds `concat/1,2`, `slice/3`, `shift/2`, fun-driven
constructors `from/2,3`, index-bounded traversal forms such as `foldl/5`, and
the `mapfold` families, including `mapfoldl/3` and `sparse_mapfoldr/5`.

Map key order is still undefined, but in `otp-29` all traversal mechanisms for
one map produce the same order, including `maps:keys/1`, `maps:to_list/1`, map
comprehensions, and iterators.

### Traverse and update ETS efficiently

`ets:first_lookup/1`, `next_lookup/2`, `last_lookup/1`, and `prev_lookup/2`
combine key traversal with object lookup (`otp-27`). `ets:update_element/4`
adds a default object for a missing key:

```erlang
ets:update_element(Tab, Key, {2, Value}, {Key, Default}).
```

### Keep immutable graph versions

The `graph` module in `otp-29` is the immutable counterpart to `digraph` and
`digraph_utils`: each modifying operation returns a new graph, so prior
versions remain usable.

```erlang
G0 = graph:new(),
G1 = graph:add_vertex(G0, a),
G2 = graph:add_vertex(G1, b),
G3 = graph:add_edge(G2, a, b).
```

## Trace, profile, and measure coverage

The unified `tprof` API in `otp-27` profiles call count, time, or allocation:

```erlang
tprof:profile(M, F, Args,
              #{type => call_count | call_time | call_memory}).
```

Call counting covers all processes. Time and memory cover the caller and the
processes it spawns.

Kernel's `trace` module creates independent sessions with separate tracer,
process, and function configuration. Use `trace:session_create/3`,
`trace:process/4`, `trace:function/4`, and `trace:session_destroy/1`. Legacy
`erlang:trace/3` clients still share one global session.

On JIT-capable systems, Cover automatically uses low-overhead native coverage.
Start coverage before regular module execution with
`erl +JPcover function_counters`, and query it using
`code:get_coverage(function, Module)`.

## Harden archives, TLS, and SSH

### Bound archive extraction

Pass `{max_size, Size}` to `erl_tar` extraction to cap total extracted data
and protect a destination from disk-filling archives (`otp-29`).

### Migrate application archives

Putting application archives on the code path is deprecated in `otp-27`, as
are archive handling in `erl_prim_loader`, archive lookup through
`code:lib_dir/2`, and `-code_path_choice`. Strict code-path choice is now the
default; archive users can temporarily select `-code_path_choice relaxed`.

A single archive embedded in an escript remains supported. Access its data
files through `escript:extract/2` for forward compatibility.

### Validate OCSP stapling

Enable SSL client validation of a server's stapled OCSP response with
`{stapling, staple}`, normally alongside trusted CA certificates (`otp-27`):

```erlang
ssl:connect(Host, 443,
            [{cacerts, public_key:cacerts_get()}, {stapling, staple}]).
```

### Apply stronger defaults deliberately

In `otp-29`, SSL and SSH prefer hybrid ML-KEM-768/X25519 key exchange and
automatically fall back for older peers. SSH daemons no longer enable shell,
exec, or SFTP by default; opt into only the required services:

```erlang
ssh:daemon(Port, [{shell, {shell, start, []}},
                  {exec, erlang_eval},
                  {subsystems, [ssh_sftpd:subsystem_spec([])]}
                  | Options]).
```

## Adopt OTP 29 language and safety features

### Treat native records as experimental

`-record #name{}` declares a runtime-native record in `otp-29`. Construction,
update, matching, and field access use familiar record syntax. Records are
module-private unless listed in `-export_record`; external references use
`#module:name{}`. The feature is experimental and may break between releases.

```erlang
-module(geom).
-export([make_vec/2]).
-export_record([vec]).
-record #vec{x=0.0, y=0.0}.

make_vec(X, Y) -> #vec{x=X, y=Y}.
```

### Audit unsafe calls and code-path assumptions

The compiler warns for functions marked always unsafe. Enable
`erlc +warn_possibly_unsafe_function` to diagnose conditionally dangerous
calls such as atom creation. Xref understands `-unsafe` and adds the
`unsafe_function_calls`, `undocumented_function_calls`, and
`private_function_calls` analyses:

```erlang
xref:analyze(S, unsafe_function_calls).
```

The code server now puts the current working directory last, so a local BEAM
file cannot shadow an OTP or application module with the same name.

### Update warnings and guards

Old-style `catch Expr` warns by default in `otp-29`. In `otp-28`, opt into the
same warning with `warn_deprecated_catch`, and suppress a project setting for
one module with `-compile(nowarn_deprecated_catch)`. Prefer `try ... catch` to
avoid unintentionally hiding runtime errors:

```erlang
-compile(warn_deprecated_catch).

Result = try work()
         catch
             throw:Reason -> {error, Reason}
         end.
```

`warn_obsolete_bool_op` opts into warnings for `and` and `or`. The compiler
also warns when a variable is bound inside a subexpression then used later, or
when a match confusingly unifies constructors such as `{a,B} = {Y,Z}`. Move
the binding outward and write the latter as `{a=Y,B=Z}`.

Use `is_integer/3` to verify both integer type and bounds without accidentally
accepting floats:

```erlang
is_digit(C) -> is_integer(C, $0, $9).
```

### Produce ANSI terminal output

The `io_ansi` module builds styled terminal content. `format/2` returns a
binary containing ANSI sequences, while `fwrite/2` writes it (`otp-29`):

```erlang
io_ansi:fwrite([bold, red, "wrong answer: ", "~p\n"], [99]).
```

## Recompile regular expressions

The `re` module uses PCRE2 in `otp-28`. Its stricter parser rejects formerly
tolerated invalid escapes, while changed Unicode property data and
branch-reset behavior can alter matches and splits. The internal result of
`re:compile/2` changed and must not be reused across nodes or OTP versions.
