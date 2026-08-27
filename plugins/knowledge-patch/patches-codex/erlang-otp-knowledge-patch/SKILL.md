---
name: erlang-otp-knowledge-patch
description: Erlang/OTP
version: "29.0.3"
license: MIT
metadata:
  author: Nevaberry
---


# Erlang/OTP Knowledge Patch

Use this skill when upgrading Erlang/OTP, changing Erlang language or runtime
code, operating BEAM services, or configuring OTP networking, cryptography,
shells, builds, and test tooling. Read the relevant topic reference before
depending on historical defaults, serialized runtime terms, protocol behavior,
or application-level patch compatibility.

## Reference index

| Reference | Topics |
| --- | --- |
| [`build-operations.md`](references/build-operations.md) | Release artifacts, embedded dependencies, runtime flags, platform support, crash dumps, and vulnerability metadata |
| [`crypto-tls-certificates.md`](references/crypto-tls-certificates.md) | TLS and certificate validation, post-quantum algorithms, OCSP, crypto failures, and hardening |
| [`language-runtime.md`](references/language-runtime.md) | Comprehensions, types, compiler diagnostics, runtime APIs, collections, regular expressions, and serialization |
| [`networking-services.md`](references/networking-services.md) | DNS, TCP and sockets, HTTP, SSH/SFTP/FTP, distribution, `epmd`, Diameter, Megaco, and SNMP |
| [`shell-io-testing.md`](references/shell-io-testing.md) | Shell modes, standard input, terminal styling, Common Test, documentation tests, abstract forms, and tar/ZIP extraction |

## Upgrade-critical changes

### Replace serialized `array` terms

OTP 29 changes the internal `array` representation. Do not carry values
serialized by `term_to_binary/1` on an earlier release across the upgrade;
rebuild them from an application-owned format.

### Require SANs in certificates

Hostname validation no longer falls back to a certificate subject common name.
Certificates must have a matching subject alternative name. Error handling may
also see separate subject-name and subject-alternative-name constraint errors.

### Harden extraction boundaries

Use `erl_tar`'s `{max_size, Size}` option to cap extracted data. Current ZIP
extraction rejects relative entries such as `../x/y` that escape the target
directory; treat rejection as a security boundary, not an archive compatibility
problem.

### Audit default code loading

The current directory is last, rather than first, in the default code path.
Local BEAM files no longer shadow OTP or application modules unless the code
path is changed explicitly.

### Opt in to SSH daemon services

`ssh:daemon/2` no longer enables shell, exec, or SFTP by default:

```erlang
ssh:daemon(Port, [
    {shell, {shell, start, []}},
    {exec, erlang_eval},
    {subsystems, [ssh_sftpd:subsystem_spec([])]}
    | Options
]).
```

Enable only the services the daemon needs.

### Check ordered inputs

`gb_sets:from_ordset/1` and `gb_trees:from_orddict/1` now reject unordered
input with `badarg` instead of constructing invalid data structures.

### Account for bounded HTTP retries

After a `Retry-After` response, `httpc:request/4,5` retries once by default and
then returns the error response. Configure `{autoretry, Timeout}` or implement
an application retry policy when one retry is insufficient.

## Deprecations and diagnostics

### Migrate old-style `catch`

The warning for `catch Expr` is enabled by default. Prefer targeted
`try ... catch` clauses. Use `nowarn_deprecated_catch` only as a temporary
module-level migration escape hatch.

### Prepare for removals

Old-style guard type tests such as `integer` and `atom`, the `odbc`
application, and the `ftp` and `ct_ftp` modules are deprecated and scheduled
for removal in OTP 30.

### Review new compiler warnings

The compiler warns by default for variables exported from subexpressions and
match aliases that unify constructors. Temporary suppressions are
`nowarn_export_var_subexpr` and `nowarn_match_alias_pats`.

Enable `warn_obsolete_bool_op` to find eager `and`/`or` expressions that
should generally use `andalso`/`orelse`, or `,`/`;` in guards.

### Find unsafe calls

Functions may have `-unsafe` attributes, and calls to always-unsafe OTP
functions warn by default. Enable `warn_possibly_unsafe_function` for
conditional cases such as atom creation. The `xref` analyses
`unsafe_function_calls`, `undocumented_function_calls`, and
`private_function_calls` support wider audits.

## Language quick reference

### Strict generators

Use `<:-` for strict list and map generators and `<:=` for strict binary
generators. A pattern mismatch raises instead of silently skipping the value.

```erlang
[X || {ok, X} <:- [{ok, 1}, error, {ok, 3}]].
```

### Zip generators

Join generators with `&&` to consume their inputs in parallel rather than
forming a Cartesian product:

```erlang
[{X, Y} || X <- [1, 2] && Y <- [a, b]].
```

Any number of list, binary, or map generators can participate, alongside
ordinary generators and filters.

### Comprehension assignment

A match used as a qualifier is a compile error by default. Enable
`compr_assign` to make `P = E` behave like the strict generator `P <-:- [E]`:

```erlang
-feature(compr_assign, enable).
```

Comprehensions can also emit multiple comma-separated values per iteration,
such as `[I, -I || I <- lists:seq(1, 3)]`.

### Native records

Native records are experimental runtime types, not tagged tuples:

```erlang
-record #vec{x = 0.0, y = 0.0}.
-export_record([vec]).
```

Definitions are private by default. Other modules need `-export_record` for
construction or field-aware matches, though a field-free match is permitted.
Because early compiler, runtime, Dialyzer, and formatting defects were fixed in
29.0.1 and 29.0.2, update the full installation before experimenting with them.

### Bounded integer guards

`is_integer(Term, LowerBound, UpperBound)` succeeds only when all three
arguments are integers and the term is within the inclusive bounds. It avoids
range guards that accidentally accept floats.

### Nominal types

Use `-nominal` when structurally identical types must remain distinct in
Dialyzer specifications:

```erlang
-nominal meter() :: integer().
-nominal foot() :: integer().
```

A nominal type remains compatible with a non-opaque, non-nominal type of the
same structure.

## Runtime quick reference

### Priority signals

Create a priority-capable alias and use the `priority` send option:

```erlang
PrioAlias = alias([priority]),
erlang:send(PrioAlias, Message, [priority]).
```

Priority messages go ahead of ordinary messages while signal order is
preserved. Sending through the alias without the option remains ordinary, and
`unalias/1` revokes the capability. Priority exits use
`exit(Alias, Reason, [priority])`; event-generated links and monitors opt in
through `erlang:link/2` and `erlang:monitor/3`.

### Hibernate without discarding the stack

`erlang:hibernate/0` minimizes the calling process while it waits for the next
message but, unlike `erlang:hibernate/3`, preserves the call stack.

### Insert persistent terms idempotently

`persistent_term:put_new/2` returns quickly when the same key and value already
exist. It raises `badarg` when the key exists with a different value.

### Use consistent map iteration carefully

Standard map traversal functions now return a given map's elements in a
consistent order, including keys, values, list conversion, default iterators,
and comprehensions. The order is still undefined, unsorted, and not stable
across maps or releases.

## Security and protocol quick reference

### Treat patch hardening as compatibility-sensitive

Recent patch fixes tighten certificate paths, TLS handshakes and tickets, SSH
Diffie-Hellman and packet validation, SFTP/FTP confinement, ETF decoding,
archive extraction, `epmd`, Diameter, Megaco, and crypto input validation.
Retest negative cases and error matching instead of relying on former silent
disconnects, crashes, or permissive behavior.

### Handle unsupported crypto structurally

When EdDH or EdDSA is unavailable, `crypto:compute_key/4` and
`crypto:generate_key/2,3` raise:

```erlang
error:{notsup, Info, Description}
```

Catch that tuple when fallback is valid; do not match an unstructured failure.

### Recheck post-quantum negotiation

Hybrid ML-KEM groups and ML-DSA/SLH-DSA signatures are integrated into TLS,
SSH, `public_key`, and `crypto`. They become preferred defaults where
supported, while retaining fallback for peers that cannot negotiate them.
Confirm the linked OpenSSL capabilities and the certificate/key material.

## Further guidance

Open the reference that matches the task before changing production behavior.
The references preserve exact API names, flags, dependency constraints,
protocol limits, and migration consequences that this quick reference omits.
