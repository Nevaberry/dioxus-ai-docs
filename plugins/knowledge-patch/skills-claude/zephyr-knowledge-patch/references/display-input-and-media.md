# Display, Input, Audio, and Video

Entries are grouped by developer task and alphabetized by topic. The
parenthetical identifier records the exact source batch for each item.

## CAP12xx input binding (migration-4.1)

Change `microchip,cap1203` to `microchip,cap12xx`; the number of channels now comes from the length of `input-codes`. `CONFIG_INPUT_CAP1203_POLL` is removed—presence of `int-gpios` selects interrupt mode, otherwise polling is used—and `CONFIG_INPUT_CAP1203_PERIOD` becomes the `poll-interval-ms` property; interrupt mode also supports `repeat`.

## CFB coordinate types (migration-4.4)

`cfb_print()`, `cfb_invert_area()`, and `cfb_position()` now use signed coordinate values; callers and matching declarations must update their types.

## Display binding migrations (migration-4.4)

Rename `ilitek,ili9806e-dsi` to `ilitek,ili9806e`, drop the `fb` suffix from the SSD1306/SSD1309/SSD1327 compatibles, and rename `CONFIG_SSD1327` to `CONFIG_SSD1327_5`. STM32 LTDC nodes must specify `PANEL_PIXEL_FORMAT_RGB_888`, while `waveshare,7inch-dsi-lcd-c` and its Kconfig become `waveshare,dsi2dpi` and `CONFIG_WAVESHARE_DSI2DPI`.

## Display format corrections (migration-4.3)

The display sample now distinguishes RGB565 from BGR565, so remove format-swapping workarounds derived from the old sample. SSD1363 binding properties replace `greyscale` with `grayscale`.

## Display pixel formats (migration-4.4)

ILI9XXX Devicetree values move from `ILI9XXX_PIXEL_FORMAT_*` to `PANEL_PIXEL_FORMAT_*`. Byte-swapped RGB565 is renamed from `PIXEL_FORMAT_BGR_565`/`PANEL_PIXEL_FORMAT_BGR_565` to `PIXEL_FORMAT_RGB_565X`/`PANEL_PIXEL_FORMAT_RGB_565X`, with matching SDL and ST7789V Kconfig renames.

## Display, PWM, and haptics notifications (4.4.0)

Displays gain `display_register_event_cb()` and `display_unregister_event_cb()`. `CONFIG_PWM_EVENT` adds `pwm_event_callback`, `pwm_init_event_callback()`, `pwm_add_event_callback()`, and `pwm_remove_event_callback()`, while haptics drivers can report `haptics_error_type` through `haptics_register_error_callback()`.

## ESP32-S3 LCD_CAM topology (migration-4.4)

`espressif,esp32-lcd-cam` now represents only the common peripheral and contains `espressif,esp32-lcd-cam-dvp` and `espressif,esp32-lcd-cam-mipi-dbi` child nodes. Move camera properties into the DVP child and point `zephyr,camera` at that child.

## FT8xx multi-instance API (migration-4.1)

FT8xx driver functions now take an additional `const struct device *` argument, except for the single-instance compatibility interface in `ft8xx_reference_api.h`. `ft8xx_register_int()` and its handler also gain a `void *user_data` argument.

## GPIO and input binding changes (migration-4.4)

LiteX GPIO removes `port-is-output` and derives supported direction modes from `reg-names`; Renesas RZ GPIO `irqs` entries now use an interrupt-controller phandle followed by the pin, such as `<&tint7 3>`. The CST816S family becomes CST8xx across `hynitron,cst8xx`, `CONFIG_INPUT_CST8XX*`, and `CST8XX_*`.

## Imported video buffers and format helpers (4.4.0)

`video_import_buffer()` accepts externally supplied video storage, with named-region pools selected by `CONFIG_VIDEO_BUFFER_POOL_ZEPHYR_REGION` and `CONFIG_VIDEO_BUFFER_POOL_ZEPHYR_REGION_NAME`; helpers such as `VIDEO_FMT_IS_BAYER`, `VIDEO_FMT_IS_RGB`, `VIDEO_FMT_IS_YUV`, `VIDEO_FOREACH_BAYER`, `VIDEO_FOREACH_RGB`, and `VIDEO_FOREACH_YUV` classify and enumerate layouts.

## Input and video frameworks (4.0.0)

GPIO keys gain a `no-disconnect` property for power-managed GPIO controllers, and touchscreens gain common screen-size, inversion, and XY-swap properties. Video gains frame-rate control, partial-frame transfer through `video_buffer.line_offset`, and multi-heap allocation through `CONFIG_VIDEO_BUFFER_USE_SHARED_MULTI_HEAP`.

## Input callbacks and analog axes (migration-4.0)

`INPUT_CALLBACK_DEFINE` gains a `user_data` pointer argument, and its callback gains a matching `void *user_data` parameter; pass `NULL` to retain the old behavior. The analog-axis property `invert` is renamed to `invert-input`, alongside the new `invert-output`.

## LVGL flush and buffer symbols (migration-4.1)

Rename `CONFIG_LV_Z_FLUSH_THREAD_PRIO` to `CONFIG_LV_Z_FLUSH_THREAD_PRIORITY`; its value is now an absolute priority rather than a cooperative priority. Also rename `CONFIG_LV_Z_VBD_CUSTOM_SECTION` to `CONFIG_LV_Z_VDB_CUSTOM_SECTION`.

## LVGL monochrome and Modulino LEDs (migration-4.3)

LVGL corrects the swapped `PIXEL_FORMAT_MONO10` and `PIXEL_FORMAT_MONO01` handling; remove old black/white inversion workarounds. Rename the LED-strip compatible `arduino,modulino-smartleds` to `arduino,modulino-pixels`.

## LVGL multiple displays (4.2.0)

The Zephyr LVGL integration now supports multiple simultaneous displays with correct input-device-to-display binding. It also supports L8/Y8 display formats and optional monochrome hardware inversion through `CONFIG_LV_Z_COLOR_MONO_HW_INVERSION`.

## LVGL named memory regions (4.3.0)

LVGL memory pools and VDB buffers can be placed in named Zephyr memory regions through the `CONFIG_LV_Z_MEMORY_POOL_ZEPHYR_REGION*` and `CONFIG_LV_Z_VDB_ZEPHYR_REGION*` settings.

## MIPI DBI display mode (migration-4.1)

The display `mipi-mode` property changes from an integer macro to a string:

```devicetree
mipi-mode = "MIPI_DBI_MODE_SPI_4WIRE";
```

## Nordic comparator inputs (migration-4.3)

The `psel` and `extrefsel` properties of `nordic,nrf-comp` and `nordic,nrf-lpcomp` now take integer `NRF_COMP_AIN*` values; string values are deprecated. The accepted range covers external AIN0–AIN7 plus the internal VDD/2 and VDDH/5 references.

## PCA9685 PWM polarity (migration-4.3)

The `nxp,pca9685` binding removes `invert`; each PWM specifier now has three cells—`channel`, `period`, and `flags`—and uses `PWM_POLARITY_INVERTED` or `PWM_POLARITY_NORMAL`.

## Portable comparator, haptics, and stepper subsystems (4.0.0)

New standard device classes are selected with `CONFIG_COMPARATOR`, `CONFIG_HAPTICS`, and `CONFIG_STEPPER`; comparator and stepper shell support use `CONFIG_COMPARATOR_SHELL` and `CONFIG_STEPPER_SHELL`. Initial bindings include `nordic,nrf-comp`, `nordic,nrf-lpcomp`, `nxp,kinetis-acmp`, `ti,drv2605`, `adi,tmc5041`, and `zephyr,gpio-steppers`.

## STM32 display pixel order (migration-4.2)

The STM32 LTDC driver now uses `PIXEL_FORMAT_BGR565` in place of `PIXEL_FORMAT_RGB565` so the declared format matches the byte order expected by Zephyr.

## Twister display validation (4.3.0)

Twister's display harness can capture target output with a USB video camera and compare frames against prerecorded visual fingerprints.

## USB device and UVC APIs (migration-4.4)

Out-of-tree UDC drivers must stop allocating USB control-transfer buffers because USB device_next now owns them, and TCPC drivers must remove the redundant `tcpc_driver_api.alert_handler_cb` field. Rename `uvc_set_video_dev()` to `uvc_device_init()` and `uvc_add_format()` to `uvc_device_add_format()`, then use the new `uvc_device_enable()` and `uvc_device_shutdown()` lifecycle calls.

## USB MIDI 2.0 (4.1.0)

The new USB MIDI 2.0 device class lets Zephyr devices communicate with MIDI controllers and instruments. Its device compatible is `zephyr,midi2-device`, and `usb-midi2-device` demonstrates it.

## USB Video Class and video controls (4.2.0)

The USB device stack can expose a video source as a UVC device through the `zephyr,uvc-device` compatible and `uvc_set_video_dev()`; the `uvc` sample demonstrates the path. The video API adds selection get/set operations, CSI link-frequency support, V4L2-style base and camera controls, and additional Y10–Y16 and packed Bayer formats.

## USB Video Class negotiation (migration-4.3)

The UVC class no longer configures the source video's frame rate and format. After the host selects them, the application must apply that configuration to the source video device.

## UVC and video-buffer helpers (4.3.0)

USB Video Class applications can register formats with `uvc_add_format()`. The video API adds `video_estimate_fmt_size()` and `video_transfer_buffer()` for format sizing and buffer transfer.

## Video API migration (migration-4.2)

The 8-bit Bayer constants gain an `S` prefix, such as `VIDEO_PIX_FMT_BGGR8` to `VIDEO_PIX_FMT_SBGGR8`. Remove `video_endpoint_id`; supply the new required `video_buf_type` to stream hooks and `video_stream_start()`/`video_stream_stop()`, let the driver set `video_format.pitch`, and pass a single `video_ctrl_query` containing its `dev` field to `video_query_ctrl()`.

Native-simulator video projects must build with `--snippet video-sw-generator`.

## Video API units, controls, and timeouts (migration-4.1)

Video control IDs now match Linux V4L2 names, commonly by dropping the category prefix such as `VIDEO_CID_CAMERA_GAIN` to `VIDEO_CID_GAIN`. Replace byte-returning `video_pix_fmt_bpp()` with bit-returning `video_bits_per_pixel()` and divide by `BITS_PER_BYTE` when computing byte pitches.

`video_buffer_alloc()` and `video_buffer_aligned_alloc()` gain a timeout argument. Driver implementations replace separate `video_stream_start`/`video_stream_stop` hooks with `video_set_stream`; the application-level start and stop APIs remain unchanged.

## Video buffer sizing (migration-4.3)

`video_caps.min_line_count` and `.max_line_count` are removed. Allocate buffers from the new `video_format.size` instead.

## Video buffers and pixel layouts (migration-4.4)

`CONFIG_VIDEO_BUFFER_POOL_SZ_MAX` becomes byte-sized `CONFIG_VIDEO_BUFFER_POOL_HEAP_SIZE`; `CONFIG_VIDEO_HIMAX_HM01B0` becomes `CONFIG_VIDEO_HM01B0`, and `CONFIG_VIDEO_OV7670` becomes `CONFIG_VIDEO_OV767X`. `VIDEO_PIX_FMT_ARGB32` and `VIDEO_PIX_FMT_BGRA32` swap meanings to match their data layouts, and XBGR32, BGRX32, and RGBX32 formats are added.
