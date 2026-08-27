# Configuration, Policies, and Plugins

## Contents

- Inspecting effective configuration
- Main and repository precedence
- Runtime overrides and variables
- Cache, metadata, and solver controls
- Signature and transaction safety
- Plugin loading and packaged plugins
- Vendor-change policies

## Inspecting effective configuration

Use global options to inspect DNF5 state:

~~~console
dnf5 --dump-main-config
dnf5 --dump-variables
dnf5 --dump-repo-config REPO_ID
~~~

`--dump-main-config` prints effective main options and `--dump-variables` prints variable values.

## Main and repository precedence

Main drop-ins from `/usr/share/dnf5/libdnf.conf.d/` and `/etc/dnf/libdnf5.conf.d/` are merged by filename and applied alphabetically. A same-named `/etc` file masks its distribution counterpart. `/etc/dnf/dnf.conf` is applied after every drop-in and has the final word.

The default `reposdir` search order is:

1. `/etc/yum.repos.d`
2. `/etc/distro.repos.d`
3. `/usr/share/dnf5/repos.d`

These directories define repositories; they are not an override stack. If an ID appears more than once, DNF5 keeps the first definition and logs an error for later definitions.

Repository override files are a separate layer. An `/etc/dnf/repos.override.d` file masks a same-named `/usr/share/dnf5/repos.override.d` file; other files apply alphabetically with the last setting winning.

## Runtime overrides and variables

`--repo=ID_OR_GLOB` enables only the selected repositories for one run. `--repofrompath=ID,PATH` creates a temporary repository after expanding variables in both fields. Adjust it with `--setopt=ID.option=value`; combine it with `--repo=ID` to exclude all other repositories.

~~~console
dnf5 --repofrompath=staging,https://repo.example/rpms --repo=staging list
~~~

`--setopt` appends to the list-valued `excludepkgs`, `includepkgs`, `installonlypkgs`, and `tsflags`. Assign an empty value first when the configured list must be replaced.

~~~console
dnf5 --setopt=excludepkgs= --setopt=excludepkgs='*.i686' upgrade
~~~

When combining `--releasever` with `--releasever-major` or `--releasever-minor`, place component overrides after `--releasever`; otherwise splitting the full release value overwrites them.

`releasever_major` and `releasever_minor` are writable variables, have matching command-line overrides, and can be supplied by package provides. Setting `releasever` through `config-manager setvar` derives both components automatically. COPR base URLs may substitute `$distname`.

`config-manager setvar` writes to the last configured `varsdir`, normally `/etc/dnf/vars`. `unsetvar` removes only that highest-priority copy and may expose a value from an earlier directory.

~~~console
dnf5 config-manager setvar --create-missing-dir myvar1=value1
~~~

Environment variables named `DNF_VAR_NAME` define repository variable `$NAME`; legacy `DNF0` through `DNF9` are retained. Variable files come from `/etc/dnf/vars`, `/etc/yum/vars`, and `/usr/share/dnf5/vars.d`. Filenames must contain only lowercase alphanumerics or underscores. Neither files nor environment values can override `arch` or `basearch`.

## Cache, metadata, and solver controls

`cacheonly` is tri-state. `all` uses only system cache data, accepts expired entries, and performs no refresh; `metadata` limits cache-only behavior to metadata.

With default `keepcache=False`, downloaded RPMs nevertheless remain cached until the next successful DNF transaction, even a transaction that installs nothing.

`primary` and `modules` metadata are always loaded. `optional_metadata_types` defaults to `comps,updateinfo`; commands can add types at runtime, and `all` includes repository metadata types unknown to DNF5. Noncritical commands such as `group list` may reuse local metadata without checking expiry, so use `--refresh` when freshness matters. `makecache` is not guaranteed to refresh on every invocation.

`max_downloads_per_mirror` is configurable. `max_parallel_downloads` governs repository downloads as well as package downloads.

`exclude_from_weak` blocks matching names or globs from being pulled solely by recommends or supplements. Default `exclude_from_weak_autodetect=True` detects unmet weak dependencies of installed packages so their providers are not later added merely as weak dependencies.

`excludeenvs` and `excludegroups` filter comps IDs or globs. Group installation defaults to `mandatory`, `default`, and `conditional` package types, excluding `optional`. For `disable_excludes`, a repository glob bypasses that repository's package excludes, `main` bypasses main-config excludes, and `*` disables package, group, and environment filtering.

The documented `best` default is true but a distribution drop-in may replace it. Even `--best` guarantees the newest version only for directly requested packages, not every solver-selected dependency.

`skip_broken` skips uninstallable packages during dependency resolution. `skip_unavailable` skips unavailable packages later while preparing the RPM transaction. Both default to false.

## Signature and transaction safety

`--no-gpgchecks` overrides `localpkg_gpgcheck`. Both `localpkg_gpgcheck` and the `nocrypto` transaction flag are enforced per transaction element. A repository setting `pgp_gpgcheck=0` is honored even when RPM signature mode is enforcing. Package objects expose `is_pkg_gpgcheck_enabled()` to inspect effective policy.

`tsflags=test` downloads packages, checks OpenPGP keys and may import new keys permanently, then runs RPM checks such as file-conflict detection without applying the transaction. Treat it as a transaction dry run, not as side-effect-free inspection.

~~~console
dnf5 --setopt=tsflags=test install PACKAGE
~~~

`--skip-file-locks` skips file locks including the system-repository lock. The narrower `skip_system_repo_lock` setting bypasses the RPM-database-corresponding lock. Both remove protection against reads concurrent with a transaction; use only when deliberately accepting that risk.

`DNF5_FORCE_INTERACTIVE=0` treats standard I/O as noninteractive and suppresses questions; `1` forces prompts even without a terminal.

## Plugin loading and packaged plugins

Core supports multiple plugin configuration directories. `LIBDNF_PLUGINS_CONFIG_DIR` replaces the libdnf5 plugin-configuration directory.

The Python loader requires configuration files, scans `python_plugins_loader.d`, and imports the library as `libdnf5`. `DNF5_PLUGINS_DIR` replaces the application-plugin directory; an empty value disables those plugins.

`Base` has a separate plugin-configuration loading API, and `ConfigMain::load_from_config()` is available. `ConfigMain`'s `enabled` option is deprecated. `dnf5 --version` lists libdnf5 plugins.

Packaged plugins include `local` and `repomanage`. The local plugin separates packages sourced from repositories with GPG checking disabled, and it is not built on RHEL 10 or newer. Transaction-flag configuration accepts `--noplugins` to suppress RPM transaction plugins.

DNF5's Actions plugin replaces the DNF4 Snapper plugin. It can run external programs before or after transactions and interact with DNF5 configuration.

## Vendor-change policies

Vendor-change policies load from TOML configuration directories instead of existing only in memory. Configuration version `1.1` adds package-based filters and more flexible matching. The policy manager no longer limits the number of policies.
