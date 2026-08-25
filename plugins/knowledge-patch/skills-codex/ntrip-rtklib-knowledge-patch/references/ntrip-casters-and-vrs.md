# NTRIP Protocol, Casters, and VRS

## Contents

- [Protocol interoperability and VRS](#protocol-interoperability-and-vrs)
  - [Revision interoperability and upload changes](#revision-interoperability-and-upload-changes)
  - [Sourcetable flags that affect connection behavior](#sourcetable-flags-that-affect-connection-behavior)
  - [Service-dependent VRS position feedback](#service-dependent-vrs-position-feedback)
  - [Mountpoint names do not identify the delivered reference](#mountpoint-names-do-not-identify-the-delivered-reference)
  - [Demo5 local NTRIP caster output](#demo5-local-ntrip-caster-output)
- [BKG Professional NtripCaster](#bkg-professional-ntripcaster)
  - [BKG installation and process control](#bkg-installation-and-process-control)
  - [BKG pull relays and hidden aliases](#bkg-pull-relays-and-hidden-aliases)
  - [BKG inbound TLS termination](#bkg-inbound-tls-termination)
  - [BKG network ACL polarity](#bkg-network-acl-polarity)
  - [BKG listener and administrator authorization](#bkg-listener-and-administrator-authorization)
  - [BKG upload authorization](#bkg-upload-authorization)
  - [BKG dynamic sourcetable behavior](#bkg-dynamic-sourcetable-behavior)
  - [BKG live reload, restart, and monitoring](#bkg-live-reload-restart-and-monitoring)
  - [BKG LDAP password checks](#bkg-ldap-password-checks)
- [Hosted caster services](#hosted-caster-services)
  - [RTK2go client, provider, and secure ports](#rtk2go-client-provider-and-secure-ports)
  - [RTK2go mountpoint reservations and diagnostics](#rtk2go-mountpoint-reservations-and-diagnostics)
  - [Centipede RTKBase upload guardrail](#centipede-rtkbase-upload-guardrail)
  - [Emlid Caster role credentials](#emlid-caster-role-credentials)

## Protocol interoperability and VRS

### Revision interoperability and upload changes

Upstream RTKLIB's NTRIP client is Rev1-only. A Rev2 rover client should nevertheless accept a Rev1 reply, but that downward compatibility does not apply to base-station connections; uploads change from Rev1's `SOURCE` method and `Source-Agent` header to `POST` with `Source-Agent` deprecated in Rev2.

Do not send rover GGA until the caster has accepted the mountpoint request. Rev1 errors commonly return the sourcetable and close the connection, whereas Rev2 can return HTTP 4xx responses, so failure handling cannot rely on one status style.

### Sourcetable flags that affect connection behavior

Request `/`, not an invented path, to fetch the sourcetable; a Rev1 response starts with `SOURCETABLE 200 OK` and ends at `ENDSOURCETABLE`. In `STR` records the mountpoint is case-sensitive, `NMEA=1` means GGA is required, and authentication values `N`, `B`, and `D` mean none, Basic, and Digest.

### Service-dependent VRS position feedback

After a successful mountpoint response, send a usable NMEA-GGA immediately and then at the provider's required interval; 5–60 seconds is a common range. Strict casters may validate time, satellite count, and fix status and remain silent until the first acceptable GGA, while others inspect only latitude/longitude or continue using the first usable GGA even if later fixes become invalid.

### Mountpoint names do not identify the delivered reference

`NEAR` or `NRT` uses GGA to select a nearby physical base; `iMAX` likewise returns a nearby physical station with network-derived adjustments. `FKP` broadcasts correction gradients, while `MAC` uses RTCM master–auxiliary data.

A mountpoint named `VRS` is not proof that its reference is synthetic. Decode the stream's reference-station ECEF position (normally RTCM 1005 or 1006): a true VRS position should closely match the requested rover location, whereas iMAX/NEAR identifies a real nearby station.

### Demo5 local NTRIP caster output

The Demo5/rtkexplorer `str2str` adds an NTRIP-caster server output that is not present in every RTKLIB build. The current command reference exposes serial RTCM on port 12345 as mountpoint `BASE` with `ntripc://`:

```sh
str2str -in serial://ttyUSB1:115200 -out ntripc://:12345/BASE
```

The caster output can serve multiple clients when its input is a common serial, TCP, or NTRIP stream. Do not fan out a VRS input this way: each rover needs its own bidirectional session and position-dependent correction stream.

## BKG Professional NtripCaster

### BKG installation and process control

The packaged BKG Professional NtripCaster installs configuration under `/etc/ntripcaster`, logs under `/var/log/ntripcaster`, and web templates under `/usr/local/ntripcaster/templates`; initialize it by copying the `.dist` versions of `ntripcaster.conf`, `users.aut`, `groups.aut`, `clientmounts.aut`, `sourcemounts.aut`, and `sourcetable.dat` to their live names. Its wrapper supports `start`, `restart`, and `stop`, while `casterwatch` is intended to restart `ntripdaemon` automatically after a crash or configuration shutdown.

```sh
./ntripcaster start
```

### BKG pull relays and hidden aliases

The caster's integrated pull client defaults to NTRIP Rev1; `-2` selects Rev2, `-s` selects TLS and implicitly Rev2, `-i` supplies credentials, and `-m` maps the input to a local mountpoint. An HTTP proxy can be supplied as `-p host:port`, while omitting the remote mountpoint path pulls a raw TCP stream instead of using NTRIP.

```text
relay pull -2 -i user:pass -m /LOCAL remote.example:2101/REMOTE
relay pull -m /RAW 192.0.2.10:8000
```

An `alias /SHORT /LONGNAME` configuration keeps an old or alternate local mountpoint working, but aliases are absent from the sourcetable and the web source/listener views; they appear only in the caster log.

### BKG inbound TLS termination

The caster has no built-in secure listener, so inbound TLS must terminate in a proxy such as stunnel or Apache and forward to the caster's plain port. This arrangement is for NTRIP Rev2; BKG warns that Rev1 streaming is not sufficiently HTTP-compatible for TLS proxying.

### BKG network ACL polarity

`acl_policy 1` is a deny-list policy: matching `deny` records are blocked and all other addresses are admitted. `acl_policy 0` reverses the posture so only matching `allow` records are admitted, making it essential to allow the administrator's own address before applying it.

```text
acl_policy 0
allow all 141.74.*.*
```

### BKG listener and administrator authorization

Listener authorization is assembled from `users.aut`, `groups.aut`, and `clientmounts.aut`; a mountpoint absent from `clientmounts.aut` is unprotected. A trailing integer on a group limits that group's total simultaneous listeners, while `ipN` overrides `max_ip_connections` for connections from one client IP.

`users.aut`:

```text
alice:secret
```

`groups.aut`:

```text
fleet:alice:10
field:alice:ip3
```

`clientmounts.aut`:

```text
/BASE:fleet,field
```

The reserved `/admin:` and `/oper:` entries in `clientmounts.aut` grant groups limited administration and full operator rights respectively. These web/user-file roles are separate from the `admin_password` and `oper_password` values used by the Telnet console.

### BKG upload authorization

Rev1 sources use the single `encoder_password` from `ntripcaster.conf`; Rev2 sources instead need a `users.aut` account, membership in a `groups.aut` group, and permission for the target in `sourcemounts.aut`. A slashless `default:group` entry controls undefined upload mountpoints: that group may create them and all other groups are denied.

`users.aut`:

```text
provider1:password1
```

`groups.aut`:

```text
uploaders:provider1
```

`sourcemounts.aut`:

```text
/SYDNEY:uploaders
default:uploaders
```

### BKG dynamic sourcetable behavior

The delivered sourcetable is generated from `sourcetable.dat` but includes only listed mountpoints that are currently active, and the file itself must not contain an `ENDSOURCETABLE` record. An `STR` record's protection field is informational only; actual listener access comes from `clientmounts.aut`.

A properly authorized source may upload to an unlisted mountpoint, but it stays out of the dynamic sourcetable and can be reached only by clients that already know its name.

### BKG live reload, restart, and monitoring

After editing the configuration and authorization files, `/admin?mode=rehash` reloads them without dropping streams; `/admin?mode=resync` restarts the daemon and disconnects streams for roughly 20 seconds to one minute. Changes made only through Telnet administration commands are temporary and disappear on restart.

Prometheus-format metrics are exposed at `/admin?mode=stats&argument=prom&nohtml=1`. Daily access logs are CSV, and the caster never prunes its daily access, caster, or usage logs, so retention must be managed externally.

### BKG LDAP password checks

LDAP replaces only password verification: every permitted username must still appear in the normal authorization files, commonly with `*` as its `users.aut` password. Setting the LDAP server, UID prefix, and people context makes the caster bind as `{prefix}={user},{context}`.

```text
ldap_server 127.0.0.1
ldap_uid_prefix uid
ldap_people_context ou=people
```

## Hosted caster services

### RTK2go client, provider, and secure ports

Rovers connect to `rtk2go.com:2101` without an account, using a valid email address as the username and `none` when client software insists on a password; the password value is ignored. Base-station uploads require a mountpoint reservation and its private password, and must use the Rev1 or Rev2 style assigned to that reservation.

Port 2101 accepts unencrypted Rev1 and Rev2 sessions. Port 2102 accepts only TLS-protected Rev2 sessions, so clients should surface certificate validation problems rather than silently treating the secure port like the legacy one.

### RTK2go mountpoint reservations and diagnostics

Provider mountpoints must be unique single strings, should use letters plus `-` or `_`, must not contain commas or spaces, and must not begin with a digit; `SNIP` and several generic equipment names are reserved. Name collisions or repeated authentication failures can reject the source and eventually cause a temporary IP ban.

`http://rtk2go.com:2101/SNIP::STATUS` reports current and former streams and temporary bans. For RTCM 3.x, SNIP auto-parses and filters the stream and fills missing caster-table metadata after about 200 seconds; mixed RTCM/proprietary data, CMR/CMR+, and other unparsed formats are relayed as supplied, so the provider must furnish the caster-table entry. RTK2go does not archive the incoming streams.

### Centipede RTKBase upload guardrail

For Centipede, RTKBase's Ntrip A service uses `caster.centipede.fr:2101`, the shared password `centipede`, and a unique all-uppercase mount name of at most four characters. Configure it but do not enable the upload while the base still has approximate coordinates; enable File Service first and obtain a complete 00:00–23:59 daily recording for precise positioning.

### Emlid Caster role credentials

Signing in at `caster.emlid.com` creates the NTRIP credentials needed by both the base and rover for the assigned mountpoint. The service is receiver-agnostic as long as both roles support NTRIP and have Internet access.
