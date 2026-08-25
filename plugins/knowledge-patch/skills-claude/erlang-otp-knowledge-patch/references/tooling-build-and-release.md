# Tooling, build, release, and platform behavior

## Native-code and dependency builds

### Windows source-tree native loading (since 28.1)

On Windows, NIFs and linked-in drivers can be loaded while Erlang runs in an Erlang source tree. Native-code build and test workflows can operate directly in that layout.

### Embedded third-party selection (since 28.5)

`--enable-use-embedded-3pp-alternatives` forces suitable external alternatives for affected embedded components; `--disable-use-embedded-3pp-alternatives` selects all bundled implementations. By default, bundled implementations are used except that an available OS `zlib` is preferred.

```text
./configure --enable-use-embedded-3pp-alternatives
```

Affected components are `zstd`, `zlib`, Ryu with STL, OpenSSL, and Tcl. Alternatives require `zstd` 1.5.6 or newer, `zlib` 1.2.5 or newer, C++17 for Ryu, and glibc 2.32 `strerrorname_np()` for Tcl. OpenSSL needs no external replacement because OTP uses its own MD5 implementation. Inspect `erlang:system_info(embedded_3pps)` at runtime to see which embedded implementations are active.

## Release construction and platform support

### Separate runtime, documentation, and tests (since 28.4)

`make release` places only runtime code in the release directory. Generate the other artifacts with `make release_docs` and `make release_tests`.

### Encrypted crash dumps (since 29.0)

Configure Erlang/OTP with `--enable-encrypted-crash-dumps` to build runtime support for encrypted crash dumps.

### End of 32-bit Windows builds (since 29.0)

OTP no longer provides a 32-bit Erlang/OTP build for Windows.

## Code loading, analysis, and documentation

### Safer default code path (since 29.0)

The current working directory (`.`) is last rather than first in the default code path. A local BEAM file does not shadow an OTP or application module unless the path is changed explicitly.

### Documentation tests (since 29.0)

`ct_doctest` runs shell-style examples from Erlang module documentation and documentation files, including expected failures. It can compile example modules for the test shell and accepts pluggable parsers for formats such as EDoc and AsciiDoc.

### Controlled `xref` failure (since 29.0.2)

When a BEAM file lacks debug information and has `moduledoc(false)`, `xref` returns an error instead of crashing. Callers must handle the error result.

## Supply-chain metadata

### OpenVEX statements (since 28.3)

OTP publishes per-release OpenVEX statements under `https://erlang.org/download/vex/`, for example `otp-28.openvex.json`. They identify vendor CVEs that do not affect Erlang/OTP so scanners can suppress false positives. The SPDX 2.3 source SBOM links to them through a security external reference.
