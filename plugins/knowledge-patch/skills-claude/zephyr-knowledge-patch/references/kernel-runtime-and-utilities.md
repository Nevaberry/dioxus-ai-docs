# Kernel, Runtime, and Utilities

Entries are grouped by developer task and alphabetized by topic. The
parenthetical identifier records the exact source batch for each item.

## Additional symbol migrations (4.4.0)

Replace `I2S_OPT_BIT_CLK_MASTER`/`I2S_OPT_FRAME_CLK_MASTER` with `I2S_OPT_BIT_CLK_CONTROLLER`/`I2S_OPT_FRAME_CLK_CONTROLLER`, and `I2S_OPT_BIT_CLK_SLAVE`/`I2S_OPT_FRAME_CLK_SLAVE` with `I2S_OPT_BIT_CLK_TARGET`/`I2S_OPT_FRAME_CLK_TARGET`; also replace `CONFIG_XOPEN_STREAMS` with `CONFIG_XSI_STREAMS` and `CONFIG_CTR_DRBG_CSPRNG_GENERATOR` with `CONFIG_PSA_CSPRNG_GENERATOR`. Correct `BT_HCI_LE_SUPERVISON_TIMEOUT_MIN`/`BT_HCI_LE_SUPERVISON_TIMEOUT_MAX` to `BT_HCI_LE_SUPERVISION_TIMEOUT_MIN`/`BT_HCI_LE_SUPERVISION_TIMEOUT_MAX`.

## Cache coherence API (migration-4.4)

Rename `CONFIG_ARCH_HAS_COHERENCE` to `CONFIG_CACHE_CAN_SAY_MEM_COHERENCE` and replace `arch_mem_coherent()` with `sys_cache_is_mem_coherent()`. Rename `CONFIG_CACHE_DOUBLEMAP` to `CONFIG_CACHE_HAS_MIRRORED_MEMORY_REGIONS`.

## Compiler-assisted instrumentation (4.3.0)

`CONFIG_INSTRUMENTATION` adds runtime call-graph tracing and statistical profiling through compiler-managed function instrumentation. It provides call-graph and statistical mode settings, trigger/stop and exclusion controls, and `instr_*` APIs for control and UART dumps.

## Core API removals (4.0.0)

Replace `K_THREAD_STACK_MEMBER` with `K_KERNEL_STACK_MEMBER`, `ceiling_fraction` with `DIV_ROUND_UP`, the architecture CMSIS headers with `cmsis_core.h`, and `<zephyr/random/rand32.h>` with `<zephyr/random/random.h>`. `CBPRINTF_PACKAGE_COPY_*`, generated `_ENUM_TOKEN`/`_ENUM_UPPER_TOKEN`, deprecated `net_pkt` functions, and the `EARLY`, `APPLICATION`, and `SMP` device-init levels are gone; `net_buf_put()`/`net_buf_get()` and the kscan subsystem are deprecated.

## CPU load and frequency scaling (4.3.0)

The new `cpu_load` subsystem derives CPU-usage metrics from scheduler statistics. Experimental policy-driven dynamic clock scaling is selected with `CONFIG_CPU_FREQ` and can use those metrics to balance performance and power.

## CTF event identifiers (migration-4.4)

CTF metadata event IDs widen from 8 to 16 bits, permitting 65,535 events but making new traces incompatible with consumers expecting the old 8-bit format.

## Device initialization errors (migration-4.3)

`device_init()` now returns a negative `-errno` on initialization failure. Remove workarounds that interpreted the earlier erroneous positive value.

## Dictionary log parser (migration-4.3)

`scripts/logging/dictionary/log_parser_uart.py` is deprecated. Migrate invocations, including their command-line arguments, to `scripts/logging/dictionary/live_log_parser.py`.

## File-descriptor table sizing (migration-4.3)

`ZVFS_OPEN_SIZE` now determines file-descriptor table size and availability, with subsystem requirements contributed by `CONFIG_ZVFS_OPEN_ADD_SIZE_*`. `CONFIG_ZVFS_OPEN_MAX` remains but is raised to larger contributed minima unless `CONFIG_ZVFS_OPEN_IGNORE_MIN` is enabled.

## Hardware shadow stacks and Intel CET (4.3.0)

Zephyr adds architecture and kernel hardware-shadow-stack support through `CONFIG_ARCH_HAS_HW_SHADOW_STACK`, `CONFIG_HW_SHADOW_STACK`, sizing/declaration macros, and `k_thread_hw_shadow_stack_attach()`. x86 Intel CET and indirect-branch tracking are selected through the `CONFIG_X86_CET*` options.

## i.MX GPT run mode (migration-4.4)

`nxp,imx-gpt` now defaults to `run-mode = "restart"`, which resets the counter at Compare Channel 1 alarms. Set `run-mode = "free-run";` to preserve continuous pre-4.4 counting.

## In-memory core dumps (4.2.0)

`CONFIG_DEBUG_COREDUMP_BACKEND_IN_MEMORY` and `CONFIG_DEBUG_COREDUMP_BACKEND_IN_MEMORY_SIZE` retain a core dump in RAM. Minimal Cortex-M memory dumps now include the thread stack top by default through `CONFIG_DEBUG_COREDUMP_THREAD_STACK_TOP`.

## Kernel shell commands (migration-4.0)

The `kernel threads` and `kernel stacks` commands are now `kernel thread list` and `kernel thread stacks`.

## Loadable extensions and demand paging (4.0.0)

Devicetree devices are exported to LLEXT, and ARM64 gains initial LLEXT and demand-paging support. Demand paging also gains LRU eviction, SMP compatibility, and on-demand mappings through `CONFIG_DEMAND_MAPPING`.

## Maximum CPU count (migration-4.0)

`CONFIG_MP_NUM_CPUS` was removed. Use `CONFIG_MP_MAX_NUM_CPUS`.

## MCUmgr callback macro removal (migration-4.1)

The deprecated `MGMT_CB_ERROR_RET` macro is removed.

## Nordic PDK removals (4.3.0)

The emulator-only `nrf54l09pdk` target is removed pending a proper board definition, and `nrf54l20pdk` is removed in favor of `nrf54lm20dk`.

## Operational-amplifier subsystem (4.3.0)

`CONFIG_OPAMP` introduces a standard op-amp device API with initial Devicetree configuration and vendor-specific runtime configuration; initial compatibles are `nxp,opamp` and `nxp,opamp-fast`.

## Other removed core interfaces (4.1.0)

Replace `CONFIG_PM_DEVICE_RUNTIME_EXCLUSIVE` with `CONFIG_PM_DEVICE_SYSTEM_MANAGED` and `z_arch_esf_t` with `struct arch_esf`. `z_pm_save_idle_exit()`, `CONFIG_WIFI_NM_WPA_SUPPLICANT_CRYPTO`, `CONFIG_NET_PKT_BUF_DATA_POOL_SIZE`, and `CONFIG_NET_TCP_ACK_TIMEOUT` are removed.

## POSIX and kernel shell behavior (4.0.0)

The POSIX surface adds device I/O, signals, synchronized I/O, priority protection, `O_TRUNC`, `rmdir()`, `remove()`, and the reentrant time functions. The kernel shell can change thread CPU affinity at runtime, and bare `kernel reboot` now performs a cold reboot.

## POSIX headers and limits (migration-4.3)

Applications must include `<time.h>`, `<signal.h>`, and `<limits.h>` rather than the former `<zephyr/posix/...>` headers; non-POSIX C library ports may use Zephyr's `posix_time.h`, `posix_signal.h`, and `posix_limits.h`. Runtime-dependent limits may need to be obtained with `sysconf()`.

## Pressure-based CPU frequency policy (4.4.0)

The CPU frequency subsystem can select `CONFIG_CPU_FREQ_POLICY_PRESSURE` to scale frequency from scheduler load pressure.

## Rate-limited logging (4.3.0)

The `LOG_*_RATELIMIT` and `LOG_HEXDUMP_*_RATELIMIT` families rate-limit independently at each call site, using either `CONFIG_LOG_RATELIMIT_INTERVAL_MS` or an explicit rate. `CONFIG_LOG_RATELIMIT` controls the feature and `CONFIG_LOG_RATELIMIT_FALLBACK` selects log-all or drop-all behavior when it is disabled.

## Removed legacy options and moved SBC header (migration-4.4)

`CONFIG_JWT_SIGN_RSA_LEGACY` and `CONFIG_HAWKBIT_DDI_NO_SECURITY` are removed. Libsbc moves under Bluetooth, so include its header from `zephyr/bluetooth/sbc.h`.

## Reworked pipe API (migration-4.1)

The `CONFIG_PIPES` API is deprecated; the replacement pipe API is enabled automatically with `CONFIG_MULTITHREADING`. Replace `k_pipe_put()`/`k_pipe_get()` with `k_pipe_write()`/`k_pipe_read()`: `min_xfer` is gone, the byte count is returned directly, and threshold-based partial transfers are no longer supported.

Replace both flush calls with nonblocking `k_pipe_reset()`. Dynamic allocation through `k_pipe_alloc_init()`/`k_pipe_cleanup()` and availability queries are removed; `k_pipe_close()` instead closes a pipe and wakes waiters with an error, while buffered data remains readable until empty and `k_pipe_init()` reopens it.

## RTIO callback chains (migration-4.3)

RTIO callback operations gain an argument containing the first error result in the chain. Callbacks now run even when an earlier submission failed, so handlers must inspect that result instead of assuming prior success.

## Runtime power-management defaults (4.3.0)

`CONFIG_PM_DEVICE_RUNTIME_DEFAULT_ENABLE` can enable device runtime power management by default, and drivers gain `pm_device_driver_deinit()` for deinitialization.

## Scope-based cleanup (4.4.0)

`SCOPE_VAR_DEFINE`, `SCOPE_GUARD_DEFINE`, and `SCOPE_DEFER_DEFINE`, with the `scope_var`, `scope_guard`, and `scope_defer` helpers, provide RAII/defer-style cleanup when C scope exits.

## Stable and heapless Zbus observers (4.2.0)

Zbus reaches stable API version 1.0.0. Runtime observer nodes can use dynamic, static, or no allocation through `CONFIG_ZBUS_RUNTIME_OBSERVERS_NODE_ALLOC_*`; the no-allocation mode registers caller-provided nodes with `zbus_chan_add_obs_with_node()`.

## Stack-canary strength (migration-4.1)

`CONFIG_STACK_CANARIES` no longer adds `-fstack-protector-all`. Enable `CONFIG_STACK_CANARIES_ALL` when all-function stack protection is required.

## State Machine Framework event propagation (migration-4.2)

`smf_set_handled()` is removed, and hierarchical state run actions now return `smf_state_result`: return `SMF_EVENT_HANDLED` to stop propagation or `SMF_EVENT_PROPAGATE` to invoke parent run actions. Flat state machines ignore the value, for which `SMF_EVENT_HANDLED` is the appropriate return.

## Streaming COBS and disjoint sets (4.4.0)

Incremental COBS processing uses `cobs_encoder_init()`, `cobs_encoder_write()`, and `cobs_encoder_close()`, with the matching `cobs_decoder_init()`/`cobs_decoder_write()`/`cobs_decoder_close()` lifecycle. The new `sys_set_node`, `sys_set_makeset()`, `sys_set_find()`, and `sys_set_union()` APIs provide disjoint-set operations.

## Suspend-to-RAM ownership (migration-4.3)

Applications must stop selecting `CONFIG_PM_S2RAM` and `PM_S2RAM_CUSTOM_MARKING`; SoCs and enabled `suspend-to-ram` devicetree power states now control them. Updated RW61x `exit-latency-us` values may also require increasing `min-residency-us` and can change power-state selection.

## System-timer low-power companion (migration-4.4)

Out-of-tree Cortex-M timer code should replace `z_cms_lptim_hook_on_lpm_entry/exit` with `z_sys_clock_lpm_enter/exit`, the `CONFIG_CORTEX_M_SYSTICK_LPM_TIMER_*` family with `CONFIG_SYSTEM_TIMER_LPM_COMPANION_*`, and `/chosen/zephyr,cortex-m-idle-timer` with `/chosen/zephyr,system-timer-companion`.

## Tiered heap hardening (4.4.0)

`CONFIG_SYS_HEAP_HARDENING` adds Basic, Moderate, Full, and Extreme checking for `sys_heap_alloc()` and `sys_heap_free()`, progressing through double-free detection, neighbor validation, and optional per-chunk canaries.

## USB Device "Next" default (4.3.0)

The UDC-based USB device stack is now the default, with multiple simultaneous controllers and runtime configuration. The legacy stack is deprecated and scheduled for removal in Zephyr 4.5.

## Utility APIs (migration-4.3)

Include `<zephyr/sys/util_utf8.h>` for `utf8_trunc()` and `utf8_lcpy()` instead of relying on `util.h`. Rename `Z_MIN`, `Z_MAX`, and `Z_CLAMP` to `min`, `max`, and `clamp`.

## Watchdog startup (migration-4.4)

`CONFIG_WDT_DISABLE_AT_BOOT=n` no longer means a watchdog is automatically configured and running. Applications must configure it explicitly; the STM32, Raspberry Pi Pico, and TI `*_INITIAL_TIMEOUT` options used for the old behavior are removed.

## Zbus asynchronous listeners and proxy agents (4.4.0)

`CONFIG_ZBUS_ASYNC_LISTENER` and `ZBUS_ASYNC_LISTENER_DEFINE()` run observers in a workqueue rather than the publisher thread, with queue selection through `zbus_async_listener_set_work_queue()`. Experimental `CONFIG_ZBUS_PROXY_AGENT` and `CONFIG_ZBUS_PROXY_AGENT_IPC`, with `ZBUS_PROXY_AGENT_DEFINE`, `ZBUS_PROXY_ADD_CHAN`, and shadow-channel macros, forward channels across CPU or domain boundaries over IPC.

## zcbor 0.9 generated code (migration-4.0)

The generic `zcbor_simple_*()` APIs are removed; use `zcbor_bool_*()`, `zcbor_nil_*()`, or `zcbor_undefined_*()`. Regeneration may also capitalize additional C-keyword field names and rename bstr elements that use a `.size` specifier.
