# Boot, UKIs, and TPM Policy

## UKI contents and profile selection

### Image, microcode, and command-line inputs (256)

Systemd-stub can load confexts from the ESP; UKIs can carry early CPU
microcode in `.ucode`; systemd-boot accepts extra arguments from SMBIOS Type
11 `io.systemd.boot.kernel-cmdline-extra`. Automatic Secure Boot enrollment
covers `dbx` and supports UEFI Custom and Audit modes.

### Multi-profile and hardware-selected UKIs (257)

Use `.profile` sections to combine shared content with normal, debug, or
recovery variants. Multiple `.dtbauto` sections plus `.hwids` select a DTB
from firmware compatibility data or SMBIOS CHIDs. PE add-ons may carry
`.initrd`, and `ukify --extend` extends an existing UKI.

### Network and firmware UKIs (258)

BLS Type 1 entries accept `uki` and `uki-url`. A network-loaded stub records
its source in `LoaderDeviceURL`, allowing other resources to resolve against
the boot origin. UKIs may embed CHID-selected UEFI firmware in `.efifw`;
mismatched firmware is installed and the machine rebooted before normal boot.

### System DTB catalog (260)

Canonical hardware IDs live below
`/usr/lib/systemd/boot/hwids/<efi-arch>/`; ukify consumes the catalog
automatically when building UKIs.

### Ukify JSON expansion (258.10-261.2)

`ukify inspect` JSON includes every UKI section and profile. Consumers must
not assume that it contains only the selected profile or a subset of sections.

## Signing and enrollment

### Image cloning and auto-enrollment (257)

`bootctl --random-seed=yes|no` controls ESP random-seed provisioning to avoid
reuse in cloned images. `--secure-boot-auto-enroll=yes` accepts DER
certificates or ESL databases in Setup Mode, and signing tools can obtain
certificates through OpenSSL providers.

### Offline TPM and Secure Boot signing (258)

Use `systemd-measure policy-digest` or `ukify --policy-digest` to prepare PCR
policy material, then join signatures with `--join-pcrsig=` or `--pcrsig=`;
`--sign-profile=` targets one UKI profile. For Secure Boot, use
`systemd-sbsign --prepare-offline-signing`, then provide `--signed-data=` and
`--signed-data-signature=`.

## PCR-lock and TPM policy

### PCR-lock policy migration (256)

The NV-index access policy invalidated older experimental pcrlock policies.
Recreate them with:

```sh
systemd-pcrlock remove-policy
systemd-pcrlock make-policy
```

The stub can pass a policy stored as
`loader/credentials/pcrlock.<entry-token>.cred` on ESP or XBOOTLDR into the
initrd.

### Enrollment defaults and compound policy (257, 258)

Crypttab provides `password-cache=`, `fido2-pin=`, `fido2-up=`, and
`fido2-uv=`. Unlocking may require both vendor-signed PCR policy and a locally
managed pcrlock policy. The `has-tpm2` probe is in `systemd-analyze`.

New cryptenroll, repart, and creds TPM enrollments use an empty PCR mask. Add
managed pcrlock and signed PCR 11 policy when those bindings are required.

### PCR 12 self-reference and NvPCRs (259)

Pcrlock no longer includes PCR 12 by default because a policy carried as a
UKI credential is itself measured there. `TPM2_NT_EXTEND` NV indexes provide
named userspace PCR-like registers created in the initrd from a per-machine
secret; initialization is measured into PCR 9. `systemd-pcrextend` extends
them, `systemd-pcrproduct.service` measures product identity into `hardware`,
`tpm2-measure-keyslot-nvpcr=` records a LUKS slot, and
`systemd-analyze nvpcrs` inspects them.

### Verity NvPCR (260)

The `verity` NvPCR receives measurements when dm-verity images are loaded,
including by DDI dissection. Configure `/etc/veritytab` with
`tpm2-measure-nvpcr=`.

## Boot manager and early boot

### Clock and machine-ID seeding (257)

PID 1 and timesyncd choose the newest lower clock bound from their compiled
epoch, `/usr/lib/clock-epoch`, and `/var/lib/systemd/timesync/clock`.
`systemd.machine_id=firmware` derives the ID from SMBIOS or DeviceTree UUID on
physical systems and VMs.

### Loader policy and extension discovery (258)

`loader.conf` accepts `reboot-on-error` and `secure-boot-enroll-action`.
`bootctl --variables=yes|no` supersedes `--no-variables` and may force EFI
variable writes in a chroot. The stub discovers global sysext/confext images
at `ESP/loader/extensions/*.{sysext,confext}.raw`.

### Network pulls and root transition (258)

`systemd.pull=` and `rd.systemd.pull=` accept `blockdev`, `bootorigin`, and
`runtime=`. Initrd pulls default to `/run`; host pulls default to `/var`.
`root=bind:` boots a pulled tar tree, while `root=off` prevents the initrd to
host-root transition.

### Boot breakpoints (258)

`systemd.break=` and `rd.systemd.break=` open shells at `pre-udev`,
`pre-basic`, `pre-mount`, or `pre-switch-root`.

### Logging, profiles, and preferred entries (259, 260)

`loader.conf` adds `log-level=` and `secure-boot-enroll-timeout-sec=`; SMBIOS
can set `io.systemd.boot.loglevel=`. A BLS `uki` entry may select `profile`.
SMBIOS `io.systemd.boot.timeout=` controls menu timeout, while
`LoaderEntryPreferred` selects a preferred entry unless its assessment tries
reached zero. Bootctl exposes Varlink `Install()` and
`--efi-boot-option-description-with-device=yes`.

### TPM hardware floor (259)

Systemd-boot and systemd-stub no longer support TPM 1.2 integration; use TPM
2.0.
