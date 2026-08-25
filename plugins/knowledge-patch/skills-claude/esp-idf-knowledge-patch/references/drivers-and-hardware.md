# Drivers and Hardware

## Flash behavior (5.4)

Automatic flash suspend support for XMC-C series parts is removed because some
devices require a 1 ms delay between resume and the next command. If hardware
validation proves the device safe, force it with
`CONFIG_SPI_FLASH_FORCE_ENABLE_XMC_C_SUSPEND`.

## Touch and TWAI (5.5)

The redesigned capacitive-touch driver is the `esp_driver_touch_sens`
component, included as `driver/touch_sens.h`. The legacy
`driver/touch_sensor.h` remains but warns by default; suppress that migration
warning with `CONFIG_TOUCH_SUPPRESS_DEPRECATE_WARN` only while porting.

The event-driven TWAI driver is `esp_driver_twai`, with `esp_twai.h` and
`esp_twai_onchip.h`. It supports callbacks, runtime bitrate/filter changes,
multiple controllers, and ESP32-C5 TWAI FD.

- Replace `twai_read_alerts` with `on_state_change` and `on_error` callbacks.
- Call `twai_node_receive_from_isr` only from `on_rx_done`.
- There are no replacements for `twai_clear_transmit_queue` or
  `twai_clear_receive_queue`; redesign queue-reset behavior.
- Do not mix this driver with the legacy `driver/twai.h` implementation. The
  combination can crash or reboot. `CONFIG_TWAI_SKIP_LEGACY_CONFLICT_CHECK`
  only suppresses the startup compatibility check.

## Removed legacy drivers (6.0)

| Legacy subsystem | Current interface |
| --- | --- |
| ADC | `esp_adc` |
| MCPWM | `esp_driver_mcpwm` |
| Timer group | `driver/gptimer.h` |
| I2S | `driver/i2s_std.h`, `driver/i2s_pdm.h`, `driver/i2s_tdm.h` |
| PCNT | `driver/pulse_cnt.h` |
| RMT | `driver/rmt_tx.h`, `driver/rmt_rx.h`, `driver/rmt_encoder.h` |
| DAC | `driver/dac_oneshot.h`, `dac_continuous.h`, `dac_cosine.h` |
| Temperature sensor | `driver/temperature_sensor.h` |
| Sigma-delta | `driver/sdm.h` |

The sigma-delta duty operation is `sdm_channel_set_pulse_density`. Removed I2S
ADC-mode functions have no direct legacy migration path.

`driver/periph_ctrl.h` and `driver/rtc_cntl.h` are removed. Their replacements,
`esp_private/periph_ctrl.h` and `esp_private/rtc_ctrl.h`, are private and are
not stable application APIs.

## GPIO, MCPWM, LEDC, and UART (6.0)

Assigning one GPIO to multiple driver objects enables loopback directly, so
driver `io_loop_back` fields are removed. Replace RMT and MCPWM `io_od_mode`
with `gpio_od_enable`, and replace MCPWM pull fields with
`gpio_set_pull_mode`. The MCPWM group clock divider defaults to `1`.

Variadic MCPWM generator-action APIs are removed. Call typed singular setters,
such as `mcpwm_generator_set_action_on_compare_event`, once for each
`mcpwm_gen_timer_event_action_t` action.

Deep-sleep-only GPIO wakeup names are replaced by:

- `esp_sleep_enable_gpio_wakeup_on_hp_periph_powerdown`
- `gpio_wakeup_enable_on_hp_periph_powerdown_sleep`
- `gpio_wakeup_disable_on_hp_periph_powerdown_sleep`
- `esp_sleep_gpio_wake_up_mode_t`
- `GPIO_IS_HP_PERIPH_PD_WAKEUP_VALID_IO`

GPIO ROM functions use the `rom_` prefix. `gpio_iomux_input` and
`gpio_iomux_output` are private replacements for the former IOMUX names.
`gpio_uninstall_isr_service` now returns `esp_err_t`; check it.

Replace `ledc_timer_set` with `ledc_timer_config` or `ledc_set_freq`. RTC8M
clock symbols become `LEDC_SLOW_CLK_RC_FAST` and `LEDC_USE_RC_FAST_CLK`.
Prefer callbacks over `ledc_isr_register` or
`ledc_channel_config_t.intr_type`. Replace `UART_FIFO_LEN` with
`UART_HW_FIFO_LEN`, and take UART pin symbols from `soc/uart_pins.h` instead of
`soc/uart_channel.h`.

## I2C and DMA (6.0)

The legacy `driver/i2c.h` API is EOL and scheduled for removal in 7.0. The
current slave API is callback-driven: `i2c_slave_receive` and the RAM helpers
are removed, while `i2c_slave_transmit` becomes `i2c_slave_write`. A master bus
NACK now returns `ESP_ERR_INVALID_RESPONSE`, not `ESP_ERR_INVALID_STATE`.

DMA is an explicit `esp_driver_dma` dependency. Replace `gdma_new_channel` with
`gdma_new_ahb_channel` or `gdma_new_axi_channel`; replace alignment fields with
`dma_burst_size`. Replace `esp_dma_capable_malloc` and its calloc variant with
heap-cap allocation using `MALLOC_CAP_DMA | MALLOC_CAP_CACHE_ALIGNED`.
`GDMA_ISR_IRAM_SAFE` and SDMMC DMA-query fields/functions are removed because
interrupt and DMA setup belongs to the channel or owning driver.

## LCD and color formats (6.0)

- LCD GPIO fields now use `gpio_num_t`, and alignment fields are
  `dma_burst_size`.
- `color_space` and `rgb_endian` become `rgb_ele_order`.
- Express removed color types as `esp_color_fourcc_t`, for example
  `ESP_COLOR_FOURCC_RGB565`.
- Use `esp_lcd_panel_disp_on_off` for display control and
  `on_frame_buf_complete` for RGB completion callbacks.
- DPI/RGB input format is `in_color_format`.
- Configure YUV with the `*_set_yuv_conversion` APIs and
  `esp_lcd_color_conv_yuv_config_t`.
- Enable DMA2D with `esp_lcd_dpi_panel_enable_dma2d`.
- LCD I/O no longer supports the legacy I2C master bus.

## SPI, PSRAM, and flash (6.0)

`CONFIG_SPI_MASTER_IN_IRAM` is available only with
`CONFIG_FREERTOS_IN_IRAM`. Deprecated HSPI/VSPI IOMUX macros are removed.

| Old interface | Replacement |
| --- | --- |
| `esp_spiram.h` | `esp_psram.h` |
| `esp_spi_flash.h` | `spi_flash_mmap.h` |
| `spi_flash_*_counters` | `esp_flash_*_counters` |

`esp_flash_speed_t` is removed. Custom flash drivers use the semi-public
`esp_flash_chips/` headers and must handle the new `flags` argument passed to
`esp_flash_os_functions_t.start`.

ULP touch channel IDs use `int` instead of `touch_pad_t`. Likewise,
`i2s_port_t` becomes `int`, while the `I2S_NUM_*` compatibility names remain
macros.
