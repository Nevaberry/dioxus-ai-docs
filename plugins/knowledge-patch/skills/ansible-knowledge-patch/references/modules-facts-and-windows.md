# Modules, Facts, Results, and Windows

Unless a narrower patch release is stated, the changes in this reference are
attributed to batch `2.19-2.20`.

## Fact Names and Injection

`INJECT_FACTS_AS_VARS=true` is deprecated and is scheduled to default to
`false` in 2.24. Replace injected top-level access:

```yaml
when: ansible_os_distribution == 'Debian'
```

with namespaced fact access:

```yaml
when: ansible_facts['os_distribution'] == 'Debian'
```

The internal variable cache is also deprecated for removal in 2.24. Use the
`vars` and `varnames` lookups. Complete both migrations before that upgrade.

Every entry in `ansible_facts['vgs']` now has an `lvs` subkey. Prefer this
per-volume-group data where the top-level `lvs` fact can lose entries through
name deduplication.

## File and Text Modules

`blockinfile` and `lineinfile` accept `encoding` for files that are not UTF-8.
Set the real file encoding explicitly.

`replace` now reads, writes, and matches Unicode text rather than bytes.
Review regular expressions that previously depended on byte behavior.

## Package and Repository Modules

`apt` and `dnf5` add `auto_install_module_deps`. Decide whether a managed
target may install its own module dependencies, especially in minimal images
or locked-down environments.

`deb822_repository` adds `install_python_debian` to control installation of
its Python dependency.

The following parameters were removed in 2.20:

- `install_repoquery` from `dnf` and `dnf5`
- `keepcache` from `yum_repository`

`rpm_key` uses `librpm` and supports version 6 PGP keys as of 2.20.4.

## Results and Input Validation

The `started` and `finished` fields returned by `async_status` are booleans
instead of the integers `1` and `0`. Update schemas and exact-value assertions.

Modules returning non-UTF-8 strings now fail. `MODULE_STRICT_UTF8_RESPONSE`
can disable the check as a migration aid, but module output should be repaired
to return valid UTF-8.

`include_vars.extensions` and `include_vars.ignore_files` must be lists.
String-form `ignore_files` is deprecated.

## Vault Filters

The `vault` and `unvault` filters no longer accept `vaultid`. Remove the
parameter and use supported vault identity selection outside the filter call.

## Git Module Behavior

As of 2.20.6, `git` with `track_submodules=yes` follows the branch configured
in `.gitmodules`, or the remote HEAD when no branch is configured. It no
longer assumes `master`.

## Windows Hosts and PowerShell Modules

Ansible Core adds Windows Server 2025 support and a tech preview for signed
modules and scripts on hosts protected by Windows App Control, also known as
WDAC.

PowerShell modules can request execution wrappers without module utilities:

```powershell
#AnsibleRequires -Wrapper
```

WDAC audit mode with Dynamic Code Security is supported. Test signed-content
execution against the host's actual application-control policy before
enforcing it.
