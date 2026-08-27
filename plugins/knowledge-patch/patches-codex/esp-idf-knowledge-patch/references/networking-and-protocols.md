# Networking and Protocols

## HTTP Server

Since 5.5, `CONFIG_HTTPD_MAX_REQ_HDR_LEN` is an allocation ceiling rather than
a fixed allocation size. The HTTP server allocates request-header memory
according to the actual received header size, up to the configured limit.

## Network Interface Traversal

`esp_netif_next` is removed in 6.0. Choose a safe replacement based on intent:

- Use `esp_netif_next_unsafe` only in a controlled context.
- Wrap traversal in `esp_netif_tcpip_exec` when serialization through the
  TCP/IP context is appropriate.
- Use `esp_netif_find_if` with a predicate when locating one interface.

Do not introduce unsynchronized traversal merely to preserve the old loop
shape.

## DHCP Server DNS

`LWIP_DHCPS_ADD_DNS` is removed. Configure custom SoftAP DNS offers at runtime
with `esp_netif_dhcps_option(..., ESP_NETIF_DOMAIN_NAME_SERVER, ...)` and
`esp_netif_set_dns_info`.

When the option is disabled, the SoftAP address is still offered as DNS. To
suppress DNS information entirely, enable the option and configure `0.0.0.0`.

## SNTP and Ping

Replace removed `sntp.h` with `esp_sntp.h`.

The old `esp_ping.h` and `ping.h` functions are also gone. Include
`ping/ping_sock.h`, create a session with `esp_ping_new_session`, and launch it
with `esp_ping_start`.

## Network Provisioning

Built-in `wifi_provisioning` is replaced in 6.0 by the managed
`espressif/network_provisioning` component:

```yaml
dependencies:
  espressif/network_provisioning: "^1.1.0"
```

Most `wifi_prov_*` names become `network_prov_*`. The manager replacements that
do not follow a purely mechanical prefix swap are:

- `network_prov_mgr_is_wifi_provisioned`
- `network_prov_mgr_configure_wifi_sta`
- `network_prov_mgr_reset_wifi_provisioning`
- `network_prov_mgr_reset_wifi_sm_state_on_failure`
- `network_prov_mgr_reset_wifi_sm_state_for_reprovision`

## Protocomm Security

`CONFIG_ESP_PROTOCOMM_SUPPORT_SECURITY_VERSION_0` and
`CONFIG_ESP_PROTOCOMM_SUPPORT_SECURITY_VERSION_1` both default to `n`.
Explicitly enable the matching option when using unsecured protocol v0 or the
Curve25519/AES-CTR v1 protocol.

## JSON and MQTT Dependencies

The built-in `json` component becomes `espressif/cjson`, but callers keep using
`cJSON.h`. Remove `json` from `REQUIRES` or `PRIV_REQUIRES` and add the managed
dependency through Component Manager.

ESP-MQTT becomes `espressif/mqtt` while retaining `mqtt_client.h`.

## ESP-TLS

Built-in wolfSSL support and its Kconfig options are removed in 6.0. Standard
applications can use the default mbedTLS stack. To provide another TLS
implementation:

1. Enable `CONFIG_ESP_TLS_CUSTOM_STACK`.
2. Implement `esp_tls_stack_ops_t`.
3. Call `esp_tls_register_stack` before opening connections.

`esp_tls_conn_http_new` is removed. Initialize an `esp_tls_t` with
`esp_tls_init`, then call the replacement ending in `_sync` or `_async`.

## VFS Migration

Use the following API replacements:

| Removed or renamed API | Replacement |
| --- | --- |
| `esp_vfs_fat_sdmmc_unmount` | `esp_vfs_fat_sdcard_unmount` |
| `esp_vfs_dev_uart_*` | `uart_vfs_dev_*` |
| `esp_vfs_dev_usb_serial_jtag_*` | `usb_serial_jtag_vfs_*` |

New filesystem implementations should use `esp_vfs_fs_ops_t` APIs instead of
deprecated `esp_vfs_t` registration. `esp_vfs_register_fd_range` is now a
private API in `esp_private/socket.h`.

Explicit dependencies on renamed `esp_vfs_console` can be removed because
`esp_stdio` is common.

## Pre-encrypted OTA Example

In 5.5, `pre_encrypted_ota` moved out of ESP-IDF. Find it at
`esp_encrypted_img/examples/pre_encrypted_ota` in the `idf-extra-components`
repository.
