# Drivers and Hardware

## Common, ROM, and Clock Headers

### Variadic macros

ESP-Common variadic helpers gained an `ESP_` prefix in 5.4 to avoid name
collisions. Replace `__VA_NARG__` and related forms with names such as
`ESP_VA_NARG`.

### ROM includes

Include target-specific ROM headers by header name, not a chip-relative path:

```c
#include "efuse.h"  // not "esp32s3/rom/efuse.h"
```

Deprecated target-specific `rom/miniz.h` headers have been removed.

The target-specific `{IDF_TARGET_NAME}/rtc.h` is deprecated in 5.5. Include:

```c
#include "esp_rtc_time.h"
```

### Private peripheral control

`driver/periph_ctrl.h` and `driver/rtc_cntl.h` are removed in 6.0. Their
replacements, `esp_private/periph_ctrl.h` and `esp_private/rtc_ctrl.h`, are
private interfaces and should not be treated as stable application APIs.

## Touch and TWAI

### Capacitive touch

The redesigned 5.5 driver is supplied by `esp_driver_touch_sens` and included
through `driver/touch_sens.h`. The legacy `driver/touch_sensor.h` remains but
warns by default. `CONFIG_TOUCH_SUPPRESS_DEPRECATE_WARN` suppresses that warning
while a migration is staged.

### Event-driven TWAI

Use `esp_driver_twai`, `esp_twai.h`, and `esp_twai_onchip.h`. The driver
supports callback registration, runtime bitrate and filter changes, multiple
controllers, and ESP32-C5 TWAI FD.

- Replace `twai_read_alerts` with `on_state_change` and `on_error` callbacks.
- Call `twai_node_receive_from_isr` only from `on_rx_done`.
- There are no replacements for `twai_clear_transmit_queue` or
  `twai_clear_receive_queue`.
- Do not mix this driver with legacy `driver/twai.h`; doing so can crash or
  reboot. `CONFIG_TWAI_SKIP_LEGACY_CONFLICT_CHECK` only suppresses the startup
  compatibility check.

## Ethernet

`esp_eth_phy_802_3_reset_hw` now takes only the PHY object. Removed `ETH_RMII_*`
Kconfig settings move into `eth_esp32_emac_config_t.clock_config.rmii`; the
default EMAC configuration still works without customization.

```c
eth_esp32_emac_config_t emac = ETH_ESP32_EMAC_DEFAULT_CONFIG();
emac.clock_config.rmii.clock_mode = EMAC_CLK_OUT; /* or EMAC_CLK_EXT_IN */
emac.clock_config.rmii.clock_gpio = 0;
```

IP101, LAN87xx, RTL8201, DP83848, KSZ80xx, DM9051, KSZ8851SNL, and W5500
PHY/MAC drivers moved to registry components. Replace the former PTP
`esp_eth_ioctl` commands with the new PTP API.

## Legacy Peripheral Driver Migration

The legacy ADC, MCPWM, timer-group, I2S, PCNT, RMT, DAC, temperature-sensor,
and sigma-delta drivers are removed in 6.0. Use these replacements:

| Legacy area | Replacement |
| --- | --- |
| ADC | `esp_adc` |
| MCPWM | `esp_driver_mcpwm` |
| timer group | `driver/gptimer.h` |
| I2S | `driver/i2s_std.h`, `driver/i2s_pdm.h`, or `driver/i2s_tdm.h` |
| PCNT | `driver/pulse_cnt.h` |
| RMT | `driver/rmt_tx.h`, `driver/rmt_rx.h`, and `driver/rmt_encoder.h` |
| DAC | `driver/dac_oneshot.h`, `driver/dac_continuous.h`, or `driver/dac_cosine.h` |
| temperature sensor | `driver/temperature_sensor.h` |
| sigma-delta | `driver/sdm.h` |

The sigma-delta duty setter is `sdm_channel_set_pulse_density`. Removed I2S
ADC-mode functions have no direct legacy path.

## Shared GPIO and MCPWM

Driver `io_loop_back` fields are removed. Assigning the same GPIO to multiple
driver objects now enables loopback directly.

- Replace RMT and MCPWM `io_od_mode` settings with `gpio_od_enable`.
- Replace MCPWM pull settings with `gpio_set_pull_mode`.
- Account for the MCPWM group clock divider now defaulting to `1`.

The variadic MCPWM generator-action APIs are removed. Call a typed singular
setter such as `mcpwm_generator_set_action_on_compare_event` once for every
`mcpwm_gen_timer_event_action_t` action.

## GPIO Wakeup and ROM APIs

The deep-sleep-only GPIO wakeup names are removed. Use:

- `esp_sleep_enable_gpio_wakeup_on_hp_periph_powerdown`
- `gpio_wakeup_enable_on_hp_periph_powerdown_sleep`
- `gpio_wakeup_disable_on_hp_periph_powerdown_sleep`
- `esp_sleep_gpio_wake_up_mode_t`
- `GPIO_IS_HP_PERIPH_PD_WAKEUP_VALID_IO`

GPIO ROM functions now carry a `rom_` prefix. `gpio_iomux_input` and
`gpio_iomux_output` are private replacements for the former IOMUX names.
`gpio_uninstall_isr_service` now returns `esp_err_t`; check or intentionally
discard the result.

## LEDC and UART

Replace `ledc_timer_set` with `ledc_timer_config` or `ledc_set_freq`. RTC8M
LEDC symbols become `LEDC_SLOW_CLK_RC_FAST` and `LEDC_USE_RC_FAST_CLK`.
Applications should use callbacks rather than `ledc_isr_register` or
`ledc_channel_config_t.intr_type`.

Replace `UART_FIFO_LEN` with `UART_HW_FIFO_LEN`. Replace pin symbols from
`soc/uart_channel.h` with their corresponding `soc/uart_pins.h` definitions.

## I2C

The legacy `driver/i2c.h` driver is EOL in 6.0 and scheduled for removal in
7.0. The current slave API is callback-driven, removes `i2c_slave_receive` and
the RAM helpers, and replaces `i2c_slave_transmit` with `i2c_slave_write`.

Master transfers now report a bus NACK as `ESP_ERR_INVALID_RESPONSE`, not
`ESP_ERR_INVALID_STATE`; update error handling and tests.

## DMA

DMA support is in the explicit `esp_driver_dma` component.

- Replace `gdma_new_channel` with `gdma_new_ahb_channel` or
  `gdma_new_axi_channel`.
- Replace alignment fields with `dma_burst_size`.
- Replace `esp_dma_capable_malloc` and `esp_dma_capable_calloc` with heap-cap
  allocation using `MALLOC_CAP_DMA | MALLOC_CAP_CACHE_ALIGNED`.
- `GDMA_ISR_IRAM_SAFE` and SDMMC DMA-query fields/functions are removed;
  interrupt and DMA configuration belongs to each channel or owning driver.

## LCD and Color Formats

LCD GPIO fields now require `gpio_num_t`; alignment fields become
`dma_burst_size`. Replace `color_space` and `rgb_endian` with `rgb_ele_order`,
and express removed legacy color types as `esp_color_fourcc_t`, for example
`ESP_COLOR_FOURCC_RGB565`.

- Display control: `esp_lcd_panel_disp_on_off`.
- RGB completion callback: `on_frame_buf_complete`.
- DPI/RGB input format: `in_color_format`.
- YUV conversion: the `*_set_yuv_conversion` APIs with
  `esp_lcd_color_conv_yuv_config_t`.
- DMA2D: `esp_lcd_dpi_panel_enable_dma2d`.

LCD I/O no longer supports the legacy I2C master bus.

## SPI, PSRAM, and Flash

`CONFIG_SPI_MASTER_IN_IRAM` is available only with
`CONFIG_FREERTOS_IN_IRAM`. Deprecated HSPI/VSPI IOMUX macros are gone.

Replace `esp_spiram.h` with `esp_psram.h`, `esp_spi_flash.h` with
`spi_flash_mmap.h`, and `spi_flash_*_counters` with
`esp_flash_*_counters`. `esp_flash_speed_t` is removed.

Custom flash drivers must use the semi-public `esp_flash_chips/` headers and
handle the new `flags` argument to `esp_flash_os_functions_t.start`.

Flash suspend support for XMC-C parts was removed in 5.4 because some devices
need a 1 ms interval between resume and the next command. It can be forced with
`CONFIG_SPI_FLASH_FORCE_ENABLE_XMC_C_SUSPEND`, with the associated device risk.
