# Build, Toolchains, and Components

## Compiler and source compatibility

### GCC 14.2 transition (5.4)

All targets use GCC 14.2.0 rather than 13.2.0. Fix new diagnostics where
possible. `CONFIG_COMPILER_DISABLE_GCC14_WARNINGS` suppresses the set of new
GCC 14 warnings as a temporary porting aid. For the transposed-`calloc`
diagnostic, pass the count first:

```c
calloc(n, sizeof(int));
```

ESP-Common variadic helper macros gained an `ESP_` prefix to avoid collisions.
For example, replace `__VA_NARG__` with `ESP_VA_NARG` and apply the same naming
pattern to related macros.

### GCC 15 and strict defaults (6.0)

All targets use GCC 15.1 rather than 14.2. New diagnostics include unterminated
string arrays, mismatched header guards, self-move, template-body problems,
dangling references, and deleted defaulted functions. Fix them where possible;
`CONFIG_COMPILER_DISABLE_GCC15_WARNINGS` suppresses the new set collectively.

Default compiler warnings are errors because
`CONFIG_COMPILER_DISABLE_DEFAULT_ERRORS` defaults to `n`. Linker orphan
sections are also errors by default: place each section with a linker fragment,
or temporarily set `CONFIG_COMPILER_ORPHAN_SECTIONS` to `warning` or `place`.
Project Kconfig files must use esp-idf-kconfig v3 syntax.

With `NDEBUG`, assertions do not evaluate their expressions because
`CONFIG_COMPILER_ASSERT_NDEBUG_EVALUATE` defaults to `n`. Never put required
side effects inside an assertion expression.

### Constructor order (6.0)

Startup now calls `__libc_init_array()`. Non-priority `.init_array` and legacy
`.ctors` entries run in ascending rather than descending order on all targets.
Use `__attribute__((constructor(PRIO)))`, where lower priorities run first, or
replace implicit order dependencies with explicit registration.

## Headers and component boundaries

### ROM and RTC headers

Target-specific ESP ROM headers are included by header name, not a chip-relative
path (5.4):

```c
#include "efuse.h"
```

Deprecated target-specific `rom/miniz.h` headers are removed. The
`{IDF_TARGET_NAME}/rtc.h` include is deprecated; use `esp_rtc_time.h` (5.5).

### System header replacements (6.0)

| Old include or symbol | Replacement |
| --- | --- |
| `soc_memory_types.h` | `esp_memory_utils.h` |
| `intr_types.h` | `esp_intr_types.h` |
| `esp_log_internal.h` | `esp_log_buffer.h` |
| ROM `STATUS` | `ETS_STATUS` |
| Xtensa `specreg.h` names | `XT_REG_*` from `xt_specreg.h` |

Code including `esp_fault.h` may need a direct `esp_common` dependency.
`esp_vfs_cdcacm.h` requires `esp_usb_cdc_rom_console`.

Public driver headers and `esp_event.h` no longer include FreeRTOS headers
implicitly. Include the interfaces actually used, such as `freertos/queue.h`
and `freertos/semphr.h`.

## Explicit dependencies and managed components

### Split drivers (6.0)

The deprecated aggregate `driver` component no longer publicly depends on the
split `esp_driver_*` components. List every used driver in the component's
manifest or CMake requirements; do not rely on the old transitive edge.

### Components moved out of tree

- `touch_element` is `espressif/touch_element`, `usb` is `espressif/usb`, and
  the NT35510 driver is `espressif/esp_lcd_nt35510` (6.0).
- The pre-encrypted OTA example lives at
  `esp_encrypted_img/examples/pre_encrypted_ota` in the `idf-extra-components`
  repository (5.5).
- The legacy unit-test app is created from the
  `espressif/unit-test-app:unit-test-app` registry example, and Catch2 is a
  managed Catch2 3.x dependency (6.0).
- SystemView is `espressif/esp_sysview`; gcov is `espressif/esp_gcov`, uses
  `esp_gcov.h`, and selects `CONFIG_ESP_GCOV_ENABLE` instead of
  `CONFIG_APPTRACE_GCOV_ENABLE` (6.0).

The built-in `json` component becomes `espressif/cjson`; remove `json` from
`REQUIRES` or `PRIV_REQUIRES`, while keeping the `cJSON.h` API. ESP-MQTT becomes
the `espressif/mqtt` managed component while retaining `mqtt_client.h` (6.0).

## Host tools and output contracts

### Installation requirements (6.0)

Python 3.10 and CMake 3.22.1 are the minimum supported versions. The install
script no longer accepts `--enable-gdbgui`; install gdbgui separately. Every
`idf.py efuse*` invocation must receive a port through `--port` or `ESPPORT`.

### Size reports (6.0)

`idf.py size --legacy` and `ESP_IDF_SIZE_LEGACY` are removed. Request machine
output with:

```console
idf.py size --format json2
```

JSON2 is hierarchical: it reports `total`, `used`, and `free` plus per-region
`parts`. Rewrite consumers that expect the old flat JSON fields.

### Bootloader compilation (6.0)

Bootloader `-O0` support and
`CONFIG_BOOTLOADER_COMPILER_OPTIMIZATION_NONE` are removed; use `-Og`. The
unstable `RTC_CLK_SRC_INT_RC32K` slow-clock option is also removed.
