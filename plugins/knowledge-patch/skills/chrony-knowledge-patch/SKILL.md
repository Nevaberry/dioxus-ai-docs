---
name: chrony-knowledge-patch
description: chrony
license: MIT
version: "4.8"
metadata:
  author: Nevaberry
---

# chrony 4.7–4.8 Knowledge Patch

Baseline: chrony through 4.6.x. Covered range: chrony 4.7 through 4.8, plus the included operational and deployment guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [core-configuration.md](references/core-configuration.md) | Upgrade requirements, daemon and client behavior, source options, packet controls, logging, service integration |
| [reference-clocks.md](references/reference-clocks.md) | RTC, PHC, PPS, GPS, gpsd, reachability, locking, startup, and time scales |
| [hardware-timestamping-and-ptp.md](references/hardware-timestamping-and-ptp.md) | Hardware timestamping, interleaved NTP, NTP-over-PTP, transparent clocks, PHCs, and virtualization |
| [network-time-security.md](references/network-time-security.md) | NTS client state, authentication diagnostics, server setup, policy compatibility, and verification |
| [monitoring-and-troubleshooting.md](references/monitoring-and-troubleshooting.md) | `chronyc`, exporter metrics, source selection, transport errors, client records, and network recovery |

## Using this patch

- Check the upgrade notes before carrying an older configuration or build setup forward.
- Use the quick references below for common decisions, then load the indexed topic file for constraints and edge cases.
- Treat examples as fragments: retain the access controls, source diversity, measured offsets, and platform-specific paths required by the deployment.

## Breaking changes and upgrade checks

### Configuration and build compatibility

- Since 4.7, integer configuration values receive sanity checks. Values that were accepted despite being nonsensical can now fail validation.
- NTS builds require Nettle 3.6 or newer and GnuTLS 3.6.14 or newer.
- Building without POSIX threads is no longer supported.
- On RHEL, the FIPS and OSPP profiles are incompatible with NTS and can make an NTS-configured daemon exit fatally. A service-only exception can be set in `/etc/sysconfig/chronyd`:

```sh
GNUTLS_FORCE_FIPS_MODE=0
```

### Security and compatibility behavior

- In 4.8, root-run `chronyc -u` drops privileges to the configured client user.
- The `chronyc` socket is hidden to prevent unsafe permission changes against it.
- Keep both endpoints of an NTP-over-PTP connection on the same chrony version.
- Do not discipline the physical PHC used for hardware-timestamped NTP-over-PTP; use a virtual clock if PTP must share the interface.

## Core 4.7–4.8 configuration

### Source retention and identity

The `maxunreach` source option, added in batch `4.8-configuration`, limits the number of polls for which an unreachable NTP source or refclock can remain selected. It defaults to 100000, and retention also requires a sample newer than the oldest sample from any reachable source.

```conf
server ntp.example.net maxunreach 8
refclock PPS /dev/pps0 maxunreach 4
```

The `copy` option lets a closely related client assume an upstream server's reference ID and stratum. It is useful when one daemon disciplines the system clock and a second `chronyd -x` serves it. Prevent synchronization loops; `peer` does not support `copy`.

```conf
server 127.0.0.1 copy
```

### Traffic and remote-command controls

- `opencommands` selects which monitoring commands are remotely available. Expose only the required command surface.
- `dscp` marks transmitted NTP packets with a DSCP value from 0 through 63; the default is 0. For example, `dscp 46` selects Expedited Forwarding.
- `ptpdomain` filters NTP-over-PTP traffic by PTP domain. Its range is 0 through 255 and its default is 123.

```conf
dscp 46
ptpdomain 42
```

### Persistence and lifecycle

- `driftfile` accepts an `interval` option to control drift-data write frequency.
- `local` accepts `waitsynced` and `waitunsynced` for explicit synchronized and unsynchronized wait behavior.
- `chronyd` supports systemd `Type=notify` readiness signaling.
- `cyclelogs` attempts to reopen the message log selected by `-l`.

## Selection and reachability

`chronyc sources` prints `Reach` as an eight-bit poll history in octal. A set bit records a valid response or refclock sample; it does not prove the measurement passed every synchronization test.

In `chronyc selectdata`, uppercase `S` means that the source has only measurements older than reachable sources or has exceeded its `maxunreach` limit.

```sh
chronyc sources -v
chronyc selectdata -v
```

For a persistent network-delay increase, NTP test C can reject measurements for hours while older low-delay samples define its expectation. Inspect with `ntpdata`; if the change is permanent, clear retained samples.

```sh
chronyc ntpdata
chronyc reset sources
```

Repeated cases can be mitigated with a larger `maxclockerror`, or a very large `maxdelaydevratio` that effectively disables the test at the cost of weaker delay filtering.

## Reference clocks and PPS/GPS

### New and changed drivers

- Batch `4.7` adds an RTC refclock driver.
- A PHC refclock can use a network-interface name instead of a `/dev/ptpN` path.
- Refclocks no longer need multiple samples per poll and remain reachable when excessive-delay samples are discarded.
- In batch `4.8`, `extpps` works on Linux 6.15 and newer.
- Refclock samples are validated before updating reachability, so invalid samples no longer make a source appear reachable.

### Lock a precise PPS to coarse time of day

For one GPS receiver providing NMEA through gpsd SHM and PPS through `/dev/pps0`, lock PPS to the NMEA refid and mark PPS trusted. This allows PPS selection even when the much less accurate correlated NMEA source is a falseticker.

```conf
refclock SHM 0 refid NMEA offset 0.000 precision 1e-3 poll 0 filter 3
refclock PPS /dev/pps0 refid PPS lock NMEA poll 3 trust
```

Measure late NMEA delivery using statistics logs. A message arriving 900–1000 ms after its pulse can lock PPS to the wrong whole second; apply the opposite of the measured NMEA estimated offset and improve or reduce serial output if needed.

### gpsd socket choice

- gpsd 3.25 adds `/run/chrony.clk.ttyX.sock` for serial date-time; the older `/run/chrony.ttyX.sock` carries PPS only.
- Use the `.clk.` socket as a non-selected lock source, or use `SHM 0` with older gpsd.
- For a gpsd-backed SOCK refclock, start gpsd after `chronyd` creates the socket and pass `-n` so gpsd polls without waiting for a client.

## Hardware timestamping and NTP-over-PTP

Check `ethtool -T` before enabling hardware timestamps. The interface needs hardware transmit and receive timestamping, a matching `/dev/ptpN`, and `HWTSTAMP_FILTER_ALL` for ordinary NTP packets.

```sh
ethtool -T eth2
```

A local hardware-timestamped client can poll both NTP and the hardware clock at 16 Hz. F323 is experimental and improves stability when both endpoints support it.

```conf
server 192.168.123.1 minpoll -4 maxpoll -4 xleave extfield F323 filter 5
hwtimestamp * minpoll -4
```

For one-step end-to-end transparent switches, put NTP in PTP event messages on port 319 and request F324 at the client. Two-step, peer-to-peer, and boundary PTP clocks do not provide useful corrections for this mode.

```conf
server 192.168.123.1 xleave extfield F324 port 319
ptpport 319
```

At nanosecond precision, set a smaller `clockprecision`, at least on the server. Cross timestamping is automatic when the kernel provides it; `nocrossts` disables it. Transparent-clock corrections do not remove asymmetric PCIe latency between the NIC and system clock.

Limit `hwtimestamp` to interfaces not used by another timestamping application. Large interleaved-mode servers also need enough `clientloglimit` space for per-client transmit timestamps.

## Network Time Security

Require NTS on a source with `nts`, and persist established state with `ntsdumpdir` to avoid a fresh NTS-KE exchange after every reboot.

```conf
server time.example.com iburst nts
ntsdumpdir /var/lib/chrony
```

Check authentication with `chronyc -N authdata`. A working NTS source reports mode `NTS`, nonzero `KeyID`, `Type`, and `KLen`, no NAKs, and at least one stored cookie. Packet reachability alone does not establish authentication, and failed negotiation does not downgrade silently.

An NTS server needs a readable PEM key, a PEM certificate file containing required intermediates, TCP 4460 for NTS-KE, and UDP 123 for NTP.

```conf
ntsserverkey /etc/pki/tls/private/time.example.com.key
ntsservercert /etc/pki/tls/certs/time.example.com.crt
ntsdumpdir /var/lib/chrony
```

Verify from another host without changing its clock, then inspect server counters:

```sh
chronyd -Q -t 3 'server time.example.com iburst nts maxsamples 1'
chronyc serverstats
```

## Monitoring and first-response diagnostics

With `cmdport 0`, the exporter can use `unix:///run/chrony/chronyd.sock` instead of `[::1]:323`. The extended `ntpdata` source collector requires the socket; run the exporter as root or the chrony user, and add `--collector.chmod-socket` when running as root.

```sh
chrony_exporter --chrony.address=unix:///run/chrony/chronyd.sock \
  --collector.sources.with-ntpdata --collector.chmod-socket
```

An absolute clock-error bound is:

```promql
abs(chrony_tracking_last_offset_seconds) + chrony_tracking_root_dispersion_seconds + (0.5 * chrony_tracking_root_delay_seconds)
```

- `506 Cannot talk to daemon`: check daemon availability, UDP 323, firewall rules, and `cmdallow`/`bindcmdaddress`.
- `501 Not authorised`: the command needs the privileged Unix socket, or the socket directory ownership or permissions prevented its creation.
- `activity` reporting unknown addresses means DNS resolution is incomplete; `chronyc -N sources -a` still shows configured names.
- Windows NTP sources can advertise several seconds of root dispersion. Confirm with `ntpdata`, then raise `maxdistance` only as far as required.
- After an unannounced disconnection, `chronyc online` triggers immediate measurements when connectivity returns; pair it with `offline` handling.

## Platform deployment checks

- A KVM guest needs `CONFIG_PTP_1588_CLOCK_KVM` for a virtual PHC.
- On RHEL, mask `20-chrony-onoffline` if routes managed outside NetworkManager must not leave sources offline.
- On Gentoo, direct Linux PPS is a separate non-default `pps` USE flag; verify the other required time, security, and refclock feature gates.
- Gentoo OpenRC reads `/etc/conf.d/chronyd`; `-u ntp -F 2` selects the account and level-two seccomp, while `-s -r` restores RTC-derived time and saved samples when configured.
- VMware Tools immediately steps a resumed guest to repair the lifecycle-induced offset created while the guest clock and synchronizer were suspended.
