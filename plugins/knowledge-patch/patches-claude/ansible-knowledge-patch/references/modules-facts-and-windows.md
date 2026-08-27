# Modules, Facts, Results, and Windows

## Fact access and variable lookup

`INJECT_FACTS_AS_VARS=true` is deprecated in `2.19-2.20` and is scheduled to
default to false in 2.24. Replace injected top-level names such as
`ansible_os_distribution` with structured access such as
`ansible_facts['os_distribution']` before that default changes.

Each `ansible_facts['vgs']` entry has an `lvs` subkey. Use that per-volume-group
mapping when completeness matters because name deduplication can make the
top-level `lvs` fact incomplete.

The internal variable cache is also deprecated for removal in 2.24. Use the
`vars` and `varnames` lookups. Complete both migrations before upgrading to the
new injected-fact default.

## File modules and encodings

In `2.19-2.20`, `blockinfile` and `lineinfile` accept `encoding` for files that
are not UTF-8. The `replace` module reads, matches, and writes Unicode text
rather than bytes, so review byte-oriented expressions and assumptions.

## Package dependency installation

The `apt` and `dnf5` modules in `2.19-2.20` add
`auto_install_module_deps`. `deb822_repository` adds
`install_python_debian` for its Python dependency. Set the intended policy
explicitly on minimal images where automatic dependency installation affects
bootstrapping or image size.

The `dnf` and `dnf5` modules remove `install_repoquery`, and
`yum_repository` removes `keepcache`.

## Module results and input types

`async_status.started` and `async_status.finished` are booleans in
`2.19-2.20`, rather than `1` and `0`. Compare them as booleans.

Modules returning non-UTF-8 strings now fail. `MODULE_STRICT_UTF8_RESPONSE`
can disable the strict check as a compatibility escape hatch, but module
responses should be corrected instead.

`include_vars.extensions` and `include_vars.ignore_files` must be lists.
String-form `ignore_files` is deprecated.

## Filters and removed module options

The `vault` and `unvault` filters remove the `vaultid` parameter in
`2.19-2.20`. Remove calls that supply it.

## RPM key handling

In 2.20.4, `rpm_key` uses librpm and supports version 6 PGP keys.

In `2.21.3`, `rpm_key` adds a trailing newline to ASCII-armored PGP data before
passing it to librpm. This avoids parse failures where `pgpParsePkts` requires
the newline, so callers do not need to rewrite otherwise valid armor that
lacks one.

## Git submodule tracking

In 2.20.6, `git` with `track_submodules=yes` follows the branch configured in
`.gitmodules`, or the remote HEAD when no branch is configured. It no longer
assumes `master`.

## Timeout-aware parallel fact gathering

The asynchronous wrapper for parallel fact gathering in `2.21.2` considers
the remaining timeout before killing the module process. It no longer blindly
sleeps for five seconds twice before checking the time budget. Timeout tests
should assert the deadline-aware behavior rather than the former fixed delay.

## Windows platform support

In `2.19-2.20`, Windows Server 2025 is supported. Signed modules and scripts on
hosts protected by Windows App Control or WDAC are a tech preview. WDAC audit
mode with Dynamic Code Security is supported.

PowerShell modules can request execution wrappers without module utils by
declaring:

```powershell
#AnsibleRequires -Wrapper
```

Validate signed content under the target host's actual application-control
policy rather than assuming ordinary PowerShell execution covers it.

## PowerShell executable selection

When multiple `pwsh` executables match in `2.21.3`, the PowerShell execution
wrapper selects the first result. Ensure path ordering makes the intended
PowerShell executable the first match.
