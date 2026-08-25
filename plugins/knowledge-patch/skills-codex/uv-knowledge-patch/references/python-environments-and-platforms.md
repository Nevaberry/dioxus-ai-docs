# Python, Environments, and Platforms

Use this reference for interpreter selection, managed Python installation,
virtual environments, tool interpreter pins, target platforms, and images.

## Interpreter Selection and Discovery

### Honor the correct Python request source

`uv python install` respects `UV_PYTHON`, which takes precedence over
`.python-version`. In `uv pip compile`, `-p` aliases `--python`, not
`--python-version`. A missing version request may use another interpreter with
overridden tags, but a missing requested path or implementation is an error.
(Batch `0.6-0.8`.)

Arbitrary executable-name requests in `.python-version` are ignored. Use a
supported version or implementation request rather than relying on a local
executable alias. (Batch `0.6-0.8`.)

### Enforce managed and unmanaged preferences

Interpreters found on `PATH` must satisfy `--managed-python`,
`--no-managed-python`, or the configured Python preference unless explicitly
requested or supplied by an active virtual environment. Changing the
preference can invalidate and recreate the project environment. (Batch
`0.6-0.8`.)

### Understand Python 3.14 selection

Python 3.14 replaces 3.13 as the default stable version for an unversioned
install or automatic download when no system interpreter or pin applies. For
3.14+, discovery may choose a free-threaded interpreter without an explicit
`t` suffix; installs still prefer a GIL-enabled build, and `3.14+gil` requires
one. (Batch `0.9-0.10`.)

### Prefer newer standard builds on a tie

When equally prioritized interpreters match a request, uv prefers newer
versions and standard variants. Pin the implementation, version, or GIL mode
when tie-breaking must not affect reproducibility. (Since `0.12.5`.)

## Managed Python Installation

### Account for PATH and Windows registration

`uv python install` creates a versioned executable such as `python3.13` in a
`PATH` directory by default and may register the install with the Windows
`py` launcher. These executables expose only the base standard-library
environment. Use `--default` for unversioned names, `--no-bin` or
`UV_PYTHON_INSTALL_BIN=0` to suppress links, and `--no-registry` or
`UV_PYTHON_INSTALL_REGISTRY=0` to suppress registration. (Batch `0.6-0.8`.)

### Supply a custom managed-Python catalog

Select custom managed-Python metadata with
`UV_PYTHON_DOWNLOADS_JSON_URL` or `python-downloads-json-url` in `uv.toml`.
(Batch `0.6-0.8`.)

### Upgrade managed interpreters

`uv python upgrade` and `uv python install --upgrade` are stable. Minor-version
indirection lets virtual environments follow newly installed patch versions;
both commands support `--compile-bytecode` for the standard library.
`uv pip compile --python-version` can download a missing requested interpreter
when possible. (Batch `0.9-0.10`.)

### Use implementation-specific executable names

Managed PyPy, GraalPy, and Pyodide executables use names such as `pypy3.10`,
`graalpy3.10`, and `pyodide3.12`, avoiding collisions with CPython. uv can use
Python 3.6 interpreters, and Pyodide discovery supports Windows. (Batch
`0.9-0.10`.)

## Virtual Environments and Tool Interpreters

### Make virtual-environment removal explicit

Interactive `uv venv` prompts before removing an existing environment.
`--clear` or `UV_VENV_CLEAR=1` confirms removal; `--no-clear` disables removal
prompts. uv refuses to remove a directory that is not a virtual environment.
(Batch `0.6-0.8`.)

### Understand relocatable environment limits

Preview behavior can make virtual environments relocatable by default, with
`UV_VENV_RELOCATABLE` as the environment control. Relocatable environments do
not generate `activate.csh`, because that script embeds absolute paths.
(Batch `0.9-0.10`.)

### Reference a centralized environment

A `.venv` file may contain the path to a centralized project environment.
Such environments can be reused when a workspace is reached through symlinks.
Preview `uv workspace metadata --sync --active` can target the active virtual
environment. (Since `0.12.5`.)

### Apply global Python pins to tools carefully

`uv tool run` and newly created `uv tool install` environments honor a
compatible global Python pin when `--python` is absent. Existing tools retain
their interpreter until reinstalled or passed `--python`; a prior explicit
tool Python remains authoritative. (Batch `0.9-0.10`.)

## Platform Targets

### Request older Linux compatibility explicitly

The `linux` alias for `--python-platform` targets `manylinux_2_28`, not
`manylinux_2_17`. Use `x86_64-manylinux_2_17` explicitly for the older target.
The platform option also applies to `uv sync`, `uv pip check`, `uv run`, and
`uv tool`; supported targets include Android and iOS tags, RISC-V Linux, and
AArch64 Windows. (Batch `0.6-0.8`.)

### Track container and binary removals

Floating Debian and Alpine images use Debian 13 Trixie and Alpine 3.22. The
Bookworm, Alpine 3.21, and Python 3.8 tags are no longer published. Prebuilt
big-endian PPC64 binaries are removed; PPC64LE remains supported. (Batch
`0.9-0.10`.)

### Choose a writable tool bin directory in images

Derived uv images set `UV_TOOL_BIN_DIR=/usr/local/bin`, putting tool installs
on `PATH`. Override it when an unprivileged container user cannot write there.
(Batch `0.6-0.8`.)
