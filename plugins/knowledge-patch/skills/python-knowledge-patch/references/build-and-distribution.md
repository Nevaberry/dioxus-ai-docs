# Build and distribution

Use this reference for build prerequisites and configure controls, the JIT, cross-compilation and platform targets, and distribution artifacts.

## Build prerequisites and configure

### Build prerequisites and ABI-specific metadata (Python 3.13)
Building CPython now needs C11 atomics (or supported compiler intrinsics), regenerating `configure` needs Autoconf 2.71 and aclocal 1.16.5, and the `sqlite3` extension needs SQLite 3.15.2 or newer. System `libmpdec` is now preferred by default, and POSIX pkg-config names include ABI flags, such as `python-3.13t.pc` for free-threaded builds and `python-3.13d.pc` for debug builds.

### Source-build controls (Python 3.14)
Regenerating `configure` now requires Autoconf 2.72, and recommended compiler safety options are enabled by default; `--disable-safety` or `--enable-slower-safety` selects the tradeoff. Windows extensions may define `Py_NO_LINK_LIB` to suppress pragma-based `python3*.lib` linking, while `WITH_FREELISTS` and `--without-freelists` have been removed.

### Build-system controls (Python 3.15 preview)
Frame pointers are enabled by default on supported platforms and propagated through `sysconfig`; custom native build systems should preserve equivalent compiler flags, while CPython itself can opt out with `--without-frame-pointers`. The implicit bundled-`libmpdec` fallback is removed, so bundled use must be requested explicitly with `--without-system-libmpdec`.

Distributors can supply explanations for separately packaged or missing standard-library modules with `--with-missing-stdlib-config=FILE`. `--with-pymalloc-hugepages` builds 2 MiB huge-page arenas with safe fallback, but runtime use still requires `PYTHON_PYMALLOC_HUGEPAGES=1`.

## JIT

### Experimental JIT build modes (Python 3.13)
`--enable-experimental-jit=yes` builds an enabled JIT (`PYTHON_JIT=0` disables it), `yes-off` builds it disabled (`PYTHON_JIT=1` enables it), and `interpreter` enables only the Tier 2 interpreter. Windows uses `PCbuild/build.bat --experimental-jit` or `--experimental-jit-interpreter`, and JIT builds require LLVM only at build time.

### Experimental JIT in official binaries (Python 3.14)
Official macOS and Windows binaries include the experimental JIT in a disabled state; set `PYTHON_JIT=1` to test it, and query `sys._jit.is_available()` or `is_enabled()` before relying on it. It remains unsuitable for production and unavailable in free-threaded builds.

### JIT and source-build controls (3.15.0b3)
JIT builders can set `CFLAGS_JIT`, override the tool directory with `LLVM_TOOLS_INSTALL_DIR`, or select an unsupported LLVM version with `LLVM_VERSION`. Configure also accepts `--disable-epoll` and `--enable-static-libpython-for-interpreter`; the latter keeps building a shared library under `--enable-shared` while statically linking the interpreter executable.

## Cross-compilation and platform targets

### Platform and cross-build baselines (3.14.0)
The Windows runtime baseline is Windows 10, Android's minimum is 7.0/API 24, the default iOS minimum is 13.0, and Emscripten builds require Node 18 or newer. Windows source builds require Python 3.10 or newer; `--with-emscripten-target` is removed, and the WASI target triple is now `wasm32-wasip1`.

### Apple application embedding controls (3.14.0)
`PyConfig.use_system_logger` now defaults on for iOS and off for macOS, and embedded macOS/iOS apps can redirect standard output and error to the system log. Source builds also accept `--with-app-store-compliance` to patch out known App Store review problems.

### Cross-build and platform changes (3.15.0b3)
CPython now targets POSIX 2024 rather than POSIX 2008, and WASI cross-builds require an explicit `HOSTRUNNER`; downstream WASI builders may pass `--enable-wasm-dynamic-linking` even though CPython itself does not implement it. `RUNSHARED` is preserved during cross-compilation for executable shared builds, `build-details.py` is omitted by `make altinstall`, and `pybuilddir.txt` is the sole source-tree landmark rather than `Modules/Setup.local`.

### Windows free-threaded build layouts (3.15.0b3)
Windows free-threaded source builds use paths and ordinary executable names such as `PCbuild/amd64t/python.exe`. Normal non-free-threaded installs also include a `python3t.dll` compatibility library, allowing them to load extensions linked against that DLL.

## Distribution metadata and artifacts

### Static build metadata (Python 3.14)
Every installation now places `build-details.json` in `sysconfig.get_path('stdlib')`, exposing build information to launchers and cross-compilation tools without executing the interpreter.

### Distribution and platform changes (Python 3.14)
Official Android binaries are now published, and Emscripten is a tier-3 platform with `ctypes`, `termios`, and `fcntl` support. Python 3.14 and later release artifacts no longer carry PGP signatures; verification uses the accompanying Sigstore materials.
