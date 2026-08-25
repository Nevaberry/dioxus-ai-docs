# Transactions, Upgrades, and History

## Contents

- Transaction staging and package selection
- Check-upgrade automation
- History inspection and mutation
- Stored replay
- Offline transactions
- Major-release upgrades
- Restart detection
- Locking and reproducibility

## Transaction staging and package selection

Every command that composes a transaction supports `--offline` and `--store`. Both modes reuse cached packages. Storing overrides `keepcache` so downloaded RPMs survive. Offline downloads live under `/var/lib/dnf`; stored transactions prefix repository names except for the system repository.

`dnf5 upgrade --minimal` installs the lowest versions that fix applicable advisories, not the newest builds. `--destdir=PATH` implies download-only mode; without a destination, download-only output defaults to the current directory. `--allow-downgrade` permits dependency downgrades during resolution.

~~~console
dnf5 upgrade --minimal --security
dnf5 upgrade --destdir=/srv/update-rpms
~~~

Repository provenance can constrain transactions with `--from-repo=REPO`; see the repository reference for its command-specific behavior.

## Check-upgrade automation

`dnf5 check-upgrade` uses a nonstandard success-like status:

- Exit `0`: no updates are available.
- Exit `100`: updates are available.
- Other statuses indicate failure.

Automation must not treat every nonzero result as failure. `--minimal` reports the lowest versions that fix bugfix, enhancement, security, or new-package advisories, and advisory filters further restrict the fixes.

~~~console
dnf5 check-upgrade --minimal --security
~~~

The JSON result is an object keyed by text-output section names. Each value is an array of package objects with `name`, `arch`, `evr`, and `repository`; only the obsoleting-packages section adds an `obsoletes` array.

## History inspection and mutation

History requires transactions committed with `history_record` enabled. Address transactions by numeric ID, `last`, offsets such as `last-1`, or ranges such as `4..8`. `history list` defaults to all transactions and `history info` to the latest one.

- `undo` reverses one transaction.
- `rollback` reverses every transaction after the selected one.
- `redo` repeats one transaction, automatically ignoring extra installed packages and installed-package mismatches. It can finish an interrupted transaction, but it also overrides installation reasons for transaction packages already installed.

~~~console
dnf5 history undo last
dnf5 history rollback 8
dnf5 history redo last-1
~~~

`history list --json` returns summary objects containing transaction IDs, command lines, times, user IDs, status, release version, and altered counts. `history info --json` returns detail objects with RPM-database versions, user details, description/comment, and package entries containing NEVRA, action, reason, and repository; it also includes group or environment arrays when applicable. Empty queries return `[]`.

## Stored replay

`history store` stores the selected transaction and defaults to the latest. Replay consumes a directory containing `transaction.json`; the directory may also bundle RPMs, groups, or environments.

`dnf5 replay` normally reproduces operations exactly and errors when installed packages or versions differ. Relax checks with `--ignore-extras` and `--ignore-installed`; omit problem packages with `--skip-broken` and `--skip-unavailable`.

~~~console
dnf5 replay ./transaction --ignore-installed --skip-unavailable
~~~

## Offline transactions

Offline state lives under `/usr/lib/sysimage/libdnf5/offline`.

- `dnf5 offline status` inspects staged state.
- `dnf5 offline log` lists attempted offline boots.
- `dnf5 offline log --number=-1` reads the newest attempt.
- `dnf5 offline clean` removes the staged transaction and cached packages.
- `dnf5 offline reboot --poweroff` powers off after success but reboots after failure.

Set `DNF_SYSTEM_UPGRADE_NO_REBOOT` to suppress the workflow's automatic reboot or poweroff.

~~~console
dnf5 offline status
dnf5 offline log --number=-1
dnf5 offline reboot --poweroff
~~~

## Major-release upgrades

Fully update the current release, then let `system-upgrade download` resolve and stage packages before entering the shared offline updater.

~~~console
dnf5 --refresh upgrade
dnf5 system-upgrade download --releasever 43
dnf5 offline reboot
~~~

The download defaults to `distro-sync` behavior, including downgrades to target-release builds. `--no-downgrade` changes it to update-like behavior; `--allowerasing` permits removal of conflicting installed packages.

`system-upgrade clean`, `log`, and `reboot` operate on the same staged offline transaction. Logs accept negative boot indexes such as `--number=-1`.

Fedora supports upgrading to the next release or skipping one release; advance older installations in smaller steps. On Fedora 43, `system-upgrade` is built into the normal DNF5 command set, so do not install the DNF4-era `dnf-plugin-system-upgrade` package for this workflow.

## Restart detection

With no mode option, `dnf5 needs-restarting` checks important packages and `reboot_suggested` advisories. It exits `1` when a reboot is recommended and `0` when no requested action is found. `--reboothint` is a compatibility no-op.

`--services` aggressively reports systemd units whose executable package or dependencies changed since the unit started; it also exits `1` if it finds any. `--processes` reports both PID and command line, and process JSON also identifies the providing package. Use `--exclude-services` to omit service processes where appropriate.

~~~console
dnf5 needs-restarting
dnf5 needs-restarting --services
dnf5 needs-restarting --processes
~~~

JSON is always an array:

- Default mode returns one `type: "reboot"` object even when `reboot_required` is false.
- Service mode returns `type: "unit"` objects.
- Process mode returns `type: "process"` objects.
- Empty service or process results are `[]`.

## Locking and reproducibility

DNF5 holds the system-repository lock from repository load until process exit. The lock is `/var/lib/dnf/system-repo.lock`, and active-transaction data improves concurrent-transaction diagnostics.

When `SOURCE_DATE_EPOCH` is set, transaction and history packages are sorted deterministically and history timestamps use the supplied epoch.
