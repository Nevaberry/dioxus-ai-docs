# Credentials and Enrollment

## Encrypted credentials

### User-bound credentials (256)

`systemd-creds encrypt` and `decrypt` accept `--user` and `--uid=` to bind
encrypted service credentials to a specific unprivileged user.

### Base64 input for `systemd-creds cat` (257)

`systemd-creds cat` expects base64-encoded encrypted credentials, consistent
with `decrypt` and `LoadCredentialEncrypted=`. Encode callers' raw binary
credential data first.

### Null-key policy (256, 259)

The key selector formerly called `tpm2-absent` is `null`; it provides neither
confidentiality nor integrity. Decryption requires an intentional policy.
`--allow-null` accepts it and `--refuse-null` rejects it. If neither is set,
acceptance remains conditional on UEFI Secure Boot being reported off, so
automation should always choose explicitly.

### User services and sandboxed system services (258)

Encrypted credentials work for user services. A system service restricted by
`PrivateDevices=` or `DeviceAllow=`/`DevicePolicy=` decrypts through
`systemd-creds.socket` instead of receiving automatic TPM device access.

## LUKS and hardware enrollment

### Implicit cryptenroll target (256)

With no device argument, `systemd-cryptenroll` derives a block device from the
backing device of `/var`, commonly the root LUKS volume. Automation should pass
the device explicitly when that inference is unsafe. Enrollment also supports
PKCS#11 public keys and EC keys and can add a new slot while unlocking the old
one through TPM2.

### FIDO2 and compound PCR controls (257)

Crypttab `password-cache=yes|no|read-only` controls password caching.
`fido2-pin=`, `fido2-up=`, and `fido2-uv=` separately govern PIN, user
presence, and verification. Unlocking may combine vendor-signed PCR policy
with local pcrlock policy. Probe TPM2 through `systemd-analyze has-tpm2`.

### Empty TPM PCR enrollment defaults (258)

New cryptenroll, repart, and creds TPM2 enrollments use an empty PCR mask,
not literal PCR 7. Add managed pcrlock and signed PCR 11 policy when those
guarantees are needed.

### Recovery keys for existing homed users (259)

`homectl update --recovery-key=` adds a recovery key after account creation.
First-boot homed no longer asks for login shell or supplementary groups unless
its prompt controls request them.

## Image keys and certificates

### Repart encryption input (259)

Partition definitions accept `TPM2PCRs=` for TPM-bound encryption and
`KeyFile=` for binary LUKS keys. Repart is also exposed over Varlink.

### Integrity and volume-key pinning (260)

Repart `Integrity=`/`IntegrityAlgorithm=` enables dm-integrity for LUKS.
Image dissection policy can require `encryptedwithintegrity`. Crypttab
`fixate-volume-key=` pins an entry to a hash derived from the volume key, and
repart can generate the required data.

### Certificate and public-key extraction (260)

Use `systemd-keyutil extract-certificate` for X.509 output and
`extract-public` for a public key. The old `public` verb remains an alias.
