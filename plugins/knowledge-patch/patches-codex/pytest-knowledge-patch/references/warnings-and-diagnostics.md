# Warnings and diagnostics

## Lifecycle-wide warning filtering

Since 8.4.0, configured and command-line `filterwarnings` rules cover more of
the pytest lifecycle. Very late warnings, unraisable exceptions, and unhandled
thread exceptions can therefore fail a suite under matching filters.

Multiple unraisable and unhandled-thread exceptions may be collected during
each test phase. The lsof plugin's warning category is
`pytest.PytestFDWarning`.

## Invalid warning filters

Since 9.0.0, a warning filter that names a class pytest cannot import produces
a diagnostic message instead of aborting the run.

## Removal-warning policy

Since 9.0.0, `PytestRemovedIn9Warning` is an error by default. During the
9.0.x series only, it can be temporarily suppressed:

```ini
[pytest]
filterwarnings =
    ignore::pytest.PytestRemovedIn9Warning
```

Features covered by these warnings are effectively removed in 9.1.0. Prefer
migration over long-lived suppression.

## Warning-count limits

Since 9.1.0, set a hard warning budget with `--max-warnings` or
`max_warnings`. The run fails after the observed warning count exceeds the
threshold:

```ini
[pytest]
max_warnings = 10
```

## Failure summary and snippets

Since 8.4.0:

- `--force-short-summary` retains the condensed failure summary regardless of
  verbosity.
- `truncation_limit_lines` caps the line count of displayed snippets.
- `truncation_limit_chars` caps the character count of displayed snippets.
- `console_output_style = times` displays each test's execution time.

## Source highlighting

Since 8.4.0, `pygments` is a required dependency, so source output is
highlighted by default. Use `--code-highlight=no` to turn highlighting off.
