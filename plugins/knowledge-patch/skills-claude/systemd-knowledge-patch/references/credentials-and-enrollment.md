# Credentials and Enrollment

## Encrypted service credentials

### User-bound credentials (256)

`systemd-creds encrypt` and `decrypt` accept `--user` and `--uid=` to bind an
encrypted credential to a specific unprivileged user.

### Base64 input to `cat` (257)

`systemd-creds cat` expects base64-encoded encrypted credentials, like
`decrypt` and `LoadCredentialEncrypted=`. Encode callers' raw binary input.

### User-service and sandboxed decryption (258)

Encrypted credentials work for user services. System services using
`PrivateDevices=` or `DeviceAllow=`/`DevicePolicy=` decrypt through
`systemd-creds.socket` instead of receiving automatic TPM device access.

## Null-key policy

### Explicit null-key naming (256)

The selector formerly called `tpm2-absent` is `null`; it provides no
confidentiality or integrity. At this version, decryption requires
`systemd-creds decrypt --allow-null`.

### Deterministic acceptance policy (259)

Decryption and its Varlink method accept both `--allow-null` and
`--refuse-null`. If neither is given, acceptance is conditional on UEFI Secure
Boot being reported off. Automation should always select an explicit policy.

## Storage enrollment and key policy

### Cryptenroll's implicit target (256)

When no device is supplied, `systemd-cryptenroll` derives one from the backing
device of `/var`, often the root LUKS volume. Pass a device in automation when
that inference is unsafe. Enrollment supports PKCS#11 public and EC keys and
can enroll a new slot while TPM2 unlocks an old one.

### FIDO2 and compound PCR policy (257)

Crypttab supports `password-cache=yes|no|read-only` and independent
`fido2-pin=`, `fido2-up=`, and `fido2-uv=` controls. A volume can require both
a vendor-signed PCR policy and a locally managed pcrlock policy.

### Repart encryption definitions (259)

Partition definitions accept `TPM2PCRs=` and a binary `KeyFile=` rather than
requiring those encryption inputs only on the repart command line. Repart is
also available through Varlink.

### Integrity and volume-key pinning (260)

Repart's `Integrity=` and `IntegrityAlgorithm=` enable dm-integrity for LUKS
volumes; dissection policy can require `encryptedwithintegrity`. Crypttab's
`fixate-volume-key=` pins an entry to a hash derived from the encrypted
volume's key, and repart can generate the required information. Verity
measurements are performed by `systemd-veritysetup` when configured.

## Certificate and public-key operations

### Keyutil verbs (260)

`systemd-keyutil extract-certificate` emits an X.509 certificate.
`extract-public` is the current public-key verb; `public` remains an alias.
