---
name: chrony-knowledge-patch
description: "Chrony NTP changes since training cutoff (latest: 4.8) — RTC refclock, PHC by interface name, opencommands, local waitsynced/activate, NTS AEAD, maxunreach failover. Load before working with chrony configuration."
license: MIT
version: "4.8"
metadata:
  author: Nevaberry
---

# Chrony Knowledge Patch (4.6 – 4.8)

Baseline: NTP basics, chrony as NTP client/server, basic chrony.conf directives.
Covers: 4.6 through 4.8 (2024-09 to 2025-08).

## Index

| Topic | Reference | Key features |
|---|---|---|
| Refclock drivers | [references/refclock-drivers.md](references/refclock-drivers.md) | RTC driver, PHC by interface name |
| Server, sources & NTS | [references/server-sources-and-nts.md](references/server-sources-and-nts.md) | ipv4/ipv6, maxunreach, ntsaeads, leapseclist |
| Local reference & orphan mode | [references/local-reference-and-orphan.md](references/local-reference-and-orphan.md) | waitsynced/waitunsynced, activate option |
| Monitoring & misc | [references/monitoring-and-misc.md](references/monitoring-and-misc.md) | opencommands, driftfile interval, ptpdomain, rate limiting, chronyc -u |

---

## New Directives & Options Quick Reference

| Directive / Option | Context | Since | Description |
|---|---|---|---|
| `refclock RTC` | `chrony.conf` | 4.7 | RTC hardware clock as refclock source |
| PHC by interface name | `refclock PHC` | 4.7 | Use `eth0` instead of `/dev/ptpN` |
| `opencommands` | `chrony.conf` | 4.7 | Unauthenticated remote monitoring commands |
| `waitsynced` / `waitunsynced` | `local` | 4.7 | Control local reference activation timing |
| `driftfile ... interval N` | `chrony.conf` | 4.7 | Minimum seconds between drift file writes |
| `ntsaeads` | `chrony.conf` | 4.6.1 | NTS AEAD algorithm selection |
| `leapseclist` | `chrony.conf` | 4.6 | Read leap seconds from NIST/IERS file |
| `activate` | `local` | 4.6 | Min root distance before local activates |
| `ipv4` / `ipv6` | `server`, `pool` | 4.6 | Force address family per source |
| `maxunreach` | `server`, `pool` | 4.8 | Max polls before deselecting unreachable source |
| `kod` | `ratelimit` | 4.6 | Send KoD RATE responses |
| `ptpdomain` | `chrony.conf` | 4.6 | PTP domain for NTP-over-PTP |
| `chronyc -u` | CLI | 4.8 | Drop root privileges in chronyc |

---

## Breaking / Important Behavioral Changes

### RTC refclock excludes rtcfile/rtcsync (4.7)

The new `refclock RTC` driver cannot be combined with `rtcfile` or `rtcsync` directives. If migrating an RTC-tracking setup to use the refclock driver, remove the old directives.

```
refclock RTC /dev/rtc0
# Do NOT also have rtcfile or rtcsync in the same config
```

---

## Essential Patterns

### Fast failover with maxunreach (4.8)

Limit how many polls an unreachable source stays selected. Default is 100000 (effectively infinite). Lower values enable faster failover to backup sources.

```
server ntp1.example.com iburst maxunreach 5
server ntp2.example.com iburst maxunreach 5
```

### Local stratum server with sync guards (4.6 + 4.7)

Combine `activate` (require initial sync) with `waitsynced`/`waitunsynced` (timing guards) for robust local stratum servers:

```
server ntp.upstream.com iburst
local stratum 10 orphan distance 0.0 activate 0.5 waitsynced 7200 waitunsynced 300
```

- `activate 0.5` — local reference only activates after root distance first drops below 0.5s (ensures at least one upstream sync)
- `waitsynced 7200` — wait 2h after last clock update before activating local
- `waitunsynced 300` — deactivate local after 5min without upstream updates

### Unauthenticated remote monitoring (4.7)

Allow specific chronyc monitoring commands without NTS/authentication:

```
cmdallow 192.168.0.0/16
opencommands sources sourcestats tracking activity
```

Available commands: `activity`, `authdata`, `clients`, `manual`, `ntpdata`, `rtcdata`, `selectdata`, `serverstats`, `smoothing`, `sourcename`, `sources`, `sourcestats`, `tracking`.

### PHC refclock by network interface (4.7)

Use network interface names directly instead of discovering `/dev/ptpN`:

```
refclock PHC eth0 poll 0 dpoll -2
refclock PHC enp3s0:extpps:pin=0 width 0.2 poll 2
```

### RTC as refclock source (4.7)

Use the hardware Real Time Clock as a time source. Cannot be combined with `rtcfile` or `rtcsync`. Supports `utc` option for clocks keeping UTC.

```
refclock RTC /dev/rtc0
refclock RTC /dev/rtc0:utc
```

---

## Source & Address Options

### Force address family per source (4.6)

```
server ntp.example.com iburst ipv4
server ntp.example.com iburst ipv6
```

Do not override chronyd `-4`/`-6` command-line flags.

### Leap second list (4.6)

Alternative to `leapsectz` — reads leap seconds directly from a NIST/IERS file:

```
leapseclist /usr/share/zoneinfo/leap-seconds.list
```

---

## NTS Authentication

### AEAD algorithm selection (4.6.1)

`ntsaeads` selects AEAD algorithms for NTS, in decreasing priority. Algorithm 15 is AES-SIV-CMAC-256 (required by RFC 8915). Applies separately to client and server sides.

```
ntsaeads 15
```

---

## Server Operations

### Reduce driftfile writes (4.7)

Control minimum interval (seconds) between driftfile updates. Default 3600. Useful for flash-based storage:

```
driftfile /var/lib/chrony/drift interval 300
```

### KoD rate limiting (4.6)

Enable Kiss-o'-Death RATE responses for rate-limited NTP clients (without `kod`, limited requests are silently dropped):

```
ratelimit interval 1 burst 4 kod
```

### PTP domain for NTP-over-PTP (4.6)

```
ptpdomain 123
```

Default is 123. NTP-over-PTP encapsulates NTP packets within PTP event messages for hardware timestamping.

### Drop privileges in chronyc (4.8)

```bash
chronyc -u sources
chronyc -u tracking
```

The `-u` flag drops root privileges. The unprivileged user is set at compile time.

---

## Reference Files

- **[references/refclock-drivers.md](references/refclock-drivers.md)** — RTC refclock driver details, PHC by interface name with all options
- **[references/server-sources-and-nts.md](references/server-sources-and-nts.md)** — ipv4/ipv6 per-source, maxunreach failover, ntsaeads algorithm selection, leapseclist
- **[references/local-reference-and-orphan.md](references/local-reference-and-orphan.md)** — waitsynced/waitunsynced timing, activate threshold, combined patterns
- **[references/monitoring-and-misc.md](references/monitoring-and-misc.md)** — opencommands remote monitoring, driftfile interval, ptpdomain, KoD rate limiting, chronyc -u
