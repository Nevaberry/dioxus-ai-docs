# Build and Operations

## Produce release artifacts separately

Since 28.4, `make release` places only runtime code in the release directory.
Generate the other deliverables explicitly:

```text
make release_docs
make release_tests
```

Update packaging and CI jobs that assumed documentation or tests were part of
the runtime release tree.

## Select embedded third-party implementations

Since 28.5, configure the affected embedded components with:

```text
./configure --enable-use-embedded-3pp-alternatives
./configure --disable-use-embedded-3pp-alternatives
```

The enable form forces suitable external alternatives; the disable form
selects every bundled implementation. By default, bundled implementations are
used except that an available OS `zlib` is preferred.

The affected components and requirements are:

- `zstd` 1.5.6 or newer;
- `zlib` 1.2.5 or newer;
- Ryu with STL and a C++17 compiler;
- Tcl with glibc 2.32's `strerrorname_np()`;
- OpenSSL, for which no external replacement is needed because OTP uses its
  own MD5 implementation.

At runtime, `erlang:system_info(embedded_3pps)` returns a map describing the
embedded implementations in use. Use it to verify the built artifact rather
than inferring the result from the build host.

## Audit code-path precedence

In 29.0, the current working directory (`.`) moved from the first to the last
entry in the default code path. A local BEAM file therefore no longer shadows
an OTP or application module unless the path is changed explicitly. Remove
tests and launch scripts that depended on implicit local precedence.

## Tune memory reclamation

Since 28.1, `+Mumadtn <bool>` selects `MADV_DONTNEED` instead of
`MADV_FREE`:

```text
erl +Mumadtn true
```

Choose deliberately when operating-system reclamation behavior or memory
accounting requires it.

## Build encrypted crash-dump support

Since 29.0, pass `--enable-encrypted-crash-dumps` while configuring Erlang/OTP
to build the runtime with encrypted-crash-dump support. Ensure the operational
dump-handling path matches the resulting build capability.

## Account for platform support changes

OTP 29.0 no longer supplies a 32-bit Windows build. Migrate affected deployment
and test lanes to a supported architecture.

Since 28.1, Windows can load NIFs and linked-in drivers while Erlang runs in an
Erlang source tree. Native-code build and test workflows no longer need to
relocate the runtime solely to enable loading in that layout.

## Feed OpenVEX data to scanners

Since 28.3, OTP publishes per-release OpenVEX statements under
`https://erlang.org/download/vex/`, for example `otp-28.openvex.json`. These
statements record published CVEs that do not affect Erlang/OTP so scanners can
avoid false positives. The SPDX 2.3 source SBOM links to the statement through
a security external reference.
