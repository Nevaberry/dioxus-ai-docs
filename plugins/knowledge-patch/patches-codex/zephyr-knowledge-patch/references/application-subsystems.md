# Application Subsystems and Services

Use these notes for application-facing services, messaging, observability, shell integration, and reusable utility subsystems.

## Messaging and state

### Stable and heapless Zbus observers — `4.2.0`

Zbus reaches stable API version 1.0.0. Runtime observer nodes can use dynamic, static, or no allocation through `CONFIG_ZBUS_RUNTIME_OBSERVERS_NODE_ALLOC_*`; the no-allocation mode registers caller-provided nodes with `zbus_chan_add_obs_with_node()`.

### Zbus asynchronous listeners and proxy agents — `4.4.0`

`CONFIG_ZBUS_ASYNC_LISTENER` and `ZBUS_ASYNC_LISTENER_DEFINE()` run observers in a workqueue rather than the publisher thread, with queue selection through `zbus_async_listener_set_work_queue()`. Experimental `CONFIG_ZBUS_PROXY_AGENT` and `CONFIG_ZBUS_PROXY_AGENT_IPC`, with `ZBUS_PROXY_AGENT_DEFINE`, `ZBUS_PROXY_ADD_CHAN`, and shadow-channel macros, forward channels across CPU or domain boundaries over IPC.

## Logging, metrics, and shell

### Prometheus metric declarations — `migration-4.1`

Prometheus counters, gauges, histograms, and summaries no longer require a separate `struct prometheus_metric`; the corresponding `PROMETHEUS_*_DEFINE` macro prototypes have changed.

### Rate-limited logging — `4.3.0`

The `LOG_*_RATELIMIT` and `LOG_HEXDUMP_*_RATELIMIT` families rate-limit independently at each call site, using either `CONFIG_LOG_RATELIMIT_INTERVAL_MS` or an explicit rate. `CONFIG_LOG_RATELIMIT` controls the feature and `CONFIG_LOG_RATELIMIT_FALLBACK` selects log-all or drop-all behavior when it is disabled.

### SDHC and shell callbacks — `migration-4.4`

Move `bus_4_bit_support`, `hs200_support`, and `hs400_support` from `sdhc_host_caps` to `sdhc_host_props`. `shell_set_bypass()` and `shell_bypass_cb_t` also gain a user-data pointer.

## Application services and utilities

### zcbor 0.9 generated code — `migration-4.0`

The generic `zcbor_simple_*()` APIs are removed; use `zcbor_bool_*()`, `zcbor_nil_*()`, or `zcbor_undefined_*()`. Regeneration may also capitalize additional C-keyword field names and rename bstr elements that use a `.size` specifier.

### Connector and Nordic UART behavior — `4.2.0`

Boards with Qwiic, Stemma, or Grove I2C connectors now expose the common `zephyr_i2c` devicetree label, allowing connectorized I2C shields to work across branding through `west build --shield`. The Nordic UART receiver mode that uses an extra timer is no longer deprecated because it is the reliable receive path without hardware flow control.

### OCPP 1.6 charge points — `4.3.0`

`CONFIG_OCPP` adds an OCPP 1.6 Charge Point library over WebSocket, including core authorization, transaction-management, and meter-value operations for EV charging stations.

### Biometrics and wake-up controllers — `4.4.0`

Zephyr adds standard biometrics and Wake-up Controller device classes. Initial biometrics bindings are `adh-tech,gt5x`, `zhiantec,zfm-x0`, and `zephyr,biometrics-emul`; the initial WUC binding is `nxp,llwu`.

### Streaming COBS and disjoint sets — `4.4.0`

Incremental COBS processing uses `cobs_encoder_init()`, `cobs_encoder_write()`, and `cobs_encoder_close()`, with the matching `cobs_decoder_init()`/`cobs_decoder_write()`/`cobs_decoder_close()` lifecycle. The new `sys_set_node`, `sys_set_makeset()`, `sys_set_find()`, and `sys_set_union()` APIs provide disjoint-set operations.
