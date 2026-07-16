# Boot, UKIs, and TPM Policy

## Build and select UKIs

- UKIs can carry early CPU microcode in a `.ucode` PE section, and systemd-stub can load configuration extensions from the ESP (since 256).
- Multi-profile UKIs use `.profile` sections to combine shared content with normal, debug, recovery, or other profile-specific sections. A BLS Type 1 `uki` entry can select one with `profile recovery` (since 257; BLS selection since 259).
- Multiple `.dtbauto` sections plus `.hwids` let the stub choose a DeviceTree blob from firmware compatibility information or SMBIOS CHIDs. PE add-ons may carry `.initrd`, and `ukify --extend` adds sections to an existing UKI (since 257).
- Canonical DeviceTree hardware-ID definitions live below `/usr/lib/systemd/boot/hwids/<efi-arch>/`; ukify automatically consumes this catalog when constructing UKIs (since 260).
- UKIs can embed CHID-selected UEFI firmware in `.efifw`. If installed firmware does not match, the matching firmware is installed and the machine reboots before continuing normal boot (since 258).
- A network-loaded stub records its origin in `LoaderDeviceURL`, allowing other resources to resolve relative to the boot source. BLS Type 1 entries accept both `uki` and `uki-url` (since 258).
- Pair a 258 systemd-stub with ukify 257.9 or newer.

```text
title Network recovery
uki-url https://boot.example.invalid/recovery.efi
```

## Sign images and enroll Secure Boot

- Automatic Secure Boot enrollment includes `dbx` and supports UEFI Custom and Audit modes (since 256).
- `bootctl --secure-boot-auto-enroll=yes` installs DER certificates or ESL-formatted databases while firmware is in Setup Mode. Signing tools can obtain certificates through OpenSSL providers (since 257).
- `systemd-measure policy-digest` and `ukify --policy-digest` calculate TPM policy separately from signing. Use `ukify --join-pcrsig=` or `--pcrsig=` to insert prepared signatures, and `--sign-profile=` to choose the profile (since 258).
- For offline Secure Boot signing, `systemd-sbsign --prepare-offline-signing` emits material for an external signer; return it with `--signed-data=` and `--signed-data-signature=` (since 258).
- `loader.conf` controls enrollment failure behavior with `secure-boot-enroll-action` and the enrollment wait with `secure-boot-enroll-timeout-sec=` (since 258 and 259 respectively).

## Configure systemd-boot and the stub

- Systemd-boot can append kernel arguments from the SMBIOS Type 11 string `io.systemd.boot.kernel-cmdline-extra` (since 256).
- `bootctl --random-seed=yes|no` controls ESP random-seed provisioning, which is important when cloning images (since 257).
- `loader.conf` supports `reboot-on-error`, `log-level=`, and `secure-boot-enroll-timeout-sec=`. SMBIOS Type 11 can set `io.systemd.boot.loglevel=` (since 258 and 259).
- `bootctl --variables=yes|no` replaces `--no-variables` and can force EFI-variable writes in a chroot (since 258).
- SMBIOS Type 11 can set the boot-menu timeout with `io.systemd.boot.timeout=`. `LoaderEntryPreferred` chooses a preferred entry unless boot assessment has exhausted its tries (since 260).
- `bootctl` exposes a Varlink `Install()` method. `--efi-boot-option-description-with-device=yes` disambiguates identically named installations on different disks (since 260).
- The stub discovers global system and configuration extensions at `ESP/loader/extensions/*.{sysext,confext}.raw` (since 258).
- `SystemdOptions` and `bootctl systemd-efi-options` are deprecated; use credentials and configuration extensions instead (announced in 257).

## Maintain PCR policy

- The experimental PCR-lock NV-index access policy changed in 256. Recreate older stored policy with:

```sh
systemd-pcrlock remove-policy
systemd-pcrlock make-policy
```

- A PCR-lock policy may be stored as `loader/credentials/pcrlock.<entry-token>.cred` on the ESP or XBOOTLDR, for the stub to pass into the initrd (since 256).
- TPM enrollment can require both an externally signed PCR policy and a locally managed `systemd-pcrlock` policy (since 257).
- New TPM2 enrollments by `systemd-cryptenroll`, `systemd-repart`, and `systemd-creds` use an empty PCR mask rather than binding literally to PCR 7. Combine managed PCR-lock policy with signed PCR 11 policy when those guarantees are needed (since 258).
- PCR-lock policy no longer includes PCR 12 by default because a policy supplied as a UKI credential is itself measured into PCR 12 (since 259).
- Boot integration supports TPM 2.0 only; TPM 1.2 support was removed from systemd-boot and systemd-stub in 259.

## Use named userspace PCRs

- `TPM2_NT_EXTEND` NV indexes can act as named PCR-like registers. They are created only in the initrd, require a per-machine secret anchor, are unavailable before userspace, and have their initialization measured into PCR 9 (since 259).
- `systemd-pcrextend` can extend these NvPCRs. `systemd-pcrproduct.service` measures the SMBIOS or DeviceTree product identity into `hardware`; `tpm2-measure-keyslot-nvpcr=` measures the chosen LUKS keyslot; `systemd-analyze nvpcrs` inspects the values (since 259).
- The `verity` NvPCR receives measurements when dm-verity images are loaded, including during DDI dissection. In `/etc/veritytab`, `tpm2-measure-nvpcr=` controls this behavior for `systemd-veritysetup` (since 260).

## Debug and seed early boot

- PID 1 and timesyncd choose the newest minimum clock from the compiled epoch, `/usr/lib/clock-epoch`, and `/var/lib/systemd/timesync/clock` (since 257).
- `systemd.machine_id=firmware` derives the machine ID from the SMBIOS or DeviceTree UUID on physical systems as well as VMs (since 257).
- `systemd.break=` and `rd.systemd.break=` open a shell at `pre-udev`, `pre-basic`, `pre-mount`, or `pre-switch-root` (since 258).
