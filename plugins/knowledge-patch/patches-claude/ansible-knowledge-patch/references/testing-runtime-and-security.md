# Testing, Runtime Support, and Security

## Runtime and maintenance support

For `2.21.2`, control nodes support Python 3.12 through 3.14, while target nodes
support Python 3.9 through 3.14. Windows targets support Windows PowerShell 5.1
and PowerShell 7.6 LTS.

The release line moves to critical-fix maintenance in November 2026,
security-only maintenance in May 2027, and end of life in November 2027. Align
controller and execution-environment upgrades with those dates.

## Pre-timeout thread diagnostics

When a deadline configured by `ansible-test env --timeout` approaches in
`2.21.2`, `ansible-test` invokes a timeout callback that dumps thread stacks
before terminating the run. Give the job enough deadline headroom and preserve
its final logs so these diagnostics are emitted and collected.

## Integration-test environment variables

In `2.19-2.20`, static environment variables can be declared in an integration
target's `aliases` file:

```text
env/set/MY_KEY/MY_VALUE
```

A doubled separator starts an absolute value:

```text
env/set/MY_PATH//an/abs/path
```

The `ansible-test shell` command propagates remote-debug and test settings on
the controller. Use `--raw` when the shell must bypass that environment setup.

## Role installer command safety

The 2.19.11 and 2.20.7 role installer passes role requirements to `git clone`
positionally. This prevents a malicious role author from injecting arbitrary
Git configuration through role dependencies. Retain patched maintenance
releases wherever role requirements can come from an untrusted source.

## `no_log` transport protection

The 2.19.10 and 2.20.6 PSRP and WinRM transports do not log raw standard output
or standard error at verbosity 5 when `no_log: true` is set. Do not rely on a
lower verbosity level as the only protection for sensitive Windows task data.
