---
name: esp-idf-knowledge-patch
description: ESP-IDF
version: 6.0
license: MIT
metadata:
  author: Nevaberry
---


# ESP-IDF Compatibility Guide

Use this skill when upgrading, reviewing, or generating ESP-IDF projects whose
code may depend on removed APIs, renamed components, stricter build behavior,
or changed runtime defaults.

## How to Use This Skill

1. Inspect the project's ESP-IDF version, target, component manifests,
   `sdkconfig`, and `sdkconfig.defaults`.
2. Start with the breaking-change checklist below.
3. Open only the reference files relevant to the affected subsystem.
4. Prefer current public APIs and explicit component dependencies.
5. Treat private and semi-public headers as migration bridges, not stable
   application interfaces.
6. Reconfigure, build, and exercise target-specific paths after migration.

## Reference Index

| Reference | Topics |
| --- | --- |
| [build-tooling-and-components.md](references/build-tooling-and-components.md) | Toolchains, warnings, Kconfig, component manifests, registry moves, install tools, size reports, tracing, testing |
| [drivers-and-hardware.md](references/drivers-and-hardware.md) | ROM and peripheral headers, Ethernet, legacy-driver replacements, GPIO, DMA, LCD, SPI, flash, TWAI, touch |
| [networking-and-protocols.md](references/networking-and-protocols.md) | HTTP, netif, DHCP, SNTP, ping, provisioning, MQTT, TLS, VFS |
| [wireless-and-bluetooth.md](references/wireless-and-bluetooth.md) | Bluedroid, Classic Bluetooth, A2DP, ESP-NOW, Wi-Fi, NAN |
| [crypto-and-security.md](references/crypto-and-security.md) | SHA, Mbed TLS 4, PSA Crypto, hardware keys, NVS-backed key storage, BluFi, secure boot |
| [system-runtime-and-logging.md](references/system-runtime-and-logging.md) | Logging, libc, FreeRTOS, sleep, OTA, core dumps, headers, bootloader, memory capabilities |

## Breaking-Change Checklist

### Make dependencies explicit

- Add each used `esp_driver_*` component to the component manifest; the
  aggregate `driver` component no longer supplies them publicly.
- Include FreeRTOS headers directly when public driver headers or
  `esp_event.h` no longer provide the declarations transitively.
- Replace built-in components that moved to the registry, including network
  provisioning, MQTT, JSON, USB, touch elements, LCD, SystemView, gcov, and
  unit-test tooling.
- Remove stale `REQUIRES` and `PRIV_REQUIRES` entries for renamed built-ins.

See [build-tooling-and-components.md](references/build-tooling-and-components.md).

### Fix the build before suppressing diagnostics

- Linker orphan sections are errors; place them with linker fragments.
- Default compiler warnings are errors, and project Kconfig files must use the
  current syntax.
- Fix new compiler diagnostics where possible. Use the version-specific
  aggregate suppression options only as temporary migration aids.
- Do not depend on historical global-constructor ordering; assign explicit
  constructor priorities or redesign registration.

### Replace removed peripheral drivers

Audit ADC, MCPWM, timer group, I2S, PCNT, RMT, DAC, temperature sensor, and
sigma-delta use. Migrate to their current split components and typed APIs.
The old I2S ADC-mode functions have no direct legacy path.

Do not mix legacy and event-driven TWAI drivers. They use incompatible
ownership models and can crash or reboot the device.

See [drivers-and-hardware.md](references/drivers-and-hardware.md).

### Replace removed network APIs

- Never substitute `esp_netif_next_unsafe` into arbitrary code. Traverse in a
  controlled TCP/IP context, or use predicate-based lookup.
- Configure SoftAP DHCP DNS offers at runtime instead of using the removed
  compile-time switch.
- Replace old SNTP and ping headers and session APIs.
- Migrate Wi-Fi provisioning to the managed network-provisioning component.
- Register a custom ESP-TLS stack before opening connections, or use the
  default mbedTLS stack.

See [networking-and-protocols.md](references/networking-and-protocols.md).

### Migrate cryptography to PSA

Call `psa_crypto_init()` before cryptographic use, including certificate
parsing and TLS, unless normal startup has already initialized it. Replace
removed legacy primitives with PSA Crypto, import hardware ECDSA keys with
`psa_import_key`, and initialize NVS before persistent PSA keys are used.

See [crypto-and-security.md](references/crypto-and-security.md).

### Account for libc and runtime changes

- PicolibC shares standard streams globally. Select Newlib when full Newlib
  reentrancy behavior is required.
- Do not expect assertion expressions to run under `NDEBUG` by default.
- Use the multi-cause sleep-wakeup bitmap when more than one source matters.
- Enable explicit IRAM options when ISR-time code depends on FreeRTOS or ring
  buffer routines being resident in IRAM.

See [system-runtime-and-logging.md](references/system-runtime-and-logging.md).

## High-Value API Replacements

### Headers and components

| Old | Current |
| --- | --- |
| `{target}/rtc.h` | `esp_rtc_time.h` |
| `sntp.h` | `esp_sntp.h` |
| `esp_ping.h` / `ping.h` | `ping/ping_sock.h` |
| `esp_spiram.h` | `esp_psram.h` |
| `esp_spi_flash.h` | `spi_flash_mmap.h` |
| `driver/periph_ctrl.h` | `esp_private/periph_ctrl.h` |
| `driver/rtc_cntl.h` | `esp_private/rtc_ctrl.h` |
| built-in `wifi_provisioning` | `espressif/network_provisioning` |
| built-in `json` | `espressif/cjson` |
| built-in ESP-MQTT | `espressif/mqtt` |

### Drivers and system APIs

| Old | Current |
| --- | --- |
| `twai_read_alerts` | `on_state_change` / `on_error` callbacks |
| `gdma_new_channel` | `gdma_new_ahb_channel` or `gdma_new_axi_channel` |
| `ledc_timer_set` | `ledc_timer_config` or `ledc_set_freq` |
| `esp_vfs_fat_sdmmc_unmount` | `esp_vfs_fat_sdcard_unmount` |
| `esp_sleep_get_wakeup_cause` | `esp_sleep_get_wakeup_causes` |
| `esp_app_get_description` via OTA headers | `esp_app_format` and `esp_app_desc.h` |
| `pxTaskGetStackStart` | `xTaskGetStackStart` |

### Logging

Replace the deprecated buffer functions with macros:

```c
ESP_LOG_BUFFER_HEX(tag, buffer, length);
ESP_LOG_BUFFER_CHAR(tag, buffer, length);
```

When using Log V2 internals, replace `esp_log_write` and `esp_log_writev` with
`esp_log` and `esp_log_va`. V2-only formatting and execution-context features
are not backward-compatible with Log V1.

## Frequently Used New Behavior

### Event-driven TWAI

Use `esp_driver_twai` with `esp_twai.h` and `esp_twai_onchip.h`. Register
callbacks, receive only from `on_rx_done` via `twai_node_receive_from_isr`, and
use runtime bitrate and filter changes where needed. The interface supports
multiple controllers and TWAI FD on supported hardware.

### Dynamic HTTP request headers

`CONFIG_HTTPD_MAX_REQ_HDR_LEN` is an allocation ceiling. Request-header memory
is allocated to the received size up to that ceiling, so it is no longer a
fixed per-request allocation.

### Multiple wakeup causes

Test the returned bitmap rather than comparing one enum value:

```c
uint32_t causes = esp_sleep_get_wakeup_causes();
if (causes & BIT(ESP_SLEEP_WAKEUP_TIMER)) {
    handle_timer_wakeup();
}
```

### Machine-readable size reports

Use the hierarchical JSON2 schema:

```console
idf.py size --format json2
```

Consumers must read `total`, `used`, `free`, and per-region `parts` rather
than the removed flat JSON fields.

## Migration Method

### Inventory

Search source, manifests, and configuration for removed headers, old component
names, legacy peripheral includes, deprecated symbols, and Kconfig escape
hatches. Pay special attention to transitive includes and dependencies.

### Convert one subsystem at a time

Change the manifest and includes first, then types and configuration, then
runtime call sequences and callbacks. Avoid combining legacy and replacement
drivers in the same subsystem.

### Validate semantics

Compile success is insufficient. Verify changed error codes, callback context,
constructor order, DNS offers, wakeup-cause handling, crypto initialization,
flash timing, and task/ISR memory-placement assumptions.

### Keep escape hatches temporary

Options that suppress compiler warnings, legacy-driver conflicts, or
deprecation warnings should unblock staged migration only. Record why each is
enabled and remove it after the corresponding conversion.

## Target-Specific Cautions

- Confirm target availability before using RTC-memory attributes or
  `MALLOC_CAP_EXEC`; these may be absent under current hardware or protection
  settings.
- Treat `esp_private/*` and `esp_flash_chips/*` headers as unstable contracts.
- Validate clock GPIOs, GPIO sharing, DMA channel type, and LCD color format on
  the actual target.
- Re-test secure storage, BluFi clients, provisioning clients, and TLS peers
  together with firmware when protocol or crypto defaults change.
