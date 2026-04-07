# Server, Sources & NTS

## ipv4 / ipv6 Source Options (4.6)

Force address family for a source. Useful when a hostname resolves to both IPv4 and IPv6 but only one family is desired. Do not override chronyd `-4`/`-6` command-line flags.

```
server ntp.example.com iburst ipv4
server ntp.example.com iburst ipv6
```

## maxunreach Option (4.8)

Limits how many consecutive polls an unreachable source can stay selected before being deselected. Default is 100000 (effectively never deselects). Lower values enable faster failover to backup sources.

```
server ntp1.example.com iburst maxunreach 5
server ntp2.example.com iburst maxunreach 5
```

With `maxunreach 5`, if a source misses 5 consecutive polls, chrony deselects it and switches to the next best source.

## NTS AEAD Algorithm Selection — ntsaeads (4.6.1)

Selects AEAD algorithms for NTS authentication, listed in decreasing priority. Applies separately to client and server sides. Algorithm 15 is AES-SIV-CMAC-256, which is required by RFC 8915.

```
ntsaeads 15
```

## Leap Second List — leapseclist (4.6)

Reads leap seconds from a NIST/IERS `leap-seconds.list` file. This is an alternative to `leapsectz` (which reads from the timezone database). Only one of `leapseclist` or `leapsectz` should be configured.

```
leapseclist /usr/share/zoneinfo/leap-seconds.list
```
