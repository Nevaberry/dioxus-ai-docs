# Compatibility and Configuration

## Runtime requirements

### Python and SQLAlchemy floors (1.15.0)

Alembic 1.15 drops Python 3.8 and SQLAlchemy 1.3. It requires Python 3.9 or
newer and SQLAlchemy 1.4 or newer. Upgrade the application runtime and ORM
dependency before adopting that Alembic line.

### Python 3.10 minimum (1.17.0)

Alembic 1.17 drops Python 3.9 and requires Python 3.10 or newer. Environments
that must remain on Python 3.9 cannot upgrade to this line.

### Raised SQLAlchemy floor (1.18.0)

Alembic 1.18 requires SQLAlchemy 1.4.23 or newer, raising the previous
SQLAlchemy 1.4.0 floor. Check resolved dependency versions, not only broad
requirement specifiers.

## Packaging and source builds

### Yanked 1.15.0 wheel

The move to PEP 621 packaging omitted Alembic's template files from the 1.15.0
wheel, so that release was yanked. The 1.15.1 wheel corrected the package;
install 1.15.1 or later in that series rather than pinning 1.15.0.

### Setuptools build requirement (1.16.0)

Building Alembic from source requires setuptools 77.0.3 or newer. The higher
floor accompanied the adoption of PEP 639 license metadata. Ensure isolated
build environments can resolve this version.

## Configuration sources

### Source settings in `pyproject.toml` (1.16.0)

Alembic can read source-code and generation settings from `pyproject.toml`,
including local paths and post-write hooks. TOML lists avoid separator
ambiguity for `version_locations` and `prepend_sys_path`. In TOML values,
`%(here)s` resolves relative to the parent directory of `pyproject.toml`.

Keep database connectivity and logging as deployment settings in
`alembic.ini` or `env.py`. When `env.py` supplies them, the `pyproject` init
template permits omitting `alembic.ini` entirely.

### Cross-platform path separation (1.16.0)

`path_separator` supersedes `version_path_separator` and applies to both
`version_locations` and `prepend_sys_path`:

```ini
[alembic]
path_separator = os
```

The `os` value splits paths with `os.pathsep`. If `path_separator` is absent,
Alembic retains the older splitting behavior and emits a deprecation warning.
Set it explicitly for predictable behavior across operating systems.

## Public path APIs

### `PathLike` inputs (1.16.0)

Public command, configuration, and script APIs that accept path strings also
accept `os.PathLike` objects. Public accessors that return paths continue to
return strings, so do not change calling code to require `Path` results.

Private underscored APIs can return `pathlib.Path` objects after the path
handling refactor. Code relying on private path types should migrate to public
APIs or normalize the returned value explicitly.
