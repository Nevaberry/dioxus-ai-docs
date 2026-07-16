# Security and cryptography

## Apply SELinux policy changes

- SELinux userspace 3.6 can express deny rules on Rocky Linux 9.4.
- Rocky Linux 9.5 adds a boolean permitting QEMU Guest Agent to run confined
  commands.
- Rocky Linux 9.6 confines `iio-sensor-proxy`, `power-profiles-daemon`,
  `switcheroo-control`, and `samba-bgqd` in the bundled policy.
- Rocky Linux 10.0 inverts file-context equivalence to `/var/run = /run`.

## Configure system cryptography

Rocky Linux 9.5 upgrades OpenSSL to 3.2.2 with TLS certificate compression and
Brainpool curves in TLS 1.3, and rebases NSS to 3.101. Trusted CA roots are now
supplied in OpenSSL directory format, and system crypto policies extend to Java
algorithm sections.

Rocky Linux 10.0 enables post-quantum cryptography in OpenSSL and OpenSSH
through system crypto policies. GnuTLS can compress client and server
certificates. OpenSSH restores `0600` host-key permissions instead of `0640`,
and yescrypt becomes the default user-password algorithm.

On Rocky Linux 9.7, enable the `PQ` subpolicy to make post-quantum algorithms
available to participating applications and tools.

## Use post-quantum components

Rocky Linux 9.8 supplies GnuTLS 3.8.10 with ML-KEM hybrid key exchange and
ML-DSA algorithms. `p11-kit` 0.26.1 adds PQC definitions to its PKCS #11
headers. OpenSSH is rebased from 8.7 to 9.9.

In Rocky Linux 10.2, OpenSSH adds an ML-KEM and elliptic-curve hybrid key
exchange in FIPS mode. `libssh` supports PQ/T hybrid methods combining ML-KEM
with ECDH, and `podman-sequoia` supports composite post-quantum signatures.

## Configure providers, attestation, and package signing

- OpenSSL supports a drop-in directory for provider-specific configuration on
  Rocky Linux 9.4.
- Keylime verifier and registrar components are available as containers on 9.4.
- `clevis-pin-trustee` can automatically encrypt and decrypt LUKS volumes using
  remote attestation through the Trustee Key Broker Service on 9.8.
- Sequoia PGP can sign RPM packages on 10.1.
- Rocky Linux 10.2 includes `keylime-agent` 0.2.9.

## Harden logging and policy enforcement

On Rocky Linux 9.4, rsyslog adds customizable TLS/SSL settings and options for
dropping capabilities. `libkcapi` 1.4.0 adds `-T` to choose target filenames in
hash-sum calculations. Rocky Linux 9.8 rebases `fapolicyd` to 1.4.3, including
new rule-filtering functionality.

