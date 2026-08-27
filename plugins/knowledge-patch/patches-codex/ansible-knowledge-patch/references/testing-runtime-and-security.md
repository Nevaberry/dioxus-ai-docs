# Testing, Runtime Support, and Security

## Controller and target runtimes

For `2.21.2`, control nodes support Python 3.12 through 3.14, while target nodes
support Python 3.9 through 3.14. Windows targets support Windows PowerShell 5.1
and PowerShell 7.6 LTS.

The release line enters critical-fix maintenance in November 2026,
security-only maintenance in May 2027, and reaches end of life in November
2027. Use those dates when planning controller and execution-environment
upgrades.

## Integration-test environment variables

Since `2.19-2.20`, an integration target can declare static environment
variables in its `aliases` file:

```text
env/set/MY_KEY/MY_VALUE
```

A doubled separator begins an absolute value:

```text
env/set/MY_PATH//an/abs/path
```

The `ansible-test shell` command propagates remote-debug and test settings on
the controller. Use `--raw` to bypass that environment setup.

## Timeout diagnostics

In `2.21.2`, when a deadline set by `ansible-test env --timeout` approaches,
`ansible-test` invokes a timeout callback that dumps thread stacks before the
test run is terminated. Leave enough deadline headroom for that diagnostic
output and retain it in CI logs.

Parallel fact gathering is also timeout-aware: its async wrapper considers the
remaining timeout before killing the module process rather than unconditionally
sleeping for five seconds twice before checking the deadline.

## Explicit target versions

In `2.21.3`, `ansible-test` target filtering preserves versions explicitly
provided by the user even when they are absent from completion configuration.
Do not strip such versions in wrapper-side prevalidation merely because shell
completion does not list them.

## Role installation security

Since the 2.19.11/2.20.7 patch lines, the role installer passes role
requirements to `git clone` positionally. This prevents a malicious role author
from injecting arbitrary Git configuration through role dependencies. Do not
reintroduce command construction that treats a role requirement as an option.

## Secret-safe Windows transport logging

Since the 2.19.10/2.20.6 patch lines, PSRP and WinRM suppress raw standard
output and standard error at verbosity 5 when `no_log: true` is active. Test
diagnostic wrappers to ensure they preserve this behavior.
