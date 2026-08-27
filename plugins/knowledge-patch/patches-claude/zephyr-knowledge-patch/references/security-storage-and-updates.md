# Security, Storage, and Firmware Updates

Entries are grouped by developer task and alphabetized by topic. The
parenthetical identifier records the exact source batch for each item.

## Board flash-layout upgrades (migration-4.3)

The `b_u585i_iot02a/ns` TF-M layout expands partitions and moves secondary slots to external NOR, preventing image upgrades from older Zephyr releases. `nucleo_h753zi` also has an incompatible reordered layout with a two-sector storage partition and no scratch partition, so firmware upgrades from its old layout may fail.

## Build suffixes and MCUboot swap mode (migration-4.1)

The deprecated build-type feature is removed; use application file suffixes and `sysbuild_file_suffixes`. Rename `SB_CONFIG_MCUBOOT_MODE_SWAP_WITHOUT_SCRATCH` to `SB_CONFIG_MCUBOOT_MODE_SWAP_USING_MOVE`, and rename `CONFIG_MCUBOOT_BOOTLOADER_MODE_SWAP_WITHOUT_SCRATCH` to `CONFIG_MCUBOOT_BOOTLOADER_MODE_SWAP_USING_MOVE`.

## FATFS automount and KVSS headers (migration-4.4)

`CONFIG_FS_FATFS_FSTAB_AUTOMOUNT` is now enabled automatically when an enabled `zephyr,fstab,fatfs` node has `automount`; explicitly disable it to opt out. NVS and ZMS headers move from `zephyr/fs/` to `zephyr/kvss/`.

## Filesystem and hawkBit dependencies (migration-4.1)

Rename EXT2's `CONFIG_MAX_FILES` to `CONFIG_EXT2_MAX_FILES`. hawkBit now requires both `CONFIG_SMF` and `CONFIG_SMF_ANCESTOR_SUPPORT`.

## Firmware-loader and RAM-load flows (4.2.0)

Sysbuild can compose a firmware-loader image with `SB_CONFIG_MCUBOOT_MODE_FIRMWARE_UPDATER`, `SB_CONFIG_FIRMWARE_LOADER`, and an image selection such as `SB_CONFIG_FIRMWARE_LOADER_IMAGE_SMP_SVR`; single-application RAM loading uses `SB_CONFIG_MCUBOOT_MODE_SINGLE_APP_RAM_LOAD`. MCUmgr image management supports firmware-updater mode through `CONFIG_MCUBOOT_BOOTLOADER_MODE_FIRMWARE_UPDATER`, and OS reset requests can carry a retention boot mode with `CONFIG_MCUMGR_GRP_OS_RESET_BOOT_MODE`.

## Firmware-update management controls (4.3.0)

hawkBit gains no-reboot, confirm-on-init, and erase-secondary-on-confirm controls. MCUmgr adds a UDP/DTLS transport with `CONFIG_MCUMGR_TRANSPORT_UDP_DTLS` and can permit confirmation of a non-active slot with `CONFIG_MCUMGR_GRP_IMG_ALLOW_CONFIRM_NON_ACTIVE_SLOT`.

## Flash commands and integrity (migration-4.4)

The `flash erase` and `flash write` shell commands now require an explicit device argument. Both `CONFIG_FLASH_AREA_CHECK_INTEGRITY_MBEDTLS` and `CONFIG_FLASH_AREA_CHECK_INTEGRITY_PSA` are removed because the integrity path no longer has a selectable crypto backend.

## Flash integrity crypto (migration-4.3)

`FLASH_AREA_CHECK_INTEGRITY_MBEDTLS` is deprecated and `FLASH_AREA_CHECK_INTEGRITY_PSA` is now the default. Without TF-M, Mbed TLS supplies the PSA Crypto implementation.

## hawkBit API and headers (migration-4.0)

`hawkbit_autohandler()` now takes one argument; pass `true` for the former behavior. Replace `<zephyr/mgmt/hawkbit.h>` with `<zephyr/mgmt/hawkbit/hawkbit.h>`, and include the split `<zephyr/mgmt/hawkbit/autohandler.h>` or `<zephyr/mgmt/hawkbit/config.h>` interfaces where needed.

## hawkBit authentication (4.2.0)

`CONFIG_HAWKBIT_DDI_NO_SECURITY` is deprecated because hawkBit servers no longer support anonymous authentication. Deployments must use an authenticated DDI configuration.

## hawkBit custom device IDs (migration-4.2)

With `CONFIG_HAWKBIT_CUSTOM_DEVICE_ID`, Zephyr no longer prepends `CONFIG_BOARD` to the callback-provided device ID; custom callbacks must add the board name themselves if it remains part of the server-side identity.

## hawkBit runtime features (4.1.0)

hawkBit gains tenant selection, event callbacks, and saved update progress through `CONFIG_HAWKBIT_TENANT`, `CONFIG_HAWKBIT_EVENT_CALLBACKS`, and `CONFIG_HAWKBIT_SAVE_PROGRESS`.

## Link-address and TLS credential types (migration-4.2)

`net_linkaddr_storage` becomes the new inline-storage `net_linkaddr`, replacing the old pointer-based structure. Code that used `lladdr->addr == NULL` to detect an unset address must test `lladdr->len == 0`; also rename `TLS_CREDENTIAL_SERVER_CERTIFICATE` to `TLS_CREDENTIAL_PUBLIC_CERTIFICATE`.

## Management and settings dependencies (migration-4.4)

`CONFIG_MCUMGR_TRANSPORT_UART` no longer selects its UART automatically, so also enable `CONFIG_UART_MCUMGR`. Rename `CONFIG_SETTINGS_TFM_ITS` to `CONFIG_SETTINGS_TFM_PSA` and `CONFIG_CSPRNG_AVAILABLE` to `CONFIG_ENTROPY_NODE_ENABLED`; TF-M's `SECURE_UART1` is now controlled by `CONFIG_TFM_SECURE_UART`.

## Mapped code partitions (migration-4.4)

Boards using `CONFIG_USE_DT_CODE_PARTITION` or `zephyr,code-partition` should migrate the selected node to `compatible = "zephyr,mapped-partition"`. Its unit address supplies the mapped address, nested partitions use `ranges` without `fixed-subpartitions`, and `CONFIG_FLASH_LOAD_OFFSET`/`CONFIG_FLASH_LOAD_SIZE` cannot be used with it.

## Mbed TLS and TF-PSA-Crypto split (migration-4.4)

Zephyr's Mbed TLS module moves to 4.1.0 and now provides TLS/X.509 only; crypto comes from the new TF-PSA-Crypto 1.1 module, while TF-M continues using Mbed TLS 3.6.5. Legacy Mbed TLS crypto and custom configuration are no longer supported, including `CONFIG_CUSTOM_MBEDTLS_CFG_FILE`, DES and the removed 192/224-bit PSA curves, and the old algorithm-level `CONFIG_MBEDTLS_*` toggles.

## Mbed TLS configuration (migration-4.0)

TLS 1.0/1.1 options `CONFIG_MBEDTLS_TLS_VERSION_1_0` and `CONFIG_MBEDTLS_TLS_VERSION_1_1` are removed. Rename `CONFIG_MBEDTLS_ENTROPY_ENABLED` to `CONFIG_MBEDTLS_ENTROPY_C` and `CONFIG_MBEDTLS_ZEPHYR_ENTROPY` to `CONFIG_MBEDTLS_ENTROPY_POLL_ZEPHYR`; `CONFIG_MBEDTLS_SSL_EXPORT_KEYS` is also removed because export-key support is now assumed enabled.

## Mbed TLS Kconfig alignment (migration-4.3)

Rename `CONFIG_MBEDTLS_MD`, `CONFIG_MBEDTLS_LMS`, `CONFIG_MBEDTLS_TLS_VERSION_1_2`, and `CONFIG_MBEDTLS_DTLS` to `CONFIG_MBEDTLS_MD_C`, `CONFIG_MBEDTLS_LMS_C`, `CONFIG_MBEDTLS_SSL_PROTO_TLS1_2`, and `CONFIG_MBEDTLS_SSL_PROTO_DTLS`. Also rename the TLS 1.3, session-ticket, CTR-DRBG, and HMAC-DRBG symbols to `CONFIG_MBEDTLS_SSL_PROTO_TLS1_3`, `CONFIG_MBEDTLS_SSL_SESSION_TICKETS`, `CONFIG_MBEDTLS_CTR_DRBG_C`, and `CONFIG_MBEDTLS_HMAC_DRBG_C`.

## Mbed TLS Kconfig replacements (migration-4.4)

Rename `CONFIG_MBEDTLS_ENTROPY_POLL_ZEPHYR` to `CONFIG_MBEDTLS_PSA_DRIVER_GET_ENTROPY`, `CONFIG_MBEDTLS_SERVER_NAME_INDICATION` to `CONFIG_MBEDTLS_SSL_SERVER_NAME_INDICATION`, and `CONFIG_MBEDTLS_TEST` to `CONFIG_MBEDTLS_DEBUG_C`. Replace `CONFIG_MBEDTLS_PEM_CERTIFICATE_FORMAT` with the needed combination of `CONFIG_MBEDTLS_PEM_PARSE_C`, `CONFIG_MBEDTLS_PEM_WRITE_C`, and `CONFIG_MBEDTLS_BASE64_C`.

## Mbed TLS random source and key slots (migration-4.1)

When `CONFIG_CSPRNG_ENABLED` is set, `CONFIG_MBEDTLS_PSA_CRYPTO_EXTERNAL_RNG` is now the default instead of `CONFIG_MBEDTLS_PSA_CRYPTO_LEGACY_RNG`. The new `CONFIG_MBEDTLS_PSA_KEY_SLOT_COUNT` explicitly sizes PSA Crypto key storage and defaults to 16 rather than Mbed TLS's previous implicit default of 32.

## Mbed TLS selection names (4.4.0)

Replace deprecated `CONFIG_MBEDTLS_USER_CONFIG_ENABLE` and `CONFIG_MBEDTLS_CFG_FILE` with `CONFIG_MBEDTLS_CONFIG_FILE`, and `CONFIG_MBEDTLS_LIBRARY` with `CONFIG_MBEDTLS_CUSTOM`.

## MCUboot encryption API (4.0.0)

MCUboot replaces `boot_encrypt()` with `boot_enc_encrypt()` and `boot_enc_decrypt()`, renames the `boot_enc_decrypt` symbol to `boot_decrypt_key`, and changes `boot_enc_valid()`/`boot_enc_load()` to use slots rather than image indexes. Target configuration now uses `EXTRA_CONF_FILE` instead of deprecated `OVERLAY_CONFIG`.

## MCUboot image capabilities (4.0.0)

MCUboot and imgtool gain SHA-512 support plus compressed LZMA2 images with an ARM Thumb filter. Other new controls include `CONFIG_MCUBOOT_ENC_BUILTIN_KEY`, encrypted scratch-area retention, a non-bootable image flag, and automatic maximum-sector calculation.

## MCUboot image signing (migration-4.0)

The build system no longer invokes `west sign` for MCUboot, so `CONFIG_MCUBOOT_CMAKE_WEST_SIGN_PARAMS` is removed. Pass imgtool arguments with `CONFIG_MCUBOOT_EXTRA_IMGTOOL_ARGS`; the imgtool portion of `west sign` is deprecated.

## MCUboot offset swap and encrypted HEX flags (4.1.0)

Sysbuild can select the experimental MCUboot swap-using-offset mode with `SB_CONFIG_MCUBOOT_MODE_SWAP_USING_OFFSET`. Signed HEX output now has the encrypted image-header flag set when an encryption-key Kconfig is enabled.

## MCUboot offset-swap default (migration-4.3)

MCUboot now defaults to swap-using-offset rather than swap-using-move. For an optimized unequal layout, make the secondary slot one sector larger than the primary instead of the reverse, or retain move mode with `SB_CONFIG_MCUBOOT_MODE_SWAP_USING_MOVE`; equal-size slots remain supported.

## MCUmgr confirmed-image event data (4.1.0)

The `MGMT_EVT_OP_IMG_MGMT_DFU_CONFIRMED` image-management event now exposes the confirmed image through its `img_mgmt_image_confirmed` data field.

## MCUmgr discovery and transports (4.0.0)

MCUmgr adds supported-group discovery through `mcumgr_smp_group_10`, image slot-information reporting, and custom OS bootloader-info responses through `CONFIG_MCUMGR_GRP_OS_BOOTLOADER_INFO_HOOK` and `os_mgmt_bootloader_info_data`. A LoRaWAN transport is available through `CONFIG_MCUMGR_TRANSPORT_LORAWAN`.

## MCUmgr platform identity and hashing (migration-4.3)

The OS application-info response now reports the complete board target, including SoC and board variant, instead of the short board-plus-revision form; enable `CONFIG_MCUMGR_GRP_OS_INFO_HARDWARE_INFO_SHORT_HARDWARE_PLATFORM` for compatibility. MCUmgr filesystem hashing is PSA-only, and `CONFIG_MCUMGR_GRP_FS_HASH_SHA256` brings in Mbed TLS's PSA implementation when TF-M is absent.

## NAND flash translation and bad blocks (4.4.0)

The `zephyr,ftl-dhara` disk driver exposes NAND as a standard disk with wear leveling and bad-block management. Flash drivers can implement `FLASH_EX_OP_MARK_BAD_BLOCK` and `FLASH_EX_OP_IS_BAD_BLOCK`, while `jedec,mspi-nor` can configure read, write, and control commands separately in Devicetree.

## NVMEM subsystem (4.3.0)

The new `CONFIG_NVMEM` subsystem exposes named or indexed Devicetree cells through `NVMEM_CELL_GET_BY_NAME`/`NVMEM_CELL_GET_BY_IDX` variants and provides readiness, read, and write APIs. `CONFIG_NVMEM_EEPROM` supplies an EEPROM-backed implementation.

## OTP and flash-backed NVMEM (4.4.0)

`CONFIG_OTP` introduces standard `otp_read()` and `otp_program()` access, with programming gated by `CONFIG_OTP_PROGRAM`; OTP devices are also accessible through NVMEM. NVMEM itself gains flash storage through `CONFIG_NVMEM_FLASH` and optional writes through `CONFIG_NVMEM_FLASH_WRITE`.

## Partition macros (migration-4.4)

The `FIXED_PARTITION_*` macro family is deprecated in favor of corresponding `PARTITION_*` names, such as `PARTITION_ID`, `PARTITION_OFFSET`, `PARTITION_DEVICE`, and `PARTITION_BY_NODE`; the replacements also support `zephyr,mapped-partition`.

## Persistence configuration (4.0.0)

Settings commit handlers can be ordered with `SETTINGS_STATIC_HANDLER_DEFINE_WITH_CPRIO()` or `settings_register_with_cprio()`. FATFS gains opt-ins for direct library linking/native APIs, 64-bit LBA and GPT, multiple GPT/MBR partitions, and RTC timestamps through `CONFIG_FILE_SYSTEM_LIB_LINK`, `CONFIG_FS_FATFS_EXTRA_NATIVE_API`, `CONFIG_FS_FATFS_LBA64`, `CONFIG_FS_FATFS_MULTI_PARTITION`, and `CONFIG_FS_FATFS_HAS_RTC`.

## PSA Crypto provider selection (4.3.0)

`CONFIG_PSA_CRYPTO` selects TF-M as the PSA provider for `CONFIG_BUILD_WITH_TFM` builds and Mbed TLS otherwise; `CONFIG_PSA_CRYPTO_PROVIDER_CUSTOM` supports an application-supplied provider. Built-in PSA keys are enabled with `CONFIG_MBEDTLS_PSA_CRYPTO_BUILTIN_KEYS`.

## PSA key slots and persistent key IDs (4.1.0)

`CONFIG_MBEDTLS_PSA_STATIC_KEY_SLOTS` adds static PSA key-slot configuration. Persistent PSA Crypto key IDs must now be constructed from the user and subsystem ranges allocated in `<zephyr/psa/key_ids.h>`.

## PSA-only crypto paths (migration-4.3)

TinyCrypt is removed, and PSA Crypto is the recommended replacement. UpdateHub also removes its legacy Mbed TLS path; `CONFIG_UPDATEHUB` automatically selects Mbed TLS's PSA implementation when TF-M is unavailable.

## Renesas RA flash naming (migration-4.2)

Rename `CONFIG_RA_FLASH_HP` to `CONFIG_SOC_FLASH_RENESAS_RA_HP` and `CONFIG_FLASH_RA_WRITE_PROTECT` to `CONFIG_FLASH_RENESAS_RA_HP_WRITE_PROTECT`; `CONFIG_DUAL_BANK_MODE` is removed. The generic `renesas,ra-nv-flash` binding is split into `renesas,ra-nv-code-flash` and `renesas,ra-nv-data-flash`.

## Secure storage (4.0.0)

The new secure-storage subsystem makes the PSA Secure Storage API and persistent PSA Crypto keys available on all board targets, and is the standard path for device-specific protection of data at rest.

## Secure storage and stream-flash sizing (migration-4.1)

Secure-storage backends no longer select or imply their dependencies. In particular, `CONFIG_SECURE_STORAGE_ITS_STORE_IMPLEMENTATION_SETTINGS` no longer pulls in settings and NVS, so applications must explicitly enable the intended dependencies.

`stream_flash_init()` no longer interprets a zero `size` as auto-detection; provide the device size explicitly or the call fails.

## Secure storage and TF-M settings (4.3.0)

Secure storage is no longer experimental. The settings subsystem can use TF-M Internal Trusted Storage through `CONFIG_SETTINGS_TFM_ITS`.

## Secure-storage UID compatibility (migration-4.3)

`psa_storage_uid_t` shrinks from 64 to 30 bits, breaking authentication of existing entries. Enable `CONFIG_SECURE_STORAGE_64_BIT_UID` when upgrading an installed system that must retain pre-4.3 secure-storage data.

## Security fixes (4.2.0)

This release addresses TLS server-authentication skipping and handshake authentication bypasses, an LMS signature-verification bypass, a DNS-name parsing infinite loop, and several Mbed TLS memory and timing flaws. The bundled Mbed TLS version is updated from 3.6.2 to 3.6.4.

## Security update (4.4.2)

Zephyr 4.4.2 fixes HTTP static-resource path traversal permitting arbitrary file reads (CVE-2026-8023), crafted-ext2 division by zero (CVE-2026-7007), concurrent `net_buf` reference-count corruption (CVE-2026-10653), and memory-safety or denial-of-service flaws across Bluetooth, sockets, DNS, SNTP, WireGuard, USB, kernel userspace, storage, and multiple drivers. Security-sensitive 4.4.1 deployments should upgrade as a unit; the release also reserves many CVEs whose details were still embargoed.

## STM32N6 security state (migration-4.4)

STM32N6 projects must now explicitly select either `CONFIG_TRUSTED_EXECUTION_SECURE` or `CONFIG_TRUSTED_EXECUTION_NON_SECURE` according to the state in which Zephyr executes.

## Stream Flash erasure (4.1.0)

`stream_flash_erase_page()` is deprecated; use `flash_area_erase()` or `flash_erase()`. Erasing storage directly can destroy Stream Flash data and is appropriate only when Stream Flash is not configured to erase or when removing data before or after its use of the area.

## TF-M attestation upgrades (migration-4.3)

The TF-M v2.1 attestation incompatibility affects Zephyr 3.7 through 4.2 upgrades to later TF-M versions; the fix is included in Zephyr 4.3. Migrate directly from an affected earlier Zephyr release to 4.3 or later to preserve attestation upgrade compatibility.

## TF-M BL2 signing and FOTA images (migration-4.3)

TF-M NS boards using BL2 must describe the flash controller in their layout. Signing now derives alignment from devicetree `write_block_size`, calculates maximum sectors across images, and confirms both S and NS HEX files; the new S and NS BIN files are unconfirmed FOTA images and must be accepted with `psa_fwu_accept()` to avoid rollback after reboot.

## TF-M module sourcing (migration-4.3)

CMake no longer downloads MCUboot or Ethos automatically for TF-M builds. The in-tree modules are used by default; select custom versions by adding them to a west manifest.

## TF-M non-secure headers (4.4.0)

TF-M non-secure interface headers are now exported automatically through `zephyr_interface`; non-secure applications no longer need to link `tfm_api` explicitly.

## TF-M rollback counter (migration-4.0)

Hardware rollback protection now takes its security counter explicitly from `CONFIG_TFM_IMAGE_SECURITY_COUNTER` instead of deriving it from the image version. Set it deliberately during migration, especially for versions beyond `0.0.1024`.

## TF-PSA-Crypto customization (4.4.0)

`CONFIG_TF_PSA_CRYPTO_USER_CONFIG_FILE` supplies a TF-PSA-Crypto user configuration, and `CONFIG_PSA_WANT_ALG_SHAKE128` and `CONFIG_PSA_WANT_ALG_SHAKE256` request SHAKE support. `CONFIG_ENTROPY_PSA_CRYPTO_RNG` is deprecated.

## TinyCrypt-dependent crypto (migration-4.0)

TinyCrypt removal has begun: its shim driver is deprecated, CTR-DRBG now requires Mbed TLS when `CONFIG_CTR_DRBG_CSPRNG_GENERATOR` is enabled, and JWT no longer uses TinyCrypt. JWT signatures default to PSA Crypto; replace `CONFIG_JWT_SIGN_RSA`/`CONFIG_JWT_SIGN_ECDSA` with `CONFIG_JWT_SIGN_RSA_PSA`, `CONFIG_JWT_SIGN_RSA_LEGACY`, or `CONFIG_JWT_SIGN_ECDSA_PSA`.

## TLS 1.3 (4.0.0)

TLS sockets and Mbed TLS now support TLS 1.3 through `CONFIG_MBEDTLS_TLS_VERSION_1_3`. Session tickets use `CONFIG_MBEDTLS_TLS_SESSION_TICKETS`, while PSK, ephemeral, and PSK-ephemeral exchange use the corresponding `CONFIG_MBEDTLS_SSL_TLS1_3_KEY_EXCHANGE_MODE_*` symbols.

## WPA supplicant crypto default (migration-4.4)

`CONFIG_WIFI_NM_WPA_SUPPLICANT_CRYPTO_MBEDTLS_PSA` is now enabled by default.

## ZMS key-value storage (4.0.0)

ZMS is a new key-value subsystem that works with conventional NOR flash and with no-erase nonvolatile media such as RRAM and MRAM.
