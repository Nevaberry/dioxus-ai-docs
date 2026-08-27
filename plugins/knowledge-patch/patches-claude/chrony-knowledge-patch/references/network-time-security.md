# Network Time Security

## Build and policy prerequisites

NTS support requires Nettle 3.6 or newer and GnuTLS 3.6.14 or newer. Current builds also require POSIX threads.

On RHEL, the FIPS and OSPP profiles are incompatible with chrony NTS. An NTS-configured `chronyd` can abort with a fatal error under either profile. To exempt only this service, add the GnuTLS override before restarting it:

```sh
# /etc/sysconfig/chronyd
GNUTLS_FORCE_FIPS_MODE=0
```

This changes the cryptographic-policy behavior for chronyd; keep the exception explicit and scoped to the service.

## Require and persist authenticated client state

The `nts` source option requires authenticated synchronization. `ntsdumpdir` preserves established NTS state so a reboot does not force a new NTS-KE exchange.

```conf
server time.example.com iburst nts
ntsdumpdir /var/lib/chrony
```

On RHEL, DHCP can inject unauthenticated NTP sources through:

```conf
sourcedir /run/chrony-dhcp
```

Remove that source directory when DHCP-provided, unauthenticated sources must not be mixed with explicitly configured NTS sources.

## Diagnose authentication separately from reachability

Inspect authentication and packet exchange independently:

```sh
chronyc -N authdata
chronyc -N sources
```

For a working source, `authdata` reports:

- `Mode` equal to `NTS`
- Nonzero `KeyID`, `Type`, and `KLen`
- No NAKs
- At least one stored cookie

A nonzero `Reach` value in `sources` confirms packet exchange, but it does not replace the authentication check. If NTS negotiation fails, that source remains unused; chronyd does not silently downgrade it to unauthenticated synchronization.

## Configure an NTS server

The server needs:

- A PEM private key
- A PEM certificate file that contains the required intermediate certificates
- Key and certificate files readable by the chrony user
- A persistent NTS dump directory
- Client access to TCP port 4460 for NTS-KE
- Client access to UDP port 123 for protected NTP

```conf
ntsserverkey /etc/pki/tls/private/time.example.com.key
ntsservercert /etc/pki/tls/certs/time.example.com.crt
ntsdumpdir /var/lib/chrony
```

## Verify the complete server path

From a different host, run a one-sample query that performs NTS-KE and obtains a protected NTP response without changing the local clock:

```sh
chronyd -Q -t 3 'server time.example.com iburst nts maxsamples 1'
```

Then inspect the server:

```sh
chronyc serverstats
```

Successful end-to-end use should make both `NTS-KE connections accepted` and `Authenticated NTP packets` nonzero.
