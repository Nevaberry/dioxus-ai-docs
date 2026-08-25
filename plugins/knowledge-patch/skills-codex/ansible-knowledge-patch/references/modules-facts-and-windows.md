# Modules, Facts, Results, and Windows

## Injected facts and variable access

`INJECT_FACTS_AS_VARS=true` is deprecated and is scheduled to default to false
in 2.24 (`2.19-2.20`). Migrate injected top-level variables to the
`ansible_facts` mapping:

```yaml
# Avoid
when: ansible_os_distribution == 'Debian'

# Preferred
when: ansible_facts['os_distribution'] == 'Debian'
```

The internal variable cache is also deprecated for removal in 2.24. Use the
`vars` and `varnames` lookups instead. Complete both migrations before that
upgrade.

Each `ansible_facts['vgs']` entry contains an `lvs` subkey. Use the logical
volumes attached to each volume group when completeness matters; the top-level
`lvs` fact can lose entries through name deduplication.

## File modules and encodings

`blockinfile` and `lineinfile` accept `encoding` for non-UTF-8 files. The
`replace` module reads, matches, and writes Unicode text rather than bytes, so
review byte-oriented regular expressions and content handling.

Module response strings must be valid UTF-8. A non-UTF-8 response fails unless
`MODULE_STRICT_UTF8_RESPONSE` disables the check; use that setting only as a
temporary compatibility escape hatch.

## Package and repository modules

`apt` and `dnf5` accept `auto_install_module_deps`, and `deb822_repository`
accepts `install_python_debian`. Decide explicitly whether dependency
installation is acceptable on minimal or tightly controlled targets.

The `dnf` and `dnf5` modules no longer accept `install_repoquery`, and
`yum_repository` no longer accepts `keepcache`.

`rpm_key` switched to librpm and gained support for version 6 PGP keys in
2.20.4. In `2.21.3`, it adds a trailing newline to armored PGP input before
calling librpm, preventing parse failures when `pgpParsePkts` requires the
newline.

## Module result types and input shapes

The `async_status` result fields `started` and `finished` are booleans rather
than the integers `1` and `0`. Test them as booleans.

`include_vars.extensions` and `include_vars.ignore_files` require lists. The
string form of `ignore_files` is deprecated.

## Git submodules

Since 2.20.6, `git` with `track_submodules=yes` follows the branch configured
in `.gitmodules`, or the remote HEAD when no branch is configured. It no longer
assumes `master`.

## Windows targets and wrappers

Ansible 2.19 added support for Windows Server 2025 and a tech preview for signed
modules and scripts on hosts protected by Windows App Control/WDAC. WDAC audit
mode with Dynamic Code Security is supported.

PowerShell modules can request execution wrappers without importing module
utilities:

```powershell
#AnsibleRequires -Wrapper
```

In `2.21.3`, when multiple `pwsh` executables match, the PowerShell execution
wrapper selects the first result. Make executable discovery order deterministic
when a target has multiple PowerShell installations.
