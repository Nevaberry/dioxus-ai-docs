---
name: erlang-otp-knowledge-patch
description: Erlang/OTP
version: 29.0.3
license: MIT
metadata:
  author: Nevaberry
---


# Erlang/OTP Knowledge Patch

Use this skill when writing, reviewing, upgrading, or troubleshooting Erlang/OTP code whose behavior may depend on recent language, runtime, standard-library, security, or build changes.

Check the installed OTP release and patch level before applying version-sensitive advice. Prefer the project's code, configuration, release artifacts, and tests when they demonstrate behavior more precisely than general guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/language-and-compiler.md](references/language-and-compiler.md) | Comprehensions, literals, types, native records, warnings, deprecations, abstract output |
| [references/runtime-and-data.md](references/runtime-and-data.md) | Priority messages, shell and I/O, regular expressions, arrays, maps, graphs, archives, ETF |
| [references/crypto-tls-and-ssh.md](references/crypto-tls-and-ssh.md) | Cryptography, TLS, certificates, OCSP, SSH, and SFTP |
| [references/networking-and-protocols.md](references/networking-and-protocols.md) | DNS, TCP, HTTP, FTP, sockets, SCTP, SNMP, Diameter, Megaco, and `epmd` |
| [references/tooling-build-and-release.md](references/tooling-build-and-release.md) | Native-code loading, build inputs, releases, SBOM/VEX, documentation tests, crash dumps, and `xref` |

## Breaking changes and migration priorities

### Treat native records as experimental runtime types

Native records use `-record #name{...}.` and are distinct runtime types rather than tagged tuples. Their definitions are private unless exported with `-export_record`; field-aware construction and matching from another module require that export.

Do not assume tuple-record representation, serialization, comparison, formatting, or analysis behavior applies. Keep the full OTP installation current because compiler, ERTS, Dialyzer, and formatting fixes have landed across patch releases.

```erlang
-record #vec{x = 0.0, y = 0.0}.
-export_record([vec]).

make_vec(X, Y) -> #vec{x = X, y = Y}.
```

### Audit comprehension qualifiers

A match used as a comprehension qualifier is a compile error by default. If assignment semantics are intentional, enable `compr_assign`; the assignment then behaves like a strict one-element generator.

Use strict generators when a mismatch should fail rather than skip:

```erlang
[X || {ok, X} <:- Results].
```

Use `&&` to zip generators in parallel. It does not produce a Cartesian product.

### Address compiler warnings deliberately

Old-style `catch Expr` now warns by default. Prefer targeted `try ... catch` handling; use `nowarn_deprecated_catch` only as a migration aid.

Also review default warnings for variables exported from subexpressions and aliases that unify constructors. The opt-in obsolete-boolean-operator warning helps migrate eager `and` and `or` to short-circuit operators or guard syntax.

Old-style guard type tests, `odbc`, `ftp`, and `ct_ftp` are deprecated for removal. Avoid new dependencies on them.

### Do not carry serialized arrays across the representation change

The `array` module gained substantial new construction, slicing, concatenation, traversal, and map-fold APIs, but its internal representation changed. Recreate or migrate array data rather than decoding array terms serialized by an earlier runtime.

### Recheck code-path assumptions

The current working directory is last in the default code path. A local BEAM file no longer shadows an OTP or application module unless the path is changed explicitly.

### Configure SSH daemon services explicitly

`ssh:daemon/2` does not enable shell, exec, or SFTP services automatically. Opt in only to required services:

```erlang
ssh:daemon(Port, [
    {shell, {shell, start, []}},
    {exec, erlang_eval},
    {subsystems, [ssh_sftpd:subsystem_spec([])]}
    | Options
]).
```

### Require SANs in certificates

Hostname validation no longer falls back to a certificate subject common name. Certificates need a matching subject alternative name, and error handling may need to distinguish subject-name from subject-alternative-name constraint failures.

Keep OCSP responses within the enforced size limit and expect expired responder certificates, malformed chains, policy-tree explosions, and chain cycles to be rejected.

### Preserve confinement at protocol and archive boundaries

Do not depend on redirects forwarding credentials to a changed host or port, FTP passive replies redirecting data connections, SFTP revealing paths outside its root, or ZIP entries escaping their extraction directory. These behaviors are rejected.

Use `{max_size, Size}` for bounded tar extraction. SFTP clients must split reads larger than the server limit.

## High-value language features

### Strict, zipped, and multi-valued comprehensions

Strict list/map generators use `<:-`; strict binary generators use `<:=`. Join generators with `&&` to consume inputs in parallel. A comprehension may also emit several comma-separated values for each iteration.

```erlang
Pairs = [{X, Y} || X <- [1, 2] && Y <- [a, b]],
Signed = [I, -I || I <- lists:seq(1, 3)].
```

### Precise guards and application syntax

`is_integer(Term, Lower, Upper)` checks both integer type and inclusive bounds without admitting floats. Function application is left associative, so `f(X)(Y)` applies the result of `f(X)` to `Y`.

### Based floating-point literals and nominal types

Based floats can express non-decimal values and based exponents. Dialyzer `-nominal` declarations keep structurally identical domain types distinct in specifications.

## Runtime and data quick reference

### Priority messages

Create a priority-capable alias and send with the `priority` option. Sending through the same alias without that option remains ordinary, and `unalias/1` revokes the capability.

```erlang
PrioAlias = alias([priority]),
erlang:send(PrioAlias, Message, [priority]).
```

Priority exits use `exit(Alias, Reason, [priority])`; link- and monitor-generated signals require the corresponding priority option when the link or monitor is created.

### Memory and persistent terms

`erlang:hibernate/0` minimizes the calling process while it waits without discarding its call stack. `persistent_term:put_new/2` is quick and idempotent when the same key/value pair already exists, but raises `badarg` for a different existing value.

### Regular expressions

PCRE2 makes pattern validation stricter and can change Unicode-property and branch-reset behavior. Do not persist or directly transfer the internal value from `re:compile/2`; use the supported export/import facility when moving compiled expressions between node instances.

### Deterministic-within-a-map iteration

Map order is still undefined, but standard keys, values, list conversion, iterators, and comprehensions agree on the order chosen for a given map. Do not treat that order as sorted or stable across maps or runtime conditions.

### Functional graphs and terminal styling

The `graph` module returns a new persistent graph from each modifying operation. `io_ansi` uses local terminal capabilities to format colors and styles; remote writes use the destination terminal's capabilities.

## Cryptography and networking quick reference

### Post-quantum algorithms

With a suitable OpenSSL build, the crypto stack supports ML-DSA and ML-KEM, while TLS and SSH support hybrid post-quantum groups. The hybrid TLS and SSH choices are preferred defaults with fallback for peers that lack support.

Do not assume the backend supports every EdDH or EdDSA operation. Catch the structured `{notsup, Info, Description}` error where absence is an expected deployment condition.

### Bound retries and batch socket work

`httpc` performs one retry by default after `Retry-After`, then returns the error response. Configure `{autoretry, Timeout}` or implement an application retry policy rather than assuming unbounded retries.

The socket implementation exposes batched receive/send operations corresponding to `recvmmsg()` and `sendmmsg()`.

### Check patch-level protocol hardening

Security-sensitive deployments should review patch-level changes to `epmd`, TLS handshakes and tickets, SSH Diffie-Hellman and packet alignment, certificate paths, ETF decoding, crypto inputs, Diameter AVPs, Megaco names, and archive extraction.

If localhost-bound `epmd` stops working after the denial-of-service mitigation, install the follow-up ERTS patch that restores loopback binding.

## Build, release, and test quick reference

### Split release artifacts

`make release` produces runtime code. Build documentation and tests separately with `make release_docs` and `make release_tests`.

### Select embedded third-party implementations consciously

The configure switches for embedded third-party alternatives control bundled versus suitable external implementations. Inspect `erlang:system_info(embedded_3pps)` at runtime to see what is in use.

### Keep documentation executable and preserved

`ct_doctest` runs shell-style examples, including expected failures, from module documentation and documentation files. Compiling with `to_abstr` preserves source `-doc` attributes for downstream tooling.

### Use release security metadata

Per-release OpenVEX statements identify vendor CVEs that do not affect Erlang/OTP, and the source SBOM links to them. Feed those statements to vulnerability tooling rather than maintaining local suppressions without provenance.

## Applying this patch

1. Identify the exact OTP and application patch versions in the deployed artifact.
2. Start with breaking changes, deprecations, security boundaries, and changed defaults.
3. Open the topic reference that matches the code or operational surface being changed.
4. Distinguish full-OTP upgrades from application-only patching; honor stated cross-application dependencies.
5. Recompile native code and BEAM artifacts where representation, compiler, or platform behavior changed.
6. Exercise malformed-input, legacy-peer, and confinement tests for externally reachable services.
7. Verify runtime behavior on every supported OS and crypto backend rather than assuming optional capabilities exist.
