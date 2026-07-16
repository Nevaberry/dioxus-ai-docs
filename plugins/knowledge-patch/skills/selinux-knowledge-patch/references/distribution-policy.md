# Distribution Policy and Activation

## openSUSE Tumbleweed defaults

Starting with Tumbleweed snapshot 20250211, new ISO installations default to
SELinux in enforcing mode. Tumbleweed minimalVM images also ship with SELinux
enabled. The installer still allows AppArmor to be selected.

Activation is driven by the installer, not by a general kernel-configuration
change. Existing Tumbleweed installations and Leap 15.x systems are therefore
unchanged; do not assume an upgrade silently switches their active LSM.

## SLE Micro policy availability

SLE Micro 6.0 installs SELinux by default through YaST and in pre-built images.
It includes a supported `targeted` policy. This differs from SLES 15 SP7, whose
SELinux support does not include a policy.

The SLE Micro default policy blocks containers from files outside container
data, including bind-mounted host paths, while permitting all network access.
See [Container policy](container-policy.md) for the Udica workflow used to
grant specific host-file access.

## Relabeling SLE Micro after SELinux was disabled

Never re-enable SELinux after it has been disabled without relabeling the
filesystem. SLE Micro supports `restorecon`, the `autorelabel` boot parameter,
and a marker-file workflow:

```console
touch /etc/selinux/.autorelabel
reboot
```

After the relabel completes, the boot replaces `/etc/selinux/.autorelabel`
with `/etc/selinux/.relabelled`. This prevents an unnecessary relabel on the
next boot. If the marker remains, investigate whether the relabel completed.

## SLES 15 SP7 support boundary

SLES 15 SP7 supplies the SELinux framework, binaries, and libraries, but no
default policy. Production use requires a custom-built policy. Third-party
policies are unsupported, and policies from the openSUSE legacy repository are
for testing only. Use SLE Micro when a supplied, supported SELinux policy is a
requirement.

Installed tools alone are therefore not evidence that an SLES host is ready to
enter enforcing mode.

## Selecting SELinux instead of AppArmor on SLES

SLES initially configures `/etc/selinux/config` for permissive mode. Add both
arguments to `GRUB_CMDLINE_LINUX_DEFAULT`:

```ini
GRUB_CMDLINE_LINUX_DEFAULT="lsm=selinux,bpf selinux=1"
```

`lsm=selinux,bpf` selects SELinux instead of AppArmor, while `selinux=1`
enables SELinux. Regenerate the GRUB 2 configuration and reboot:

```console
grub2-mkconfig -o /boot/grub2/grub.cfg
reboot
```

Remain permissive while validating the custom policy and filesystem labels;
boot selection does not supply the missing policy or make enforcing mode safe.
