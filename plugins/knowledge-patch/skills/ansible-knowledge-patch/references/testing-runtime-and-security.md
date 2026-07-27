# Testing, Runtime Support, and Security

This reference combines testing changes from batch `2.19-2.20` with runtime
and timeout behavior from batch `2.21.2`.

## Integration-Test Environment Variables

An integration target can declare static environment variables in its
`aliases` file:

```text
env/set/MY_KEY/MY_VALUE
```

A doubled separator begins an absolute value:

```text
env/set/MY_PATH//an/abs/path
```

The `ansible-test` `shell` command propagates remote-debug and test settings
on the controller. Pass `--raw` when the shell must bypass that environment
setup.

## Timeout Diagnostics

When a deadline configured by `ansible-test env --timeout` approaches,
`ansible-test` invokes a timeout callback that dumps thread stacks before
terminating the test run. Preserve this diagnostic output in CI logs and
allow enough deadline headroom for the callback to run.

Parallel fact gathering is also timeout-aware. Its async wrapper considers
the remaining timeout when deciding whether to kill the module process,
instead of always sleeping for five seconds twice before checking the
remaining time. Timeout-sensitive tests should not assume the former fixed
delay.

## Controller and Target Runtimes

For the 2.21 runtime line represented by batch `2.21.2`:

| Environment | Supported runtime |
| --- | --- |
| Control node | Python 3.12 through 3.14 |
| Target node | Python 3.9 through 3.14 |
| Windows target | Windows PowerShell 5.1 or PowerShell 7.6 LTS |

Validate both controller and target interpreters; their supported Python
ranges differ.

## Maintenance Schedule

The same runtime line moves to critical-fix maintenance in November 2026,
security-only maintenance in May 2027, and end of life in November 2027.
Plan controller upgrades before the applicable maintenance boundary.

## Role-Installer Hardening

In 2.19.11 and 2.20.7, the role installer passes role requirements to
`git clone` positionally. This prevents a malicious role author from
injecting arbitrary Git configuration through role dependencies.

Keep role installation on a fixed release and do not recreate the earlier
command construction in wrappers.

## Secret-Safe Windows Transport Logging

In 2.19.10 and 2.20.6, the PSRP and WinRM transports no longer log raw stdout
and stderr at verbosity 5 when `no_log: true` is set.

Treat earlier logs as potentially sensitive, and ensure custom logging or
callback code also honors `no_log`.
