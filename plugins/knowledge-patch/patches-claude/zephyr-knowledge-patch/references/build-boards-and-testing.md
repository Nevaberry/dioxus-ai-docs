# Build, Boards, Toolchains, and Testing

Entries are grouped by developer task and alphabetized by topic. The
parenthetical identifier records the exact source batch for each item.

## Board and ADC-node renames (migration-4.3)

On `mimxrt11x0`, `lpadc1` becomes `lpadc2` and `lpadc0` becomes `lpadc1`. Rename board targets `frdm_mcxa166` to `frdm_mcxa346`, `frdm_mcxa276` to `frdm_mcxa266`, and `panb511evb` to `panb611evb`.

## Board and driver configuration ownership (4.0.0)

STM32 MCO configuration moves to devicetree, while board configurations should stop selecting `CONFIG_CLOCK_CONTROL` and `CONFIG_PINCTRL` because the family or consuming drivers now select them. Nordic's per-instance `CONFIG_UART_n_GPIO_MANAGEMENT` options are removed, and the NXP flash binding is renamed from `nxp,iap-msf1` to `nxp,msf1`.

## Board and shield target changes (migration-4.1)

Replace the `mikroe_weather_click` shield target with either `mikroe_weather_click_i2c` or `mikroe_weather_click_spi`. On `stm32f4_disco`, CAN1 and USART1 are disabled because their pin control conflicts with I2C1 audio-codec use.

## Board metadata and build variables (migration-4.4)

New `board.yml` board entries require `full_name`, and `BOARD_QUALIFIERS` no longer starts with `/`, so concatenation must use `${BOARD}/${BOARD_QUALIFIERS}`. `SNIPPET_ROOT` no longer includes the application source directory by default; add it through `snippet_root = <dir>` in `zephyr/module.yml` or append it in CMake.

## Board target migrations (migration-4.2)

NEORV32 implementations must update to version 1.11.6, and the former `neorv32` target becomes `neorv32/neorv32/up5kdemo`. Use `nucleo_wba55cg` instead of removed `nucleo_wba52cg`, and use the unified `esp32_devkitc` target instead of `esp32_devkitc_wroom` or `esp32_devkitc_wrover`.

The Renesas RA Arduino Uno R4 and MikroE Clicker RA4M1 boards now use FSP-based devicetrees: replace the removed `renesas,ra-gpio`, `renesas,ra-uart-sci`, `renesas,ra-pinctrl`, and `renesas,ra-clock-generation-circuit` bindings with `renesas,ra-gpio-ioport`, `renesas,ra-sci-uart`, `renesas,ra-pinctrl-pfs`, and `renesas,ra-cgc-pclk-block`.

## Board target revisions (4.2.0)

Use `arduino_uno_r4@minima` or `arduino_uno_r4@wifi` instead of the deprecated separate Uno R4 targets. The ESP32-C6 targets become `esp32c6_devkitc/esp32c6/hpcore` and `xiao_esp32c6/esp32c6/hpcore`.

## Board targets, blobs, and STM32 flashing (migration-4.0)

Use `native_sim` instead of deprecated `native_posix`, and `qemu_xtensa/dc233c` instead of deprecated `qemu_xtensa`. STM32WBA BLE builds fetch blobs with `west blobs fetch hal_stm32`; official STM32 boards now default `west flash` to STM32CubeProgrammer, so select alternatives explicitly with `--runner` or `-r`.

## Build and sysbuild controls (4.0.0)

EDT-generation arguments such as `--dts`, `--bindings-dirs`, and `--edt-pickle-out` move from `EXTRA_GEN_DEFINES_ARGS` to `EXTRA_GEN_EDT_ARGS`, and `west flash` accepts ELF input with the jlink, pyocd, and linkserver runners. Sysbuild can select the MCUboot operating mode with `SB_CONFIG_MCUBOOT_MODE`, including RAM-load mode.

## Build dashboard and ztest benchmarks (4.4.0)

The new build dashboard combines RAM/ROM footprint, Devicetree, and subsystem-initialization information. The ztest benchmarking framework standardizes cycle-accurate measurements with overhead compensation, automated collection, and statistical reporting; see `ztest_benchmark`.

## Build-time constants and sysbuild variants (4.4.0)

`zephyr_constants_library()` generates headers containing build-time constants derived from C structure layouts. Sysbuild adds `SB_CONFIG_MERGED_HEX_FILES`, experimental `ExternalZephyrVariantProject_Add()`, automatic direct-XIP slot-1 variants through `SB_CONFIG_MCUBOOT_DIRECT_XIP_GENERATE_VARIANT`, and the `slot1-partition` snippet.

## CMSIS 6 module (migration-4.2)

Cortex-M boards and SoCs now require the `CMSIS_6` module, so run `west update` before building and migrate overrides from `CONFIG_ZEPHYR_CMSIS_MODULE_DIR` to `CONFIG_ZEPHYR_CMSIS_6_MODULE_DIR`. Cortex-A and Cortex-R continue to use the older CMSIS module.

## Devicetree enum-array tests (migration-4.2)

`DT_ENUM_HAS_VALUE` and `DT_INST_ENUM_HAS_VALUE` now search every element of an array property rather than testing only its first element.

## Flash runner erase and reset behavior (migration-4.1)

The BOSSA runner no longer performs a full erase by default; request one with `west flash --erase`. nRF52 boards now default to a soft reset, with `west flash --pinreset` retaining pin reset, and both nrfjprog and nrfutil now honor the presence or absence of `--erase` for nRF52/nRF53 external flash.

## Generated-header dependencies (migration-4.4)

`kernel.h` now includes the generated `zephyr/heap_constants.h`. A downstream CMake library that races its generation must add `add_dependencies(${lib} zephyr_generated_headers)`.

## Hardware-model-v1 board aliases (4.1.0)

All deprecated HWMv1 board-name aliases introduced for compatibility in Zephyr 3.7 are removed. Builds must use the current non-alias board target names.

## HWMv1 removal (migration-4.2)

HWMv1 support is removed completely, so out-of-tree boards and SoCs must be converted to HWMv2 before they can build with Zephyr 4.2 or later.

## IAR and Rust application support (4.1.0)

Zephyr applications can now be built experimentally with the `toolchain_iar_arm` IAR compiler. Rust application support is initially available through the optional `language_rust` module.

## Keyboard matrix timing (migration-4.4)

Rename `poll-period-ms` and `stable-poll-period-ms` to `poll-period-us` and `stable-poll-period-us`, converting values to microseconds; for example, 10 ms becomes `<10000>`.

## Native PTY UART (migration-4.2)

`uart_native_posix` becomes `uart_native_pty`, with `zephyr,native-pty-uart`, `CONFIG_UART_NATIVE_PTY*`, and `CONFIG_UART_NATIVE_PTY_0` replacing the old POSIX names. Instantiate one devicetree node per UART; at runtime, `--<uart_name>_stdinout` connects an instance to standard input/output instead of a PTY.

## Native simulator and x86 symbols (migration-4.1)

`CONFIG_NATIVE_APPLICATION` is deprecated for out-of-tree boards in favor of the native simulator runner. `CONFIG_NATIVE_SIM_NATIVE_POSIX_COMPAT` now defaults to disabled and is deprecated, so code must stop depending on `CONFIG_BOARD_NATIVE_POSIX`.

On x86, replace the removed `CONFIG_DISABLE_SSBD` and `CONFIG_ENABLE_EXTENDED_IBRS` with `CONFIG_X86_DISABLE_SSBD` and `CONFIG_X86_ENABLE_EXTENDED_IBRS`.

## Native simulator renames (migration-4.2)

Rename `CONFIG_NATIVE_POSIX_SLOWDOWN_TO_REAL_TIME` to `CONFIG_NATIVE_SIM_SLOWDOWN_TO_REAL_TIME` and `zephyr,native-posix-cpu` to `zephyr,native-sim-cpu`. Counter, fake-entropy, and timer implementations likewise move from `native_posix` names to `native_sim`, including `CONFIG_COUNTER_NATIVE_SIM`, `CONFIG_FAKE_ENTROPY_NATIVE_SIM`, `CONFIG_NATIVE_SIM_TIMER`, `zephyr,native-sim-counter`, and `zephyr,native-sim-rng`.

The native Ethernet driver is now `ethernet_native_tap`; replace `CONFIG_ETH_NATIVE_POSIX*` with `CONFIG_ETH_NATIVE_TAP*`.

## Nordic flashing defaults (migration-4.2)

Nordic boards that formerly defaulted to `nrfjprog` now default to nRF Util; install `nrfutil` or retain the old runner with `west flash -r nrfjprog`. nRF54L boards also stop erasing internal storage by default; use `west flash --erase-mode ranges` to restore erasure of the ranges being written.

## OpenOCD and native simulator defaults (migration-4.4)

OpenOCD runner arguments `--use-elf`, `--use-bin`, and `--use-hex` are deprecated in favor of `--file-type=elf`, `bin`, or `hex`; `--file` selects a custom artifact. `native_sim` host FUSE access now defaults to libfuse3, with `CONFIG_FUSE_LIBRARY_VERSION` selecting another version.

## OpenRISC and simulator builds (4.4.0)

Zephyr now supports the OpenRISC architecture, and `native_sim` targets can be cross-compiled. Xtensa's `CONFIG_XTENSA_MMU_DOUBLE_MAP`, `CONFIG_XTENSA_RPO_CACHE`, `CONFIG_XTENSA_CACHED_REGION`, and `CONFIG_XTENSA_UNCACHED_REGION` options are removed.

## STM32 board runners and variants (migration-4.2)

STM32 board definitions should include `openocd-stm32.board.cmake` instead of `openocd.board.cmake`. The default `stm32n6570_dk/stm32n657xx` target is now a chainloaded application and must use `--sysbuild`; select `stm32n6570_dk/stm32n657xx/fsbl` explicitly for the former first-stage-bootloader behavior.

## STM32 OpenOCD transport (migration-4.3)

Updated STM32 board scripts support post-0.12 OpenOCD, whose HLA/SWD transport is deprecated, but ST-Link firmware older than v2j24 may fail to connect. Upgrade the adapter firmware or source `interface/stlink-hla.cfg` and explicitly select `hla_swd`; OpenOCD 0.12 and older remain supported.

## Toolchain and C language floor (migration-4.4)

Zephyr 4.4 requires Zephyr SDK 1.0.0 and Python 3.12, and now defaults to C17. Toolchains without C17 must temporarily select the now-deprecated `CONFIG_STD_C99` or `CONFIG_STD_C11`.

## Twister list syntax (4.1.0)

Twister configuration files no longer accept space-separated lists. Convert legacy files with `scripts/utils/twister_to_list.py`.

## Twister power testing and option removal (4.2.0)

Twister gains a power harness that measures device-under-test consumption and checks it against a tolerance. Remove `--disable-unrecognized-section-test` from invocations; that option and test are gone because disabling the check is now the default behavior.

## Ztest identifiers (4.1.0)

Ztest case identifiers now have the form `<test_scenario_name>.<ztest_suite_name>.<ztest_name>` in logs, `twister.json`, `testplan.json`, and `--sub-test` arguments. `--no-detailed-test-id` omits the scenario-name prefix.
