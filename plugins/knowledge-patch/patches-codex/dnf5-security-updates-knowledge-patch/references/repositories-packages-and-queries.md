# Repositories, Packages, and Queries

## Contents

- Repository provenance
- Creating and overriding repositories
- Repository inspection
- Downloads and manifests
- Groups, environments, and package reasons
- Repoquery behavior
- Version locks
- Query formatting

## Repository provenance

`--from-repo=REPO` is supported by `download`, `install`, `upgrade`, `reinstall`, `downgrade`, `swap`, `distro-sync`, `do`, and `builddep`. It enables and validates the named source repositories. For `upgrade` and `distro-sync`, it applies only when package specifications are present.

`--installed-from-repo=REPO` is available across transaction and query commands. On `list`, it implies `--installed`. Commands also support `--from-vendor=VENDOR`.

~~~console
dnf5 upgrade --from-repo=updates kernel
dnf5 list --installed-from-repo=fedora
~~~

In query output, `from_repo` is installation provenance and is empty for packages that are not installed. `repoid` instead names the repository containing the queried package.

## Creating and overriding repositories

`config-manager addrepo --from-repofile=URL_OR_PATH` copies a validated repository file. An inline definition requires a nonempty `baseurl`, `mirrorlist`, or `metalink` supplied through `--set`.

Both forms write beneath the first `reposdir`, normally `/etc/yum.repos.d`, and reject an ID already defined elsewhere. `--save-filename` chooses the target filename; `--overwrite` permits replacing the target file; `--add-or-replace` instead adds or replaces an ID inside an existing file.

~~~console
dnf5 config-manager addrepo --from-repofile=https://example.com/example.repo
dnf5 config-manager addrepo --id=example --set=baseurl=https://example.com/packages --set=enabled=0
~~~

`config-manager setopt` writes main options to the main configuration file, normally `/etc/dnf/dnf.conf`. Repository options and `enable`/`disable` are written only to `/etc/dnf/repos.override.d/99-config_manager.repo`; source `.repo` files remain unchanged. Repository globs expand to repositories that exist now rather than becoming future matching rules.

A same-named file in `/etc/dnf/repos.override.d` masks its counterpart in `/usr/share/dnf5/repos.override.d`. Remaining overrides apply alphabetically and the last value wins. `unsetopt` removes only the main-file or config-manager layer, so a lower-layer value can become visible again.

~~~console
dnf5 config-manager setopt keepcache=1 '*-debuginfo.pkg_gpgcheck=0'
dnf5 config-manager disable '*-debuginfo'
~~~

## Repository inspection

`dnf5 repo` defaults to enabled repositories; add `--all` for disabled entries.

- `repo list --json` returns an array of `{id, name, is_enabled}` objects.
- `repo info --json` adds effective expanded `base_url` values, configuration path, priority, cost, signature settings, metadata times, package counts, size, and content tags.
- `dnf5 --dump-repo-config REPO_ID` provides similar effective configuration detail.

~~~console
dnf5 repo info --all --json
~~~

Automatic source/debug repository pairing depends on IDs. `fedora` pairs with `fedora-source` and `fedora-debuginfo`; an ID ending in `-rpms`, such as `base-rpms`, pairs with `base-source-rpms` and `base-debug-rpms`.

## Downloads and manifests

`download --resolve` omits dependencies already installed; add `--alldeps` to include them. `--srpm`, `--debuginfo`, and `--debugsource` automatically enable the matching repositories for enabled binary repositories.

`--url` prints locations instead of downloading. Repeat `--urlprotocol` to allow `http`, `https`, `ftp`, or `file`; `--allmirrors` prints space-separated URLs from every available mirror for each package.

~~~console
dnf5 download --srpm dnf5
dnf5 download --url --allmirrors --urlprotocol https python
~~~

The manifest plugin is experimental. It separates `new` and `resolve`, supports `--source` and `--use-host-repos`, rejects duplicate repository IDs, and reports a missing source RPM as an error.

## Groups, environments, and package reasons

DNF5 supports environment `install`, `remove`, and `upgrade`, and exposes `CompsTypePreferred` to select the preferred comps object type. Environment `info` distinguishes default groups from optional groups. Install and upgrade include default groups; group upgrades cover every package in the group. Already-installed groups or environments are not installed again.

`dnf5 mark user`, `dependency`, and `weak` set installation reasons. A user-marked package is protected from dependency cleanup; a dependency-marked package becomes removable when nothing requires it. `dnf5 mark group GROUP_ID PACKAGE...` associates packages with a comps group so group operations, including removal, treat them as members.

~~~console
dnf5 mark user fuse-devel
dnf5 mark group xfce-desktop vim-enhanced
~~~

## Repoquery behavior

`--whatdepends` covers requires, enhances, recommends, suggests, and supplements. `--exactdeps` is valid only with `--whatdepends` or `--whatrequires`.

`--providers-of=ATTRIBUTE` turns dependency attributes from the initially selected set into provider packages. `--recursive` is supported only for:

- `--providers-of=requires`, a forward dependency closure.
- `--whatrequires`, a reverse dependency closure.

`--available`, `--installed`, and `--arch` continue to bound packages added recursively.

~~~console
dnf5 repoquery --installed --providers-of=requires --recursive bash
dnf5 repoquery --installed --whatrequires=systemd --recursive
~~~

Installed-set audits have precise scopes:

- `--duplicates` finds multiple installed versions for a name/architecture pair but excludes install-only packages.
- `--installonly` selects install-only packages separately.
- `--extras` finds installed packages absent from every available repository.
- `--unneeded` matches the exact autoremove set.
- A negative `--latest-limit=N` selects everything except the newest `abs(N)` versions.
- `--userinstalled` excludes dependency and weak-dependency reasons, but includes explicit, comps-group, module-profile, and unknown reasons. Configuration excludes can change the result.

~~~console
dnf5 repoquery --installed --duplicates
dnf5 repoquery --userinstalled --queryformat='%{name} %{reason}\n'
~~~

After filtering, `--srpm` maps results to source RPMs and enables source repositories. Formatting selectors are mutually exclusive. Default `%{full_nevra}` includes epoch zero. Shorthand relation and file selectors sort and deduplicate values. Use `--querytags` to list supported tags.

## Version locks

`versionlock add SPEC` locks matching installed NEVRAs first. Only when no installed package matches does it lock all currently available matches. `exclude` records negative matches, `delete` removes matching rules, and `clear` removes all rules.

Locks affect transactions, not `repoquery`, `list`, or `info`. The locked installed version remains visible, allowing `reinstall`.

~~~console
dnf5 versionlock add acpi
dnf5 versionlock exclude iftop-1.2.3-7.fc38
~~~

State is stored in `/etc/dnf/versionlock.toml` using format version `1.0`. Each `[[packages]]` entry has a glob-capable name and conditions over `epoch`, `evr`, or `arch` with `<`, `<=`, `=`, `>=`, `>`, or `!=`. Conditions within one entry are ANDed; package entries are ORed.

~~~toml
version = "1.0"

[[packages]]
name = "bash"
[[packages.conditions]]
key = "evr"
comparator = "="
value = "0:5.2.15-5.fc39"
~~~

## Query formatting

`repoclosure --check=` accepts glob patterns. `repoquery --queryformat` interprets the `\n` escape. TOML-defined command aliases can consume values rather than expanding only to fixed argument lists.

~~~console
dnf5 repoclosure --check='python3-*'
dnf5 repoquery --queryformat='%{name}\n' 'python3-*'
~~~
