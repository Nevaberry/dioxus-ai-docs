---
name: selinux-knowledge-patch
description: SELinux current compatibility guidance. Use for SELinux work.
license: MIT
version: null
metadata:
  author: Nevaberry
---

# SELinux Knowledge Patch

Read the relevant reference before changing SELinux policy, relabeling a
filesystem, configuring container confinement, enabling a distribution policy,
or administering MLS. Policy availability, boot activation, relabel behavior,
and MLS recovery paths differ materially by platform and policy type.

## Reference index

| Reference | Topics |
| --- | --- |
| [Userspace tools and relabeling](references/userspace-tooling.md) | Removed interfaces, `secilcheck`, CIL conversion, xperms, `restorecon`, `setfiles`, `restorecond`, `mcstrans`, and build workflow |
| [Container policy](references/container-policy.md) | Udica templates, Incus, overlay transitions, ptrace control, nested containers, and confined identities |
| [RHEL MLS](references/rhel-mls-and-upgrade.md) | MLS activation, SSH administration, clearances, secure terminals, file sensitivity, and separation of duties |
| [Distribution policy and activation](references/distribution-policy.md) | openSUSE defaults, SLE Micro policy and relabeling, SLES policy availability, and boot selection |

## Breaking and removed userspace interfaces

### Replace removed process-kill options

`sandbox` and `seunshare` no longer accept `-k` or `--kill`. Use `killall -Z`
when process selection by SELinux context is required. Do not preserve the old
switches in scripts as compatibility aliases.

### Remove legacy policy syntax

`checkpolicy` no longer accepts the legacy `fscon` statement. Migrate policy
sources instead of attempting to enable a compatibility mode.

### Require Python 3 for audit tooling

`audit2why` no longer supports Python 2. Package and invoke it with Python 3.

### Emit valid CIL class permissions

A CIL `classperm` declaration must contain at least one permission. Treat an
empty declaration as invalid input rather than a harmless no-op.

## Start with the safety constraints

Before changing a host, identify all four of these:

1. The distribution and release.
2. The installed policy type, such as `targeted` or `mls`.
3. Whether the system is enforcing, permissive, or disabled.
4. Whether a complete relabel and reboot are acceptable.

Do not assume that installed SELinux binaries imply an installed or supported
policy. Do not enable enforcing mode immediately after changing policy type or
re-enabling SELinux. Relabel first, inspect denials in permissive mode, and only
then enforce.

## Relabel safely

### Guard files with multiple hard links

Library callers can pass `SELINUX_RESTORECON_SKIP_MULTILINK` to make
`selinux_restorecon(3)` refuse to relabel files with multiple hard links.
`restorecond` always applies this protection because a pathname in a watched
location such as a home directory or `/tmp` may be a link to another inode.

`setfiles -A` has a different purpose: it disables
`SELINUX_RESTORECON_ADD_ASSOC`. Do not describe `-A` as the switch that enables
the multiple-link guard.

### Account for path resolution

When `/proc` is available, `selinux_restorecon(3)` operates through
`/proc/self/fd` paths; otherwise it falls back to full paths. Without
`SELINUX_RESTORECON_REALPATH`, it follows no symlinks. With that flag, the
initial path can still canonicalize intermediate symlinks.

Audit command-line and configured paths containing intermediate symlinks when
behavior differs among `setfiles`, `restorecond`, `sandbox`, and `seunshare`.
Do not infer identical resolution semantics merely because all use libselinux.

### Continue across read-only filesystems

`restorecon` logs an error and continues when a traversal encounters a
read-only filesystem. This matters for walks crossing read-only Btrfs
subvolumes: inspect the error, but do not assume the entire walk stopped.

### Run restorecond in the foreground

Use foreground mode when supervising `restorecond` directly:

```console
restorecond -F
```

The system service uses this mode, so custom service definitions should not
expect the daemon to fork itself.

## Validate and convert policy

Use `secilcheck` to check CIL `neverallow` rules against a compiled binary
policy. This is distinct from merely compiling the CIL source.

When diagnosing generated policy, account for corrected conversion behavior:

- Module-to-CIL conversion emits `constrain` and `validatetrans` unless a
  constraint contains a level-based expression.
- It distinguishes `tunableif` from `booleanif` and omits empty conditional
  blocks.
- CIL-to-`policy.conf` conversion handles constraint name lists correctly.
- Xperm permission linking, out-of-range values, and complements at range
  boundaries are handled correctly.

Regenerate policy before hand-editing output that was produced to work around
older conversion behavior.

## Apply container policy deliberately

### Prefer generated least-privilege policy for host mounts

The default SLE Micro container policy denies access to files outside container
data, including bind-mounted host paths, while allowing all network access.
Use Udica with container inspection JSON, install the generated modules, and
start the container with the generated type via `--security-opt`.

Container policy packages can carry deployable Udica templates. This permits
Udica-generated policy to be installed on OpenShift nodes without installing
Udica on every node.

### Check runtime-specific support

Current container policy supports Incus-managed containers. Its supplied
`container_contexts` also supports containers running inside containers.

For `overlay-containers` and `overlay2-containers`, directory transitions label
new directories `container_ro_file_t`; they should not inherit `data_home_t`
merely because of where they were created.

### Honor global ptrace restrictions

Ptrace permission for `container_runtime_domain` is conditional on
`deny_ptrace` being false. Enabling `deny_ptrace` therefore restricts runtime
domains as well as the other domains governed by that boolean.

On systems with confined SELinux users, use the installed `container_u`
identity description for container workloads.

## Activate RHEL MLS conservatively

RHEL 10 MLS has no `unconfined` module: even `root` remains confined. Do not use
this MLS policy on a system running the X Window System. Users created under a
different SELinux policy cannot simply be reused under MLS.

Install and activate MLS from permissive mode, request a complete on-boot
relabel, reboot, and inspect denials:

```console
dnf install selinux-policy-mls
# Set SELINUX=permissive and SELINUXTYPE=mls in /etc/selinux/config
fixfiles -F onboot
reboot
ausearch -m AVC,USER_AVC,SELINUX_ERR,USER_SELINUX_ERR -ts recent -i
```

If remote administration is required, enable `ssh_sysadm_login` before the
first MLS boot. After MLS is active, a root login in `staff_r` must enter
`sysadm_r` with `newrole -r sysadm_r` before changing that boolean.

## Manage MLS clearances precisely

An SELinux user's default level and allowed range are separate settings. After
changing them, regenerate home-directory contexts, restore those contexts, set
the login mapping's level, and relabel the individual home.

```console
semanage user -m -L s1 -r s1-s15 staff_u
genhomedircon
restorecon -R -F -v /home/
semanage login -m -r s1 example_user
chcon -R -l s1 /home/example_user
```

`newrole -l` starts a nested shell. A single level changes the lower bound of
the current range, so changing `s0-s2` to `s1` yields `s1-s2`; `exit` returns to
the prior shell. It works only on terminal types listed in
`/etc/selinux/mls/contexts/securetty_types`. SSH is not secure by default, so
add its `tty` type only after assessing the risk.

## Make MLS file levels persistent

Membership in `mlsfilewrite` lets selected domains write below their current
lower clearance bound by promoting the file to that lower bound:

```cil
(typeattributeset mlsfilewrite (staff_t))
```

This automatic promotion is not a persistent file-context rule; `restorecon`
can revert it. For a durable sensitivity, configure the range and restore it:

```console
semanage fcontext -a -r s2 /path/to/file
restorecon -F -v /path/to/file
```

## Preserve an MLS security-administration path

The enabled `sysadm_secadm` module grants policy-administration rights to
`sysadm_r`. Before disabling it, provision a reachable `staff_u` account whose
sudo rule enters `secadm_r`. Use `semodule -d sysadm_secadm`; do not use
`semodule -r`, which deletes the packaged module and requires reinstalling the
MLS policy package to recover it.

## Verify distribution policy availability

- New openSUSE Tumbleweed ISO installations select enforcing SELinux by
  default, and minimalVM images enable it. Installer choice controls this;
  existing systems are not switched automatically.
- SLE Micro 6.0 installs a supported `targeted` policy and supports boot-time
  relabeling with `/etc/selinux/.autorelabel`.
- SLES 15 SP7 supplies the framework, binaries, and libraries but no default
  policy. Production use requires a custom-built policy; use SLE Micro when a
  supplied supported policy is required.

For the exact boot arguments, relabel markers, and support boundaries, read
[Distribution policy and activation](references/distribution-policy.md).
