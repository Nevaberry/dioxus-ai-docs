# Devicetree and Hardware Description

Entries are grouped by developer task and alphabetized by topic. The
parenthetical identifier records the exact source batch for each item.

## ADC bindings and clocks (migration-4.3)

The Silabs IADC driver and compatible move from `iadc_gecko.c` and `silabs,gecko-iadc` to `adc_silabs_iadc.c` and `silabs,iadc`. STM32 ADC nodes now require `clock-names` matching `clocks`, using `adcx` for the register clock, `adc-ker` for the kernel source, and, where applicable, `adc-pre` for the RCC prescaler.

## Additional removals and binding deprecations (4.3.0)

Devicetree's base `status` enum no longer accepts `ok`, STM32 LPTIM clock selection must move from `CONFIG_STM32_LPTIM_CLOCK_LSI`/`CONFIG_STM32_LPTIM_CLOCK_LSE` to Devicetree, and `maxim,ds3231` is deprecated in favor of `maxim,ds3231-rtc`.

## Architecture current-pointer hooks (4.1.0)

Architecture ports can provide a custom current-thread implementation with `CONFIG_ARCH_HAS_CUSTOM_CURRENT_IMPL`. RISC-V can keep the current-thread pointer in the global pointer register with `CONFIG_RISCV_CURRENT_VIA_GP`.

## Architecture Kconfig changes (migration-4.2)

`CONFIG_SRAM_VECTOR_TABLE` now additionally depends on `CONFIG_XIP`, `CONFIG_ARCH_HAS_VECTOR_TABLE_RELOCATION`, and `CONFIG_ROMSTART_RELOCATION_ROM`. Rename the x86-only `CONFIG_DEBUG_INFO` option to `CONFIG_X86_DEBUG_INFO`.

## Architecture support and execution protection (4.2.0)

Zephyr gains initial Renesas RX support, including `rsk_rx130` and a QEMU-based target, while NIOS2 support is removed. With `CONFIG_ARM_MPU_PXN` and `CONFIG_USERSPACE`, `__ramfunc` and `__ram_text_reloc` are privileged-execute-never, so privileged code can no longer execute from those regions.

## AXP MFD and nRF ETR configuration (migration-4.3)

The combined `MFD_AXP192_AXP2101` symbol is removed; select `MFD_AXP192` or `MFD_AXP2101` for the corresponding device. The nRF ETR driver moved under debug: rename `NRF_ETR*` symbols to `DEBUG_NRF_ETR*` and explicitly enable `DEBUG_DRIVER`.

## Clock-control bindings (migration-4.4)

Bouffalo Lab clock nodes move to the consolidated `bflb,flash-clk`, `bflb,pll`, and `bflb,root-clk` compatibles. Remove `resource-type`, `resource-instance`, and `resource-channel` from out-of-tree `infineon,peri-div` nodes.

## Devicetree binding defaults (migration-4.4)

Bindings may no longer define defaults for `status`, `#address-cells`, or `#size-cells`; doing so is a build error. Put required values explicitly in the Devicetree source instead.

## Devicetree include and property style (migration-4.2)

Includes of Zephyr files moved out of `dts/common` must drop the `common/` prefix; Silicon Labs Series 2 SoC includes move under a superfamily directory such as `silabs/xg24/`. Local bindings must use hyphens rather than underscores in property names; `scripts/utils/migrate_bindings_style.py` performs the mechanical conversion.

## Devicetree iteration and nexus mappings (4.4.0)

`DT_FOREACH_REG`, `DT_FOREACH_REG_SEP`, `DT_FOREACH_REG_VARGS`, and `DT_FOREACH_REG_SEP_VARGS`, plus their instance-number variants, iterate register entries; `DT_CHILD_BY_UNIT_ADDR_INT` and `DT_INST_CHILD_BY_UNIT_ADDR_INT` select integer unit addresses. First-class `*-map` definitions add nexus-node and specifier-mapping support.

## Devicetree property enums (4.0.0)

Bindings can define `string-array` and `array` properties as enums, with accessors such as `DT_ENUM_IDX_BY_IDX`; generated strings now correctly escape quotes, backslashes, and newlines.

## Devicetree property spelling migrations (migration-4.1)

Several bindings replace underscore spellings with hyphenated names:

- Clock: `freqs_mhz`, `cg_reg`, and `pll_ctrl_reg` become `freqs-mhz`, `cg-reg`, and `pll-ctrl-reg`.
- Counter: `primary_source`, `secondary_source`, `filter_count`, and `filter_period` become `primary-source`, `secondary-source`, `filter-count`, and `filter-period`.
- CAN and display: `clock_div8`, `pclk_pol`, and `data_cmd-gpios` become `clock-div8`, `pclk-pol`, and `data-cmd-gpios`.
- DAC: `voltage_reference` and `power_down_mode` become `voltage-reference` and `power-down-mode`.
- GPIO: `pin_mask`, `pinmux_mask`, `vbatts_pins`, `bit_per_gpio`, `off_val`, and `on_val` become their corresponding hyphenated names.
- HW spinlock, I2C, I2S, and LED: use `num-locks`, `port-sel`, `fifo-depth`, and `max-curr-opt`.
- SDHC: `power_delay_ms` and `max_current_330` become `power-delay-ms` and `max-current-330`.
- Timer and USB: `ticks_us` and `phy_handle` become `ticks-us` and `phy-handle`.

## Devicetree register literals (migration-4.0)

`DT_REG_ADDR` and its variants now expand to unsigned literals, as do `DT_REG_SIZE` variants. Code that uses an address as a devicetree index must switch to the corresponding `DT_REG_ADDR_RAW` macro; there is no raw size variant.

## Devicetree, Kconfig, and footprint diagnostics (4.3.0)

`dtdoctor` diagnoses Devicetree build errors, the `traceconfig` build target explains symbol origins and final values, and interactive footprint charts visualize application RAM and ROM use.

## Driver compatible and power-domain migrations (migration-4.0)

Rename LiteX compatibles `litex,eth0` to `litex,liteeth` and `litex,uart0` to `litex,uart`. Microchip `microchip,mcp230xx`/`microchip,mcp23sxx` nodes must use a chip-specific compatible such as `microchip,mcp23017` and drop `ngpios`; open-drain MCP23x09/MCP23x18 outputs now expose their real semantics through `gpio_pin_set`.

Replace the singular `power-domain` property with `power-domains`. Providers declare `#power-domain-cells`, and consumers may name multiple entries with `power-domain-names`.

## Infineon and interrupt-controller names (migration-4.4)

Infineon CAT1 Kconfigs and bindings lose `CAT1`, for example `CONFIG_*_INFINEON_CAT1` becomes `CONFIG_*_INFINEON` and `infineon,cat1-adc` becomes `infineon,adc`; its CYW43xx HCI UART symbols become `CONFIG_BT_HCI_UART_INFINEON` and `infineon,bt-hci-uart`. Rename `swerv,pic` to `cdns,swerv-pic`.

## nRF52/nRF53 internal regulators (migration-4.0)

The `CONFIG_SOC_DCDC_NRF52X*` and `CONFIG_SOC_DCDC_NRF53X*` options are deprecated in favor of regulator devicetree nodes. Set `regulator-initial-mode = <NRF5X_REG_MODE_DCDC>` on nodes such as `vregmain`/`vregradio`, and enable high-voltage nodes such as `reg0` or `vregh` with `status = "okay"`.

## nRF53 oscillator configuration (migration-4.0)

nRF53 LFXO/HFXO capacitor settings move from the deprecated `CONFIG_SOC_*LFXO*` and `CONFIG_SOC_*HFXO*` options to devicetree. Select external capacitors with `load-capacitors = "external"`; for internal capacitors also set `load-capacitance-picofarad` on LFXO or `load-capacitance-femtofarad` on HFXO.

## NXP binding migrations (migration-4.1)

Rename the following compatibles: `nxp,kinetis-adc12` to `nxp,adc12`, `nxp,imx-lpi2c` to `nxp,lpi2c`, `nxp,kinetis-mpu` to `nxp,sysmpu`, `nxp,kinetis-pinctrl` to `nxp,port-pinctrl`, `nxp,kinetis-pinmux` to `nxp,port-pinmux`, and `nxp,kinetis-ftm-pwm` to `nxp,ftm-pwm`. The MPU Kconfig rename is `CPU_HAS_NXP_MPU` to `CPU_HAS_NXP_SYSMPU`.

Also rename `nxp,kinetis-lpuart` to `nxp,lpuart`, `nxp,imx-lpspi` to `nxp,lpspi`, `nxp,kinetis-dspi` to `nxp,dspi`, `nxp,kinetis-rtc` to `nxp,rtc`, `nxp,kinetis-ftm` to `nxp,ftm`, and `nxp,kinetis-wdog32` to `nxp,wdog32`; the FTM binding also moves under the timer bindings.

## NXP EDMA discriminator (migration-4.4)

`CONFIG_DMA_MCUX_EDMA_V5` is removed now that EDMA v4 and v5 share one driver path; out-of-tree conditionals should use the unified `DMA_MCUX_EDMA_V4` handling.

## NXP FlexSPI NOR topology (migration-4.4)

An `nxp,imx-flexspi-nor` node is now a controller containing a `soc-nv-flash` child; move erase/write sizes and partitions to the child and add `ranges` to the controller. Point `zephyr,flash` at the child and `zephyr,flash-controller` at the controller.

## NXP I2S master clock direction (migration-4.2)

For `nxp,mcux-i2s`, set the new `mclk-output` devicetree property to make MCLK an output; `I2S_OPT_BIT_CLK_SLAVE` no longer controls MCLK direction.

## NXP includes and system timers (migration-4.4)

NXP ARM DTSI includes move into family directories, for example `<nxp/nxp_rt1060.dtsi>` becomes `<nxp/imxrt/nxp_rt1060.dtsi>`. Boards using `CONFIG_MCUX_LPTMR_TIMER` must select the timer with `/chosen/zephyr,system-timer = &lptmr0`.

## NXP LPTMR filtering (migration-4.4)

`nxp,lptmr` no longer treats `prescale-glitch-filter = <0>` as bypass; use the boolean `prescale-glitch-filter-bypass;`, and keep active filter values in the range 0–15. In time-counter mode the divisor is `2^(N + 1)`; in pulse-counter mode a change is recognized after `2^N` rising edges and zero is not a valid active filter.

## NXP USDHC card detection (migration-4.0)

Without a configured card-detect method, NXP USDHC now assumes a card is present. Add `detect-cd` to the active USDHC node to keep using the peripheral's internal card-detect signal.

## Other compatible migrations (migration-4.1)

Rename `ti,ads114s0x-gpio` to `ti,ads1x4s0x-gpio`, `renesas,ra8-pwm` to `renesas,ra-pwm`, and `zephyr,gpio-steppers` to `zephyr,gpio-stepper`. Sensor compatibles `we,wsen-pads`, `we,wsen-pdus`, `we,wsen-tids`, and `invensense,icp10125` become `we,wsen-pads-2511020213301`, `we,wsen-pdus-25131308XXXXX`, `we,wsen-tids-2521020222501`, and `invensense,icp101xx`, respectively.

Silabs serial bindings split into `silabs,usart-uart` for Series 2 and `silabs,gecko-usart` for Series 0/1. SPI compatibles `silabs,gecko-spi-usart` and `silabs,gecko-spi-eusart` become `silabs,usart-spi` and `silabs,eusart-spi`; the deprecated `eth_mcux` driver is removed.

## POSIX and RISC-V Kconfig deprecations (4.3.0)

Rename `CONFIG_POSIX_READER_WRITER_LOCKS` to `CONFIG_POSIX_RW_LOCKS` and RISC-V's `CONFIG_EXTRA_EXCEPTION_INFO` to `CONFIG_EXCEPTION_DEBUG`; Newlib can opt into POSIX limits with `CONFIG_NEWLIB_LIBC_USE_POSIX_LIMITS_H`.

## PSRAM refresh configuration (migration-4.4)

`st,stm32-xspi-psram` and `st,stm32-ospi-psram` nodes must set `st,refresh` in memory-clock cycles; their hard-coded defaults are gone.

## QSPI and radio bindings (migration-4.4)

An STM32 QSPI node using `dual-flash` must add `ssht-enable` to retain sample shifting, which now defaults off. Rename `generic-fem-two-ctrl-pins`, `gpio-radio-coex`, and `tx-high-power-supported` to their `radio-`-prefixed forms.

## Raspberry Pi and STM32 configuration (migration-4.1)

Rename `CONFIG_SOC_SERIES_RP2XXX` to `CONFIG_SOC_SERIES_RP2040`. STM32 `st,adc-sequencer` and `st,adc-clock-source` properties now take strings instead of integer values.

## RISC-V Devicetree ownership (migration-4.4)

`CONFIG_RISCV` now requires a `riscv` Devicetree node, whose `riscv,isa-base` and `riscv,isa-extensions` properties define the base ISA and extensions; `riscv,isa` is deprecated. SoC Kconfigs that encoded ISA/FPU choices, including the CV64A6 variants and AE350 `CONFIG_RV*`/FPU options, are removed or consolidated.

## RISC-V fatal exception frames (4.0.0)

With `CONFIG_EXTRA_EXCEPTION_INFO`, `arch_esf` now has a `csf` pointer to the callee-saved registers for use by `k_sys_fatal_error_handler()`. SoCs selecting `RISCV_SOC_HAS_ISR_STACKING` must include that member in `SOC_ISR_STACKING_ESF_DECLARE`.

## RISC-V machine timer binding (migration-4.2)

Several vendor machine-timer compatibles are unified as `riscv,machine-timer`. Both MTIME and MTIMECMP addresses must be explicit, with matching required names:

```devicetree
reg = <0xd1000000 0x8>, <0xd1000008 0x8>;
reg-names = "mtime", "mtimecmp";
```

The CPU group's `timebase-frequency` property can now supply `CONFIG_SYS_CLOCK_HW_CYCLES_PER_SEC`.

## Sensor and stepper compatibles (migration-4.3)

An `invensense,icm42688` node must also list `invensense,icm4268x` in `compatible`. Replace `zephyr,gpio-stepper` with `zephyr,h-bridge-stepper`.

## Sensor bindings (migration-4.0)

MCP9808 nodes move from `microchip,mcp9808` to the generic `jedec,jc-42.4-temp` compatible. Current-sense amplifiers replace `sense-resistor-micro-ohms` with `sense-resistor-milli-ohms`, and `sense-gain-mult`/`sense-gain-div` are now limited to `UINT16_MAX`; `nxp,kinetis-acmp` properties should drop their deprecated `nxp,` name prefix.

## Sensor compatible migrations (migration-4.2)

Use `liteon,ltrf216a` instead of `ltr,f216a`, `ti,tmp11x`/`ti,tmp11x-eeprom` instead of the TMP116-only compatibles, and a pressure-specific `meas,ms5837-30ba` or `meas,ms5837-02ba` instead of `meas,ms5837`. The WSEN ITDS compatible becomes `we,wsen-itds-2533020201601`.

## Silabs RAIL and power-state configuration (migration-4.3)

Rename `CONFIG_RAIL_PA_CURVE_HEADER`, `CONFIG_RAIL_PA_CURVE_TYPES_HEADER`, and `CONFIG_RAIL_PA_ENABLE_CALIBRATION` to their `CONFIG_SILABS_SISDK_RAIL_*` forms. Series 2 SoCs remove the separate `em3` state and now choose EM2 or EM3 automatically from peripheral oscillator requests.

## Silabs Series 2 pin control (migration-4.1)

Series 2 devices use the new `silabs,dbus-pinctrl` driver, with signal macros from a SoC binding header and GPIO electrical properties expressed in devicetree groups:

```devicetree
group0 {
    pins = <I2C0_SDA_PD2>, <I2C0_SCL_PD3>;
    drive-open-drain;
    bias-pull-up;
};
```

## SoC Kconfig renames (migration-4.4)

Nordic series symbols such as `CONFIG_SOC_SERIES_NRF52X`, `CONFIG_SOC_SERIES_NRF54HX`, and `CONFIG_SOC_SERIES_NRF91X` lose their trailing `X`; SiFive Freedom symbols drop `SIFIVE_FREEDOM` from names such as `CONFIG_SOC_SERIES_SIFIVE_FREEDOM_FU700`; and `CONFIG_SOC_SERIES_CH32V00X` becomes `CONFIG_SOC_SERIES_QINGKE_V2C`.

## STM32 ADC clock source (migration-4.0)

Every STM32 ADC selecting the asynchronous source with `st,adc-clock-source` must now also define its domain clock explicitly with the `clock` property.

## STM32 clock configuration (migration-4.3)

`CONFIG_CLOCK_STM32_HSE_CLOCK` is no longer user-configurable on STM32 MPU platforms; it is derived from `clock-frequency` on an enabled `&clk_hse`. The removed `st,stm32f1-rcc` and `st,stm32f3-rcc` bindings no longer provide ADC prescaler properties, so supply the prescaler as another ADC clock.

## STM32 DCMI and external memories (migration-4.2)

STM32 DCMI sensor-interface settings move to endpoint-based `video-interfaces.yaml` bindings, and `capture-rate` is replaced by `video_set_frmival()`. STM32 xSPI/oSPI/qSPI memory nodes now separate mapping and capacity: for a 512-Mbit device use `reg = <0>;` and `size = <DT_SIZE_M(512)>;`, with the mapping address supplied by the SoC controller node.

## STM32 PLL bindings (migration-4.4)

STM32F2/F4/F7 PLL compatibles merge into `st,stm32fx-pll-clock`, with `div-divq`/`div-divr` renamed to `post-div-q`/`post-div-r`; define a post-divider whenever the corresponding `div-q`/`div-r` is used. STM32L4 PLLSAI likewise moves to `st,stm32l4-pll-clock` and `post-div-r`.

## STM32 power and tightly coupled memory (migration-4.4)

STM32 power-supply Kconfigs are removed in favor of the `st,stm32h7-pwr`, `st,stm32h7rs-pwr`, and `st,stm32-dualreg-pwr` bindings. Replace `/chosen/zephyr,ccm` and `__ccm_*_section` with `/chosen/zephyr,dtcm` and `__dtcm_*_section`.

## STM32 SPI and interrupt sizing (migration-4.4)

`CONFIG_SPI_STM32_USE_HW_SS` is removed: `cs-gpios` or `st,soft-nss` selects Soft NSS, and their absence selects Hard NSS. SPI pins now default to `very-high-speed` slew and may need an overlay to reduce power, while auto-derived `CONFIG_NUM_IRQS` may need an explicit larger value for IRQs used only through `IRQ_CONNECT()`.

## STM32U5 OTG HS PHY clock (migration-4.3)

`st,stm32u5-otghs-phy` nodes must set the new `clock-reference` property to select SYSCFG OTG HS PHY CLKSEL consistently with the RCC OTG HS kernel-clock selection.

## STM32U5 voltage scaling (4.4.0)

The `voltage-scale` property on `st,stm32u5-pwr` selects the voltage scale manually, notably allowing USB operation at lower system clock frequencies.
