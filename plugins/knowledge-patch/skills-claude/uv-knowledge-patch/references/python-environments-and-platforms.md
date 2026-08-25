# Python, Environments, and Platforms

## Interpreter requests and compile selection (0.6-0.8)

`uv python install` honors `UV_PYTHON`, which takes precedence over
`.python-version`. In `uv pip compile`, `-p` aliases `--python`, not
`--python-version`. A missing version request may use another interpreter with
overridden tags, but a missing requested path or implementation is an error.

Arbitrary executable-name requests in `.python-version` are ignored.

## Managed Python executables (0.6-0.8)

Managed installs place a versioned executable such as `python3.13` in a `PATH`
directory by default and can register with the Windows `py` launcher. Those
executables expose only the base standard-library environment. Use `--default`
for unversioned names, `--no-bin` or `UV_PYTHON_INSTALL_BIN=0` to suppress bin
links, and `--no-registry` or `UV_PYTHON_INSTALL_REGISTRY=0` to suppress Windows
registration.

Select custom managed-Python metadata with
`UV_PYTHON_DOWNLOADS_JSON_URL` or `python-downloads-json-url` in `uv.toml`.

## Discovery preferences and environment recreation (0.6-0.8)

Interpreters found on `PATH` must satisfy `--managed-python`,
`--no-managed-python`, or the configured preference unless explicitly
requested or supplied by an active virtual environment. A preference change
can invalidate and recreate the existing project environment.

## Python 3.14 and GIL selection (0.9-0.10)

Python 3.14 replaces 3.13 as the default stable version for an unversioned
install or automatic download when no system interpreter or pin applies. On
3.14+, discovery may select a free-threaded interpreter without a `t` suffix;
installation still prefers a GIL-enabled build. A request such as `3.14+gil`
requires a GIL-enabled interpreter.

At 0.12.5, equally prioritized matching interpreters are ordered by newer
version and then by preference for standard variants.

## Managed-Python upgrades (0.9-0.10)

`uv python upgrade` and `uv python install --upgrade` are stable. Minor-version
indirection lets virtual environments follow newly installed patch versions.
Both commands accept `--compile-bytecode` for the standard library.
`uv pip compile --python-version` can download a missing requested interpreter
when possible.

## Alternative implementations (0.9-0.10)

Managed PyPy, GraalPy, and Pyodide executables use implementation-specific
names such as `pypy3.10`, `graalpy3.10`, and `pyodide3.12`, avoiding collisions
with CPython. uv can use Python 3.6 interpreters, and Pyodide discovery supports
Windows.

## Global pins and tool environments (0.9-0.10)

`uv tool run` and newly created `uv tool install` environments use a compatible
global Python pin when `--python` is absent. An existing tool keeps its
interpreter until reinstalled or given `--python`; an earlier explicit tool
Python remains authoritative.

## Protect existing virtual environments (0.6-0.8)

Interactive `uv venv` prompts before removing an existing virtual environment.
`--clear` or `UV_VENV_CLEAR=1` confirms replacement; `--no-clear` suppresses
removal prompts. uv refuses to remove a directory that is not a virtual
environment.

## Relocatable and centralized environments

Preview behavior can make environments relocatable by default, with
`UV_VENV_RELOCATABLE` as an environment-level control (0.9-0.10). Relocatable
environments do not generate `activate.csh`, because it embeds absolute paths.

At 0.12.5, `.venv` may be a file containing the path to a centralized project
environment. Centralized environments can also be reused when a workspace is
reached through symlinks.

## Cross-platform targets (0.6-0.8)

The `linux` alias for `--python-platform` targets `manylinux_2_28`, not
`manylinux_2_17`. Request `x86_64-manylinux_2_17` explicitly for the older
compatibility target.

`--python-platform` is supported by `uv sync`, `uv pip check`, `uv run`, and
`uv tool`. Target support includes Android and iOS tags, explicit RISC-V Linux,
and AArch64 Windows.
