# Credentials and Enrollment

## Encrypt credentials for users and services

- `systemd-creds encrypt` and `decrypt` accept `--user` and `--uid=` so an encrypted credential can be bound to a specific unprivileged user (since 256).
- Encrypted credentials work in user services. A system service using `PrivateDevices=` or `DeviceAllow=`/`DevicePolicy=` obtains TPM decryption through `systemd-creds.socket` rather than automatic access to the TPM device (since 258).
- `ImportCredential=` can rename a credential while importing it (since 257).
- Mount units accept `SetCredential=`, `LoadCredential=`, `ImportCredential=`, and the related credential directives (since 258).

## Handle encrypted input formats safely

- `systemd-creds cat` expects a base64-encoded encrypted credential, matching `decrypt` and `LoadCredentialEncrypted=`. Encode callers' raw encrypted binary input before passing it (since 257).
- The key selector formerly called `tpm2-absent` is named `null`. It supplies neither confidentiality nor integrity; `systemd-creds decrypt --allow-null` is required in the original explicit-policy interface (since 256).
- Decryption later added `--refuse-null` and the corresponding Varlink behavior. If neither allow nor refuse is specified, a null-key credential is conditionally accepted when UEFI Secure Boot is reported off. Automation should always choose one policy explicitly (since 259).

## Enroll encrypted storage

- The block-device argument to `systemd-cryptenroll` is optional. If omitted, the tool derives it from the backing device of `/var`, often the root LUKS volume. Automation should name the device whenever that inference could target the wrong volume (since 256).
- Cryptenroll supports PKCS#11 public keys and EC keys. A new slot can be enrolled while an existing slot is unlocked through TPM2 (since 256).
- `password-cache=yes|no|read-only` in crypttab controls cryptsetup password caching. `fido2-pin=`, `fido2-up=`, and `fido2-uv=` independently require FIDO2 PIN, user presence, and user verification (since 257).
- The `has-tpm2` probe moved from `systemd-creds` to `systemd-analyze` (since 257).
- Repart partition definitions accept `TPM2PCRs=` and a binary `KeyFile=` for LUKS setup, rather than requiring those inputs only on the command line (since 259).
- Crypttab's `fixate-volume-key=` binds an entry to a hash derived from the encrypted volume key. Repart can generate the matching information (since 260).

## Maintain keys and certificates

- `systemd-keyutil extract-certificate` prints an X.509 certificate. `extract-public` is the explicit public-key verb; `public` remains a compatibility alias (since 260).
- Existing homed accounts can receive a recovery key with `homectl update --recovery-key=` (since 259).
- For TPM PCR-lock enrollment, signed and locally managed compound policies, changed default PCR masks, and NvPCRs, see [Boot, UKIs, and TPM Policy](boot-uki-and-tpm.md).
