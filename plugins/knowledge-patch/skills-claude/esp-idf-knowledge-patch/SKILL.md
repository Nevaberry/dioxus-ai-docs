---
name: esp-idf-knowledge-patch
description: ESP-IDF
version: 6.0
license: MIT
metadata:
  author: Nevaberry
---


# ESP-IDF Knowledge Patch

Use this skill when updating an ESP-IDF application, component, build, or tool
integration and the failure may come from a renamed API, removed component,
changed default, or stricter contract. Start with the breaking-change triage,
then open the topic reference that matches the affected subsystem.

## Reference index

| Reference | Topics |
| --- | --- |
| [build-and-components.md](references/build-and-components.md) | Toolchains, warnings, Kconfig, dependencies, managed components, tools, size output, bootloader |
| [drivers-and-hardware.md](references/drivers-and-hardware.md) | Touch, TWAI, legacy-driver replacements, GPIO, MCPWM, I2C, DMA, LCD, SPI, PSRAM, flash |
| [connectivity.md](references/connectivity.md) | Bluetooth, Ethernet, esp-netif, DHCP, SNTP, ping, provisioning, Wi-Fi, NAN, HTTP server |
| [security-and-crypto.md](references/security-and-crypto.md) | SHA, ESP-TLS, Mbed TLS, PSA Crypto, secure boot, BluFi, NVS encryption |
| [runtime-and-diagnostics.md](references/runtime-and-diagnostics.md) | Logging, VFS, libc, sleep, app trace, SystemView, gcov, FreeRTOS, core dumps, OTA |

## Breaking-change triage

Check failures in this order:

1. Treat warnings, orphan sections, and Kconfig parser failures as real build
   blockers. Fix the diagnostic or placement; use compatibility switches only
   as temporary migration aids.
2. Audit `idf_component.yml`, `REQUIRES`, and `PRIV_REQUIRES`. Split drivers and
   formerly built-in libraries no longer arrive through broad transitive
   dependencies.
3. Replace removed legacy drivers with their handle-based or channel-based
   successors. Do not mix the legacy and event-driven TWAI drivers.
4. Add FreeRTOS headers explicitly where public driver or event headers used to
   supply them indirectly.
5. Review networking callbacks and structures. Several callback arguments,
   flexible-array fields, and init/error semantics changed.
6. Initialize PSA Crypto before direct cryptographic or certificate use, and
   ensure NVS is initialized before persistent PSA keys are accessed.
7. Revalidate libc assumptions, constructor ordering, IRAM placement, and
   scripts that parse `idf.py size` output.

## Build and dependency essentials

### Make warnings and linker placement explicit

- Correct warning-producing code first. In particular, call allocation APIs
  with the element count before the element size: `calloc(n, sizeof(int))`.
- Linker orphan sections are errors by default. Place them with a linker
  fragment rather than depending on incidental linker behavior.
- Default warnings are errors. A global warning-disable setting can unblock a
  port temporarily, but it also hides diagnostics introduced by a new
  toolchain.
- Project Kconfig files must satisfy esp-idf-kconfig v3 syntax.

### Declare what each component uses

Name every `esp_driver_*` dependency used by a component. Also add direct
dependencies for headers that moved behind component boundaries, including
`esp_common`, `esp_usb_cdc_rom_console`, `esp_trace`, and managed components
where applicable.

Common manifest migrations include:

| Former assumption | Current dependency or approach |
| --- | --- |
| Built-in `json` | `espressif/cjson`; keep using `cJSON.h` |
| Built-in ESP-MQTT | `espressif/mqtt`; keep using `mqtt_client.h` |
| Built-in provisioning | `espressif/network_provisioning` |
| Built-in SystemView | `espressif/esp_sysview` |
| Built-in gcov | `espressif/esp_gcov` and `esp_gcov.h` |
| Bundled Catch2 | Managed Catch2 3.x component |

## Driver migration essentials

Use these replacements as entry points; the hardware reference carries field,
callback, and configuration details.

| Removed or legacy interface | Preferred interface |
| --- | --- |
| ADC legacy driver | `esp_adc` |
| MCPWM legacy driver | `esp_driver_mcpwm` |
| Timer group | `driver/gptimer.h` |
| Legacy I2S | `driver/i2s_std.h`, `i2s_pdm.h`, or `i2s_tdm.h` |
| PCNT | `driver/pulse_cnt.h` |
| RMT legacy API | `driver/rmt_tx.h`, `rmt_rx.h`, and `rmt_encoder.h` |
| DAC legacy API | one-shot, continuous, or cosine DAC headers |
| Sigma-delta legacy API | `driver/sdm.h` |
| `gdma_new_channel` | `gdma_new_ahb_channel` or `gdma_new_axi_channel` |
| `ledc_timer_set` | `ledc_timer_config` or `ledc_set_freq` |

The redesigned touch driver is `esp_driver_touch_sens` with
`driver/touch_sens.h`. The event-driven TWAI interface uses `esp_driver_twai`,
`esp_twai.h`, and `esp_twai_onchip.h`; receive from `on_rx_done` with
`twai_node_receive_from_isr`.

## Connectivity migration essentials

- Replace unsafe assumptions around `esp_netif_next`. Prefer
  `esp_netif_find_if`; otherwise execute traversal in a controlled TCP/IP
  context.
- Configure SoftAP DNS offers at runtime with `esp_netif_dhcps_option` and
  `esp_netif_set_dns_info`.
- Replace old ping helpers with sessions from `ping/ping_sock.h`, and include
  `esp_sntp.h` instead of `sntp.h`.
- Use Wi-Fi events for DPP, PHY APIs for antenna control, and
  `esp_now_set_peer_rate_config` for ESP-NOW peer rates.
- Initialize newly added structure fields with designated initializers,
  especially NAN USD and off-channel request structures.
- A repeated `esp_wifi_init` is an error; do not use it as an idempotent
  initialization probe.

## Security migration essentials

### PSA and TLS

Call `psa_crypto_init()` before direct cryptographic, certificate, or TLS use.
Normal startup performs initialization, but code that runs outside that path
must not assume it. Import hardware-backed ECDSA keys with `psa_import_key` and
an `esp_ecdsa_opaque_key_t` representation.

If a non-mbedTLS transport is required, enable `CONFIG_ESP_TLS_CUSTOM_STACK`,
implement `esp_tls_stack_ops_t`, and register it before opening connections.
Create connections from an `esp_tls_t` returned by `esp_tls_init`; the old HTTP
connection convenience function is unavailable.

### SHA and persistent keys

Select the SHA mode with `esp_sha_set_mode` before calling the block or DMA
sub-functions. Persistent PSA storage uses NVS, so initialize NVS first and
handle its availability as a dependency of persistent key operations.

## Runtime and tooling essentials

### Logging

Prefer `ESP_LOG_BUFFER_HEX` and `ESP_LOG_BUFFER_CHAR`. Device-side log colors
are off by default because IDF Monitor colors on the host; either enable device
colors for another monitor or use `idf.py monitor --disable-auto-color`.

Log V2 is selected with `CONFIG_LOG_VERSION`. In a V2 handler use `esp_log` and
`esp_log_va` for internal formatting. Dynamic formatting and execution-context
detection are V2-only, so keep shared code within the V1-compatible subset when
both modes must work.

### Libc, sleep, and memory placement

PicolibC shares stdin, stdout, and stderr globally. Select full Newlib when code
depends on task-local Newlib reentrancy internals; the compatibility switch is
not a complete emulation. Use standard `<signal.h>` and `<dirent.h>` includes.

Use `esp_sleep_get_wakeup_causes()` when more than one wake source can fire and
test the returned bitmap with `BIT(cause)`. If interrupt-time code requires
FreeRTOS or ring-buffer functions in IRAM, enable the respective IRAM options
explicitly.

### Tool-facing contracts

- Supply `--port` or `ESPPORT` to every `idf.py efuse*` command.
- Consume `idf.py size --format json2`; its region and part data are
  hierarchical rather than flat.
- Treat core dumps as ELF with SHA-256 only.
- Enable the partial-download option before relying on partial HTTPS OTA.

## High-value new behavior

### Dynamic HTTP request headers

`CONFIG_HTTPD_MAX_REQ_HDR_LEN` is an allocation ceiling. The HTTP server now
allocates request-header memory according to the received header size up to
that limit, so capacity planning should consider peak concurrent requests
rather than assuming a fixed per-request allocation.

### Multiple wakeup causes

```c
uint32_t causes = esp_sleep_get_wakeup_causes();
if (causes & BIT(ESP_SLEEP_WAKEUP_TIMER)) {
    handle_timer_wakeup();
}
```

### Explicit constructor priority

Unprioritized `.init_array` and legacy `.ctors` ordering changed. Express a
real dependency with `__attribute__((constructor(PRIO)))`—lower priorities run
first—or move the dependency into explicit startup registration.

## Migration workflow

1. Pin the failing target and reproduce with a clean configure/build.
2. Classify the failure as build/dependency, driver, connectivity, security,
   or runtime/tooling.
3. Open the matching reference and apply every related structure, callback,
   dependency, and default change together.
4. Remove temporary suppression switches once the code compiles cleanly.
5. Exercise hardware and error paths; many migrations change runtime semantics
   even when the replacement compiles.
6. Re-run host tooling and schema consumers, especially monitor, efuse, size,
   unit-test, core-dump, and OTA workflows.
