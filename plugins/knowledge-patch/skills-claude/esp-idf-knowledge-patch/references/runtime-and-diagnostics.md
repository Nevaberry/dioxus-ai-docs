# Runtime and Diagnostics

## Logging

### Buffer logging and colors (5.4)

`esp_log_buffer_hex` and `esp_log_buffer_char` are deprecated. Use
`ESP_LOG_BUFFER_HEX` and `ESP_LOG_BUFFER_CHAR`. `CONFIG_LOG_COLORS` defaults to
false because IDF Monitor colors logs on the host. Enable it for other
monitors, or disable host coloring with:

```console
idf.py monitor --disable-auto-color
```

### Optional Log V2 (5.5)

Select the log generation with `CONFIG_LOG_VERSION`; Log V1 remains supported.
For V2 handler-internal formatting, replace `esp_log_write` and
`esp_log_writev` with `esp_log` and `esp_log_va`. V2 dynamic formatting and
execution-context detection are not backward-compatible with V1.

## VFS and libc (6.0)

Apply these VFS replacements:

| Old interface | Replacement |
| --- | --- |
| `esp_vfs_fat_sdmmc_unmount` | `esp_vfs_fat_sdcard_unmount` |
| `esp_vfs_dev_uart_*` | `uart_vfs_dev_*` |
| `esp_vfs_dev_usb_serial_jtag_*` | `usb_serial_jtag_vfs_*` |
| deprecated `esp_vfs_t` registration | `esp_vfs_fs_ops_t` APIs |

`esp_vfs_register_fd_range` is private in `esp_private/socket.h`. Explicit
dependencies on renamed `esp_vfs_console` can be removed because `esp_stdio`
is shared.

PicolibC is the default libc. stdin, stdout, and stderr are globally shared and
cannot be redefined per task. `CONFIG_LIBC_PICOLIBC_NEWLIB_COMPATIBILITY` is
limited and can corrupt stacks in libraries that access Newlib `struct reent`
internals; choose `CONFIG_LIBC_NEWLIB` for full Newlib behavior. Under PicolibC,
replace `<sys/signal.h>` with `<signal.h>` and include `<dirent.h>` rather than
`<sys/dirent.h>`.

## Sleep, memory, and capabilities (6.0)

`esp_sleep_get_wakeup_causes` returns a bitmap containing every triggered wake
source and supersedes the single-value `esp_sleep_get_wakeup_cause`. Test each
`esp_sleep_wakeup_cause_t` with `BIT(...)`:

```c
uint32_t causes = esp_sleep_get_wakeup_causes();
if (causes & BIT(ESP_SLEEP_WAKEUP_TIMER)) {
    handle_timer_wakeup();
}
```

LP-Core exceptions during deep sleep wake the main CPU unless
`CONFIG_ULP_TRAP_WAKEUP` is disabled. `MALLOC_CAP_EXEC` is undefined when
system memory protection is enabled. Replace `EXT_RAM_ATTR` with
`EXT_RAM_BSS_ATTR`; RTC memory attributes do not exist on chips without RTC
memory.

## App trace, SystemView, and gcov (6.0)

Applications must select the `ESP-IDF apptrace` transport, depend on
`esp_trace` rather than `app_trace`, and remove the destination argument from
apptrace calls. The destination is global or supplied by runtime callbacks.
For UART, use `CONFIG_APPTRACE_DEST_UART=y` and
`CONFIG_APPTRACE_DEST_UART_NUM`. Replace `ESP_APPTRACE_DEST_TRAX` with
`ESP_APPTRACE_DEST_JTAG`.

```text
CONFIG_ESP_TRACE_ENABLE=y
CONFIG_ESP_TRACE_LIB_NONE=y
CONFIG_ESP_TRACE_TRANSPORT_APPTRACE=y
```

SystemView is the `espressif/esp_sysview` managed component and shares the
app-trace JTAG/UART transport. Gcov is `espressif/esp_gcov`, includes
`esp_gcov.h`, and uses `CONFIG_ESP_GCOV_ENABLE` rather than
`CONFIG_APPTRACE_GCOV_ENABLE`.

## FreeRTOS APIs and placement (6.0)

Affinity and per-CPU task helpers use `xTaskGetCoreID`,
`xTaskGetIdleTaskHandleForCore`, and `xTaskGetCurrentTaskHandleForCore`.
Replace `pxTaskGetStackStart` with `xTaskGetStackStart`.

Replace removed compatibility functions with `xQueueReceive`, `xQueuePeek`,
`xSemaphoreTake`, `xTaskDelayUntil`, or their macros as appropriate. Include
snapshot APIs from `freertos/freertos_debug.h` and suspend the scheduler around
live snapshots.

Most FreeRTOS and ring-buffer functions are in flash by default. Enable
`CONFIG_FREERTOS_IN_IRAM` and `CONFIG_RINGBUF_IN_IRAM` when an interrupt-time
path requires their former IRAM placement.

## Core dumps and OTA (6.0)

Core dumps support only ELF with SHA-256. On an erased partition,
`esp_core_dump_partition_and_size_get` returns `ESP_ERR_NOT_FOUND`.

HTTPS OTA partial downloads require
`CONFIG_ESP_HTTPS_OTA_ENABLE_PARTIAL_DOWNLOAD`. App-description helpers move to
`esp_app_format` as `esp_app_get_description` and
`esp_app_get_elf_sha256`; include `esp_app_desc.h` rather than `esp_ota_ops.h`
for these calls.
