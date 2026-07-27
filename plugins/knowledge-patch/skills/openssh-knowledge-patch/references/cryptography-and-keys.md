# Cryptography, Certificates, and Keys

## Removed algorithms and older peers

OpenSSH 10.0 removes DSA signature support entirely (batch `10.0-10.3`). It also removes finite-field `diffie-hellman-group*` and `diffie-hellman-group-exchange-*` methods from the server's default `KexAlgorithms`; the client default remains unchanged. Add a legacy method only for a specifically identified peer and only on the side that needs it.

When a moduli file is present but contains no suitable groups, do not expect fallback to compiled-in groups. Treat the file as an explicit policy source and repair its contents.

OpenSSH 10.1 removes experimental XMSS keys.

## Key-exchange and cipher defaults

From 10.0, expect `mlkem768x25519-sha256` to be the default key exchange. Expect this cipher preference order:

1. ChaCha20/Poly1305
2. AES-GCM 128 and 256
3. AES-CTR 128, 192, and 256

From 10.1, negotiating a non-post-quantum key exchange produces a default-on warning. Control the warning with `WarnWeakCrypto`; do not mistake it for a negotiation failure.

Expect warnings that SHA1 SSHFP records will eventually be ignored. `ssh-keygen -r` now generates only SHA256 SSHFP records, so update DNS publishing workflows that expect SHA1 output.

## Experimental composite signatures

OpenSSH 10.4 adds an experimental composite signature scheme combining ML-DSA 44 with Ed25519 (batch `10.4`). It is disabled by default. Generate a key with:

```sh
ssh-keygen -t mldsa44-ed25519
```

Add the algorithm explicitly to the lists where it is required, including `HostKeyAlgorithms` and `PubkeyAcceptedAlgorithms`. Do not infer that generating or installing the key enables it automatically.

## Algorithm-list validation

Expect invalid cipher or MAC lists in configuration files and command-line arguments to be rejected during configuration processing. Remove invalid names or list modifiers; do not rely on a later runtime failure.

OpenSSH 10.3 makes `PubkeyAcceptedAlgorithms` and `HostbasedAcceptedAlgorithms` exact for ECDSA. Listing one ECDSA algorithm admits only that named variant. Do not rely on the earlier behavior in which any listed ECDSA name could admit all ECDSA variants.

## Revocation material

OpenSSH 10.3 lets client `RevokedHostKeys` and server `RevokedKeys` name multiple files. Split routine and emergency material without an external merge step:

```sshconfig
RevokedKeys /etc/ssh/revoked-keys /etc/ssh/emergency-revoked-keys
```

## Key formats and resident keys

OpenSSH 10.3 can write Ed25519 private keys in PKCS#8 format. Use `ssh-keygen` operations with `-m PKCS8` for Ed25519 when an interoperable PKCS#8 container is required.

In 10.4, `ssh-keygen` and `ssh-add` skip unsupported key types while downloading resident keys from a FIDO token. A mixed-type token no longer aborts the whole download at the first unsupported type; inspect the resulting set if the caller must report skipped keys.
