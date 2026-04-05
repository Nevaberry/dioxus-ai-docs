# openSUSE Leap 15.6 (2024-06-10)

## Bumblebee Removed

The X11:Bumblebee packages (`bbswitch`, `bumblebee`, `bumblebee-status`, `primus`) are removed from the distribution. They are superseded by [NVIDIA SUSE Prime](https://en.opensuse.org/SDB:NVIDIA_SUSE_Prime).

## Cockpit Web Console (New)

Cockpit is newly part of openSUSE Leap 15.6 for web-based system administration. Root password login is disabled by default (matching sshd behavior).

To enable root login:
1. Edit `/etc/cockpit/disallowed-users` and remove `root`
2. Restart: `systemctl restart cockpit.socket`

## NVIDIA GPU Drivers

### nouveau disabled for Turing/Ampere

The `nouveau` driver is experimental for Turing and Ampere GPUs and is disabled by default.

### openGPU driver recommendation

Install:
- `nvidia-open-driver-G06-signed-kmp-default`
- `kernel-firmware-nvidia-gsp-G06`

Then uncomment in `/etc/modprobe.d/50-nvidia-default.conf`:
```
options nvidia NVreg_OpenRmEnableUnsupportedGpus=1
```

To use `nouveau` anyway: add `nouveau.force_probe=1` to kernel boot parameters and do not install the openGPU packages.

## Secure Boot and Third-Party Drivers

Kernel module signature check (`CONFIG_MODULE_SIG=y`) requires proper signing for third-party drivers. KMPs from official repos are signed. For custom modules, generate a certificate and enroll in MOK database.

For NVIDIA drivers specifically, enroll MOK key per [NVIDIA driver instructions](https://en.opensuse.org/SDB:NVIDIA_drivers#Secureboot).

## Signing Key

4096-bit RSA RPM and repository signing key (replacing 2048-bit). Introduced to 15.4 users via maintenance update. Users from older releases must import manually.

## python-podman

Now based on `podman-py` project (was `python-podman`).

## Transactional Server Role

Available as installation system role. Uses Btrfs snapshots for atomic updates. Root filesystem mounted read-only. `/etc` uses OverlayFS, `/var` is separate writable subvolume.

Commands: `transactional-update up`, `transactional-update pkg in PACKAGE`, `transactional-update rollback`.

Minimum 12 GB disk space required. YaST does not work in transactional mode.

## Desktop

KDE 4 and Qt 4 packages removed. Plasma 5 and Qt 5 are current. Some Qt 4 packages may remain for compatibility.

## iotop

`iotop` requires kernel boot parameter `delayacct` or sysctl `kernel.task_delayacct=1` to display SWAPIN and IO% values (since kernel 5.14).

## Raspberry Pi 4

Network install image hangs on USB boot. Fix: add `console=tty` boot parameter.
