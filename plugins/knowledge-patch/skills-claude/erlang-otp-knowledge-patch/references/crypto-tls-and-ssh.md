# Cryptography, TLS, certificates, SSH, and SFTP

## Cryptographic algorithms

### ML-DSA and ML-KEM (since 28.1)

When OTP is built with OpenSSL 3.5, `crypto:sign/4` and `crypto:verify/5` support ML-DSA through `mldsa44`, `mldsa65`, and `mldsa87`. ML-KEM is available through `crypto:encapsulate_key/2` and `crypto:decapsulate_key/3` with `mlkem512`, `mlkem768`, and `mlkem1024`; `public_key` and `ssl` integrate both families.

### Additional TLS algorithms (since 28.3)

TLS 1.3 supports the ML-KEM hybrid groups `x25519mlkem768`, `secp384r1mlkem1024`, and `secp256r1mlkem768`. The `public_key` and `ssl` applications also support SLH-DSA.

### Preferred post-quantum defaults (since 29.0)

`ssl` prefers `x25519mlkem768`, and `ssh` prefers `mlkem768x25519-sha256`, with fallback for peers that lack support. With a suitable certificate, `ssl` prefers ML-DSA signatures followed by `slh_dsa_sha2_256f`.

### Structured unsupported-backend errors (since 29.0.3)

When the crypto backend lacks EdDH or EdDSA, `crypto:compute_key/4` and `crypto:generate_key/2,3` raise `error:{notsup, Info, Description}`.

```erlang
try crypto:generate_key(eddh, x25519) of
    Key -> Key
catch
    error:{notsup, Info, Description} ->
        {unsupported, Info, Description}
end.
```

### Input hardening (since 29.0.4)

`crypto:macN/5` no longer crashes when `MacLength` exceeds the underlying hash output. Invalid AEAD initialization no longer segfaults, and `chacha20_poly1305` key handling no longer reads past its key buffer.

## Certificate and PKI handling

### Early PEM validation (since 28.1)

TLS servers fail early when a configured PEM file is missing or invalid. Treat a bad path or bad contents as an immediate deployment or startup configuration failure.

### PKICMP ASN.1 support (since 28.2)

`public_key` 1.19 adds ASN.1 support for the Public-Key Infrastructure Certificate Management Protocol. If applying this application patch independently, first satisfy its dependency on the OpenSSL-backed `crypto` version shipped in OTP 28.1.

### SAN-only hostname validation (since 29.0.1)

`public_key` follows RFC 9525 and does not fall back to the subject common name during hostname validation (CVE-2026-42790). Certificates need a matching subject alternative name. Error matching should account for separate subject-name and subject-alternative-name constraint errors.

When patching applications separately, `ssl-11.7.1` requires matching `public_key-1.21.1`.

### Path and OCSP validation (since 29.0.1)

Expired OCSP responder certificates are rejected. Certificate-path basic-constraint validation is corrected for RFC 5280 (CVE-2026-42789).

### OCSP response limit (since 29.0.3)

OCSP responses larger than 100 KB are rejected before ASN.1 decoding. Keep validation-service responses within that limit.

### Bounded and acyclic chain construction (since 29.0.4)

Certificate path validation caps policy-tree nodes and rejects crafted `policyMappings` chains with `{bad_cert, policy_tree_exceeded}` instead of allowing exponential memory use. TLS chain building also prevents cycles caused by invalid, unordered, or extraneous certificates.

## TLS protocol behavior

### Duplicate handshake messages (since 28.2)

`ssl` 11.4.2 rejects duplicate `change_cipher_spec` messages and a second certificate message with an unexpected-message alert. Malformed peers and negative tests now fail immediately instead of leaving corrupt handshake state. An independently patched `ssl` also requires matching `crypto` and `public_key` versions.

### Alerts for malformed clients (since 29.0.1)

SSL servers send an alert for bad-client cases that previously closed silently. Tests and clients can observe an alert where the initial 29.0 release produced only a disconnect.

### TLS distribution LAN checks (since 29.0.2)

TLS distribution enforces the same-LAN restriction when `check_ip` is enabled. Connections accepted by older patch levels can be rejected; verify the intended LAN boundary and certificate setup during rollout.

### Handshake and ticket validation (since 29.0.3)

TLS clients reject application data injected in the handshake plaintext window and reject a second HelloRetryRequest. PSK binder/identity mismatches produce `illegal_parameter`. TLS 1.3 stateless tickets are checked against server lifetime and freshness data even when the client reports an age of zero.

### Pre-TLS 1.3 algorithm selection (since 29.0.4)

Clients verify that a server-selected algorithm was among those the client offered. This closes a path that could allow a man-in-the-middle to bypass server-certificate validation.

## SSH key exchange and packet handling

### Hybrid key exchange (since 28.4)

SSH supports `mlkem768x25519-sha256`, combining ML-KEM-768 with X25519.

### Explicit daemon services (since 29.0)

`ssh:daemon/2` no longer enables shell, exec, or SFTP by default. Opt in explicitly.

```erlang
ssh:daemon(Port, [
    {shell, {shell, start, []}},
    {exec, erlang_eval},
    {subsystems, [ssh_sftpd:subsystem_spec([])]}
    | Options
]).
```

### Removed OpenSSH 7.x workaround (since 29.0.3)

SSH no longer applies the obsolete SHA-1 authentication workaround for OpenSSH 7.x. Retest legacy peers that depended on it.

### Diffie-Hellman validation (since 29.0.4)

SSH enforces `1 < e/f < p-1` and `1 < K < p-1` on every DH path. For DH-GEX, clients reject `P` below 2048 bits or `G` outside `(1, P-1)`, and the default `dh_gex_limits` minimum is 2048 for both clients and servers.

### Cipher-block alignment (since 29.0.5)

The client and server in `ssh` 6.0.4 reject packets not aligned to the cipher block size. CBC uses a timing-safe discard path before disconnecting so structural errors cannot be distinguished from MAC failures; AEAD and encrypt-then-MAC disconnect immediately. This SSH application patch can be applied independently to a full OTP 29 installation.

## SFTP confinement

### `READLINK` root handling (since 29.0.2)

SFTP `READLINK` does not reveal host paths outside the configured root; returned paths stay relative to that root.

### `REALPATH` confinement and read bounds (since 29.0.3)

`REALPATH` requests containing `..` no longer reveal whether out-of-root paths exist. Read requests are limited to 255 KiB, so clients must split larger reads.
