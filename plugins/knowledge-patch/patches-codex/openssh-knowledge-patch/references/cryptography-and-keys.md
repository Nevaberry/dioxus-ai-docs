# Cryptography, Certificates, and Keys

## Algorithm removals and changed defaults

### Remove legacy cryptography dependencies (batch 10.0-10.3)

- OpenSSH 10.0 removes DSA signature support entirely.
- The server default `KexAlgorithms` no longer contains finite-field
  `diffie-hellman-group*` or `diffie-hellman-group-exchange-*` methods. The
  client default was not changed at the same time, so test each endpoint role.
- A present moduli file with no suitable groups no longer falls back to
  compiled-in groups.
- OpenSSH 10.1 removes experimental XMSS keys.
- OpenSSH 10.3 drops compatibility for peers that cannot rekey. Upgrade or
  replace those peers rather than broadly weakening policy.

### Adopt the new cryptographic defaults and warnings (batch 10.0-10.3)

- OpenSSH 10.0 makes `mlkem768x25519-sha256` the default key exchange.
- Cipher preference is ChaCha20/Poly1305, AES-GCM 128/256, then AES-CTR
  128/192/256.
- From 10.1, a non-post-quantum negotiated key exchange produces a default-on
  warning. Configure it with `WarnWeakCrypto`.
- The client warns that SHA1 SSHFP records will eventually be ignored, and
  `ssh-keygen -r` emits only SHA256 SSHFP records. Migrate DNS records and
  consumers away from SHA1.

## Algorithm configuration

### Enable the composite signature explicitly (batch 10.4)

OpenSSH supports an experimental composite post-quantum signature combining
ML-DSA 44 with Ed25519. Generate the key with:

```sh
ssh-keygen -t mldsa44-ed25519
```

The scheme is disabled by default. Add it explicitly wherever it should be
negotiated, including applicable `HostKeyAlgorithms` and
`PubkeyAcceptedAlgorithms` lists. Key generation alone does not enable it.

### Validate cipher and MAC lists early (batch 10.4)

Invalid cipher or MAC lists in configuration files and command-line arguments
are rejected while processing configuration rather than at a later runtime
operation. Validate generated lists at configuration-test time.

### Keep ECDSA allowlists exact (batch 10.0-10.3)

From 10.3, listing one ECDSA algorithm in `PubkeyAcceptedAlgorithms` or
`HostbasedAcceptedAlgorithms` admits only that exact algorithm. Older releases
could admit every ECDSA variant when any ECDSA name appeared. Audit whether an
old configuration accidentally relied on that broader behavior.

## Revocation and certificate principals

### Split revocation material across files (batch 10.0-10.3)

From 10.3, client `RevokedHostKeys` and server `RevokedKeys` accept multiple
files. External concatenation is unnecessary:

```sshconfig
RevokedKeys /etc/ssh/revoked-keys /etc/ssh/emergency-revoked-keys
```

### Enforce certificate principals correctly (batch 10.0-10.3)

- A user certificate with an empty principals list is no longer a wildcard
  when its CA is trusted through an `authorized_keys` `principals="..."`
  restriction.
- Principal wildcards are supported consistently for host certificates, not
  for user certificates.
- Matching correctly distinguishes a comma inside one certificate principal
  from a configured list containing multiple principals.

Re-test user-certificate authorization that depended on empty principals,
wildcards, or comma-containing names.

## Key storage and hardware-backed keys

### Download mixed FIDO resident keys robustly (batch 10.4)

`ssh-keygen` and `ssh-add` skip unsupported key types while downloading
resident keys from a FIDO token. A mixed token no longer aborts the whole
download at the first unsupported key. Tooling should handle a partial set of
supported results rather than treating the skipped types as a fatal failure.

### Write Ed25519 keys as PKCS#8 (batch 10.0-10.3)

From 10.3, `ssh-keygen` can write Ed25519 private keys in PKCS#8 format with
`-m PKCS8`. Interoperability workflows no longer need to exclude Ed25519 solely
because that output format was unavailable.
