# Configuration and CLI

## Native TOML configuration

Since 9.0.0, use `[tool.pytest]` in `pyproject.toml` for native TOML values
such as arrays:

```toml
[tool.pytest]
minversion = "9.0"
addopts = ["-ra", "-q"]
testpaths = ["tests", "integration"]
```

`[pytest]` in `pytest.toml` or `.pytest.toml` provides the same native TOML
style. `[tool.pytest.ini_options]` remains supported but cannot coexist with
`[tool.pytest]`.

When configuration exists in more than one candidate file, pytest 9.0.0 and
newer warn that only one file is used. Consolidate the configuration to make
precedence unambiguous.

## Unified strict mode

Since 9.0.0, `strict = true` or `--strict` enables all of:

- `strict_config`
- `strict_markers`
- `strict_parametrization_ids`
- `strict_xfail`

Explicit individual settings override the global setting.
`strict_parametrization_ids` makes duplicate parameter IDs errors rather than
silently suffixing them. Future strictness options automatically join unified
strict mode, so use it when adopting stricter future behavior is intentional.

## Plugin autoload and early startup

Since 8.4.0, `--disable-plugin-autoload` is the command-line equivalent of
`PYTEST_DISABLE_PLUGIN_AUTOLOAD`. The option can be persisted in `addopts`:

```ini
[pytest]
addopts = --disable-plugin-autoload
```

The `pythonpath` setting is also applied early enough to affect plugins loaded
with `-p`.

Since 9.0.0, a single `pytest --version` on the command line avoids loading
plugins. Use `pytest --version --version` to include plugin information. This
early behavior applies only when `--version` is passed directly; it does not
apply through `PYTEST_ADDOPTS` or configured `addopts`.

## Terminal progress

In 9.0.0, an internal plugin automatically emits OSC 9;4 progress updates when
pytest runs in a supported TTY. Disable it for incompatible terminals with:

```ini
[pytest]
addopts = -p no:terminalprogress
```

The direct command-line form is `pytest -p no:terminalprogress`.

## Stepwise execution

Since 8.4.0, running without `--stepwise` no longer clears the remembered last
failure. A later stepwise run resumes at that test unless the suite-size check
invalidates stale state.

Use `--stepwise-reset` or its alias `--sw-reset` to discard the stored state
and restart from the beginning.

## Faulthandler timeouts

Since 9.0.0, `faulthandler_exit_on_timeout` controls whether a faulthandler
timeout interrupts pytest in a deadlock. The default is false, which preserves
the traceback-dump-only behavior. Set it to true when timeout should terminate
the run.

## CI detection

Since 9.0.0, defining `CI` or `BUILD_NUMBER` with an empty value does not
activate CI mode. At least one of those variables must have a non-empty value.

## Output controls

Since 8.4.0:

- `--force-short-summary` keeps the condensed failure summary regardless of
  verbosity.
- `truncation_limit_lines` controls how many lines a snippet may contain.
- `truncation_limit_chars` controls how many characters a snippet may contain.
- `console_output_style = times` displays each test's execution time.

Source output is highlighted by default because `pygments` is a required
dependency. Use `--code-highlight=no` to disable highlighting.

## Warning-count limit

Since 9.1.0, `--max-warnings` and the `max_warnings` configuration option fail
a run once its warning count exceeds the threshold:

```ini
[pytest]
max_warnings = 10
```
