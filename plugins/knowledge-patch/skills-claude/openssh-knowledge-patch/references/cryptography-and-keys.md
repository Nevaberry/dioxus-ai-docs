# Cryptography, Certificates, and Keys

## Algorithm availability and negotiation

### Remove legacy algorithms and incompatible peers

The 10.0-10.3 changes remove several compatibility assumptions:

- OpenSSH 10.0 removes DSA signature support entirely.
- The server's default `KexAlgorithms` no longer contains finite-field
  `diffie-hellman-group*` or `diffie-hellman-group-exchange-*` methods. The
  client default is unchanged, so apply server and client policy separately.
- A moduli file that exists but contains no suitable groups no longer falls
  back to compiled-in groups.
- OpenSSH 10.1 removes experimental XMSS keys.
- OpenSSH 10.3 drops compatibility for peers that cannot rekey.

Remove obsolete keys and upgrade incompatible peers. Add a legacy algorithm
only as a narrowly scoped exception for a peer that demonstrably needs it.

### Apply the post-quantum key-exchange default and warnings

OpenSSH 10.0 makes `mlkem768x25519-sha256` the default key exchange. Its cipher
preference is ChaCha20/Poly1305, AES-GCM 128/256, followed by AES-CTR
128/192/256.

From OpenSSH 10.1, selecting a non-post-quantum key exchange produces a
default-on warning controlled by `WarnWeakCrypto`. The client also warns that
SHA1 SSHFP records will eventually be ignored, while `ssh-keygen -r` emits only
SHA256 records. Update DNS and automation that still depend on SHA1 SSHFP.

### Enable the experimental composite signature explicitly

OpenSSH 10.4 supports an experimental composite signature scheme combining
ML-DSA 44 with Ed25519. Generate the key with:

```sh
ssh-keygen -t mldsa44-ed25519
```

The scheme is disabled by default. Add it explicitly to every applicable
algorithm list, including `HostKeyAlgorithms` and
`PubkeyAcceptedAlgorithms`; key generation alone does not make it negotiable.

### Reject invalid cipher and MAC lists early

OpenSSH 10.4 rejects invalid cipher or MAC lists supplied through configuration
files or command-line arguments while it processes configuration. Do not
expect an invalid list to survive until a later runtime failure. Validate
generated configuration as part of deployment.

### Use exact ECDSA allowlists

OpenSSH 10.3 fixes `PubkeyAcceptedAlgorithms` and
`HostbasedAcceptedAlgorithms` so that an ECDSA algorithm name admits only that
algorithm. Earlier releases could accept every ECDSA variant when any ECDSA
name appeared. Re-test allowlists after upgrading and do not depend on the
earlier expansion.

## Certificates and revocation

### Constrain certificate principals

OpenSSH 10.3 hardens principal authorization in three ways:

- A user certificate with an empty principals list is not a wildcard when its
  CA is trusted through an `authorized_keys` `principals="..."` restriction.
- Principal wildcards are supported consistently for host certificates and
  are not supported for user certificates.
- A comma inside a certificate principal is not confused with a configured
  list containing multiple principals.

Audit authorization rules that relied on empty principals, user-certificate
wildcards, or ambiguous comma handling.

### Split revocation material across files

OpenSSH 10.3 allows both client `RevokedHostKeys` and server `RevokedKeys` to
name multiple files. Separate routine and emergency material without an
external merge step, for example:

```sshconfig
RevokedKeys /etc/ssh/revoked-keys /etc/ssh/emergency-revoked-keys
```

## Key storage and token operations

### Download supported resident keys from mixed FIDO tokens

In OpenSSH 10.4, `ssh-keygen` and `ssh-add` skip unsupported key types when
downloading resident keys from a FIDO token. A mixed token no longer aborts the
entire download at the first unsupported key. Check the resulting key set
rather than treating one skipped type as total failure.

### Write Ed25519 private keys as PKCS#8

OpenSSH 10.3 supports Ed25519 private-key output in PKCS#8 format. Workflows
using `ssh-keygen -m PKCS8` no longer need to exclude Ed25519 solely because of
the output format.
