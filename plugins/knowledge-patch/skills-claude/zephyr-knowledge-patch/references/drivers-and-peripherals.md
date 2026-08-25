# Drivers and Peripherals

Entries are grouped by developer task and alphabetized by topic. The
parenthetical identifier records the exact source batch for each item.

## 64-bit counter ticks (migration-4.4)

Drivers implementing `get_value_64` must select `CONFIG_COUNTER_SUPPORTS_64BITS_TICKS`, and applications must select `CONFIG_COUNTER_64BITS_TICKS` before using that API.

## ADC migrations (migration-4.4)

Rename `renesas,ra-adc` to `renesas,ra-adc12`, `CONFIG_ADC_MCUX_SAR_ADC` to `CONFIG_ADC_NXP_SAR_ADC`, and STM32 ADC `resolutions` to `st,adc-resolutions`. NXP SAR ADC nodes must add `zephyr,input-positive`, and supported SoCs should use `ADC_REF_VDD_1` rather than `ADC_REF_INTERNAL`.

## ADC sequence priority (4.4.0)

`adc_sequence.priority`, enabled with `CONFIG_ADC_SEQUENCE_PRIORITY`, lets ADC requests carry an explicit sequence priority.

## Asynchronous runtime power management (4.2.0)

Device runtime PM can execute synchronously or asynchronously and can use the system workqueue or a dedicated workqueue. Configure this with `CONFIG_PM_DEVICE_RUNTIME_ASYNC`, `CONFIG_PM_DEVICE_RUNTIME_USE_SYSTEM_WQ`, or `CONFIG_PM_DEVICE_RUNTIME_USE_DEDICATED_WQ` and the dedicated-workqueue size, priority, and init-priority options.

## Biometrics and wake-up controllers (4.4.0)

Zephyr adds standard biometrics and Wake-up Controller device classes. Initial biometrics bindings are `adh-tech,gt5x`, `zhiantec,zfm-x0`, and `zephyr,biometrics-emul`; the initial WUC binding is `nxp,llwu`.

## CAN API removals (4.1.0)

Replace `CAN_MAX_STD_ID` and `CAN_MAX_EXT_ID` with `CAN_STD_ID_MASK` and `CAN_EXT_ID_MASK`, and replace `can_get_min_bitrate()` and `can_get_max_bitrate()` with `can_get_bitrate_min()` and `can_get_bitrate_max()`. `can_calc_prescaler()` is removed without a listed replacement.

## CAN capacity configuration (migration-4.4)

The generic `CONFIG_CAN_MAX_FILTER`, `CONFIG_CAN_MAX_STD_ID_FILTER`, and `CONFIG_CAN_MAX_EXT_ID_FILTER` options are removed; configure the driver-specific limit, such as `CONFIG_CAN_MCUX_FLEXCAN_MAX_FILTERS` or the STM32 BXCAN/FDCAN standard and extended filter limits. FlexCAN's `CONFIG_CAN_MAX_MB` likewise moves to the per-instance `number-of-mb` Devicetree property.

## CAN driver settings (migration-4.4)

Rename `CONFIG_CAN_MCUX_MCAN` to `CONFIG_CAN_NXP_LPC_MCAN`. A `ti,tcan4x5x` node must set `ti,nwkrq-voltage-vio` to retain the former VIO default, while an `nxp,flexcan` `clk-source` now selects between the named `clksrc0` and `clksrc1` inputs.

## Connector and Nordic UART behavior (4.2.0)

Boards with Qwiic, Stemma, or Grove I2C connectors now expose the common `zephyr_i2c` devicetree label, allowing connectorized I2C shields to work across branding through `west build --shield`. The Nordic UART receiver mode that uses an extra timer is no longer deprecated because it is the reliable receive path without hardware flow control.

## DMA userspace access (migration-4.3)

The DMA API no longer exposes userspace syscalls because their access and parameter verification could not be made safe. Userspace code can no longer invoke the DMA API through the former syscall surface.

## Driver API introspection (4.1.0)

`DEVICE_API_IS` tests whether a device implements a particular API. Shell completion uses it to offer only compatible devices where a command expects one.

## EEPROM target access (migration-4.4)

I2C EEPROM target code should replace deprecated `eeprom_target_program()` with `eeprom_target_read_data()` and `eeprom_target_write_data()`, which take explicit offset and length arguments.

## H-bridge stepper migration (migration-4.4)

Rename `zephyr,h-bridge-stepper` to `zephyr,h-bridge-stepper-ctrl`, replace `micro-step-res` with `lut-step-gap`, remove `en-gpios`, and stop calling hardware-driver APIs such as `stepper_enable()` on that controller. The generic ISR settings are now `CONFIG_STEPPER_CTRL_ISR_SAFE_EVENTS` and `CONFIG_STEPPER_CTRL_EVENT_QUEUE_LEN`, with ISR-safe events enabled by default.

## I3C address-management API (4.0.0)

`i3c_ccc_do_setdasa()` now takes the dynamic address explicitly, `i3c_determine_default_addr()` is removed, and `attach_i3c_device()` no longer takes an address because the driver derives it from `i3c_device_desc`. Controllers may advertise SETAASA support with the `supports-setaasa` devicetree property.

## I3C target, RTIO, and controller handoff (4.1.0)

New I3C surfaces include `CONFIG_I3C_TARGET_BUFFER_MODE`, `CONFIG_I3C_RTIO`, `i3c_ibi_hj_response()`, `i3c_ccc_do_getacccr()`, and `i3c_device_controller_handoff()`. Initial controller bindings include `snps,designware-i3c` and `st,stm32-i3c`.

## MCXC242 asynchronous UART (4.4.2)

The MCXC242 LPUART driver now supports DMA-backed operation through Zephyr's asynchronous UART API.

## MDIO lifecycle (migration-4.4)

`mdio_bus_enable()` and `mdio_bus_disable()` are removed because MDIO drivers now manage bus state internally.

## nPM1300 to nPM13xx migration (migration-4.2)

GPIO, LED, MFD, regulator, sensor-charger, and watchdog headers, APIs, defines, and Kconfigs move from `NPM1300`/`npm1300` names to `NPM13XX`/`npm13xx`. Regulator rail GPIOs no longer reference a GPIO controller: replace a value such as `enable-gpios = <&pmic_gpios 3 GPIO_ACTIVE_LOW>;` with `enable-gpio-config = <3 GPIO_ACTIVE_LOW>;`.

## Out-of-tree driver API declarations (migration-4.1)

Driver APIs now live in iterable sections for runtime validation. Out-of-tree implementations of upstream driver classes must declare their API with `DEVICE_API()`.

## Raspberry Pi Pico PWM division (migration-4.0)

The Pico PWM driver now chooses its frequency division adaptively when the channel divider is omitted or zero. Set a nonzero `divider-int-0` (or the corresponding channel property) explicitly when fixed, pre-4.0 division behavior is required.

## Raw UART MCUmgr transport (4.4.0)

MCUmgr can carry raw SMP over UART using `CONFIG_UART_MCUMGR_RAW_PROTOCOL` and `CONFIG_MCUMGR_TRANSPORT_RAW_UART`; input timeout behavior is controlled by `CONFIG_MCUMGR_TRANSPORT_RAW_UART_INPUT_TIMEOUT` and `CONFIG_MCUMGR_TRANSPORT_RAW_UART_INPUT_TIMEOUT_TIME_MS`.

## Scheduler and I3C configuration (4.2.0)

Replace deprecated `CONFIG_SCHED_DUMB` and `CONFIG_WAITQ_DUMB` with `CONFIG_SCHED_SIMPLE` and `CONFIG_WAITQ_SIMPLE`. I3C group addressing and `CONFIG_I3C_USE_GROUP_ADDR` are removed; choose `CONFIG_I3C_CONTROLLER_ROLE_ONLY`, `CONFIG_I3C_TARGET_ROLE_ONLY`, or `CONFIG_I3C_DUAL_ROLE` through `CONFIG_I3C_MODE`.

## SCMI call controls (4.3.0)

`ARM_SCMI_CHAN_SEM_TIMEOUT_USEC` configures the SCMI channel semaphore timeout, and `scmi_send_message()` gains an argument selecting polling. Callers should use `scmi_status_to_errno()` directly to translate returned command status.

## SCMI firmware interface (4.0.0)

Zephyr gains initial Arm SCMI support for subsets of clock and pin-control commands over shared-memory and mailbox transports.

## SD and MMC disk names (migration-4.0)

SDMMC and MMC devicetree disk definitions now require `disk-name` so multiple devices can register. `"SD"` is the suggested SD default and `"SD2"` the suggested MMC default.

## SDHC and shell callbacks (migration-4.4)

Move `bus_4_bit_support`, `hs200_support`, and `hs400_support` from `sdhc_host_caps` to `sdhc_host_props`. `shell_set_bypass()` and `shell_bypass_cb_t` also gain a user-data pointer.

## Signal-only IPM callbacks (4.4.0)

Mailbox-backed IPM now supports signal-only messages; callbacks must accept a `NULL` payload when the mailbox supplies no data buffer.

## SPI chip-select timing (migration-4.3)

`SPI_CS_CONTROL_INIT*`, `SPI_CONFIG_DT*`, and `SPI_DT_SPEC_GET*` no longer accept a delay argument. Put peripheral chip-select timing in devicetree with `spi-cs-setup-delay-ns` and `spi-cs-hold-delay-ns`.

## SPI NOR deep power-down (migration-4.0)

`CONFIG_SPI_NOR_IDLE_IN_DPD` is removed. Enable device runtime power management for the SPI NOR device and tune the replacement behavior with `CONFIG_SPI_NOR_ACTIVE_DWELL_MS`.

## Step/direction stepper support (4.1.0)

`CONFIG_STEP_DIR_STEPPER` adds generic step/direction stepper support. New stepper bindings include `adi,tmc2209` and `ti,drv8424`.

## Stepper API and TMC50xx (migration-4.1)

Rename `stepper_set_actual_position()` to `stepper_set_reference_position()`, `stepper_move()` to `stepper_move_by()`, and `stepper_set_target_position()` to `stepper_move_to()`. `stepper_enable_constant_velocity_mode()` becomes argument-free `stepper_run()` after setting speed with `stepper_set_microstep_interval()`; that interval-in-nanoseconds API also replaces `stepper_set_max_velocity()`.

The TMC5041 driver becomes TMC50xx, and `STEPPER_ADI_TMC_RAMP_GEN` becomes `STEPPER_ADI_TMC50XX_RAMP_GEN`; use `tmc50xx_stepper_set_max_velocity()` or `tmc50xx_stepper_set_ramp()` for its velocity. Its properties use the hyphenated names `en-spreadcycle`, `i-scale-analog`, `index-otpw`, `index-step`, `internal-rsense`, `lock-gconf`, `mstep-reg-select`, `pdn-disable`, `poscmp-enable`, and `test-mode`.

## Stepper controller redesign (migration-4.4)

Motion APIs are renamed from `stepper_*` to `stepper_ctrl_*`, and events move from `stepper_event`/`STEPPER_EVENT_*` to `stepper_ctrl_event`/`STEPPER_CTRL_EVENT_*`. Step/dir hardware nodes no longer own motion properties; create a `zephyr,gpio-step-dir-stepper-ctrl` node with `stepper-driver` and place `step-gpios`, `dir-gpios`, `invert-direction`, and `counter` there.

## Stepper enable and disable (migration-4.2)

The former `stepper_enable(device, bool)` API is split into argument-free `stepper_enable(device)` and `stepper_disable(device)` operations.

## u-blox GNSS (migration-4.0)

The purported M10 driver is now identified as M8-only: change compatibles to `u-blox,m8` and Kconfig to `CONFIG_GNSS_U_BLOX_M8`. The `gnss_set_periodic_config` and `gnss_get_periodic_config` APIs are removed.

## UART readiness and LiteX Kconfig (migration-4.0)

Treat `uart_irq_tx_ready()` as ready when its return value is greater than zero, not only when it equals one; the value is now a lower bound on bytes accepted by `uart_fifo_fill()`. Rename `CONFIG_UART_LITEUART` to `CONFIG_UART_LITEX`.

## USB host-class framework (4.4.0)

Experimental USB host support gains a host-class driver framework and UVC camera support for Zephyr devices acting as hosts; `usb-host-uvc` demonstrates the new path.
