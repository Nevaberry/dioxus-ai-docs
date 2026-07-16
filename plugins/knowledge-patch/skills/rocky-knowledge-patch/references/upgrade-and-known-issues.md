# Upgrade and known issues

## Verify OpenZFS before a Rocky Linux 9.6 upgrade

The OpenZFS module available when Rocky Linux 9.6 shipped does not load on 9.6.
An update on the 2.2.8 branch fixes the issue; the 2.3 branch remains without a
compatible update. Verify that a fixed module is available before upgrading a
ZFS system.

## Account for `passt` and SELinux

On Rocky Linux 9.6 workstation, server, or virtual-host systems with a `passt`
back end installed, the interface fails to start when SELinux is enabled.

## Resolve GStreamer transaction conflicts

An upgrade to Rocky Linux 9.6 can fail its transaction test when older
`gstreamer1-plugins-ugly` and `gstreamer1-plugins-bad-freeworld` packages are
installed. Swap them to the 9.6 free builds, then retry:

```console
$ sudo dnf swap gstreamer1-plugins-ugly-1:1.22.1-1.el9.x86_64 gstreamer1-plugins-ugly-free-1.22.12-3.el9_6.x86_64
$ sudo dnf swap gstreamer1-plugins-bad-freeworld-1:1.22.1-1.el9.x86_64 gstreamer1-plugins-bad-free-1.22.12-4.el9_6.x86_64
```

## Recover a stalled Rocky Linux 10.0 installer

Anaconda can hang at a grey screen before its wizard appears on affected
hardware, including virtual machines with 3D graphics enabled. Switch from tty6
to tty1 with `Ctrl`+`Alt`+`F1`, then return with `Ctrl`+`Alt`+`F6`.

