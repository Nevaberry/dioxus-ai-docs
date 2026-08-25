---
name: zephyr-knowledge-patch
description: Zephyr RTOS
version: 4.4.0
license: MIT
metadata:
  author: Nevaberry
---


# Zephyr RTOS Knowledge Patch

Use this skill when maintaining Zephyr applications, boards, drivers, modules,
or tooling where current APIs, Kconfig symbols, Devicetree bindings, build
behavior, or subsystem contracts matter.

## Working method

1. Read the project's manifest, module revisions, board target, overlays, and
   configuration before applying guidance.
2. Identify the subsystem being changed and open the matching reference below.
3. Apply migration notes only when the project's selected Zephyr revision
   includes the change. Treat project source, generated Devicetree, Kconfig
   diagnostics, and tests as authoritative.
4. Search application code, out-of-tree drivers, bindings, board definitions,
   CI commands, and sysbuild configuration for both removed and replacement
   names.
5. Reconfigure from a pristine build directory after Kconfig, Devicetree,
   board-target, toolchain, or sysbuild changes.
6. Build every affected board qualifier and image, then run relevant Twister,
   ztest, hardware, networking, security, and upgrade tests.

## Reference index

| Reference | Topics |
| --- | --- |
| [Application subsystems and services](references/application-subsystems.md) | Zbus, logging, settings, shell, OCPP, CPU metrics, instrumentation, utility libraries, and service APIs |
| [Bluetooth](references/bluetooth.md) | Host, controller, HCI, GATT, Mesh, Classic, LE Audio, ISO, pairing, and channel sounding |
| [Builds, boards, flashing, and testing](references/build-boards-testing.md) | Toolchains, west, sysbuild, targets, runners, native simulation, Twister, ztest, and diagnostics |
| [Devicetree, drivers, and hardware](references/devicetree-drivers.md) | Bindings, ADC, CAN, clocks, Ethernet hardware, flash, I3C, sensors, SPI, timers, and power |
| [Graphics, input, stepper, and USB](references/graphics-input-usb.md) | Displays, LVGL, video, input, haptics, PWM, steppers, USB device, UVC, and USB host |
| [Kernel, architecture, and core APIs](references/kernel-architecture.md) | Kernel, POSIX, scheduling, userspace, architecture ports, memory, runtime PM, and core utilities |
| [Networking and protocols](references/networking-protocols.md) | Sockets, HTTP, CoAP, DHCP, DNS, Ethernet L2, LwM2M, MQTT, OpenThread, Wi-Fi, and LoRa |
| [Security, storage, and firmware update](references/security-storage-update.md) | PSA Crypto, Mbed TLS, secure storage, filesystems, MCUboot, MCUmgr, hawkBit, TF-M, and security fixes |

## Breaking-change quick reference

### Build, boards, and flashing

- Use current hardware-model board targets; the first-generation hardware
  model and its compatibility aliases are gone.
- Prefer `native_sim` naming throughout native boards and drivers. Native UART
  instances use `uart_native_pty` and `zephyr,native-pty-uart`.
- Account for runner changes: Nordic boards prefer nRF Util, current STM32
  boards may prefer STM32CubeProgrammer, and erase/reset behavior is now more
  explicit.
- Use application file suffixes and `sysbuild_file_suffixes`; the old build-type
  feature is removed.
- Update OpenOCD file selection to `--file-type=elf`, `bin`, or `hex` and use
  `--file` for an alternate artifact.
- Require Python 3.12, Zephyr SDK 1.0.0, and C17-capable tooling; temporary C99
  and C11 fallbacks are deprecated.
- Add `zephyr_generated_headers` dependencies to downstream CMake targets that
  consume generated headers during parallel builds.

### Kernel, architecture, and core APIs

- Replace `CONFIG_MP_NUM_CPUS` with `CONFIG_MP_MAX_NUM_CPUS`.
- Replace the deprecated pipe API with `k_pipe_write()`, `k_pipe_read()`,
  `k_pipe_reset()`, and `k_pipe_close()`; transfer thresholds and dynamic pipe
  allocation are gone.
- Treat `device_init()` failures as negative `-errno` values.
- Use standard POSIX headers rather than `<zephyr/posix/...>` wrappers, and
  enable `CONFIG_POSIX_API` when unprefixed socket names are required.
- Update file-descriptor sizing around `ZVFS_OPEN_SIZE` and contributed
  `CONFIG_ZVFS_OPEN_ADD_SIZE_*` requirements.
- DMA no longer exposes a userspace syscall surface.
- Use `min`, `max`, and `clamp` instead of `Z_MIN`, `Z_MAX`, and `Z_CLAMP`.
- Replace cache-coherence hooks with `CONFIG_CACHE_CAN_SAY_MEM_COHERENCE` and
  `sys_cache_is_mem_coherent()`.

### Devicetree and driver contracts

- Use `DT_REG_ADDR_RAW` when an address is used as a Devicetree index; normal
  register address and size macros now produce unsigned literals.
- Bindings must use hyphenated property names and cannot default `status`,
  `#address-cells`, or `#size-cells`.
- Use plural `power-domains`, declare `#power-domain-cells`, and use
  `power-domain-names` for multiple entries.
- Out-of-tree implementations of upstream driver classes must declare their
  iterable-section API with `DEVICE_API()`.
- Configure PHY link settings through the PHY API and Devicetree rather than
  removed Ethernet MAC Kconfigs and requests.
- Use driver-specific CAN filter limits and Devicetree mailbox counts instead
  of removed generic capacity options.
- For 64-bit counter values, select both driver support and application use
  with the corresponding counter Kconfigs.
- RISC-V platforms require a `riscv` Devicetree node with `riscv,isa-base` and
  `riscv,isa-extensions`.

### Security, storage, and update

- Pass MCUboot imgtool arguments through `CONFIG_MCUBOOT_EXTRA_IMGTOOL_ARGS`;
  the build no longer invokes `west sign` for MCUboot.
- Set `CONFIG_TFM_IMAGE_SECURITY_COUNTER` explicitly rather than deriving the
  rollback counter from the image version.
- Use PSA Crypto paths. TinyCrypt is removed, and current Mbed TLS provides
  TLS/X.509 while TF-PSA-Crypto provides cryptography.
- Explicitly select secure-storage backend dependencies; settings, NVS, ZMS,
  and related storage are not implied.
- Preserve installed secure-storage data with
  `CONFIG_SECURE_STORAGE_64_BIT_UID` when compatibility with old 64-bit UIDs is
  required.
- Size `stream_flash_init()` explicitly; zero no longer discovers capacity.
- Use authenticated hawkBit DDI configuration; anonymous mode is removed.
- Treat signed secure and non-secure TF-M BIN outputs as unconfirmed FOTA
  images and accept them before reboot when appropriate.

### Networking and protocols

- Include network buffers from `<zephyr/net_buf.h>` and update socket-service
  callbacks to receive `struct net_socket_service_event *`.
- Update `net_mgmt` handlers to accept a 64-bit event and decode it with
  `NET_MGMT_LAYER_CODE` and `NET_MGMT_GET_COMMAND`.
- Use `net_linkaddr.len == 0` to detect an unset inline link address.
- Pass the new required arguments to CoAP block, HTTP response, ICMP, DNS
  reconfiguration, MQTT disconnect, and LwM2M APIs.
- Review HTTP service `_concurrent`, `_backlog`, `_config`, and fallback-resource
  arguments: current service macros honor all of them.
- Update networking identifiers to `net_`, `NET_`, and `ZSOCK_` forms, and
  include POSIX socket headers directly when using POSIX APIs.
- Secure sockets enforce their protocol argument as the minimum TLS version;
  explicitly choose TLS versions and ciphersuites.
- Forwarded IPv4 and IPv6 packets now decrement their TTL or hop limit.

### Bluetooth

- Register BAP Unicast Server, Scan Delegator, PACS, and related profiles at
  runtime before use; enable their dependencies explicitly.
- Rename the codec QoS family to `bt_bap_qos_cfg` and use `BT_BAP_QOS_CFG*`
  constants.
- Restart legacy connectable advertising explicitly when the application
  relied on automatic resumption; extended advertising never auto-resumes.
- Use the normal driver model for HCI drivers. Current HCI buffers carry the
  H:4 type in the payload and commands are allocated with
  `bt_hci_cmd_alloc()`.
- Create and remove ISO data paths explicitly and secure the ACL before
  connecting an ISO channel.
- Migrate Mesh storage to PSA carefully: incompatible key storage requires
  unprovisioning and reprovisioning.
- Legacy LE passkey-entry bonds no longer provide MITM authentication.
- Audio foreach callbacks return `true` to continue and `false` to stop.

### Graphics, input, video, and USB

- Pass `user_data` through input callback definitions and callbacks; use
  `NULL` for context-free behavior.
- Update video code for `video_buf_type`, bit-based pixel sizes, timeout-aware
  allocation, `video_format.size`, and the consolidated stream hook.
- Apply UVC-negotiated format and frame rate to the source device in the
  application.
- Use `uvc_device_init()`, `uvc_device_add_format()`,
  `uvc_device_enable()`, and `uvc_device_shutdown()`.
- Migrate stepper motion calls and events to `stepper_ctrl_*` and
  `STEPPER_CTRL_EVENT_*`, and move step/direction motion properties to a
  controller node.
- Remove display color-format workarounds that depended on earlier RGB/BGR or
  monochrome inversions.

## High-value additions

### Platform and developer tooling

- Use `dtdoctor`, `traceconfig`, footprint charts, and the build dashboard to
  investigate configuration and image-size problems.
- Twister supports power measurement and camera-based display validation;
  ztest includes a benchmark framework with overhead compensation and
  statistical reporting.
- `zephyr_constants_library()` can generate C headers from build-time structure
  layout constants.
- Scope helpers provide RAII/defer-style cleanup in C, and tiered heap
  hardening adds progressively stronger allocator checks.

### Devices and application services

- Standard subsystems now cover secure storage, ZMS, comparators, haptics,
  steppers, operational amplifiers, NVMEM, OTP, biometrics, and wake-up
  controllers.
- Zbus provides heapless runtime observers, asynchronous listeners, and
  experimental IPC proxy agents.
- CPU load metrics, pressure-based frequency policy, and compiler-assisted
  instrumentation support profiling and adaptive performance.
- The OCPP library supplies charge-point authorization, transaction, and meter
  operations over WebSocket.

### Connectivity and firmware management

- Networking adds WireGuard, Wi-Fi Direct, MQTT 5, secure CoAP services,
  HTTP compression, FTP, richer DNS records, and asynchronous SNTP.
- MCUmgr adds discovery, slot information, LoRaWAN, UDP/DTLS, raw UART, and
  firmware-updater flows.
- MCUboot supports offset swap, RAM-load and firmware-loader compositions,
  SHA-512, compressed LZMA2 images, and direct-XIP slot variants.
- Bluetooth adds Classic HFP roles, LE Audio group management, Alert
  Notification Service, callback unregistration, and Mesh key synchronization.

## Validation checklist

- Re-run CMake configuration after changing board targets, qualifiers, module
  manifests, Kconfig, Devicetree, snippets, or sysbuild composition.
- Compile every code path affected by callback signatures, structure layout,
  enum values, constness, or renamed symbols.
- Validate generated Devicetree and Kconfig values rather than assuming an old
  default still applies.
- Test bootloader upgrades and storage migrations on copies of installed data,
  including rollback counters, partition layouts, key formats, and image
  confirmation.
- Exercise networking and Bluetooth teardown, retry, timeout, resumption, and
  security paths, not only successful setup.
- Run unit tests, Twister scenarios, and hardware tests appropriate to each
  changed subsystem.
