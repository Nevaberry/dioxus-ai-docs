# System, Runtime, and Logging

## Logging

### Buffer logging and color

In 5.4, `esp_log_buffer_hex` and `esp_log_buffer_char` are deprecated. Use
`ESP_LOG_BUFFER_HEX` and `ESP_LOG_BUFFER_CHAR`.

`CONFIG_LOG_COLORS` now defaults to false because IDF Monitor colors logs on
the host. Enable it for other monitors, or disable automatic host coloring:

```console
idf.py monitor --disable-auto-color
```

### Optional Log V2

Log V2 is selected through `CONFIG_LOG_VERSION`; Log V1 remains supported.
For V2 handler internals, replace `esp_log_write` and `esp_log_writev` with
`esp_log` and `esp_log_va`. V2-only dynamic formatting and execution-context
detection are not backward-compatible with V1.

## PicolibC Default

PicolibC is the default libc in 6.0. `stdin`, `stdout`, and `stderr` are shared
globally instead of being redefinable per task.

`CONFIG_LIBC_PICOLIBC_NEWLIB_COMPATIBILITY` offers only limited compatibility
and can corrupt stacks when a library accesses Newlib `struct reent` internals.
Select `CONFIG_LIBC_NEWLIB` when full Newlib behavior is required.

Under PicolibC, replace `<sys/signal.h>` with `<signal.h>` and include
`<dirent.h>` rather than `<sys/dirent.h>` for directory function declarations.

## Multiple Sleep Wakeup Causes

`esp_sleep_get_wakeup_causes` returns a bitmap containing every triggered
source, superseding the single-value `esp_sleep_get_wakeup_cause`. Test each
`esp_sleep_wakeup_cause_t` value through `BIT(...)`:

```c
uint32_t causes = esp_sleep_get_wakeup_causes();
if (causes & BIT(ESP_SLEEP_WAKEUP_TIMER)) {
    handle_timer_wakeup();
}
```

## System Headers and Bootloader

Use these replacements:

| Old | Current |
| --- | --- |
| `soc_memory_types.h` | `esp_memory_utils.h` |
| `intr_types.h` | `esp_intr_types.h` |
| `esp_log_internal.h` | `esp_log_buffer.h` |
| ROM `STATUS` | `ETS_STATUS` |
| Xtensa `specreg.h` names | `XT_REG_*` from `xt_specreg.h` |

Code that includes `esp_fault.h` may need an explicit `esp_common` dependency.
`esp_vfs_cdcacm.h` requires `esp_usb_cdc_rom_console`.

Bootloader `-O0` support and `CONFIG_BOOTLOADER_COMPILER_OPTIMIZATION_NONE` are
removed; use `-Og`. The unstable `RTC_CLK_SRC_INT_RC32K` slow-clock option is
also removed.

## FreeRTOS APIs and Placement

Affinity and per-CPU task helpers now use `xTaskGetCoreID`,
`xTaskGetIdleTaskHandleForCore`, and `xTaskGetCurrentTaskHandleForCore`.
Replace `pxTaskGetStackStart` with `xTaskGetStackStart`.

Replace removed compatibility functions with the direct APIs or their macros:

- `xQueueReceive`
- `xQueuePeek`
- `xSemaphoreTake`
- `xTaskDelayUntil`

Include snapshot APIs from `freertos/freertos_debug.h`. Suspend the scheduler
around snapshots of live task state.

Most FreeRTOS and ring-buffer functions now default to flash. Enable
`CONFIG_FREERTOS_IN_IRAM` and `CONFIG_RINGBUF_IN_IRAM` when application timing
or ISR use requires their former IRAM placement.

## Core Dumps and OTA

Core dumps support only ELF with SHA-256. For an erased core-dump partition,
`esp_core_dump_partition_and_size_get` returns `ESP_ERR_NOT_FOUND`.

HTTPS OTA partial downloads require
`CONFIG_ESP_HTTPS_OTA_ENABLE_PARTIAL_DOWNLOAD`.

Application-description helpers moved to `esp_app_format` as
`esp_app_get_description` and `esp_app_get_elf_sha256`. Include
`esp_app_desc.h` rather than `esp_ota_ops.h` for these calls.

## Runtime Defaults and Capabilities

With `NDEBUG`, assertions no longer evaluate their expressions because
`CONFIG_COMPILER_ASSERT_NDEBUG_EVALUATE` defaults to `n`. Never depend on side
effects inside `assert`.

LP-Core exceptions during deep sleep wake the main CPU unless
`CONFIG_ULP_TRAP_WAKEUP` is disabled.

`MALLOC_CAP_EXEC` is undefined when system memory protection is enabled.
Replace `EXT_RAM_ATTR` with `EXT_RAM_BSS_ATTR`. RTC-memory attributes do not
exist on chips without RTC memory, so guard target-specific declarations.
