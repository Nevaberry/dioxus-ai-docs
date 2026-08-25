# Languages, Toolchains, and Packaging Workflows

## Contents

- Java and JVM tooling
- JavaScript and web stacks
- Python and Django
- Rust, C, C++, and LLVM
- Build systems and packaging automation
- Other language toolchains

## Java and JVM tooling

### Java libraries no longer guarantee a runtime (41)

Java library RPMs no longer have to require a JRE. Applications and images
that execute Java must depend on or install a suitable runtime explicitly
instead of relying on a library dependency to pull one in.

### Legacy Fedora OpenJDKs move to Temurin (42)

Fedora retires `java-1.8.0-openjdk`, `java-11-openjdk`, and
`java-17-openjdk`. When those LTS releases are required, install
`adoptium-temurin-java-repository` and select `temurin-8-jdk` or
`temurin-8-jre` through `temurin-21-jdk` or `temurin-21-jre` as appropriate.

### Java 25 is preferred without a single system JDK (43)

`java-25-openjdk` is the preferred JDK, but Fedora packages no longer assume
one universal system JDK. Packages that failed the Java 25 mass rebuild could
explicitly remain on `java-21-openjdk` for this release.

### `java-21-openjdk` is removed (44)

The Fedora Java 21 OpenJDK packages are removed one release earlier than
previously planned. Do not carry the prior release's Java 21 fallback into
dependencies or deployment automation.

### Maven 4 is parallel-installable (43)

Apache Maven 4 is available alongside Maven 3 rather than replacing it. Builds
can select the new major line explicitly while keeping Maven 3 installed.

## JavaScript and web stacks

### Node.js 20 compatibility path (41)

Node.js 22 is the default. Applications not ready for it must depend on
`nodejs20` and invoke `/usr/bin/node20` rather than relying on
`/usr/bin/node`.

### Shared Node.js modules move to a stream-neutral path (43)

Fedora provides a shared, stream-agnostic installation location for Node.js
modules. Packaging and applications must not hard-code the former
stream-specific `node_modules` path.

### Node.js command symlinks use swappable subpackages (44)

Swappable packages such as `nodejsXX-bin` and `nodejsXX-npm-bin` manage
`/usr/bin/node`, `/usr/bin/npm`, and related command links. Stop managing these
links manually and depend on the appropriate subpackage.

### PHP is 64-bit only (41)

Fedora no longer builds PHP for 32-bit architectures. Packages and deployments
that require PHP must target a supported 64-bit architecture.

### Django major versions use parallel package names (42)

The default Django 5.1 stack is in unsuffixed `python3-django`. Other supported
major lines use names such as `python3-django5`; versioned package names omit
the minor version intentionally.

### Django 6 becomes the default stack (44)

The unversioned Fedora Django stack moves from the 5.x major line to 6.x.
Applications using the distribution package must follow the Django 6 migration
path.

## Python packaging and runtime

### Setuptools removes `setup.py test` (42)

Setuptools 74 no longer implements `setup.py test`. Declare test dependencies
through Fedora packaging mechanisms and invoke `pytest`, `unittest`, or
another runner directly.

### `python-pytest-runner` is deprecated (42)

Remove `pytest-runner` from `setup_requires` and remove testing requirements
from `tests_require`. Declare test dependencies normally and invoke `pytest`
directly or through tox.

### Python 3.8 is retired (42)

The `python3.8` compatibility package is removed without replacement.
`python3.6` remains available for developers who target RHEL 8, but it is not
a substitute runtime for Fedora applications requiring 3.8.

### NumPy 2 is the system stack (42)

The distribution NumPy stack moves from 1.26 to 2.2.4. Port downstream
packages and applications with the NumPy 2 migration guidance rather than
assuming Fedora still supplies the 1.x API and ABI.

### Legacy Python build macros are deprecated (43)

`%py3_build`, `%py3_install`, `%py3_build_wheel`, and their `%py_*` variants
are deprecated with the `setup.py` build path. Use `pyproject.toml` and the
corresponding `%pyproject` RPM macros.

### `python-nose` is removed (43)

The unmaintained `python-nose` package does not build with Python 3.14 and is
retired without a replacement. Port package test suites to another runner.

### `python-async-timeout` is deprecated (43)

`python3-async-timeout` remains available but deprecated. Use timeout support
built into `asyncio` since Python 3.11, retaining a conditional import only
when older Python compatibility is required.

### Fedora packages finish migrating away from `python-mock` (44)

Remaining Fedora package uses of the long-deprecated `python-mock` library are
removed in preparation for retiring the compatibility package. Use the
standard-library mocking interfaces in maintained Python versions.

## Rust, C, C++, and LLVM

### LLVM 19 compatibility packages (41)

LLVM 19 is the main stack. LLVM 18 remains through `clang18`, `llvm18`,
`lld18`, `compiler-rt18`, and `libomp18`; the former version 17 compatibility
packages are retired.

### LLVM 20 layout and compatibility (42)

LLVM subprojects move to 20 with a new library soname. `llvm19` preserves
version 19 consumers. Versioned content lives below
`/usr/lib64/llvm$VERSION/`, with binary and library symlinks exposed under
`/usr`.

### LLVM 22 requires newer Rust bindgen packages (44)

The LLVM stack moves to 22. Packaged Rust dependents must move to bindgen 0.72
or newer because LLVM 22 fixes are present in bindgen 0.72.1 and later.

### Rust compatibility crates are retired or deprecated (42)

Fedora removes PyO3 0.19 through 0.21, zbus v1, and zvariant v2. Packaged
consumers must use PyO3 0.22 or newer and zbus v4 or v5. The unmaintained GTK3
Rust bindings are deprecated and cannot back new Fedora package dependencies.

### The Rust `async-std` crate is deprecated (43)

The unmaintained `async-std` crate package is deprecated. Direct new consumers
toward `smol` and migrate existing packaged consumers where practical.

### Deprecated GTK Rust bindings are retired (43)

The deprecated `gtk3-rs` packages are retired together with `gtk-rs-core`
0.18 and `gtk4-rs` 0.7. Packaged Rust consumers must move to maintained
binding versions or toolkits.

### The gold linker is deprecated (43)

`binutils-gold` is deprecated ahead of removal. Port builds that explicitly
select gold to a supported linker.

### YASM is deprecated (43)

Fedora is moving package builds from YASM to NASM. Port build systems that
explicitly require YASM before its removal.

### TagLib 2 breaks ABI and API compatibility (44)

TagLib moves from 1.13 to the 2.x line. Rebuild or port dependent packages for
the new ABI and API.

### dtrace is packaged separately (41)

`/usr/bin/dtrace` is split from `systemtap-sdt-devel` into the `dtrace`
package. Build environments that call it must request that package directly.

## Build systems and packaging automation

### Fedora Go packages prefer vendored dependencies (43)

Go application RPMs default to vendored rather than separately packaged
dependencies. Go Vendor Tools support license scanning, cumulative SPDX
expressions, and reproducible vendor archives for this workflow.

### New packages receive Packit onboarding pull requests (43)

New projects on `src.fedoraproject.org` automatically receive a pull request
with initial Packit configuration. Merging it opts the project into Packit
release automation.

### Fedora CMake packaging defaults to Ninja (44)

The `%cmake` RPM macro selects Ninja rather than Unix Makefiles. Package build
steps must not assume `%cmake` generated a Makefile.

### CMake 4.2 removes pre-3.5 policy compatibility (44)

Fedora moves from CMake 3.31 to 4.2. A project whose
`cmake_minimum_required()` has only a lower bound below 3.5 must raise it or
declare a supported policy range:

```cmake
cmake_minimum_required(VERSION 3.12...4.0)
```

Fedora provides no `%cmake4*` macros or `/usr/bin/cmake3`. `%cmake3` remains
an alias of `%cmake`, and `/usr/bin/cmake4` temporarily points to `cmake`.

### R packaging gains standardized RPM macros (44)

Use Fedora's R packaging guidelines and standardized RPM macros for common R
build quirks instead of repeating package-specific handling.

## Other language toolchains

### Tcl/Tk 9 and version 8 compatibility packages (42)

Tcl and Tk default to the incompatible 9.0 major release. Applications not
yet ported can explicitly use the `tcl8` and `tk8` compatibility packages.

### Ansible 11 interpreter compatibility (42)

`ansible` moves to 11 and `ansible-core` to 2.18. Controller support drops
Python 3.10, target support drops Python 3.7, and Python 3.13 is supported in
both. Workflows targeting Python 2.7 or 3.6 systems, including default EL7 or
EL8 interpreters, need a newer remote interpreter or an older Ansible stack.

### Ansible 13 tightens templating and controller requirements (44)

Fedora moves to Ansible 13 and Core 2.20. The reworked templating engine
rejects some invalid playbooks that formerly ran, `INJECT_FACTS_AS_VARS` is
deprecated, and Python 3.8 controllers are unsupported.

### SDL 2 is provided through SDL 3 (42)

Fedora replaces the SDL 2 implementation with `sdl2-compat` backed by SDL 3.
The SDL 2 interface remains, but applications run on a different underlying
implementation.

### Free Pascal gains cross-compilers (43)

Fedora's Free Pascal Compiler packages support cross-compilation in addition
to native targets.

### Idris 2 and Hare are packaged (43)

Fedora packages the dependently typed Idris 2 language and the Hare systems
language toolchain. Hare is still under development; its language, standard
library, and reference tools can make breaking changes.

### Ruby 4 becomes the system Ruby (44)

The system Ruby stack moves from 3.4 to the 4.0 major line. Test packaged and
locally deployed applications against Ruby 4 before upgrading.

### `ruby-build` is split by implementation (44)

The base package is supplemented by implementation-specific packages such as
`ruby-build-jruby` and `ruby-build-truffleruby`. Install only the dependency
set for the Ruby implementations being built.

### Nix is available from Fedora repositories (44)

The Nix functional package manager is available as a Fedora-packaged developer
tool; prefer the distribution package when Fedora lifecycle integration is
desired.

### Haskell profiling libraries become architecture-limited (44)

GHC moves from 9.8 to 9.10 and Stackage LTS from 23 to 24. Profiling libraries
other than GHC's own are built only on x86_64 and AArch64.
