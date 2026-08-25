# TLS and Certificates

## Per-certificate frontend policy

The 3.2.0 frontend `ssl-f-use` directive references a certificate in a
`crt-store` independently of `bind`. It can attach certificate-specific TLS
versions, ALPN, ciphers, and signature algorithms without a separate crt-list.

```haproxy
crt-store my_files
    load crt "foo.com.crt" key "foo.com.key" alias "foo"

frontend mysite
    bind :443 ssl
    ssl-f-use crt "@my_files/foo" ssl-min-ver TLSv1.2
```

## HTTP-01 ACME workflow

Experimental built-in ACME in 3.2.0 is intended for one load balancer and
requires `expose-experimental-directives`. An `acme` section configures the
directory, account, HTTP-01 challenge, and virtual map; the `crt-store` load
associates certificate domains and an account.

```haproxy
global
    expose-experimental-directives

acme letsencrypt-staging
    directory https://acme-staging-v02.api.letsencrypt.org/directory
    account-key /etc/haproxy/account.key
    contact admin@example.com
    challenge HTTP-01
    map virt@acme

crt-store my_files
    crt-base /etc/haproxy/
    key-base /etc/haproxy/
    load crt "example.com.pem" acme letsencrypt-staging domains "example.com" alias "example"
```

The HTTP frontend must serve `/.well-known/acme-challenge/` from the ACME map.
`acme renew @my_files/example` starts issuance and `acme status` lists tasks.
The resulting certificate is only in running memory until saved with
`dump ssl cert @my_files/example`.

## DNS-01 ACME workflow

HAProxy 3.3.0 adds DNS-01 through Data Plane API 3.3. The API talks to the DNS
provider and saves issued certificates to the load balancer filesystem. The
workflow still targets a single load balancer; synchronize certificates
manually when several instances terminate TLS.

The `acme` trace source exposes automation events:

```haproxy
traces
    trace acme sink stdout level user event +any verbosity clean start now
```

The Master CLI `dpapi` event ring can also carry ACME notifications.

## Automatic backend SNI

From 3.3.0, server-side TLS derives SNI automatically from the HTTP `host`
header. Use `sni-auto` and `no-sni-auto` for traffic and
`check-sni-auto` and `no-check-sni-auto` for health checks. Combining
`strict-sni` with `default-crt` on a frontend `bind` warns because the
policies conflict.

## Protected private keys

The 3.3.0 global `ssl-passphrase-cmd` names a script that returns the
passphrase for an encrypted key. Previously obtained passphrases are tried
before the script is invoked again.

```haproxy
global
    ssl-passphrase-cmd /usr/local/bin/tls-key-passphrase
```

Make the script non-interactive, tightly permissioned, and safe under reload.

## Experimental Encrypted Client Hello

The 3.3.0 `ech` argument on a TLS `bind` enables Encrypted Client Hello and
requires `expose-experimental-directives`. Clients must retrieve the matching
public key from DNS, so test DNS publication and fallback behavior together.

## Certificate-list aliases

Since 3.3.0, Runtime API `add ssl crt-list` no longer requires a certificate
filesystem path to match its in-memory name, enabling `crt-store` aliases with
`crt-list`. The caller must ensure the supplied path or alias resolves to the
intended certificate.

Use the 3.3.0 `haproxy-dump-certs` utility to persist certificates retrieved
through a stats or master socket.

## TLS tracing and ClientHello samples

The Runtime API trace command gained the `ssl` source in 3.2.0. ClientHello
capability fetches from the same release are `req.ssl_cipherlist`,
`req.ssl_keyshare_groups`, `req.ssl_sigalgs`, and
`req.ssl_supported_groups`; they return binary values. Also,
`accept_date` and `request_date` fall back to session time when a failure
occurs before a stream exists.

The 3.4.0 `ssl_fc_crtname` fetch returns the name of the selected incoming
certificate.

## Binary and cryptographic converters

HAProxy 3.3.0 adds `base2`, which renders each input byte as eight binary
digits, and `le2dec`, which renders little-endian chunks as unsigned decimal.
`aes_gcm_enc` and `aes_gcm_dec` accept an optional AAD argument.

HAProxy 3.4.0 adds `jwt_decrypt_cert`, `jwt_decrypt_secret`, and
`jwt_decrypt_jwk` for JWT decryption with a certificate, base64-encoded secret,
or JSON Web Key. `aes_cbc_enc` and `aes_cbc_dec` operate on raw bytes using
AES-128, AES-192, or AES-256 CBC according to their bits argument. Validate
input encodings explicitly and keep authentication requirements distinct from
encryption.

## TLS 1.3 KeyUpdate limits

HAProxy 3.4.3 adds `tune.ssl.keyupdate-rate-limit` to bound peer-triggered TLS
1.3 KeyUpdate processing. Set a deliberate limit on public listeners and
monitor rejected or delayed update behavior during rollout.
