# Devicetree, Drivers, and Hardware

Use these notes for bindings, out-of-tree drivers, buses, clocks, SoC integration, and hardware-specific migrations.

## Devicetree and driver model

### Devicetree register literals — `migration-4.0`

`DT_REG_ADDR` and its variants now expand to unsigned literals, as do `DT_REG_SIZE` variants. Code that uses an address as a devicetree index must switch to the corresponding `DT_REG_ADDR_RAW` macro; there is no raw size variant.

### Devicetree property enums — `4.0.0`

Bindings can define `string-array` and `array` properties as enums, with accessors such as `DT_ENUM_IDX_BY_IDX`; generated strings now correctly escape quotes, backslashes, and newlines.

### Out-of-tree driver API declarations — `migration-4.1`

Driver APIs now live in iterable sections for runtime validation. Out-of-tree implementations of upstream driver classes must declare their API with `DEVICE_API()`.

### NXP binding migrations — `migration-4.1`

Rename the following compatibles: `nxp,kinetis-adc12` to `nxp,adc12`, `nxp,imx-lpi2c` to `nxp,lpi2c`, `nxp,kinetis-mpu` to `nxp,sysmpu`, `nxp,kinetis-pinctrl` to `nxp,port-pinctrl`, `nxp,kinetis-pinmux` to `nxp,port-pinmux`, and `nxp,kinetis-ftm-pwm` to `nxp,ftm-pwm`. The MPU Kconfig rename is `CPU_HAS_NXP_MPU` to `CPU_HAS_NXP_SYSMPU`.

Also rename `nxp,kinetis-lpuart` to `nxp,lpuart`, `nxp,imx-lpspi` to `nxp,lpspi`, `nxp,kinetis-dspi` to `nxp,dspi`, `nxp,kinetis-rtc` to `nxp,rtc`, `nxp,kinetis-ftm` to `nxp,ftm`, and `nxp,kinetis-wdog32` to `nxp,wdog32`; the FTM binding also moves under the timer bindings.

### Other compatible migrations — `migration-4.1`

Rename `ti,ads114s0x-gpio` to `ti,ads1x4s0x-gpio`, `renesas,ra8-pwm` to `renesas,ra-pwm`, and `zephyr,gpio-steppers` to `zephyr,gpio-stepper`. Sensor compatibles `we,wsen-pads`, `we,wsen-pdus`, `we,wsen-tids`, and `invensense,icp10125` become `we,wsen-pads-2511020213301`, `we,wsen-pdus-25131308XXXXX`, `we,wsen-tids-2521020222501`, and `invensense,icp101xx`, respectively.

Silabs serial bindings split into `silabs,usart-uart` for Series 2 and `silabs,gecko-usart` for Series 0/1. SPI compatibles `silabs,gecko-spi-usart` and `silabs,gecko-spi-eusart` become `silabs,usart-spi` and `silabs,eusart-spi`; the deprecated `eth_mcux` driver is removed.

### Devicetree property spelling migrations — `migration-4.1`

Several bindings replace underscore spellings with hyphenated names:

- Clock: `freqs_mhz`, `cg_reg`, and `pll_ctrl_reg` become `freqs-mhz`, `cg-reg`, and `pll-ctrl-reg`.
- Counter: `primary_source`, `secondary_source`, `filter_count`, and `filter_period` become `primary-source`, `secondary-source`, `filter-count`, and `filter-period`.
- CAN and display: `clock_div8`, `pclk_pol`, and `data_cmd-gpios` become `clock-div8`, `pclk-pol`, and `data-cmd-gpios`.
- DAC: `voltage_reference` and `power_down_mode` become `voltage-reference` and `power-down-mode`.
- GPIO: `pin_mask`, `pinmux_mask`, `vbatts_pins`, `bit_per_gpio`, `off_val`, and `on_val` become their corresponding hyphenated names.
- HW spinlock, I2C, I2S, and LED: use `num-locks`, `port-sel`, `fifo-depth`, and `max-curr-opt`.
- SDHC: `power_delay_ms` and `max_current_330` become `power-delay-ms` and `max-current-330`.
- Timer and USB: `ticks_us` and `phy_handle` become `ticks-us` and `phy-handle`.

### Driver API introspection — `4.1.0`

`DEVICE_API_IS` tests whether a device implements a particular API. Shell completion uses it to offer only compatible devices where a command expects one.

### Devicetree include and property style — `migration-4.2`

Includes of Zephyr files moved out of `dts/common` must drop the `common/` prefix; Silicon Labs Series 2 SoC includes move under a superfamily directory such as `silabs/xg24/`. Local bindings must use hyphens rather than underscores in property names; `scripts/utils/migrate_bindings_style.py` performs the mechanical conversion.

### Devicetree enum-array tests — `migration-4.2`

`DT_ENUM_HAS_VALUE` and `DT_INST_ENUM_HAS_VALUE` now search every element of an array property rather than testing only its first element.

### RISC-V machine timer binding — `migration-4.2`

Several vendor machine-timer compatibles are unified as `riscv,machine-timer`. Both MTIME and MTIMECMP addresses must be explicit, with matching required names:

```devicetree
reg = <0xd1000000 0x8>, <0xd1000008 0x8>;
reg-names = "mtime", "mtimecmp";
```

The CPU group's `timebase-frequency` property can now supply `CONFIG_SYS_CLOCK_HW_CYCLES_PER_SEC`.

### Devicetree, Kconfig, and footprint diagnostics — `4.3.0`

`dtdoctor` diagnoses Devicetree build errors, the `traceconfig` build target explains symbol origins and final values, and interactive footprint charts visualize application RAM and ROM use.

### Additional removals and binding deprecations — `4.3.0`

Devicetree's base `status` enum no longer accepts `ok`, STM32 LPTIM clock selection must move from `CONFIG_STM32_LPTIM_CLOCK_LSI`/`CONFIG_STM32_LPTIM_CLOCK_LSE` to Devicetree, and `maxim,ds3231` is deprecated in favor of `maxim,ds3231-rtc`.

### Devicetree binding defaults — `migration-4.4`

Bindings may no longer define defaults for `status`, `#address-cells`, or `#size-cells`; doing so is a build error. Put required values explicitly in the Devicetree source instead.

### QSPI and radio bindings — `migration-4.4`

An STM32 QSPI node using `dual-flash` must add `ssht-enable` to retain sample shifting, which now defaults off. Rename `generic-fem-two-ctrl-pins`, `gpio-radio-coex`, and `tx-high-power-supported` to their `radio-`-prefixed forms.

### STM32 PLL bindings — `migration-4.4`

STM32F2/F4/F7 PLL compatibles merge into `st,stm32fx-pll-clock`, with `div-divq`/`div-divr` renamed to `post-div-q`/`post-div-r`; define a post-divider whenever the corresponding `div-q`/`div-r` is used. STM32L4 PLLSAI likewise moves to `st,stm32l4-pll-clock` and `post-div-r`.

### RISC-V Devicetree ownership — `migration-4.4`

`CONFIG_RISCV` now requires a `riscv` Devicetree node, whose `riscv,isa-base` and `riscv,isa-extensions` properties define the base ISA and extensions; `riscv,isa` is deprecated. SoC Kconfigs that encoded ISA/FPU choices, including the CV64A6 variants and AE350 `CONFIG_RV*`/FPU options, are removed or consolidated.

### Devicetree iteration and nexus mappings — `4.4.0`

`DT_FOREACH_REG`, `DT_FOREACH_REG_SEP`, `DT_FOREACH_REG_VARGS`, and `DT_FOREACH_REG_SEP_VARGS`, plus their instance-number variants, iterate register entries; `DT_CHILD_BY_UNIT_ADDR_INT` and `DT_INST_CHILD_BY_UNIT_ADDR_INT` select integer unit addresses. First-class `*-map` definitions add nexus-node and specifier-mapping support.

## Analog, sensors, clocks, and power

### Driver compatible and power-domain migrations — `migration-4.0`

Rename LiteX compatibles `litex,eth0` to `litex,liteeth` and `litex,uart0` to `litex,uart`. Microchip `microchip,mcp230xx`/`microchip,mcp23sxx` nodes must use a chip-specific compatible such as `microchip,mcp23017` and drop `ngpios`; open-drain MCP23x09/MCP23x18 outputs now expose their real semantics through `gpio_pin_set`.

Replace the singular `power-domain` property with `power-domains`. Providers declare `#power-domain-cells`, and consumers may name multiple entries with `power-domain-names`.

### STM32 ADC clock source — `migration-4.0`

Every STM32 ADC selecting the asynchronous source with `st,adc-clock-source` must now also define its domain clock explicitly with the `clock` property.

### nRF53 oscillator configuration — `migration-4.0`

nRF53 LFXO/HFXO capacitor settings move from the deprecated `CONFIG_SOC_*LFXO*` and `CONFIG_SOC_*HFXO*` options to devicetree. Select external capacitors with `load-capacitors = "external"`; for internal capacitors also set `load-capacitance-picofarad` on LFXO or `load-capacitance-femtofarad` on HFXO.

### Sensor bindings — `migration-4.0`

MCP9808 nodes move from `microchip,mcp9808` to the generic `jedec,jc-42.4-temp` compatible. Current-sense amplifiers replace `sense-resistor-micro-ohms` with `sense-resistor-milli-ohms`, and `sense-gain-mult`/`sense-gain-div` are now limited to `UINT16_MAX`; `nxp,kinetis-acmp` properties should drop their deprecated `nxp,` name prefix.

### nRF52/nRF53 internal regulators — `migration-4.0`

The `CONFIG_SOC_DCDC_NRF52X*` and `CONFIG_SOC_DCDC_NRF53X*` options are deprecated in favor of regulator devicetree nodes. Set `regulator-initial-mode = <NRF5X_REG_MODE_DCDC>` on nodes such as `vregmain`/`vregradio`, and enable high-voltage nodes such as `reg0` or `vregh` with `status = "okay"`.

### SPI NOR deep power-down — `migration-4.0`

`CONFIG_SPI_NOR_IDLE_IN_DPD` is removed. Enable device runtime power management for the SPI NOR device and tune the replacement behavior with `CONFIG_SPI_NOR_ACTIVE_DWELL_MS`.

### NXP I2S master clock direction — `migration-4.2`

For `nxp,mcux-i2s`, set the new `mclk-output` devicetree property to make MCLK an output; `I2S_OPT_BIT_CLK_SLAVE` no longer controls MCLK direction.

### Sensor compatible migrations — `migration-4.2`

Use `liteon,ltrf216a` instead of `ltr,f216a`, `ti,tmp11x`/`ti,tmp11x-eeprom` instead of the TMP116-only compatibles, and a pressure-specific `meas,ms5837-30ba` or `meas,ms5837-02ba` instead of `meas,ms5837`. The WSEN ITDS compatible becomes `we,wsen-itds-2533020201601`.

### Asynchronous runtime power management — `4.2.0`

Device runtime PM can execute synchronously or asynchronously and can use the system workqueue or a dedicated workqueue. Configure this with `CONFIG_PM_DEVICE_RUNTIME_ASYNC`, `CONFIG_PM_DEVICE_RUNTIME_USE_SYSTEM_WQ`, or `CONFIG_PM_DEVICE_RUNTIME_USE_DEDICATED_WQ` and the dedicated-workqueue size, priority, and init-priority options.

### ADC bindings and clocks — `migration-4.3`

The Silabs IADC driver and compatible move from `iadc_gecko.c` and `silabs,gecko-iadc` to `adc_silabs_iadc.c` and `silabs,iadc`. STM32 ADC nodes now require `clock-names` matching `clocks`, using `adcx` for the register clock, `adc-ker` for the kernel source, and, where applicable, `adc-pre` for the RCC prescaler.

### STM32 clock configuration — `migration-4.3`

`CONFIG_CLOCK_STM32_HSE_CLOCK` is no longer user-configurable on STM32 MPU platforms; it is derived from `clock-frequency` on an enabled `&clk_hse`. The removed `st,stm32f1-rcc` and `st,stm32f3-rcc` bindings no longer provide ADC prescaler properties, so supply the prescaler as another ADC clock.

### Silabs RAIL and power-state configuration — `migration-4.3`

Rename `CONFIG_RAIL_PA_CURVE_HEADER`, `CONFIG_RAIL_PA_CURVE_TYPES_HEADER`, and `CONFIG_RAIL_PA_ENABLE_CALIBRATION` to their `CONFIG_SILABS_SISDK_RAIL_*` forms. Series 2 SoCs remove the separate `em3` state and now choose EM2 or EM3 automatically from peripheral oscillator requests.

### ADC migrations — `migration-4.4`

Rename `renesas,ra-adc` to `renesas,ra-adc12`, `CONFIG_ADC_MCUX_SAR_ADC` to `CONFIG_ADC_NXP_SAR_ADC`, and STM32 ADC `resolutions` to `st,adc-resolutions`. NXP SAR ADC nodes must add `zephyr,input-positive`, and supported SoCs should use `ADC_REF_VDD_1` rather than `ADC_REF_INTERNAL`.

### Clock-control bindings — `migration-4.4`

Bouffalo Lab clock nodes move to the consolidated `bflb,flash-clk`, `bflb,pll`, and `bflb,root-clk` compatibles. Remove `resource-type`, `resource-instance`, and `resource-channel` from out-of-tree `infineon,peri-div` nodes.

### STM32 power and tightly coupled memory — `migration-4.4`

STM32 power-supply Kconfigs are removed in favor of the `st,stm32h7-pwr`, `st,stm32h7rs-pwr`, and `st,stm32-dualreg-pwr` bindings. Replace `/chosen/zephyr,ccm` and `__ccm_*_section` with `/chosen/zephyr,dtcm` and `__dtcm_*_section`.

### ADC sequence priority — `4.4.0`

`adc_sequence.priority`, enabled with `CONFIG_ADC_SEQUENCE_PRIORITY`, lets ADC requests carry an explicit sequence priority.

## Buses, timing, and control

### SD and MMC disk names — `migration-4.0`

SDMMC and MMC devicetree disk definitions now require `disk-name` so multiple devices can register. `"SD"` is the suggested SD default and `"SD2"` the suggested MMC default.

### u-blox GNSS — `migration-4.0`

The purported M10 driver is now identified as M8-only: change compatibles to `u-blox,m8` and Kconfig to `CONFIG_GNSS_U_BLOX_M8`. The `gnss_set_periodic_config` and `gnss_get_periodic_config` APIs are removed.

### NXP USDHC card detection — `migration-4.0`

Without a configured card-detect method, NXP USDHC now assumes a card is present. Add `detect-cd` to the active USDHC node to keep using the peripheral's internal card-detect signal.

### UART readiness and LiteX Kconfig — `migration-4.0`

Treat `uart_irq_tx_ready()` as ready when its return value is greater than zero, not only when it equals one; the value is now a lower bound on bytes accepted by `uart_fifo_fill()`. Rename `CONFIG_UART_LITEUART` to `CONFIG_UART_LITEX`.

### I3C address-management API — `4.0.0`

`i3c_ccc_do_setdasa()` now takes the dynamic address explicitly, `i3c_determine_default_addr()` is removed, and `attach_i3c_device()` no longer takes an address because the driver derives it from `i3c_device_desc`. Controllers may advertise SETAASA support with the `supports-setaasa` devicetree property.

### CAN API removals — `4.1.0`

Replace `CAN_MAX_STD_ID` and `CAN_MAX_EXT_ID` with `CAN_STD_ID_MASK` and `CAN_EXT_ID_MASK`, and replace `can_get_min_bitrate()` and `can_get_max_bitrate()` with `can_get_bitrate_min()` and `can_get_bitrate_max()`. `can_calc_prescaler()` is removed without a listed replacement.

### SPI chip-select timing — `migration-4.3`

`SPI_CS_CONTROL_INIT*`, `SPI_CONFIG_DT*`, and `SPI_DT_SPEC_GET*` no longer accept a delay argument. Put peripheral chip-select timing in devicetree with `spi-cs-setup-delay-ns` and `spi-cs-hold-delay-ns`.

### CAN capacity configuration — `migration-4.4`

The generic `CONFIG_CAN_MAX_FILTER`, `CONFIG_CAN_MAX_STD_ID_FILTER`, and `CONFIG_CAN_MAX_EXT_ID_FILTER` options are removed; configure the driver-specific limit, such as `CONFIG_CAN_MCUX_FLEXCAN_MAX_FILTERS` or the STM32 BXCAN/FDCAN standard and extended filter limits. FlexCAN's `CONFIG_CAN_MAX_MB` likewise moves to the per-instance `number-of-mb` Devicetree property.

### CAN driver settings — `migration-4.4`

Rename `CONFIG_CAN_MCUX_MCAN` to `CONFIG_CAN_NXP_LPC_MCAN`. A `ti,tcan4x5x` node must set `ti,nwkrq-voltage-vio` to retain the former VIO default, while an `nxp,flexcan` `clk-source` now selects between the named `clksrc0` and `clksrc1` inputs.

### NXP includes and system timers — `migration-4.4`

NXP ARM DTSI includes move into family directories, for example `<nxp/nxp_rt1060.dtsi>` becomes `<nxp/imxrt/nxp_rt1060.dtsi>`. Boards using `CONFIG_MCUX_LPTMR_TIMER` must select the timer with `/chosen/zephyr,system-timer = &lptmr0`.

### NXP FlexSPI NOR topology — `migration-4.4`

An `nxp,imx-flexspi-nor` node is now a controller containing a `soc-nv-flash` child; move erase/write sizes and partitions to the child and add `ranges` to the controller. Point `zephyr,flash` at the child and `zephyr,flash-controller` at the controller.

### STM32 SPI and interrupt sizing — `migration-4.4`

`CONFIG_SPI_STM32_USE_HW_SS` is removed: `cs-gpios` or `st,soft-nss` selects Soft NSS, and their absence selects Hard NSS. SPI pins now default to `very-high-speed` slew and may need an overlay to reduce power, while auto-derived `CONFIG_NUM_IRQS` may need an explicit larger value for IRQs used only through `IRQ_CONNECT()`.

### MCXC242 asynchronous UART — `4.4.2`

The MCXC242 LPUART driver now supports DMA-backed operation through Zephyr's asynchronous UART API.

## Ethernet hardware and PHYs

### Silabs Gecko Ethernet properties — `migration-4.1`

Gecko Ethernet properties `location-phy_mdc`, `location-phy_mdio`, `location-phy_pwr_enable`, `location-phy_reset`, and `location-phy_interrupt` become fully hyphenated `location-phy-*` names. The `location-rmii_*` properties for refclk, CRS/DV, TXD0/1, TX enable, RXD0/1, and RX error move to the corresponding `location-phy-*` names.

### STM32 Ethernet PHY configuration — `migration-4.2`

STM32 Ethernet no longer uses `ETH_STM32_HAL_MII`; select the interface with the devicetree `phy-connection-type` property and provide a required `phy-handle`. The old STM32 PHY address, carrier-check, autonegotiation, speed, and duplex Kconfigs are removed because those settings now belong to the Ethernet PHY API.

### Ethernet reset and checksum properties — `migration-4.3`

An active-low `microchip,vsc8541` reset must now carry `GPIO_ACTIVE_LOW` in `reset-gpios`. Xilinx GEM checksum offload now defaults on and replaces `rx-checksum-offload` and `tx-checksum-offload` with opt-out properties `disable-rx-checksum-offload` and `disable-tx-checksum-offload`; QEMU targets always disable it.

### Ethernet bus width and PHY advertisement — `migration-4.3`

Remove the obsolete Xilinx GEM `amba-ahb-dbus-width` property because the driver discovers it at runtime. `nxp,enet-mac` and `xlnx,gem` no longer constrain PHY speed and duplex during initialization; use the PHY's `default-speeds` property when the MAC supports only a subset of advertised PHY speeds.

### STM32U5 OTG HS PHY clock — `migration-4.3`

`st,stm32u5-otghs-phy` nodes must set the new `clock-reference` property to select SYSCFG OTG HS PHY CLKSEL consistently with the RCC OTG HS kernel-clock selection.

### Ethernet MAC provisioning — `migration-4.4`

Drivers adopting `net_eth_mac_config` now obtain MAC addresses from a child of `nvmem-layout`; SAM GMAC's `CONFIG_ETH_SAM_GMAC_MAC_I2C_*` options and `mac-eeprom` property are removed. On STM32, `zephyr,random-mac-address` now generates all six bytes and `local-mac-address` is used as written, rather than retaining an ST OUI.

### Ethernet PHY bindings — `migration-4.4`

The `ethernet-phy` `fixed-link` property is removed; use an `ethernet-phy-fixed-link` node with `default-speeds`. `microchip,ksz8081` reset GPIOs now use active-low semantics, `microchip,lan865x` must point `phy-handle` at its PHY node, and removal of `CONFIG_NET_DSA_DEPRECATED` also removes the unmigrated KSZ8463, KSZ8794, and KSZ8863 drivers.

### Ethernet initialization and offload — `migration-4.4`

`CONFIG_ETH_INIT_PRIORITY` now defaults to 60 and supplies the PHY, MDIO, and applicable PTP defaults. Checksum-capable out-of-tree drivers must select `CONFIG_NET_CHECKSUM_OFFLOAD_SUPPORTED`; applications enable the feature with `CONFIG_NET_CHECKSUM_OFFLOAD`.

### MDIO lifecycle — `migration-4.4`

`mdio_bus_enable()` and `mdio_bus_disable()` are removed because MDIO drivers now manage bus state internally.

### Selective Ethernet statistics — `4.4.0`

`ethernet_stats_type` and the optional `get_stats_type` callback in `ethernet_api` let callers request common, vendor, or all statistics without forcing drivers to query expensive vendor firmware data.

## Flash, memory, and miscellaneous hardware

### SCMI firmware interface — `4.0.0`

Zephyr gains initial Arm SCMI support for subsets of clock and pin-control commands over shared-memory and mailbox transports.

### Raspberry Pi and STM32 configuration — `migration-4.1`

Rename `CONFIG_SOC_SERIES_RP2XXX` to `CONFIG_SOC_SERIES_RP2040`. STM32 `st,adc-sequencer` and `st,adc-clock-source` properties now take strings instead of integer values.

### Silabs Series 2 pin control — `migration-4.1`

Series 2 devices use the new `silabs,dbus-pinctrl` driver, with signal macros from a SoC binding header and GPIO electrical properties expressed in devicetree groups:

```devicetree
group0 {
    pins = <I2C0_SDA_PD2>, <I2C0_SCL_PD3>;
    drive-open-drain;
    bias-pull-up;
};
```

### Other removed core interfaces — `4.1.0`

Replace `CONFIG_PM_DEVICE_RUNTIME_EXCLUSIVE` with `CONFIG_PM_DEVICE_SYSTEM_MANAGED` and `z_arch_esf_t` with `struct arch_esf`. `z_pm_save_idle_exit()`, `CONFIG_WIFI_NM_WPA_SUPPLICANT_CRYPTO`, `CONFIG_NET_PKT_BUF_DATA_POOL_SIZE`, and `CONFIG_NET_TCP_ACK_TIMEOUT` are removed.

### Renesas RA flash naming — `migration-4.2`

Rename `CONFIG_RA_FLASH_HP` to `CONFIG_SOC_FLASH_RENESAS_RA_HP` and `CONFIG_FLASH_RA_WRITE_PROTECT` to `CONFIG_FLASH_RENESAS_RA_HP_WRITE_PROTECT`; `CONFIG_DUAL_BANK_MODE` is removed. The generic `renesas,ra-nv-flash` binding is split into `renesas,ra-nv-code-flash` and `renesas,ra-nv-data-flash`.

### nPM1300 to nPM13xx migration — `migration-4.2`

GPIO, LED, MFD, regulator, sensor-charger, and watchdog headers, APIs, defines, and Kconfigs move from `NPM1300`/`npm1300` names to `NPM13XX`/`npm13xx`. Regulator rail GPIOs no longer reference a GPIO controller: replace a value such as `enable-gpios = <&pmic_gpios 3 GPIO_ACTIVE_LOW>;` with `enable-gpio-config = <3 GPIO_ACTIVE_LOW>;`.

### STM32 DCMI and external memories — `migration-4.2`

STM32 DCMI sensor-interface settings move to endpoint-based `video-interfaces.yaml` bindings, and `capture-rate` is replaced by `video_set_frmival()`. STM32 xSPI/oSPI/qSPI memory nodes now separate mapping and capacity: for a 512-Mbit device use `reg = <0>;` and `size = <DT_SIZE_M(512)>;`, with the mapping address supplied by the SoC controller node.

### Modbus serial settings — `migration-4.2`

Rename `modbus_serial_param.client_stop_bits` to `stop_bits`. Nonstandard stop-bit settings are disabled unless `CONFIG_MODBUS_NONCOMPLIANT_SERIAL_MODE` is enabled.

### Firmware-loader and RAM-load flows — `4.2.0`

Sysbuild can compose a firmware-loader image with `SB_CONFIG_MCUBOOT_MODE_FIRMWARE_UPDATER`, `SB_CONFIG_FIRMWARE_LOADER`, and an image selection such as `SB_CONFIG_FIRMWARE_LOADER_IMAGE_SMP_SVR`; single-application RAM loading uses `SB_CONFIG_MCUBOOT_MODE_SINGLE_APP_RAM_LOAD`. MCUmgr image management supports firmware-updater mode through `CONFIG_MCUBOOT_BOOTLOADER_MODE_FIRMWARE_UPDATER`, and OS reset requests can carry a retention boot mode with `CONFIG_MCUMGR_GRP_OS_RESET_BOOT_MODE`.

### In-memory core dumps — `4.2.0`

`CONFIG_DEBUG_COREDUMP_BACKEND_IN_MEMORY` and `CONFIG_DEBUG_COREDUMP_BACKEND_IN_MEMORY_SIZE` retain a core dump in RAM. Minimal Cortex-M memory dumps now include the thread stack top by default through `CONFIG_DEBUG_COREDUMP_THREAD_STACK_TOP`.

### AXP MFD and nRF ETR configuration — `migration-4.3`

The combined `MFD_AXP192_AXP2101` symbol is removed; select `MFD_AXP192` or `MFD_AXP2101` for the corresponding device. The nRF ETR driver moved under debug: rename `NRF_ETR*` symbols to `DEBUG_NRF_ETR*` and explicitly enable `DEBUG_DRIVER`.

### Firmware-update management controls — `4.3.0`

hawkBit gains no-reboot, confirm-on-init, and erase-secondary-on-confirm controls. MCUmgr adds a UDP/DTLS transport with `CONFIG_MCUMGR_TRANSPORT_UDP_DTLS` and can permit confirmation of a non-active slot with `CONFIG_MCUMGR_GRP_IMG_ALLOW_CONFIRM_NON_ACTIVE_SLOT`.

### NVMEM subsystem — `4.3.0`

The new `CONFIG_NVMEM` subsystem exposes named or indexed Devicetree cells through `NVMEM_CELL_GET_BY_NAME`/`NVMEM_CELL_GET_BY_IDX` variants and provides readiness, read, and write APIs. `CONFIG_NVMEM_EEPROM` supplies an EEPROM-backed implementation.

### Operational-amplifier subsystem — `4.3.0`

`CONFIG_OPAMP` introduces a standard op-amp device API with initial Devicetree configuration and vendor-specific runtime configuration; initial compatibles are `nxp,opamp` and `nxp,opamp-fast`.

### Protocol helper APIs — `4.3.0`

MQTT-SN gains APIs to predefine topics, define short topics, and update Will topics and messages. LwM2M adds `lwm2m_set_cache_filter()` for cache filtering, while `CONFIG_NET_CONFIG_CLOCK_SNTP_SET_RTC` lets network time synchronization update the RTC.

### Generated-header dependencies — `migration-4.4`

`kernel.h` now includes the generated `zephyr/heap_constants.h`. A downstream CMake library that races its generation must add `add_dependencies(${lib} zephyr_generated_headers)`.

### SoC Kconfig renames — `migration-4.4`

Nordic series symbols such as `CONFIG_SOC_SERIES_NRF52X`, `CONFIG_SOC_SERIES_NRF54HX`, and `CONFIG_SOC_SERIES_NRF91X` lose their trailing `X`; SiFive Freedom symbols drop `SIFIVE_FREEDOM` from names such as `CONFIG_SOC_SERIES_SIFIVE_FREEDOM_FU700`; and `CONFIG_SOC_SERIES_CH32V00X` becomes `CONFIG_SOC_SERIES_QINGKE_V2C`.

### Mapped code partitions — `migration-4.4`

Boards using `CONFIG_USE_DT_CODE_PARTITION` or `zephyr,code-partition` should migrate the selected node to `compatible = "zephyr,mapped-partition"`. Its unit address supplies the mapped address, nested partitions use `ranges` without `fixed-subpartitions`, and `CONFIG_FLASH_LOAD_OFFSET`/`CONFIG_FLASH_LOAD_SIZE` cannot be used with it.

### STM32N6 security state — `migration-4.4`

STM32N6 projects must now explicitly select either `CONFIG_TRUSTED_EXECUTION_SECURE` or `CONFIG_TRUSTED_EXECUTION_NON_SECURE` according to the state in which Zephyr executes.

### NXP LPTMR filtering — `migration-4.4`

`nxp,lptmr` no longer treats `prescale-glitch-filter = <0>` as bypass; use the boolean `prescale-glitch-filter-bypass;`, and keep active filter values in the range 0–15. In time-counter mode the divisor is `2^(N + 1)`; in pulse-counter mode a change is recognized after `2^N` rising edges and zero is not a valid active filter.

### i.MX GPT run mode — `migration-4.4`

`nxp,imx-gpt` now defaults to `run-mode = "restart"`, which resets the counter at Compare Channel 1 alarms. Set `run-mode = "free-run";` to preserve continuous pre-4.4 counting.

### NXP EDMA discriminator — `migration-4.4`

`CONFIG_DMA_MCUX_EDMA_V5` is removed now that EDMA v4 and v5 share one driver path; out-of-tree conditionals should use the unified `DMA_MCUX_EDMA_V4` handling.

### EEPROM target access — `migration-4.4`

I2C EEPROM target code should replace deprecated `eeprom_target_program()` with `eeprom_target_read_data()` and `eeprom_target_write_data()`, which take explicit offset and length arguments.

### ESP32-S3 LCD_CAM topology — `migration-4.4`

`espressif,esp32-lcd-cam` now represents only the common peripheral and contains `espressif,esp32-lcd-cam-dvp` and `espressif,esp32-lcd-cam-mipi-dbi` child nodes. Move camera properties into the DVP child and point `zephyr,camera` at that child.

### Infineon and interrupt-controller names — `migration-4.4`

Infineon CAT1 Kconfigs and bindings lose `CAT1`, for example `CONFIG_*_INFINEON_CAT1` becomes `CONFIG_*_INFINEON` and `infineon,cat1-adc` becomes `infineon,adc`; its CYW43xx HCI UART symbols become `CONFIG_BT_HCI_UART_INFINEON` and `infineon,bt-hci-uart`. Rename `swerv,pic` to `cdns,swerv-pic`.

### PSRAM refresh configuration — `migration-4.4`

`st,stm32-xspi-psram` and `st,stm32-ospi-psram` nodes must set `st,refresh` in memory-clock cycles; their hard-coded defaults are gone.

### Flash commands and integrity — `migration-4.4`

The `flash erase` and `flash write` shell commands now require an explicit device argument. Both `CONFIG_FLASH_AREA_CHECK_INTEGRITY_MBEDTLS` and `CONFIG_FLASH_AREA_CHECK_INTEGRITY_PSA` are removed because the integrity path no longer has a selectable crypto backend.

### Removed legacy options and moved SBC header — `migration-4.4`

`CONFIG_JWT_SIGN_RSA_LEGACY` and `CONFIG_HAWKBIT_DDI_NO_SECURITY` are removed. Libsbc moves under Bluetooth, so include its header from `zephyr/bluetooth/sbc.h`.

### CTF event identifiers — `migration-4.4`

CTF metadata event IDs widen from 8 to 16 bits, permitting 65,535 events but making new traces incompatible with consumers expecting the old 8-bit format.

### Pressure-based CPU frequency policy — `4.4.0`

The CPU frequency subsystem can select `CONFIG_CPU_FREQ_POLICY_PRESSURE` to scale frequency from scheduler load pressure.

### Additional symbol migrations — `4.4.0`

Replace `I2S_OPT_BIT_CLK_MASTER`/`I2S_OPT_FRAME_CLK_MASTER` with `I2S_OPT_BIT_CLK_CONTROLLER`/`I2S_OPT_FRAME_CLK_CONTROLLER`, and `I2S_OPT_BIT_CLK_SLAVE`/`I2S_OPT_FRAME_CLK_SLAVE` with `I2S_OPT_BIT_CLK_TARGET`/`I2S_OPT_FRAME_CLK_TARGET`; also replace `CONFIG_XOPEN_STREAMS` with `CONFIG_XSI_STREAMS` and `CONFIG_CTR_DRBG_CSPRNG_GENERATOR` with `CONFIG_PSA_CSPRNG_GENERATOR`. Correct `BT_HCI_LE_SUPERVISON_TIMEOUT_MIN`/`BT_HCI_LE_SUPERVISON_TIMEOUT_MAX` to `BT_HCI_LE_SUPERVISION_TIMEOUT_MIN`/`BT_HCI_LE_SUPERVISION_TIMEOUT_MAX`.

### STM32U5 voltage scaling — `4.4.0`

The `voltage-scale` property on `st,stm32u5-pwr` selects the voltage scale manually, notably allowing USB operation at lower system clock frequencies.

### Signal-only IPM callbacks — `4.4.0`

Mailbox-backed IPM now supports signal-only messages; callbacks must accept a `NULL` payload when the mailbox supplies no data buffer.
