# Runtime and data

## Processes, messages, and memory

### Priority messages (since 28.0)

A receiver opts in with `alias([priority])`. A sender using that alias with the `priority` option places the message ahead of ordinary messages while preserving signal order. Sending through the alias without the option remains ordinary, and `unalias/1` revokes the capability.

```erlang
PrioAlias = alias([priority]),
erlang:send(PrioAlias, Message, [priority]).
```

Use `exit(PrioAlias, Reason, [priority])` for a priority exit signal. For event-generated link and monitor signals, pass `priority` to `erlang:link/2` or `erlang:monitor/3` when creating them.

### Stack-preserving hibernation (since 28.0)

`erlang:hibernate/0` minimizes the calling process's memory while it waits for the next message. Unlike `erlang:hibernate/3`, it does not discard the call stack.

### Idempotent persistent-term insertion (since 28.4)

`persistent_term:put_new/2` returns quickly when the same key and value already exist. It raises `badarg` when the key exists with a different value.

```erlang
persistent_term:put_new(config, Config).
```

### Selecting `MADV_DONTNEED` (since 28.1)

The emulator flag `+Mumadtn <bool>` selects `MADV_DONTNEED` instead of `MADV_FREE`.

```text
erl +Mumadtn true
```

## Shell and terminal I/O

### Lazy standard input (since 28.0)

Standard input is read only when `io:get_line/2` or an equivalent operation requests it. The `-noinput` workaround for unwanted greedy reads is no longer necessary.

### Raw `noshell` mode (since 28.0)

`noshell` remains cooked by default. Raw mode disables line editing and output echo and allows keystroke reads without waiting for Enter.

```erlang
shell:start_interactive({noshell, raw}).
```

### Remote-shell lifecycle and tracing (since 28.1)

A remote shell can exit by closing its input stream without terminating the remote node. The default tracer recognizes remote-shell use and directs trace output to the remote group leader.

### Terminal styling (since 29.0)

`io_ansi` formats or writes terminal colors and styles using the local terminfo database; remote calls use the destination terminal's capabilities. `io_ansi:format/2` returns the encoded sequence as a binary instead of writing it.

```erlang
io_ansi:fwrite([bold, red, "wrong answer: ", "~p~n"], [99]).
```

## Regular expressions

### PCRE2 compatibility (since 28.0)

The `re` module uses PCRE2. Validation is stricter, so invalid escapes such as `\M`, `\i`, `\B`, or `\8` can raise `badarg`. Newer Unicode property data can change property matches, and branch-reset groups can change `re:split/3` results.

The internal value returned by `re:compile/2` is not reusable across nodes or OTP versions. Retest patterns and any code that persisted or transferred those values.

### Transferable compiled expressions (since 28.1)

Use the supported `re` export/import facility to transfer compiled regular expressions safely between Erlang node instances. Do not directly transfer the compiled pattern's internal value.

## Collections and iteration

### Ordered Common Test rendering (since 28.1)

Common Test prints map keys in the same order as `maps:iterator(Map, ordered)`. Update golden-output comparisons and rendered-map consumers accordingly.

### Expanded arrays and serialization break (since 29.0)

`array` adds `prepend/2`, `append/2`, `concat/1,2`, `slice/3`, `shift/2`, `from/2,3`, index-bounded traversal variants such as `foldl/5`, and map-fold families such as `mapfoldl/3` and `sparse_mapfoldr/5`.

The internal representation changed. Array terms serialized with `term_to_binary/1` on an earlier OTP release are incompatible and must not be carried across the upgrade unchanged.

### Consistent map iteration (since 29.0)

Map order remains undefined, but all standard forms now produce a given map's elements in the same order. This aligns `maps:keys/1`, `maps:values/1`, `maps:to_list/1`, default iterators, and map comprehensions without promising sorted or stable order.

### Checked ordered inputs (since 29.0)

`gb_sets:from_ordset/1` and `gb_trees:from_orddict/1` reject unordered input instead of creating invalid structures. For example, `gb_sets:from_ordset([3,2,1])` raises `badarg` with reason `not_ordset`.

### Persistent functional graphs (since 29.0)

`graph` is a functional counterpart to `digraph` and `digraph_utils`. Each modifying operation returns a new graph and leaves earlier versions usable.

```erlang
G0 = graph:new(),
G1 = graph:add_vertex(G0, a),
G2 = graph:add_vertex(G1, b),
G3 = graph:add_edge(G2, a, b).
```

## Archives and external terms

### Bounded tar extraction (since 29.0)

Pass `{max_size, Size}` to `erl_tar` extraction to cap total extracted data. Symlink validation accepts safe relative targets such as `dir/link -> ../file` that older releases rejected.

### External Term Format hardening (since 29.0.4)

`binary_to_term` no longer corrupts the heap for an invalid tuple arity of 2^31 or larger, and crafted ETF payloads no longer crash the runtime. Treat external terms as untrusted input and deploy the corrected runtime where decoding is exposed.

### ZIP path confinement (since 29.0.4)

`zip:unzip/1,2` and `zip:extract/1,2` reject relative entries such as `../x/y` that would write outside the intended extraction directory.
