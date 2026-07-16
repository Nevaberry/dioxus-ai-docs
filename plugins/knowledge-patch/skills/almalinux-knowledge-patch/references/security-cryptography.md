# Security, Cryptography, Identity, and Trust

Use this reference for system crypto-policy behavior, OpenSSL and OpenPGP
changes, SELinux policy work, Keylime attestation, and identity baselines.
Security advisories are kept separately in
[security-advisories.md](security-advisories.md).

## Cryptographic-policy transitions

### Post-quantum defaults

- AlmaLinux 10.0 system crypto policies, OpenSSL, and OpenSSH 9.9 support
  post-quantum algorithms (`10.0`).
- AlmaLinux 9.7 adds the `PQ` crypto-policy subpolicy to opt into
  post-quantum algorithms (`9.7`).
- AlmaLinux 10.1 enables post-quantum algorithms by default across every
  system-wide cryptographic policy; a separately selected mode is no longer
  required (`10.1`).

OpenSSL 3.5 in AlmaLinux 9.7 supports ML-KEM, ML-DSA, and SLH-DSA, and puts
hybrid ML-KEM algorithms in the default TLS group list (`9.7`).

### OpenSSL, TLS, and certificate trust

- AlmaLinux 9.4 OpenSSL provides a drop-in directory for provider-specific
  configuration, so provider settings need not be placed in the main
  configuration (`9.4`).
- `stunnel` 5.71 changes its behavior with OpenSSL 1.1 or later in FIPS mode
  and supports modern PostgreSQL clients (`9.4`).
- AlmaLinux 9.5 OpenSSL 3.2.2 supports the RFC 8879 certificate-compression
  extension and RFC 8734 Brainpool curves for TLS 1.3 (`9.5`).
- AlmaLinux 9.5 `crypto-policies` extends system-wide algorithm-selection
  controls to Java (`9.5`).
- AlmaLinux 9.5 `ca-certificates` supplies trusted CA roots in OpenSSL
  directory format, and NSS is rebased to 3.101 (`9.5`).
- AlmaLinux 10.0 OpenSSL can create FIPS-compliant PKCS #12 files and provides
  `pkcs11-provider` for hardware-token access (`10.0`).

### RPM and OpenPGP signatures

AlmaLinux 10.1 supports RPMv6 signatures, including multiple signatures on a
single RPM. Sequoia PGP can sign RPMs with post-quantum algorithms and create
or verify OpenPGPv6 signatures (`10.1`).

AlmaLinux 10.0 also provides Sequoia's `sq` and `sqv` alongside GnuPG for
OpenPGP encryption and signature workflows (`10.0`).

## Security and identity component baselines

| Coverage batch | Baselines |
| --- | --- |
| `9.6` | SELinux policy 38.1.53 and SSSD 2.9.6. |
| `9.7` | SELinux policy 38.1.65, SSSD 2.9.7, and Keylime 7.12.1. |
| `9.8` | OpenSSL 3.5.5, OpenSSH 9.9p1, GnuTLS 3.8.10, SELinux policy 38.1.75, SSSD 2.9.8, and `crypto-policies` 20260224. |
| `10.1` | SELinux policy 42.1.7 and SSSD 2.11.1. |
| `10.2` | SELinux policy 42.1.18, SSSD 2.12.0, Keylime 7.14.1, Libreswan 5.3-8, audit 4.0.3-5, AIDE 0.19.2, and `crypto-policies` 20260216. |

## SELinux policy and tooling

- SELinux userspace 3.6 supports explicit deny rules for policy
  customization (`9.4`).
- AlmaLinux 9.5 policy adds a boolean that allows QEMU Guest Agent to execute
  confined commands (`9.5`).
- SELinux userspace 3.8 can make `audit2allow` emit CIL and lets the SELinux
  sandbox work under Wayland (`10.0`).

## Keylime attestation

- AlmaLinux 9.4 makes the Keylime verifier and registrar available as
  containers (`9.4`).
- Keylime agent 0.2.7 supports Initial Device Identity (IDevID) and Initial
  Attestation Key (IAK) credentials and defaults to TLS 1.3 (`10.0`).
- The `keylime-policy` tool consolidates Keylime policy-management tasks
  (`10.0`).

## Fleet security administration

AlmaLinux 10.0 includes a `sudo` system role for managing sudo configuration
consistently across fleets (`10.0`).
