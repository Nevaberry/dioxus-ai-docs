# Boot, UKIs, and TPM Policy

## UKI construction and selection

### Boot image inputs (256)

Systemd-stub can load confexts from the ESP, UKIs may contain early CPU
microcode in `.ucode`, and systemd-boot accepts extra kernel arguments from
SMBIOS Type 11 string `io.systemd.boot.kernel-cmdline-extra`. Automatic Secure
Boot enrollment covers `dbx` and supports UEFI Custom and Audit modes.

### Multi-profile and hardware-selecting UKIs (257)

Use `.profile` to combine shared and profile-specific normal, debug, or
recovery entries. Multiple `.dtbauto` sections plus `.hwids` select a
DeviceTree from firmware compatibility or SMBIOS CHIDs. PE add-ons may carry
`.initrd`, and `ukify --extend` extends an existing UKI.

### Network and firmware UKIs (258)

Systemd-boot accepts BLS Type 1 `uki` and `uki-url`; a network-loaded stub
records `LoaderDeviceURL` for resolving later resources. A UKI may embed
CHID-selected UEFI firmware in `.efifw`; matching firmware is installed and
the machine rebooted before normal boot.

### Profile selection and DTB catalogs (259, 260)

A BLS Type 1 `uki` entry can set `profile`. Canonical DeviceTree hardware IDs
live in `/usr/lib/systemd/boot/hwids/<efi-arch>/`, and ukify consumes them
automatically so firmware identity can choose a DTB without per-device UKIs.

### Ukify inspection JSON is expanded (258.10-261.2)

`ukify inspect` JSON contains every UKI section and profile in all covered
point releases. Consumers must not assume a selected profile or subset.

## Secure Boot and boot-loader policy

### Image cloning and enrollment (257)

Use `bootctl --random-seed=yes|no` to control ESP random-seed provisioning and
avoid cloned-image reuse. `--secure-boot-auto-enroll=yes` installs DER or ESL
databases in Setup Mode; signing can obtain certificates through OpenSSL
providers.

### Offline signing (258)

`systemd-measure policy-digest` and `ukify --policy-digest` prepare TPM policy
calculation separately from signing. Join results with `--join-pcrsig=` or
`--pcrsig=` and target `--sign-profile=`. Secure Boot has an analogous
`systemd-sbsign --prepare-offline-signing` flow using `--signed-data=` and
`--signed-data-signature=`.

### Boot-loader controls (258, 259, 260)

`loader.conf` in 258 adds `reboot-on-error` and
`secure-boot-enroll-action`; `bootctl --variables=yes|no` supersedes
`--no-variables` and can force chroot EFI writes. The stub discovers global
sysext/confext images at `ESP/loader/extensions/*.{sysext,confext}.raw`.

Version 259 adds loader `log-level=` and
`secure-boot-enroll-timeout-sec=`, plus SMBIOS
`io.systemd.boot.loglevel=`. Version 260 adds SMBIOS
`io.systemd.boot.timeout=`, `LoaderEntryPreferred` (excluding exhausted
boot-assessment entries), Varlink `Install()`, and bootctl
`--efi-boot-option-description-with-device=yes`.

## PCR-lock and NvPCRs

### Rebuild experimental PCR-lock policies (256)

The TPM NV-index access policy changed. Run
`systemd-pcrlock remove-policy`, then `systemd-pcrlock make-policy`.
Policies may live as `loader/credentials/pcrlock.<entry-token>.cred` on ESP or
XBOOTLDR for stub delivery to the initrd.

### Enrollment defaults and compound policy (257, 258)

Crypttab controls password caching with `password-cache=` and FIDO2 PIN,
presence, and verification through `fido2-pin=`, `fido2-up=`, and
`fido2-uv=`. Unlocking may require both vendor-signed PCR policy and local
pcrlock policy; use `systemd-analyze has-tpm2` for probing.

New cryptenroll, repart, and creds TPM enrollments in 258 use an empty PCR
mask rather than literal PCR 7. Add managed pcrlock plus signed PCR 11 policy
when required.

### PCR 12 and named userspace PCRs (259)

Pcrlock excludes PCR 12 because a UKI pcrlock credential is itself measured
there. TPM2 `TPM2_NT_EXTEND` NV indexes provide named PCR-like registers,
created only in the initrd from a per-machine secret and initialized into PCR
9. `systemd-pcrextend` targets them; `systemd-pcrproduct.service` measures the
product ID into `hardware`; `tpm2-measure-keyslot-nvpcr=` records a LUKS
keyslot; `systemd-analyze nvpcrs` inspects values.

### Dedicated Verity NvPCR (260)

The `verity` NvPCR receives measurements when dm-verity images are loaded,
including through DDI dissection. Control `/etc/veritytab` measurement with
`tpm2-measure-nvpcr=`.

## Early boot and recovery

### Random seed, firmware machine ID, and TPM version (257, 259)

Use `systemd.machine_id=firmware` to derive identity from SMBIOS or
DeviceTree. Systemd-boot and stub TPM functionality requires TPM 2.0 from 259.

### Breakpoints and factory reset (258)

`systemd.break=` and `rd.systemd.break=` can stop at `pre-udev`, `pre-basic`,
`pre-mount`, or `pre-switch-root` for interactive debugging. Factory-reset
orchestration and TPM clearing are covered in the device administration
reference.
