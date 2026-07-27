# Packaging, Runtime, and Service Integration

This reference organizes the packaging, systemd, runtime, and distribution
changes carried by batch `26.1`.

## Installation layout

Since 25.1, cloud-init packages install files under `/usr/lib` rather than
`/lib`. Downstream packaging and image construction should use the current
installed paths.

Audit places that can preserve the older layout implicitly:

- package file manifests
- absolute paths in downstream patches
- image-building copy steps
- service integration that names installed helpers
- tests that assert package contents

A compatibility symlink on one system is not a reason to keep `/lib` in the
package definition. Validate the actual installation result under `/usr/lib`.

## Meson build migration

Cloud-init changed its build backend from setuptools/distutils to Meson in
25.3. Downstream packages should be reviewed for both command and layout
differences.

The migration affects assumptions such as:

- how the build is configured and invoked;
- where staged files appear;
- which files are included in the final package;
- whether downstream setuptools or distutils patches still apply.

Do not translate an old build command without checking its output. Compare the
Meson installation result with the package manifest and correct the manifest or
downstream patches deliberately.

Batch 26.1 also adds BSD support for the Meson build. BSD packaging should use
that support rather than retaining a setuptools/distutils-only build path.

## systemd socket-command compatibility

In 25.3, the socket protocol used by cloud-init's systemd units changed for
compatibility with alternative commands such as `ncat -U`.

This matters when a downstream replaces a unit's `ExecStart=`. The override is
responsible for following the changed protocol and must be updated.

Inspect effective units, including drop-ins:

```sh
systemctl cat cloud-init.service
```

For each replaced `ExecStart=`:

1. Identify the corresponding current packaged unit.
2. Compare the socket command and its arguments.
3. Update the downstream command to use the current protocol.
4. Recheck any alternative Unix-socket client, including `ncat -U`.

An override can hide vendor-unit changes, so reviewing only the file installed
by the package is insufficient when a drop-in replaces the command.

## Python support

Python 3.8 is no longer supported. Current builds, packages, test environments,
and image runtime selections must use a supported Python version instead of
pinning 3.8.

Check explicit interpreter constraints in:

- package build dependencies
- continuous-integration matrices
- image package selections
- downstream launchers

The relevant compatibility fact is the removal of Python 3.8 support; this
patch does not prescribe a particular replacement version.

## Distribution-specific module behavior

### Rocky Linux certificate management

The `ca_certs` module supports Rocky Linux. Distribution dispatch and tests can
route Rocky Linux through the supported certificate-management behavior.

### openEuler subscription handling

`cc_rh_subscription` no longer handles openEuler. Do not route openEuler
through that module based on older Red Hat-family grouping.

### RHEL sshd key-generation configuration

On RHEL, cloud-init no longer overwrites changes in
`disable-sshd-keygen-if-cloud-init-active.conf`.

Treat local edits to this file as persistent administrator configuration. A
downstream package or image customization should not reinstate the older
overwrite behavior as part of an upgrade.

## Upgrade audit

Use this compact audit when maintaining a downstream package:

- Replace `/lib` file expectations with the `/usr/lib` installation layout.
- Migrate build integration from setuptools/distutils to Meson.
- Include Meson's BSD support for BSD targets.
- Compare custom systemd `ExecStart=` commands with the changed socket
  protocol.
- Remove Python 3.8 from supported build and runtime selections.
- Enable `ca_certs` behavior for Rocky Linux.
- Stop applying `cc_rh_subscription` to openEuler.
- Preserve local RHEL edits to
  `disable-sshd-keygen-if-cloud-init-active.conf`.
