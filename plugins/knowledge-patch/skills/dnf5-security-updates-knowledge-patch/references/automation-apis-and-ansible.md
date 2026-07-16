# Automation, APIs, and Ansible

## Contents

- CLI machine-readable contracts
- D-Bus sessions, authorization, and repositories
- D-Bus queries and transactions
- D-Bus event and history interfaces
- libdnf5 API changes
- Native plugin roles
- Ansible requirements and behavior

## CLI machine-readable contracts

JSON output is available for `history list`/`info`, `list`, `repo`, `check-upgrade`, `repoclosure`, and `needs-restarting`. Advisory JSON standardizes timestamps and suppresses ordinary error text on stdout. Individual commands have distinct schemas; do not assume a common package record.

~~~console
dnf5 history list --json
dnf5 check-upgrade --json
dnf5 list --json
~~~

For shell automation, use exit status rather than whether stderr is nonempty. DNF5 can write normal transaction progress and scriptlet status, including terminal control sequences, to stderr. Scriptlet messages are grouped by origin in logs, while transaction-error scriptlet output is included on stdout.

## D-Bus sessions, authorization, and repositories

`org.rpm.dnf.v0.SessionManager.open_session(a{sv})` returns a session object path. Sessions load the system repository and enabled available repositories by default. Options can disable either load, provide string-valued configuration overrides, or replace `releasever` and `locale`. Unknown option names are silently ignored, so validate option dictionaries client-side.

~~~text
open_session({
  "load_system_repo": true,
  "load_available_repos": true,
  "releasever": "43",
  "locale": "en_US.UTF-8"
}) -> session_object_path
~~~

Most daemon methods permit unprivileged callers. Protected calls such as `Goal.do_transaction()`, repository enable/disable, and key confirmation use Polkit `CheckAuthorization()` with interaction allowed. With an authentication agent, the D-Bus call blocks for the prompt and has a hard-coded two-minute timeout.

Within a session:

- `Base.read_all_repos()` explicitly loads metadata.
- `Base.reset()` completely resets the session.
- `Base.clean()` accepts `all`, `packages`, `metadata`, `dbcache`, or `expire-cache`.
- `rpm.Repo.list()` filters ID patterns, defaults to enabled repositories, and uses `repo_attrs` to choose returned fields.
- Repository enable, disable, and key confirmation have ordinary and option-bearing method variants.

## D-Bus queries and transactions

`rpm.Rpm.list(a{sv})` returns selected package attributes as `aa{sv}`. It can filter by pattern, scope, architecture, repository, latest limit, and dependency relationship. Default pattern matching checks NEVRA, provides, filenames, and `/usr/bin` or `/usr/sbin` binary names; it is case-insensitive and includes source RPMs unless matching boolean options disable those behaviors.

For large results, use `list_fd(options, writable_fd)`. The daemon writes one JSON object per package, returns a transfer ID, closes the descriptor, then emits `write_to_fd_finished(success, transfer_id, error_msg)`. Drain the pipe concurrently: an undrained full pipe has a 30-second server timeout.

Package methods such as `Rpm.install()`, `upgrade()`, `remove()`, `distro_sync()`, `downgrade()`, and `reinstall()` add jobs to the session goal; they do not immediately modify the system. `install()` documents job options `repo_ids`, `skip_broken`, and `skip_unavailable`; `upgrade()` documents `repo_ids`.

`Goal.resolve({"allow_erasing": bool})` returns transaction-item tuples and a result:

| Result | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Success with information or warnings |
| `2` | Failure |

Clients can obtain human-readable or structured problems, execute the resolved goal, cancel only while packages are downloading, and call `Goal.reset()` before constructing another transaction in the same session.

The daemon supports download-only transactions. Its mutating APIs accept an `interactive` option on `Rpm::system_upgrade()`, `Offline` and `Repo` methods, `Goal::do_transaction()`, and `Base::clean()`.

`Offline.schedule_for_next_boot()` schedules staged work. Cancelling an offline transaction returns its state to `download-complete`. Repository-key import emits the informational `repo_key_imported` signal.

## D-Bus event and history interfaces

Track repository and package downloads with `download_add_new`, `download_progress`, `download_mirror_failure`, and `download_end`. Final transfer status is `0` for success, `1` when already present, or `2` for error.

RPM execution has separate signals for transaction start/completion, package actions, scriptlet success/error, verification, preparation, and unpack failures. Package-action progress is throttled to at most one signal every 400 ms, so small packages may have no intermediate event.

`org.rpm.dnf.v0.comps.Group.list()` selects attributes and filters by scope, ID patterns, contained packages, hidden status, and translation language. It matches group IDs but not names by default, uses scope `all`, and excludes hidden groups unless `with_hidden` is true.

The daemon exposes a `History` interface. `History.recent_changes()` returns keys `installed`, `removed`, `upgraded`, and `downgraded`, filterable by change type and Unix `since` timestamp. Installed, upgraded, and downgraded records describe the current package; upgraded and downgraded records add `original_evr`; removed records contain only the removed name, architecture, and EVR. It also supports `all_advisories` and install-only-package handling.

## libdnf5 API changes

`rpm::PackageQuery` adds `filter_from_repo_id()` and `is_dep_satisfied()`. `GoalJobSettings` exposes `set_from_repo_ids()` and `set_to_repo_ids()`. `OptionBinds` is iterable in language bindings. `OptionStringContainer` parses escapes and emits escaped values with the correct delimiter.

Direct `RepoDownloader` consumers must replace the former `download_metadata` API with `Add` and `Download`. The new API can fetch only repomd/metalink data, makes `perform()` static, and separates callback data from full-download completion callbacks.

## Native plugin roles

Native extension APIs are C++ and divide into:

- Active DNF5 plugins, which add one or more commands.
- Passive LIBDNF5 plugins, which attach library hooks.

These are distinct APIs and delivery paths, not interchangeable plugin types.

## Ansible requirements and behavior

`ansible.builtin.dnf5` is included in `ansible-core` from 2.15 and requires `python3-libdnf5` on the target. Fresh Fedora 41 installations may omit the binding, while Fedora 40-to-41 upgrades install it.

~~~console
sudo dnf5 install python3-libdnf5
~~~

From ansible-core 2.19, `auto_install_module_deps` defaults to true. If the selected interpreter cannot import the binding, the module searches system-owned interpreters, attempts dependency installation when absent, and respawns under an interpreter that can import it.

`enable_plugin` and `disable_plugin` apply only to the current install or update operation and require `python3-libdnf5` 5.2.0.0 or newer. A plugin in both lists is disabled.

~~~yaml
- name: Install with one plugin suppressed
  ansible.builtin.dnf5:
    name: httpd
    state: present
    disable_plugin:
      - actions
~~~

`allow_downgrade` is implemented by the Ansible module, not DNF5. It can make tasks non-idempotent as dependency changes affect other requested packages, and wildcard package names can produce surprising results.

Package specifications accept:

- Version comparisons only when spaces surround the operator, such as `httpd >= 2.4`.
- An absolute executable path to install its provider.
- `@`-prefixed package groups.
- Local filesystem paths or URLs to RPMs.

`security` and `bugfix` apply only with `state: latest`; like `upgrade-minimal`, they also constrain dependency updates.

~~~yaml
- name: Install a bounded version
  ansible.builtin.dnf5:
    name: "httpd >= 2.4"
    state: present
~~~

`lock_timeout` is accepted but does nothing because DNF5 has no configurable lock timeout. `validate_certs` is only a compatibility parameter for HTTPS URLs used directly as RPM sources; repository-server TLS verification is controlled by `sslverify`.

The module fully supports check and diff modes, but not Ansible `async`. Its `list` parameter is non-idempotent and intended for ad hoc `/usr/bin/ansible` calls, not playbooks; use `ansible.builtin.package_facts` for declarative inventory.
