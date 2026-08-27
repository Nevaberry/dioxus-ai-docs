# Kernel, Architecture, and Core APIs

Use these notes for kernel APIs, POSIX integration, scheduling, userspace, architecture ports, memory, and low-level utilities.

## Kernel, scheduling, and power

### Kernel shell commands — `migration-4.0`

The `kernel threads` and `kernel stacks` commands are now `kernel thread list` and `kernel thread stacks`.

### Reworked pipe API — `migration-4.1`

The `CONFIG_PIPES` API is deprecated; the replacement pipe API is enabled automatically with `CONFIG_MULTITHREADING`. Replace `k_pipe_put()`/`k_pipe_get()` with `k_pipe_write()`/`k_pipe_read()`: `min_xfer` is gone, the byte count is returned directly, and threshold-based partial transfers are no longer supported.

Replace both flush calls with nonblocking `k_pipe_reset()`. Dynamic allocation through `k_pipe_alloc_init()`/`k_pipe_cleanup()` and availability queries are removed; `k_pipe_close()` instead closes a pipe and wakes waiters with an error, while buffered data remains readable until empty and `k_pipe_init()` reopens it.

### Scheduler and I3C configuration — `4.2.0`

Replace deprecated `CONFIG_SCHED_DUMB` and `CONFIG_WAITQ_DUMB` with `CONFIG_SCHED_SIMPLE` and `CONFIG_WAITQ_SIMPLE`. I3C group addressing and `CONFIG_I3C_USE_GROUP_ADDR` are removed; choose `CONFIG_I3C_CONTROLLER_ROLE_ONLY`, `CONFIG_I3C_TARGET_ROLE_ONLY`, or `CONFIG_I3C_DUAL_ROLE` through `CONFIG_I3C_MODE`.

### Suspend-to-RAM ownership — `migration-4.3`

Applications must stop selecting `CONFIG_PM_S2RAM` and `PM_S2RAM_CUSTOM_MARKING`; SoCs and enabled `suspend-to-ram` devicetree power states now control them. Updated RW61x `exit-latency-us` values may also require increasing `min-residency-us` and can change power-state selection.

### CPU load and frequency scaling — `4.3.0`

The new `cpu_load` subsystem derives CPU-usage metrics from scheduler statistics. Experimental policy-driven dynamic clock scaling is selected with `CONFIG_CPU_FREQ` and can use those metrics to balance performance and power.

### Runtime power-management defaults — `4.3.0`

`CONFIG_PM_DEVICE_RUNTIME_DEFAULT_ENABLE` can enable device runtime power management by default, and drivers gain `pm_device_driver_deinit()` for deinitialization.

### System-timer low-power companion — `migration-4.4`

Out-of-tree Cortex-M timer code should replace `z_cms_lptim_hook_on_lpm_entry/exit` with `z_sys_clock_lpm_enter/exit`, the `CONFIG_CORTEX_M_SYSTICK_LPM_TIMER_*` family with `CONFIG_SYSTEM_TIMER_LPM_COMPANION_*`, and `/chosen/zephyr,cortex-m-idle-timer` with `/chosen/zephyr,system-timer-companion`.

### Watchdog startup — `migration-4.4`

`CONFIG_WDT_DISABLE_AT_BOOT=n` no longer means a watchdog is automatically configured and running. Applications must configure it explicitly; the STM32, Raspberry Pi Pico, and TI `*_INITIAL_TIMEOUT` options used for the old behavior are removed.

## Architecture and memory

### RISC-V fatal exception frames — `4.0.0`

With `CONFIG_EXTRA_EXCEPTION_INFO`, `arch_esf` now has a `csf` pointer to the callee-saved registers for use by `k_sys_fatal_error_handler()`. SoCs selecting `RISCV_SOC_HAS_ISR_STACKING` must include that member in `SOC_ISR_STACKING_ESF_DECLARE`.

### Loadable extensions and demand paging — `4.0.0`

Devicetree devices are exported to LLEXT, and ARM64 gains initial LLEXT and demand-paging support. Demand paging also gains LRU eviction, SMP compatibility, and on-demand mappings through `CONFIG_DEMAND_MAPPING`.

### Architecture current-pointer hooks — `4.1.0`

Architecture ports can provide a custom current-thread implementation with `CONFIG_ARCH_HAS_CUSTOM_CURRENT_IMPL`. RISC-V can keep the current-thread pointer in the global pointer register with `CONFIG_RISCV_CURRENT_VIA_GP`.

### Architecture Kconfig changes — `migration-4.2`

`CONFIG_SRAM_VECTOR_TABLE` now additionally depends on `CONFIG_XIP`, `CONFIG_ARCH_HAS_VECTOR_TABLE_RELOCATION`, and `CONFIG_ROMSTART_RELOCATION_ROM`. Rename the x86-only `CONFIG_DEBUG_INFO` option to `CONFIG_X86_DEBUG_INFO`.

### Architecture support and execution protection — `4.2.0`

Zephyr gains initial Renesas RX support, including `rsk_rx130` and a QEMU-based target, while NIOS2 support is removed. With `CONFIG_ARM_MPU_PXN` and `CONFIG_USERSPACE`, `__ramfunc` and `__ram_text_reloc` are privileged-execute-never, so privileged code can no longer execute from those regions.

### Cache coherence API — `migration-4.4`

Rename `CONFIG_ARCH_HAS_COHERENCE` to `CONFIG_CACHE_CAN_SAY_MEM_COHERENCE` and replace `arch_mem_coherent()` with `sys_cache_is_mem_coherent()`. Rename `CONFIG_CACHE_DOUBLEMAP` to `CONFIG_CACHE_HAS_MIRRORED_MEMORY_REGIONS`.

## POSIX and file descriptors

### POSIX and kernel shell behavior — `4.0.0`

The POSIX surface adds device I/O, signals, synchronized I/O, priority protection, `O_TRUNC`, `rmdir()`, `remove()`, and the reentrant time functions. The kernel shell can change thread CPU affinity at runtime, and bare `kernel reboot` now performs a cold reboot.

### POSIX headers and limits — `migration-4.3`

Applications must include `<time.h>`, `<signal.h>`, and `<limits.h>` rather than the former `<zephyr/posix/...>` headers; non-POSIX C library ports may use Zephyr's `posix_time.h`, `posix_signal.h`, and `posix_limits.h`. Runtime-dependent limits may need to be obtained with `sysconf()`.

### File-descriptor table sizing — `migration-4.3`

`ZVFS_OPEN_SIZE` now determines file-descriptor table size and availability, with subsystem requirements contributed by `CONFIG_ZVFS_OPEN_ADD_SIZE_*`. `CONFIG_ZVFS_OPEN_MAX` remains but is raised to larger contributed minima unless `CONFIG_ZVFS_OPEN_IGNORE_MIN` is enabled.

### POSIX and RISC-V Kconfig deprecations — `4.3.0`

Rename `CONFIG_POSIX_READER_WRITER_LOCKS` to `CONFIG_POSIX_RW_LOCKS` and RISC-V's `CONFIG_EXTRA_EXCEPTION_INFO` to `CONFIG_EXCEPTION_DEBUG`; Newlib can opt into POSIX limits with `CONFIG_NEWLIB_LIBC_USE_POSIX_LIMITS_H`.

## Core utilities and execution

### Maximum CPU count — `migration-4.0`

`CONFIG_MP_NUM_CPUS` was removed. Use `CONFIG_MP_MAX_NUM_CPUS`.

### Core API removals — `4.0.0`

Replace `K_THREAD_STACK_MEMBER` with `K_KERNEL_STACK_MEMBER`, `ceiling_fraction` with `DIV_ROUND_UP`, the architecture CMSIS headers with `cmsis_core.h`, and `<zephyr/random/rand32.h>` with `<zephyr/random/random.h>`. `CBPRINTF_PACKAGE_COPY_*`, generated `_ENUM_TOKEN`/`_ENUM_UPPER_TOKEN`, deprecated `net_pkt` functions, and the `EARLY`, `APPLICATION`, and `SMP` device-init levels are gone; `net_buf_put()`/`net_buf_get()` and the kscan subsystem are deprecated.

### Stack-canary strength — `migration-4.1`

`CONFIG_STACK_CANARIES` no longer adds `-fstack-protector-all`. Enable `CONFIG_STACK_CANARIES_ALL` when all-function stack protection is required.

### I3C target, RTIO, and controller handoff — `4.1.0`

New I3C surfaces include `CONFIG_I3C_TARGET_BUFFER_MODE`, `CONFIG_I3C_RTIO`, `i3c_ibi_hj_response()`, `i3c_ccc_do_getacccr()`, and `i3c_device_controller_handoff()`. Initial controller bindings include `snps,designware-i3c` and `st,stm32-i3c`.

### State Machine Framework event propagation — `migration-4.2`

`smf_set_handled()` is removed, and hierarchical state run actions now return `smf_state_result`: return `SMF_EVENT_HANDLED` to stop propagation or `SMF_EVENT_PROPAGATE` to invoke parent run actions. Flat state machines ignore the value, for which `SMF_EVENT_HANDLED` is the appropriate return.

### Device initialization errors — `migration-4.3`

`device_init()` now returns a negative `-errno` on initialization failure. Remove workarounds that interpreted the earlier erroneous positive value.

### Utility APIs — `migration-4.3`

Include `<zephyr/sys/util_utf8.h>` for `utf8_trunc()` and `utf8_lcpy()` instead of relying on `util.h`. Rename `Z_MIN`, `Z_MAX`, and `Z_CLAMP` to `min`, `max`, and `clamp`.

### DMA userspace access — `migration-4.3`

The DMA API no longer exposes userspace syscalls because their access and parameter verification could not be made safe. Userspace code can no longer invoke the DMA API through the former syscall surface.

### RTIO callback chains — `migration-4.3`

RTIO callback operations gain an argument containing the first error result in the chain. Callbacks now run even when an earlier submission failed, so handlers must inspect that result instead of assuming prior success.

### Compiler-assisted instrumentation — `4.3.0`

`CONFIG_INSTRUMENTATION` adds runtime call-graph tracing and statistical profiling through compiler-managed function instrumentation. It provides call-graph and statistical mode settings, trigger/stop and exclusion controls, and `instr_*` APIs for control and UART dumps.

### Hardware shadow stacks and Intel CET — `4.3.0`

Zephyr adds architecture and kernel hardware-shadow-stack support through `CONFIG_ARCH_HAS_HW_SHADOW_STACK`, `CONFIG_HW_SHADOW_STACK`, sizing/declaration macros, and `k_thread_hw_shadow_stack_attach()`. x86 Intel CET and indirect-branch tracking are selected through the `CONFIG_X86_CET*` options.

### SCMI call controls — `4.3.0`

`ARM_SCMI_CHAN_SEM_TIMEOUT_USEC` configures the SCMI channel semaphore timeout, and `scmi_send_message()` gains an argument selecting polling. Callers should use `scmi_status_to_errno()` directly to translate returned command status.

### 64-bit counter ticks — `migration-4.4`

Drivers implementing `get_value_64` must select `CONFIG_COUNTER_SUPPORTS_64BITS_TICKS`, and applications must select `CONFIG_COUNTER_64BITS_TICKS` before using that API.

### Tiered heap hardening — `4.4.0`

`CONFIG_SYS_HEAP_HARDENING` adds Basic, Moderate, Full, and Extreme checking for `sys_heap_alloc()` and `sys_heap_free()`, progressing through double-free detection, neighbor validation, and optional per-chunk canaries.

### Scope-based cleanup — `4.4.0`

`SCOPE_VAR_DEFINE`, `SCOPE_GUARD_DEFINE`, and `SCOPE_DEFER_DEFINE`, with the `scope_var`, `scope_guard`, and `scope_defer` helpers, provide RAII/defer-style cleanup when C scope exits.
