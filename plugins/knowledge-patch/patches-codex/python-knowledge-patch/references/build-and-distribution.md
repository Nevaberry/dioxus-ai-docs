# Build and distribution

## Configure and source builds

### Experimental JIT modes (`whatsnew-3.13`)

`--enable-experimental-jit` accepts `no`, `yes`, `yes-off`, or `interpreter`; a
bare option means `yes`. `interpreter` enables only the Tier 2 interpreter. JIT
builds need LLVM at build time but have no JIT runtime dependency.
`PYTHON_JIT=0` disables an enabled build, while `PYTHON_JIT=1` enables a
`yes-off` build.

```sh
./configure --enable-experimental-jit=yes-off
PYTHON_JIT=1 ./python app.py
```

### Python 3.13 build requirements

CPython requires C11 atomics, or GCC atomics or MSVC interlocked intrinsics.
Regenerating `configure` requires Autoconf 2.71 with aclocal 1.16.5, and the
`sqlite3` module requires SQLite 3.15.2 or later. System `libmpdec` is the
default. Pkg-config filenames include ABI flags, such as `python-3.13t.pc` and
`python-3.13d.pc`.

### Python 3.14 source controls

Regenerating `configure` requires Autoconf 2.72. Recommended compiler safety
flags are on by default; `--disable-safety` and `--enable-slower-safety` control
them. Official Android binaries are available. Emscripten is tier 3 and
supports `ctypes`, `termios`, and `fcntl`.

### Python 3.15 source controls

Select the bundled `libmpdec` fallback explicitly with
`--without-system-libmpdec`; JIT builds require LLVM 21. Distributors can
provide missing-module messages through `--with-missing-stdlib-config=FILE`.
Huge-page pymalloc requires both `--with-pymalloc-hugepages` and
`PYTHON_PYMALLOC_HUGEPAGES=1`.

### Frame-pointer contract

Supported Python 3.15 builds enable frame pointers by default. Native
extensions should preserve the matching compiler flags so stack unwinding
remains intact. `--without-frame-pointers` opts CPython out.

### Additional JIT and configure controls

Python 3.15.0b3 JIT builders can select tools with `LLVM_VERSION`,
`LLVM_TOOLS_INSTALL_DIR`, and `CFLAGS_JIT`. Configure adds `--disable-epoll`
and `--enable-static-libpython-for-interpreter`; the latter builds a statically
linked interpreter alongside a shared libpython.

## Runtime and artifact inspection

### Linux perf integration

`PYTHON_PERF_JIT_SUPPORT` or `-X perf_jit` enables advanced JIT integration for
Linux `perf`, allowing Python profiling without frame pointers.

### Static build metadata and signatures

Python 3.14 installations include `build-details.json` under
`sysconfig.get_path("stdlib")`, allowing inspection without executing the
interpreter. Python 3.14 release artifacts use Sigstore materials rather than
PGP signatures.

### Prebuilt JIT availability

As recorded in `3.13.15-3.14.7`, official macOS and Windows Python 3.14 binaries
include the experimental JIT, so testing it there does not require a source
build.

## Startup and packaging defenses

### Isolated ensurepip lookup

Python 3.15.0b3 `ensurepip` does not search the current working directory for
`pip-*.whl`, preventing ambient files from replacing its bundled wheel.

### Path-initialization diagnostics

Startup warns when path initialization cannot find a valid standard library.
`-X pathconfig_warnings` and `PYTHON_PATHCONFIG_WARNINGS` control these warnings.

## Cross-builds and platform artifacts

### WASI, iOS, and Linux perf

Python 3.15.0b3 WASI cross-builds require an explicit `HOSTRUNNER`, preserve
`RUNSHARED`, and accept `--enable-wasm-dynamic-linking` for downstream use. iOS
XCframework slices include dynamic-libpython linkage and privacy manifests. The
Linux perf trampoline is available on musl `x86_64` and `aarch64`.

### Windows free-threaded layouts

Free-threaded Windows builds use ABI-specific directories with ordinary
filenames, such as `PCbuild/amd64t/python.exe`. Regular Windows installs include
a `python3t.dll` compatibility copy so non-free-threaded runtimes can load
extensions linked to that name.

### Windows install manager

Windows release manifests can be installed with `py install 3.13` or
`py install 3.14`. The new manager is replacing the traditional installer, but
traditional installers remain available throughout the Python 3.14 and 3.15
release series.

### macOS floors

Python 3.13 raises its minimum supported macOS version from 10.9 to 10.13. The
Python 3.14.7 macOS installer requires macOS 10.15 or later.
