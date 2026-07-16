# Core Configuration and Upgrade Behavior

This reference covers the versioned batches `4.7`, `4.8-configuration`, and `4.8`, together with service and distribution integration guidance.

## Upgrade and build requirements

### Integer validation

Since 4.7, integer configuration values receive sanity checks. An upgrade can therefore reject nonsensical values that an older release accepted. Validate inherited configurations before rollout instead of assuming prior parsing guarantees current validity.

### Build dependencies

NTS support now requires:

- Nettle 3.6 or newer
- GnuTLS 3.6.14 or newer

Building chrony without POSIX threads is no longer supported.

## Daemon and client lifecycle

### systemd readiness

`chronyd` supports systemd `Type=notify`, allowing the service to report readiness through the systemd notification protocol instead of relying only on process creation.

### Client privilege dropping and socket protection

Since 4.8, `chronyc -u` drops root privileges to the client user chosen by the configure script. Use it for root-started monitoring commands that do not need to retain root privileges.

```sh
chronyc -u tracking
```

The socket created by `chronyc` is now hidden, preventing unsafe permission changes against that socket.

### Message-log cycling

`cyclelogs` now attempts to reopen the message log selected with `chronyd -l`. Log cycling can therefore recover that output rather than leaving the original message-log destination closed.

## Remote monitoring surface

The 4.7 `opencommands` directive selects which monitoring commands are available remotely. Restrict it to the commands remote operators and monitoring systems actually require.

This is distinct from command transport and authorization: UDP access still depends on the command address, port, firewall, and `cmdallow`/`bindcmdaddress` configuration, while privileged commands still require the Unix command socket.

## Drift and local-reference behavior

### Drift-file writes

`driftfile` accepts an `interval` option (since 4.7), allowing the drift-data save frequency to be configured rather than relying on the fixed earlier behavior.

### Local synchronization waits

The `local` directive accepts `waitsynced` and `waitunsynced` (since 4.7). These provide explicit wait controls for local-reference operation while the daemon is synchronized or unsynchronized.

## Source options

### Limit selection of unreachable sources

The `maxunreach` source option from batch `4.8-configuration` limits how many polls an unreachable NTP source or refclock can remain selected. The default is 100000.

An unreachable source is retained only when both conditions hold:

1. It has not exceeded the configured `maxunreach` poll count.
2. It has a sample newer than the oldest sample from any reachable source.

```conf
server ntp.example.net maxunreach 8
refclock PPS /dev/pps0 maxunreach 4
```

Use `chronyc selectdata -v` when diagnosing the result. Uppercase `S` indicates that a source has only measurements older than reachable sources or has exceeded its `maxunreach` limit.

### Copy an upstream server's identity

The `copy` option lets a closely related client assume the reference ID and stratum of its server. A typical use is a host where one `chronyd` instance disciplines the system clock and a second instance running with `-x` serves that clock.

```conf
server 127.0.0.1 copy
```

The surrounding topology must rule out synchronization loops. The option is not supported on a `peer` source.

## Packet classification and PTP domains

### DSCP marking

The global `dscp` directive sets the Differentiated Services Code Point on transmitted NTP packets. Values range from 0 through 63; the default is 0. Networks that prioritize time traffic can, for example, use Expedited Forwarding:

```conf
dscp 46
```

### PTP-domain filtering

The `ptpdomain` directive chooses the PTP domain used to send and accept NTP-over-PTP messages. Messages from other domains are ignored. Its range is 0 through 255 and its default is 123.

```conf
ptpdomain 42
```

## Distribution and service integration

### RHEL NetworkManager dispatcher

The NetworkManager chrony dispatcher can mark sources offline while no route exists. If a route managed outside NetworkManager later appears, the dispatcher can leave those sources offline. Mask the dispatcher when sources must stay online independently of NetworkManager events:

```sh
ln -f -s /dev/null /etc/NetworkManager/dispatcher.d/20-chrony-onoffline
```

### Gentoo feature gates

Gentoo enables these USE flags by default: `caps`, `cmdmon`, `nettle`, `ntp`, `nts`, `phc`, `readline`, `refclock`, `rtc`, `seccomp`, and `sechash`.

Direct Linux PPS support is a separate, non-default `pps` flag. Check it before configuring a direct PPS refclock. NTS also depends on the GnuTLS-backed `nts` support and hashing support.

### Gentoo OpenRC options

The OpenRC service reads `/etc/conf.d/chronyd`. In the following example, `-u ntp` selects the unprivileged account and `-F 2` enables level-two seccomp filtering:

```sh
CFGFILE="/etc/chrony/chrony.conf"
ARGS="-u ntp -F 2 -s -r"
```

Add `-s` when using an RTC file, and add `-r` when using `dumponexit`. Together they restore RTC-derived time and saved measurement samples, supporting long-term averaging across restarts.
