# Breaking Changes

## cgroup v1 Removed (v258)

Only cgroup v2 (unified hierarchy) is supported. Systems still using cgroup v1 must migrate before upgrading.

## SysV Init Scripts Removed (v260)

`systemd-sysv-generator` and `rc-local.service` are removed. All services need native unit files. There is no compatibility layer.

## `!!` ExecStart Prefix Removed (v258)

The ambient capabilities compatibility prefix is silently ignored. Remove `!!` from any `ExecStart=` lines -- it has no effect.

## Journal Default Storage Changed to `persistent` (v259)

Was `auto`. Journals are now written to `/var/log/journal/` by default. Override with `Storage=` in `journald.conf`:

```ini
# /etc/systemd/journald.conf
[Journal]
Storage=volatile
```

## IPForward= Deprecated (v256)

Use `IPv4Forwarding=` and `IPv6Forwarding=` in `.network` files or `networkd.conf`. `IPv6SendRA=` and `IPMasquerade=` now imply per-link settings, not global.

```ini
# networkd.conf -- global forwarding (replaces IPForward= in .network)
[Network]
IPv4Forwarding=yes
IPv6Forwarding=yes
```

## uaccess Tag Must Match Change Events (v258)

Rules setting the `uaccess` tag with `ACTION=="add"` no longer work. Use `ACTION!="remove"` instead:

```
# Broken since v258:
ACTION=="add", SUBSYSTEM=="hidraw", TAG+="uaccess"
# Correct:
ACTION!="remove", SUBSYSTEM=="hidraw", TAG+="uaccess"
```

## TTY Default Mode 0600 (v258)

`mesg n` is the default. Other users cannot write to terminals. Restore old behavior with build option `-Dtty-mode=0620`.

## KeepConfiguration=dynamic Replaces dhcp (v257)

`KeepConfiguration=dynamic` replaces `dhcp`. Preserves DHCPv4, DHCPv6, NDISC, and IPv4LL configs on stop (not just DHCPv4 as the old `dhcp` value did).
