# Build, Tooling, and Components

## Compiler and Build Policy

### Toolchain warnings

ESP-IDF 5.4 uses GCC 14.2.0 for all targets rather than GCC 13.2.0. Suppress
the new family of warnings together with
`CONFIG_COMPILER_DISABLE_GCC14_WARNINGS` only while migrating. For example,
fix a transposed `calloc` diagnostic by passing count before element size:

```c
calloc(n, sizeof(int));
```

ESP-IDF 6.0 moves all targets to GCC 15.1. Its aggregate temporary suppression
is `CONFIG_COMPILER_DISABLE_GCC15_WARNINGS`. New diagnostics include
unterminated string arrays, mismatched header guards, self-move, template-body
issues, dangling references, and deleted defaulted functions. Fix them where
possible because default warnings are now errors.

### Strict defaults

In 6.0, linker orphan sections are errors by default. Place every intended
section explicitly with a linker fragment. As a temporary escape hatch, set
`CONFIG_COMPILER_ORPHAN_SECTIONS` to `warning` or `place`.

`CONFIG_COMPILER_DISABLE_DEFAULT_ERRORS` now defaults to `n`, so default
compiler warnings are errors. Project Kconfig files must use esp-idf-kconfig v3
syntax.

### Global constructors

Startup now calls `__libc_init_array()`. Non-priority `.init_array` and legacy
`.ctors` entries run in ascending rather than descending order on every target.
If ordering matters, use `__attribute__((constructor(PRIO)))`; lower
priorities run first. Prefer removing implicit order dependencies entirely.

## Component Dependency Rules

### Driver and FreeRTOS dependencies

The deprecated aggregate `driver` component no longer publicly depends on the
split `esp_driver_*` components. Name every used driver in the component
manifest instead of relying on transitive dependencies.

Public driver headers and `esp_event.h` no longer implicitly include FreeRTOS
headers. Include the declarations you use directly, such as:

```c
#include "freertos/queue.h"
#include "freertos/semphr.h"
```

### Peripheral components moved to the registry

These components are no longer built in:

- `touch_element` becomes the `espressif/touch_element` dependency.
- `usb` becomes the `espressif/usb` dependency.
- The NT35510 driver becomes `espressif/esp_lcd_nt35510`.

ULP touch channel IDs now use `int` rather than `touch_pad_t`. `i2s_port_t` is
also replaced by `int`, while the `I2S_NUM_*` names remain macros.

### JSON and MQTT

The built-in `json` component becomes a managed `espressif/cjson` dependency;
the `cJSON.h` API is unchanged. Remove `json` from `REQUIRES` or
`PRIV_REQUIRES`, then add the managed dependency through Component Manager.

ESP-MQTT likewise becomes the `espressif/mqtt` managed component while keeping
the `mqtt_client.h` header.

### Unit tests

The legacy in-tree unit-test application has moved to the
`espressif/unit-test-app:unit-test-app` registry example. The bundled Catch2
copy is gone; use the managed Catch2 3.x component.

## Installation and CLI Changes

Python 3.10 and CMake 3.22.1 are the minimum supported tool versions in 6.0.
The install scripts no longer accept `--enable-gdbgui`; install gdbgui
separately.

Every `idf.py efuse*` command now requires a serial port. Supply it explicitly:

```console
idf.py --port /dev/ttyUSB0 efuse-summary
```

Alternatively set `ESPPORT`.

## Size Reporting

`idf.py size --legacy` and the `ESP_IDF_SIZE_LEGACY` environment variable are
removed. For machine-readable output use:

```console
idf.py size --format json2
```

Do not request `--format json`. The JSON2 schema is hierarchical, with
`total`, `used`, `free`, and per-region `parts`; update consumers that expect
the former flat fields.

## App Trace, SystemView, and Gcov

Applications must explicitly select the `ESP-IDF apptrace` transport and
depend on `esp_trace` instead of `app_trace`. Apptrace calls no longer take a
destination argument; configure the destination globally or with runtime
callbacks. A minimal configuration is:

```text
CONFIG_ESP_TRACE_ENABLE=y
CONFIG_ESP_TRACE_LIB_NONE=y
CONFIG_ESP_TRACE_TRANSPORT_APPTRACE=y
```

For UART, set `CONFIG_APPTRACE_DEST_UART=y` and
`CONFIG_APPTRACE_DEST_UART_NUM`. Replace `ESP_APPTRACE_DEST_TRAX` with
`ESP_APPTRACE_DEST_JTAG`.

SystemView is now the `espressif/esp_sysview` managed component and shares the
app-trace JTAG/UART transport. Gcov is now `espressif/esp_gcov`, includes
`esp_gcov.h`, and uses `CONFIG_ESP_GCOV_ENABLE` instead of
`CONFIG_APPTRACE_GCOV_ENABLE`.
