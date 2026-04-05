# Security and Cryptography — Ubuntu 25.10

## OpenSSH 10.0

### Post-Quantum Key Agreement

Hybrid post-quantum key agreement is enabled by default. Connections automatically negotiate PQC key exchange when both sides support it.

### DSA Removed

The DSA signature algorithm is removed entirely — not just deprecated, but gone. Any hosts or keys still using DSA must migrate to Ed25519 or ECDSA.

### Version String Change

The version string is now `SSH-2.0-OpenSSH_10.0`. Scripts that match on `OpenSSH_1*` (expecting single-digit major versions like `OpenSSH_9.8`) will break. Update regex patterns:

```bash
# Broken pattern (misses 10.0+):
grep 'OpenSSH_[0-9]\.'

# Fixed pattern:
grep 'OpenSSH_[0-9]\+\.'
```

### New Configuration Features

**Glob patterns** in `AuthorizedKeysFile` and `AuthorizedPrincipalsFile`:

```
AuthorizedKeysFile /etc/ssh/authorized_keys.d/*.pub
AuthorizedPrincipalsFile /etc/ssh/principals.d/%u/*.conf
```

**New Match criteria** in `sshd_config`:

```
Match version SSH-2.0-OpenSSH_10.*
    # Rules for specific client versions

Match sessiontype shell
    # Rules for interactive sessions only

Match command scp*
    # Rules for specific commands
```

## OpenSSL 3.5 — Post-Quantum Cryptography

### PQC Algorithms

| Algorithm | Type | Standard | Purpose |
|-----------|------|----------|---------|
| ML-KEM (Kyber) | KEM | FIPS 203 | Key encapsulation / key exchange |
| ML-DSA (Dilithium) | Signature | FIPS 204 | Digital signatures |
| SLH-DSA (SPHINCS+) | Signature | FIPS 205 | Stateless hash-based signatures |

### TLS Defaults

Default TLS groups now include and prefer hybrid PQC KEM groups. This means TLS connections negotiate post-quantum key exchange automatically when both endpoints run OpenSSL 3.5+.

No application code changes needed — the default group list handles PQC negotiation transparently.

### QUIC Support

Server-side QUIC support (RFC 9000) is now available. Applications using OpenSSL for TLS can enable QUIC transport without additional libraries.

## Chrony with NTS

Chrony replaces systemd-timesyncd as the default time synchronization daemon.

### Network Time Security (NTS)

NTS is enabled by default, providing authenticated time synchronization over port **4460/tcp**.

NTS prevents man-in-the-middle attacks on NTP traffic — time responses are cryptographically authenticated.

### Firewall Considerations

Ensure port 4460/tcp outbound is open for NTS to function. If the network blocks this port, Chrony falls back to unauthenticated NTP (port 123/udp), but explicit configuration is needed:

```bash
# /etc/chrony/sources.d/ubuntu-ntp-pools.sources
# Remove NTS directives and use standard NTP pool entries:
pool ntp.ubuntu.com iburst
```

### Verifying NTS Status

```bash
chronyc -n authdata # show NTS authentication status per source
chronyc sources -v  # show time sources with verbose info
```
