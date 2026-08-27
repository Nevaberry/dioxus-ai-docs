# Build and distribution

## Configure and toolchain requirements

### Experimental JIT modes (`whatsnew-3.13`)

`--enable-experimental-jit` accepts `no`, `yes`, `yes-off`, or `interpreter`; a
bare option means `yes`, while `interpreter` enables only the Tier 2
interpreter. JIT builds need LLVM while building but no JIT runtime dependency.
`PYTHON_JIT=0` disables an enabled build, and `PYTHON_JIT=1` enables a
`yes-off` build:

```sh
./configure --enable-experimental-jit=yes-off
PYTHON_JIT=1 ./python app.py
```

### Source requirements and metadata (`whatsnew-3.13`)

Building needs C11 atomics, or GCC atomics / MSVC interlocked intrinsics.
Regenerating `configure` requires Autoconf 2.71 with aclocal 1.16.5. The
`sqlite3` module requires SQLite 3.15.2 or newer. System `libmpdec` is the
default. Pkg-config filenames include ABI flags such as `python-3.13t.pc` and
`python-3.13d.pc`.

### Source and platform controls (`whatsnew-3.14`)

Regenerating `configure` requires Autoconf 2.72. Recommended compiler safety
flags are enabled by default; use `--disable-safety` or
`--enable-slower-safety` deliberately. Official Android binaries are
available. Emscripten is tier 3 and supports `ctypes`, `termios`, and `fcntl`.

### Source-build controls (`whatsnew-3.15`)

Select bundled `libmpdec` explicitly with `--without-system-libmpdec`; JIT
builds require LLVM 21. Distributors can configure missing-module messages with
`--with-missing-stdlib-config=FILE`. Huge-page pymalloc needs both
`--with-pymalloc-hugepages` and `PYTHON_PYMALLOC_HUGEPAGES=1`.

### Frame-pointer contract (`whatsnew-3.15`)

Supported builds enable frame pointers by default. Native extensions should
retain matching compiler flags so stack unwinding remains intact.
`--without-frame-pointers` opts CPython out.

### JIT and configure refinements (`3.15.0b3`)

Select JIT tools with `LLVM_VERSION`, `LLVM_TOOLS_INSTALL_DIR`, and
`CFLAGS_JIT`. Configure adds `--disable-epoll` and
`--enable-static-libpython-for-interpreter`; the latter creates a statically
linked interpreter alongside shared libpython.

## Build metadata and verification

### Static build details (`whatsnew-3.14`)

Installations include `build-details.json` under
`sysconfig.get_path("stdlib")`, allowing inspection without executing the
interpreter. Python 3.14 artifacts do not have PGP signatures; verify with
Sigstore materials.

## Cross-build and artifact layouts

### Cross-build changes (`3.15.0b3`)

WASI cross-builds require an explicit `HOSTRUNNER`, preserve `RUNSHARED`, and
accept `--enable-wasm-dynamic-linking` for downstream use. iOS XCframework
slices include dynamic-libpython linkage and privacy manifests. The Linux perf
trampoline supports musl on `x86_64` and `aarch64`.

### Windows free-threaded layouts (`3.15.0b3`)

Free-threaded Windows builds use ABI-specific directories with ordinary names,
for example `PCbuild/amd64t/python.exe`. Regular Windows installations include
a `python3t.dll` compatibility copy so non-free-threaded runtimes can load
extensions linked against that name.

## Installers and supported platforms

### Windows install manager (`3.13.15-3.14.7`)

Install release manifests with `py install 3.13` or `py install 3.14`. The new
install manager is replacing the traditional installer, but traditional
installers remain available throughout the 3.14 and 3.15 release series.

### Prebuilt JIT (`3.13.15-3.14.7`)

Official macOS and Windows Python 3.14 binaries include the experimental JIT,
so trying it on those platforms does not require a source build.

### macOS version floors (`3.13.15-3.14.7`)

Python 3.13 raises the minimum supported macOS from 10.9 to 10.13. The Python
3.14.7 macOS installer requires macOS 10.15 or later.
