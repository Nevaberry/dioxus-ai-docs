# Packaging, Runtime, and Service Integration

Use this reference when packaging cloud-init, maintaining service overrides,
choosing a Python runtime, rendering user templates, writing mounts, or adapting
distribution-specific behavior.

## Packaging and installation

### Installed-file layout

The packaging guidance carried by 26.1 reflects a layout change made in 25.1:
packaged files install under `/usr/lib` rather than `/lib`.

Audit downstream assumptions in:

- package manifests and file lists
- patches containing absolute installation paths
- service or image assembly that copies installed files
- validation scripts that assert the old location

Use the produced `/usr/lib` layout. Do not preserve `/lib` merely because an
older package installed cloud-init there.

### Meson build backend

The packaging guidance carried by 26.1 reflects the build-backend change made
in 25.3: cloud-init builds with Meson instead of setuptools or distutils. BSD
build support is also available through the Meson build.

When updating downstream packaging:

1. Remove the setuptools or distutils build entry point from the package
   recipe.
2. Invoke the Meson build used by the current source.
3. Inspect the generated installation layout rather than translating old
   commands mechanically.
4. Reconcile package manifests and file lists with the Meson result.
5. Include the Meson BSD path when maintaining BSD packaging.

## Service integration

### Custom systemd `ExecStart=` commands

The service guidance carried by 26.1 reflects a socket-protocol change made in
25.3. The protocol used by cloud-init's systemd units now supports alternatives
such as `ncat -U`.

Downstream replacement units and drop-ins that override `ExecStart=` must
update the command for the changed protocol. Compare each replacement command
with the current packaged command before deploying the override.

## Runtime and template safety

### Python runtime

Since 26.1, Python 3.8 is unsupported. Do not select Python 3.8 as the
interpreter for a current build or package, and update downstream runtime gates
that still admit it.

### Sandboxed Jinja rendering

Since 26.2, cloud-init renders Jinja templates in a sandbox. Existing custom
templates that depend on operations forbidden by the sandbox must be revised.

Treat this as a compatibility boundary for user-data and image-supplied
templates. Exercise custom templates through the sandboxed renderer and replace
rejected operations rather than bypassing the sandbox.

## Cloud-config modules

### Amazon Linux

Since 26.2, Amazon Linux supports these modules:

- `yum_add_repo`, for configuring Yum repositories
- `ca_certs`, for configuring trusted CA certificates

Images can use these cloud-config modules instead of maintaining separate
bootstrap steps for the same repository and certificate work.

### Rocky Linux and openEuler

Since 26.1, Rocky Linux supports the `ca_certs` module. Allow the module on
Rocky Linux instead of gating it away as unsupported.

The `cc_rh_subscription` module no longer handles openEuler. Remove openEuler
from downstream conditionals that route systems through this module.

## Mount configuration

### Escaped `fstab` paths

Since 26.2, the `mounts` module escapes special characters in mount paths when
writing `fstab`. This allows paths containing those characters to be
represented correctly.

Do not unescape or rewrite the generated path before it reaches `fstab`.
Downstream tests should compare against the escaped representation rather than
the original raw path.

## Distribution behavior and defaults

### RHEL administrator changes

Since 26.1, cloud-init no longer overwrites local changes in
`disable-sshd-keygen-if-cloud-init-active.conf` on RHEL. Preserve an
administrator's edits; do not add packaging or image-finalization logic that
restores the older overwrite behavior.

### Azure Linux 4.0

Since 26.2, Azure Linux 4.0 is supported. Remove downstream unsupported-release
gates that exist solely because this release was not recognized.

### Alpine APK mirror

Since 26.2, Alpine uses its CDN as the default APK mirror. Check the resulting
default before injecting an older mirror through image customization.

### Debian Bullseye backports

Since 26.2, Debian's backports suite selection is updated for Bullseye. Do not
hard-code the older suite selection in downstream configuration; retain the
current cloud-init selection when generating repository data.
