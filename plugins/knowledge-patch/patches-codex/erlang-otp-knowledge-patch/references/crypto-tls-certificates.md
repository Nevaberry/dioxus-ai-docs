# Cryptography, TLS, and Certificates

## Enforce certificate identity and path rules

### SAN-only hostname validation

Since 29.0.1, `public_key` follows RFC 9525 and does not fall back to a
certificate subject common name. Certificates must contain a matching subject
alternative name. Code matching `ssl` or `public_key` errors must also handle
the separate subject-name and subject-alternative-name constraint errors. This
is the hostname-validation fix for CVE-2026-42790.

For application-level patching, `ssl-11.7.1` requires the matching
`public_key-1.21.1`.

### Corrected path and OCSP validation

Since 29.0.1, expired OCSP responder certificates are rejected and certificate
path basic-constraint validation follows the corrected RFC 5280 behavior
(CVE-2026-42789).

Since 29.0.3, OCSP responses larger than 100 KB are rejected before ASN.1
decoding. Keep responder output within the limit and exercise the rejection
path in certificate-validation integrations.

Since 29.0.4, certificate path validation caps policy-tree nodes. Crafted
`policyMappings` chains now fail with
`{bad_cert, policy_tree_exceeded}` instead of consuming memory exponentially.
TLS chain building also rejects cycles caused by invalid, unordered, or
extraneous certificates.

### Fail early on invalid PEM files

Since 28.1, a TLS server fails earlier when its configured PEM file is missing
or invalid. Treat a bad path or contents as a deployment/startup configuration
failure rather than expecting a later handshake failure.

## Handle stricter TLS state machines

Since 28.2, `ssl` 11.4.2 rejects duplicate `change_cipher_spec` messages and a
second certificate message with an unexpected-message alert. Negative tests
and malformed peers that previously left corrupt handshake state now fail
immediately. An individually patched `ssl` application requires the matching
`crypto` and `public_key` versions.

Since 29.0.1, servers send an alert for malformed-client cases that previously
closed the connection silently. Protocol tests and clients should accept an
observable alert rather than requiring a bare disconnect.

Since 29.0.3, TLS clients:

- reject application data injected during the handshake plaintext window;
- reject a second HelloRetryRequest;
- answer PSK binder/identity mismatches with `illegal_parameter`; and
- always validate TLS 1.3 stateless tickets against server lifetime and
  freshness data, including when the client reports an age of zero.

Since 29.0.4, pre-TLS 1.3 clients verify that the server-selected algorithm was
one the client offered. This closes a path that could bypass server-certificate
validation.

## Use post-quantum algorithms deliberately

### ML-DSA and ML-KEM APIs

With OpenSSL 3.5 and OTP 28.1, `crypto:sign/4` and `crypto:verify/5` support:

- `mldsa44`
- `mldsa65`
- `mldsa87`

`crypto:encapsulate_key/2` and `crypto:decapsulate_key/3` support:

- `mlkem512`
- `mlkem768`
- `mlkem1024`

The `public_key` and `ssl` applications integrate both families. Check the
linked OpenSSL before enabling algorithms in configurations shared by
heterogeneous nodes.

### TLS and SSH hybrid algorithms

Since 28.3, TLS 1.3 supports `x25519mlkem768`,
`secp384r1mlkem1024`, and `secp256r1mlkem768`. `public_key` and `ssl` also
support SLH-DSA.

Since 28.4, SSH supports the hybrid key exchange
`mlkem768x25519-sha256`, combining ML-KEM-768 with X25519.

In 29.0 these algorithms became preferred defaults: `ssl` puts
`x25519mlkem768` first and `ssh` puts `mlkem768x25519-sha256` first, with
fallback for peers lacking support. Given a suitable certificate, `ssl` also
prefers ML-DSA signatures and then `slh_dsa_sha2_256f`. Recheck policy,
interoperability, and performance assumptions after an upgrade.

## Use PKICMP ASN.1 support with compatible applications

`public_key` 1.19 in OTP 28.2 adds ASN.1 support for the Public-Key
Infrastructure Certificate Management Protocol (PKICMP). When applying only
this application patch, first satisfy its dependency on the OpenSSL-backed
`crypto` version shipped in OTP 28.1.

## Handle unsupported crypto backends

Since 29.0.3, a backend without EdDH or EdDSA support makes
`crypto:compute_key/4` and `crypto:generate_key/2,3` raise the structured
exception `error:{notsup, Info, Description}`:

```erlang
try crypto:generate_key(eddh, x25519) of
    Key -> Key
catch
    error:{notsup, Info, Description} ->
        {unsupported, Info, Description}
end.
```

Match the structured tuple when implementing a supported fallback.

## Expect hardened crypto inputs

Since 29.0.4:

- `crypto:macN/5` no longer crashes when `MacLength` exceeds the underlying
  hash output length;
- invalid AEAD initialization no longer segfaults; and
- `chacha20_poly1305` key handling no longer reads beyond its key buffer.

Preserve input validation in application code, but do not depend on the former
runtime-failure shapes.

## Validate SSH Diffie-Hellman parameters

Since 29.0.4, every SSH DH path enforces `1 < e/f < p-1` and
`1 < K < p-1`. DH-GEX clients reject `P` below 2048 bits or `G` outside
`(1, P-1)`, and the default minimum in `dh_gex_limits` is 2048 for clients and
servers. Retest legacy groups and custom limit configurations.
