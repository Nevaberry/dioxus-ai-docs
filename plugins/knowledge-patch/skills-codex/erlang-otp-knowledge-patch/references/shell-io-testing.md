# Shell, I/O, and Testing

## Read standard input lazily

Since 28.0, standard input is read only when `io:get_line/2` or an equivalent
operation requests it, rather than being consumed greedily in advance. Remove
the `-noinput` workaround when it existed only to prevent unwanted reads.

## Choose cooked or raw `noshell` input

`noshell` remains cooked by default. Since 28.0, raw mode disables line
editing and output echo and lets an application receive keystrokes without
waiting for Enter:

```erlang
shell:start_interactive({noshell, raw}).
```

Use it only where the application owns terminal interaction and restores
expected terminal behavior on exit.

## Create local and BIF funs in the shell

Since 28.0, the normal `fun Name/Arity` form works for auto-imported BIFs and
shell-local functions:

```erlang
F = fun is_atom/1,
true = F(example).
```

## Close remote shells without stopping nodes

Since 28.1, closing a remote shell's input stream exits that shell without
terminating the remote node. The default tracer recognizes remote-shell use
and sends trace output to the remote group leader. Automation should distinguish
shell EOF from node shutdown and expect trace output on the remote terminal.

## Render terminal styles with `io_ansi`

Since 29.0, `io_ansi` formats or writes colors and styles using the local
terminfo database. Remote calls use the destination terminal's capabilities:

```erlang
io_ansi:fwrite([bold, red, "wrong answer: ", "~p~n"], [99]).
```

Use `io_ansi:format/2` to return the encoded sequence as a binary instead of
writing it.

## Update tests that compare map output

Since 28.1, Common Test prints map keys in the same order as
`maps:iterator(Map, ordered)`. Golden-output comparisons and tools consuming
rendered maps should expect that ordering.

## Traverse map comprehensions in abstract forms

Syntax Tools 4.0.2 in OTP 28.2 annotates map comprehensions and map generators
in Erlang abstract syntax. Tools that walk abstract forms must handle them
explicitly instead of assuming every comprehension or generator has list or
binary form.

## Preserve documentation in abstract output

Since 29.0, compiling with `to_abstr` retains source `-doc` attributes in the
generated `.abstr` file. BEAM-targeting language implementations and
documentation tools can consume that metadata without reconstructing it.

## Run documentation examples

Since 29.0, `ct_doctest` runs shell-style examples from Erlang module
documentation and documentation files, including expected failures. It can
compile example modules for the test shell and accepts pluggable parsers for
formats such as EDoc and AsciiDoc.

## Bound tar extraction

Since 29.0, pass `{max_size, Size}` to `erl_tar` extraction to cap the total
data written and protect the destination from being filled. Symlink validation
also accepts safe relative targets such as `dir/link -> ../file` that earlier
releases rejected. Preserve the size boundary while allowing those confined
links.

## Confine ZIP extraction

Since 29.0.4, `zip:unzip/1,2` and `zip:extract/1,2` reject relative archive
entries such as `../x/y` that would write outside the intended extraction
directory. Treat this rejection as required path confinement.
