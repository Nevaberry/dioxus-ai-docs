# Python, Environments, and Platforms

Use this reference for interpreter discovery, managed Python installations,
virtual environments, Python pins, and target-platform behavior.

## Contents

- [Interpreter Requests and Discovery](#interpreter-requests-and-discovery)
- [Managed Python Installation and Upgrade](#managed-python-installation-and-upgrade)
- [Virtual Environment Semantics](#virtual-environment-semantics)
- [Tool Interpreter Pins](#tool-interpreter-pins)
- [Cross-Platform Targets](#cross-platform-targets)

## Interpreter Requests and Discovery

### Understand request precedence

In the 0.6-0.8 batch, `uv python install` began honoring `UV_PYTHON`, including
its precedence over `.python-version`.

For `uv pip compile`, `-p` aliases `--python`, not `--python-version`. If a
requested version is unavailable, uv may use another interpreter with
overridden tags. A missing requested path or requested implementation is an
error rather than a candidate for substitution.

Interpreters discovered on `PATH` must satisfy `--managed-python`,
`--no-managed-python`, or the configured Python preference. Explicit requests
and an active virtual environment are exceptions. Changing the preference can
invalidate and recreate an existing project environment.

### Account for Python 3.14 selection

In the 0.9-0.10 batch, Python 3.14 replaced 3.13 as the stable default for an
unversioned install or automatic download when no system interpreter or pin
applies.

For Python 3.14 and newer, discovery may select a free-threaded interpreter
without an explicit `t` suffix. Installation still prefers a GIL-enabled
build. A request such as `3.14+gil` requires a GIL-enabled interpreter.

## Managed Python Installation and Upgrade

### Know which executables are created

`uv python install` puts a versioned executable such as `python3.13` in a
`PATH` directory by default. On Windows it also registers installations with
the `py` launcher. These executables expose only the base standard-library
environment.

- Use `--default` for unversioned executable names.
- Use `--no-bin` or `UV_PYTHON_INSTALL_BIN=0` to suppress bin links.
- Use `--no-registry` or `UV_PYTHON_INSTALL_REGISTRY=0` to suppress Windows
  launcher registration.

Custom managed-Python metadata can be selected with
`UV_PYTHON_DOWNLOADS_JSON_URL` or the `python-downloads-json-url` setting in
`uv.toml`.

### Upgrade managed installations

`uv python upgrade` and `uv python install --upgrade` are stable. Minor-version
indirection lets virtual environments follow newly installed patch versions.
Both commands support `--compile-bytecode` to precompile the standard library.

`uv pip compile --python-version` can download a missing requested interpreter
when possible.

### Use implementation-specific executable names

Managed alternative implementations avoid CPython name collisions:

- PyPy uses names such as `pypy3.10`.
- GraalPy uses names such as `graalpy3.10`.
- Pyodide uses names such as `pyodide3.12`.

uv can use Python 3.6 interpreters, and Pyodide discovery supports Windows.

## Virtual Environment Semantics

### Protect existing directories

In interactive use, `uv venv` prompts before removing an existing virtual
environment. Use `--clear` or `UV_VENV_CLEAR=1` to confirm removal, or
`--no-clear` to disable removal prompts. uv refuses to remove a directory that
is not a virtual environment.

### Understand layered ephemeral runs

`uv run --with` caches the environment containing the requested requirements,
but runs through a fresh empty environment layered over that cache. Code that
inspects or mutates its runtime environment is not operating directly on the
cached layer.

### Build relocatable environments deliberately

Preview behavior can make virtual environments relocatable by default, with
`UV_VENV_RELOCATABLE` as the environment-level control. Relocatable
environments omit `activate.csh` because that activation script embeds
absolute paths.

## Tool Interpreter Pins

`uv tool run` and newly created `uv tool install` environments honor a
compatible global Python pin when `--python` is absent. An existing tool keeps
its interpreter until it is reinstalled or passed `--python`. A Python version
previously set explicitly for the tool remains authoritative.

## Cross-Platform Targets

The `linux` alias for `--python-platform` targets `manylinux_2_28`, not
`manylinux_2_17`. Request `x86_64-manylinux_2_17` explicitly when that older
compatibility level is required.

`--python-platform` is supported by `uv sync`, `uv pip check`, `uv run`, and
`uv tool`. Platform support includes Android and iOS tags, explicit RISC-V
Linux targets, and explicit AArch64 Windows targets.
