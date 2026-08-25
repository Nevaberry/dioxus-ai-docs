---
name: zephyr-knowledge-patch
description: Zephyr RTOS
version: 4.4.0
license: MIT
metadata:
  author: Nevaberry
---


# Zephyr RTOS Compatibility Guide

Use this skill when migrating, configuring, building, testing, or debugging
Zephyr applications, boards, subsystems, and out-of-tree drivers.

## How to use this skill

1. Read the project manifest and configuration before proposing changes.
2. Identify whether the problem is a removed API, renamed Kconfig symbol,
   changed Devicetree binding, new runtime registration requirement, or changed
   default.
3. Start with the breaking-change checks below.
4. Load the reference file matching the subsystem being changed.
5. Preserve explicit application choices when replacing an old default.
6. Rebuild generated Devicetree and Kconfig outputs after migrations.
7. Run the smallest relevant test first, then the affected integration suite.
8. Treat project code, manifests, generated files, and observed behavior as
   authoritative when they differ from compatibility guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [bluetooth.md](references/bluetooth.md) | Host, controller, GATT, Mesh, Classic, LE Audio, ISO, pairing, and channel sounding |
| [build-boards-and-testing.md](references/build-boards-and-testing.md) | Toolchains, board targets, runners, sysbuild, native simulation, Twister, and ztest |
| [devicetree-and-hardware.md](references/devicetree-and-hardware.md) | Bindings, properties, clocks, SoCs, architecture ports, memory, and pin control |
| [display-input-and-media.md](references/display-input-and-media.md) | Display, LVGL, input, haptics, video, UVC, pixel formats, and media buffers |
| [drivers-and-peripherals.md](references/drivers-and-peripherals.md) | ADC, CAN, UART, SPI, I3C, I2S, counters, DMA, steppers, watchdogs, and device APIs |
| [kernel-runtime-and-utilities.md](references/kernel-runtime-and-utilities.md) | Kernel APIs, POSIX, power management, logging, RTIO, Zbus, utilities, and runtime behavior |
| [networking-and-iot.md](references/networking-and-iot.md) | Ethernet, sockets, HTTP, CoAP, DNS, DHCP, MQTT, LwM2M, OpenThread, Wi-Fi, and IoT protocols |
| [security-storage-and-updates.md](references/security-storage-and-updates.md) | Security fixes, PSA Crypto, Mbed TLS, TF-M, MCUboot, flash, storage, and update flows |

## Breaking-change triage

### Build and board failures

- Convert all out-of-tree HWMv1 boards and SoCs to HWMv2.
- Use current qualified board targets; removed aliases no longer build.
- Require Zephyr SDK 1.0.0, Python 3.12, and a C17-capable toolchain.
- Add full_name to new board.yml entries.
- Do not assume BOARD_QUALIFIERS begins with a slash.
- Add application snippet roots explicitly through module metadata or CMake.
- Make downstream libraries depend on zephyr_generated_headers when they
  consume generated heap constants.
- Use file-type selection for OpenOCD artifacts.
- Update Nordic flashing automation for nRF Util defaults and explicit erase
  modes.
- Use sysbuild for STM32N6 chainloaded application targets.

### Devicetree and hardware failures

- Replace underscore property spellings with binding-defined hyphenated names.
- Do not put defaults for status, address cells, or size cells in bindings.
- Use DT_REG_ADDR_RAW when a register address is used as a Devicetree index.
- Replace power-domain with plural power-domains and declare provider cells.
- Give SDMMC and MMC disks explicit disk-name values.
- Move oscillator, regulator, clock, and pin-control choices from deprecated
  Kconfig symbols into Devicetree where required.
- Describe RISC-V ISA capabilities in the required riscv node.
- Migrate code partitions to zephyr,mapped-partition.
- Point NXP FlexSPI chosen flash and controller entries at their distinct
  child and parent nodes.
- Check active-low GPIO flags explicitly when bindings change reset semantics.

### Kernel and core API failures

- Replace CONFIG_MP_NUM_CPUS with CONFIG_MP_MAX_NUM_CPUS.
- Replace deprecated pipe calls with k_pipe_write, k_pipe_read, k_pipe_reset,
  and k_pipe_close semantics.
- Interpret device_init failure as a negative errno.
- Include the standard POSIX headers directly.
- Size the file-descriptor table through ZVFS_OPEN_SIZE and contributed minima.
- Return an SMF event result from hierarchical run actions.
- Inspect the first error passed to RTIO callback chains.
- Enable CONFIG_STACK_CANARIES_ALL when all-function protection is required.
- Enable CONFIG_POLL explicitly when Bluetooth code still uses k_poll.
- Configure watchdogs explicitly instead of relying on startup defaults.

### Driver and peripheral failures

- Declare out-of-tree implementations of upstream driver classes with
  DEVICE_API.
- Use DEVICE_API_IS for runtime API checks and compatible shell completion.
- Split stepper enable and disable calls, then migrate motion interfaces to the
  stepper_ctrl family where applicable.
- Put SPI chip-select setup and hold delays in Devicetree.
- Select driver-specific CAN filter and message-buffer capacities.
- Select both counter 64-bit capability and application support before calling
  get_value_64.
- Treat uart_irq_tx_ready values greater than zero as ready.
- Add the required timeout to video-buffer allocation calls.
- Expect signal-only IPM callbacks to receive a null payload.
- Configure watchdog timeout and startup from application code.

### Networking failures

- Include POSIX socket headers directly or use zsock-prefixed APIs.
- Update networking types and constants to net, NET, and ZSOCK namespaces.
- Treat socklen_t as a 32-bit unsigned type.
- Size HTTP concurrency and backlog arguments deliberately.
- Pass HTTP service configuration and fallback-resource arguments.
- Reset dynamic HTTP state on transaction completion.
- Return net_verdict from ICMP handlers.
- Move CoAP discovery attributes to resource metadata.
- Use the new CoAP client response-data ownership model.
- Use a source argument when reconfiguring DNS resolvers.
- Replace raw AF_PACKET protocol usage with datagram link-layer sockets or
  proper IP raw sockets.
- Expect forwarded IPv4 and IPv6 packets to have decremented hop limits.

### Bluetooth failures

- Register BAP, PACS, Scan Delegator, TBS, and related callbacks at runtime in
  the required order.
- Explicitly enable LE Audio dependencies formerly selected automatically.
- Restart legacy connectable advertising explicitly when the application
  depended on automatic resumption.
- Use the driver-model HCI API and current lower-case Devicetree bus values.
- Create and remove ISO data paths explicitly.
- Secure the ACL before connecting an ISO channel.
- Use CONFIG_PSA_CRYPTO for Mesh provider selection.
- Replace fixed-passkey configuration with an application passkey callback.
- Read BASS receive states explicitly after Broadcast Assistant discovery.
- Return true to continue audio iteration and false to stop.
- Check GATT notification permissions on the characteristic value.

### Security, storage, and update failures

- Upgrade security-sensitive deployments as a coordinated image set when a
  maintenance release fixes cross-subsystem vulnerabilities.
- Pass imgtool arguments through CONFIG_MCUBOOT_EXTRA_IMGTOOL_ARGS.
- Set the TF-M image security counter deliberately.
- Preserve installed secure-storage entries with the 64-bit UID compatibility
  option when required.
- Choose a PSA Crypto provider explicitly and remove TinyCrypt paths.
- Account for the Mbed TLS and TF-PSA-Crypto module split.
- Select TLS versions and ciphersuites explicitly for secure sockets.
- Use authenticated hawkBit DDI configuration.
- Preserve the intended MCUboot swap mode and partition-size relationship.
- Accept TF-M secure and non-secure FOTA images before reboot when required.
- Supply Secure Storage backends and their Settings, NVS, or ZMS dependencies
  explicitly.
- Use PARTITION macros in place of the deprecated FIXED_PARTITION family.

## High-value feature quick reference

### Build and diagnostics

- Use dtdoctor for Devicetree failures and traceconfig for Kconfig provenance.
- Use the build dashboard for footprint, initialization, and Devicetree views.
- Use the ztest benchmark framework for compensated cycle measurements.
- Use scope helpers for RAII-style cleanup in C.
- Generate compile-time layout constants with zephyr_constants_library.

### Runtime and data movement

- Use asynchronous Zbus listeners when observers must leave the publisher
  thread.
- Use proxy agents to bridge Zbus channels across CPU or domain boundaries.
- Enable tiered sys_heap hardening at the assurance level the target can
  afford.
- Use streaming COBS helpers for incremental framing.
- Use disjoint-set helpers for union-find workloads.
- Use the CPU-load and pressure-based frequency policies for demand-driven
  clock scaling.

### Hardware and media

- Use NVMEM cells for named hardware data and OTP for one-time programming.
- Register display, PWM, and haptics event callbacks for asynchronous status.
- Import externally owned video buffers when capture memory comes from another
  allocator or named region.
- Use video format classification helpers before calculating layouts.
- Use USB host-class UVC support when Zephyr is the camera host.

### Connectivity

- Use WireGuard for integrated VPN connectivity.
- Use Wi-Fi peer-to-peer management for direct discovery and connections.
- Use multicast CoAP clients and parallel-client DTLS servers where required.
- Use raw-UART SMP when MCUmgr framing must run directly over UART.
- Use LoRa CAD, airtime, and duty-cycle receive APIs for channel-aware radios.

## Verification checklist

- Confirm every renamed symbol is absent from the final configuration.
- Inspect generated Devicetree for required properties, child topology, and
  chosen-node targets.
- Verify flash partitions and update slots against deployed-device layouts.
- Re-run signing, flashing, reset, and rollback tests on physical hardware.
- Exercise network timeout, backlog, cancellation, and teardown paths.
- Exercise Bluetooth registration, disconnect, iteration-stop, and pairing
  downgrade paths.
- Test storage migration with a copy of persistent production data.
- Run Twister or ztest suites that cover each changed subsystem.
- Recheck security advisories before releasing a product based on an older
  maintenance image.
