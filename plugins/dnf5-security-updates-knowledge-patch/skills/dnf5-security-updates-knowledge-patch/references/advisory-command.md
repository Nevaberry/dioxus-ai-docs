# Advisory Command

`dnf5 advisory` replaces `updateinfo`. Subcommands are now **mandatory** — bare `dnf5 advisory` fails. `updateinfo` is kept as an alias.

## Subcommands

```bash
# List security advisories (subcommand required)
dnf5 advisory list --security
dnf5 advisory summary --advisory-severities=critical,important
dnf5 advisory info FEDORA-2024-abc123
```

Available subcommands: `list`, `summary`, `info`.

## JSON Output

JSON output is available via `--json`. Two formats:

```bash
# Basic JSON output
dnf5 advisory list --json

# Extended format — adds references array with CVE details
dnf5 advisory list --json --with-cve
```

## Severity Filtering

`--sec-severity` was renamed to `--advisory-severities=SEVERITY,...`.

Accepted values: `critical`, `important`, `moderate`, `low`, `none`.

```bash
dnf5 advisory list --advisory-severities=critical,important
dnf5 advisory summary --advisory-severities=critical
```

Multiple severities are comma-separated in a single flag value.
