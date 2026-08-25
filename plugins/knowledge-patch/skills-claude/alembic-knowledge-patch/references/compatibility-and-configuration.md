# Compatibility and configuration

Use this reference when upgrading runtimes, building Alembic from source, or
moving generation settings between INI and TOML configuration.

## Runtime and packaging requirements

### Python and SQLAlchemy floors

Alembic 1.15.0 requires Python 3.9 or newer and SQLAlchemy 1.4 or newer. Python
3.8 and SQLAlchemy 1.3 are no longer supported. (since 1.15.0)

Alembic 1.17.0 raises the Python requirement again to Python 3.10 or newer;
Python 3.9 is no longer supported. (since 1.17.0)

Alembic 1.18.0 requires SQLAlchemy 1.4.23 or newer, raising the earlier 1.4.0
floor. (since 1.18.0)

Check all three pins together during an upgrade. A valid Alembic pin does not
make an older interpreter or SQLAlchemy dependency compatible.

### Yanked 1.15.0 wheel

Alembic 1.15.0 was yanked because its move to PEP 621 packaging omitted the
Alembic template files from the wheel. The corrected wheel was published in
1.15.1. Install 1.15.1 or later rather than pinning 1.15.0.

### Setuptools source-build requirement

Source builds require setuptools 77.0.3 or newer after Alembic adopted PEP 639
license metadata. Wheel-only installations are not the reason for this build
dependency, but source-building CI and packaging images must provide it.
(since 1.16.0)

## TOML source configuration

### Divide source settings from deployment settings

Alembic can read source-code and generation settings from `pyproject.toml`,
including local paths and post-write hooks. Use TOML lists for
`version_locations` and `prepend_sys_path`; they avoid the separator ambiguity
of scalar INI values. `%(here)s` is resolved relative to the parent directory
of the TOML file. (since 1.16.0)

Database connectivity and logging remain deployment settings. Supply them with
`alembic.ini` or implement them in `env.py`. If `env.py` supplies them, a project
created with the `pyproject` initialization template can omit `alembic.ini`.

Keep this distinction when reorganizing configuration:

- Put source layout, generation paths, and post-write processing in TOML.
- Keep URLs, connection construction, and logging in INI or environment code.
- Resolve TOML-relative paths from the TOML file, not the process directory.

## Cross-platform path splitting

### Prefer `path_separator`

The `path_separator` setting supersedes `version_path_separator` and controls
splitting for both `version_locations` and `prepend_sys_path`. Set it to `os` to
split on the platform's `os.pathsep`. (since 1.16.0)

```ini
[alembic]
path_separator = os
```

Configurations that omit `path_separator` keep the older splitting behavior
and emit a deprecation warning. Add the setting explicitly when maintaining a
configuration across Windows and POSIX hosts.

## Public path API contract

### Accept `os.PathLike`, return strings

Public command, configuration, and script APIs that accept string paths also
accept `os.PathLike` objects. Public path-returning accessors continue to return
strings. (since 1.16.0)

Private underscored APIs are outside that compatibility promise and can return
`pathlib.Path` objects after the path-handling refactor. Normalize values at the
boundary if extension code still calls a private API; do not infer private
return types from public behavior.
