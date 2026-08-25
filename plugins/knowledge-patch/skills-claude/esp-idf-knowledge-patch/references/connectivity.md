# Connectivity

## Bluetooth and ESP-NOW

### Classic Bluetooth configuration (5.4)

SDP APIs are independently gated by `CONFIG_BT_SDP_COMMON_ENABLED`, not
`CONFIG_BT_L2CAP_ENABLED`. Enable the SDP option before using them. The
`user2_ptr_len` and `user2_ptr` members of
`esp_bluetooth_sdp_hdr_overlay_t` are deprecated.

### ESP-NOW callback and rates

The send-data callback address argument is now
`esp_now_send_info_t *tx_info`, not `uint8_t *mac_addr` (5.5). Replace
`esp_wifi_config_espnow_rate` with `esp_now_set_peer_rate_config` (6.0).

### Bluedroid removals (6.0)

- Device-name functions move from `esp_bt_dev_*` to the corresponding
  `esp_bt_gap_*` or `esp_ble_gap_*` APIs.
- Replace `esp_spp_init` with `esp_spp_enhanced_init` and `esp_spp_cfg_t`.
- Replace `esp_hf_ag_devices_status_indchange` with
  `esp_hf_ag_ciev_report`.
- `ESP_BT_GAP_RSSI_*_THRLD` has no replacement.
- Use `ESP_A2D_MEDIA_CTRL_SUSPEND` instead of `ESP_A2D_MEDIA_CTRL_STOP`.
- A2DP `esp_a2d_mcc_t` codec members use `*_info` names.
- Use `ESP_A2D_SBC_CIE_ALLOC_MTHD_SNR`; the old
  `ESP_A2D_SBC_CIE_ALLOC_MTHD_SRN` spelling remains only as a
  warning-producing alias.

## HTTP server allocation (5.5)

`CONFIG_HTTPD_MAX_REQ_HDR_LEN` is an allocation ceiling, not a fixed allocation
size. Request-header storage is allocated according to the actual received
header length, up to the configured limit.

## Ethernet (6.0)

`esp_eth_phy_802_3_reset_hw` takes only the PHY object. Custom RMII clock
settings move from removed `ETH_RMII_*` Kconfig options into
`eth_esp32_emac_config_t.clock_config.rmii`; the default EMAC configuration
continues to work unchanged.

```c
eth_esp32_emac_config_t emac = ETH_ESP32_EMAC_DEFAULT_CONFIG();
emac.clock_config.rmii.clock_mode = EMAC_CLK_OUT; /* or EMAC_CLK_EXT_IN */
emac.clock_config.rmii.clock_gpio = 0;
```

IP101, LAN87xx, RTL8201, DP83848, KSZ80xx, DM9051, KSZ8851SNL, and W5500
PHY/MAC drivers are registry components. Replace former PTP
`esp_eth_ioctl` commands with the dedicated PTP API.

## Network interfaces, DHCP, SNTP, and ping (6.0)

`esp_netif_next` is removed. Use `esp_netif_find_if` with a predicate when
searching for one interface. If traversal is necessary, either use
`esp_netif_next_unsafe` in a controlled context or wrap traversal in
`esp_netif_tcpip_exec`.

`LWIP_DHCPS_ADD_DNS` is removed. Configure SoftAP DNS offers at runtime with
`esp_netif_dhcps_option(..., ESP_NETIF_DOMAIN_NAME_SERVER, ...)` and
`esp_netif_set_dns_info`. When the option is disabled, the SoftAP address is
still offered as DNS. To advertise no DNS, enable the option and configure
`0.0.0.0`.

Replace `sntp.h` with `esp_sntp.h`. The old `esp_ping.h`/`ping.h` APIs are
removed; include `ping/ping_sock.h`, create a session with
`esp_ping_new_session`, and start it with `esp_ping_start`.

## Network provisioning and protocomm (6.0)

Replace the built-in `wifi_provisioning` component with:

```yaml
dependencies:
  espressif/network_provisioning: "^1.1.0"
```

Most `wifi_prov_*` names become `network_prov_*`. The manager exceptions are:

- `network_prov_mgr_is_wifi_provisioned`
- `network_prov_mgr_configure_wifi_sta`
- `network_prov_mgr_reset_wifi_provisioning`
- `network_prov_mgr_reset_wifi_sm_state_on_failure`
- `network_prov_mgr_reset_wifi_sm_state_for_reprovision`

Protocomm security v0 and v1 both default off. Explicitly enable
`CONFIG_ESP_PROTOCOMM_SUPPORT_SECURITY_VERSION_0` for unsecured v0 or the
corresponding `_VERSION_1` option for Curve25519/AES-CTR v1.

## Wi-Fi records and API replacements

`wifi_ap_record_t.bandwidth` is `wifi_bandwidth_t`, not `uint8_t` (5.4). The
`uph_id`, `ul_pw_headroom`, and `min_tx_pw_flag` fields of
`esp_wifi_htc_omc_t` are deprecated.

In 6.0, apply these replacements:

| Former API or symbol | Current API or symbol |
| --- | --- |
| DPP callbacks | `WIFI_EVENT_DPP_*` events |
| `esp_rrm_send_neighbor_rep_request` | `esp_rrm_send_neighbor_report_request` |
| Wi-Fi antenna functions | corresponding `esp_phy_*` APIs |
| WPA3 extended-PSK modes | `WIFI_AUTH_WPA3_PSK` |
| `ESP_IF_WIFI_STA` / `ESP_IF_WIFI_AP` | `WIFI_IF_STA` / `WIFI_IF_AP` |
| HT bandwidth names | `WIFI_BW20` / `WIFI_BW40` |
| `wifi_event_neighbor_report_t.report` | flexible `n_report` |
| inline FTM raw reports | `esp_wifi_ftm_get_report` |

Reason mappings are:

- `WIFI_REASON_ASSOC_EXPIRE` to `WIFI_REASON_AUTH_EXPIRE`
- `WIFI_REASON_NOT_AUTHED` to `WIFI_REASON_CLASS2_FRAME_FROM_NONAUTH_STA`
- `WIFI_REASON_NOT_ASSOCED` to
  `WIFI_REASON_CLASS3_FRAME_FROM_NONASSOC_STA`

## NAN and off-channel behavior (6.0)

NAN synchronization uses `esp_wifi_nan_sync_start`/`stop`,
`WIFI_NAN_SYNC_CONFIG_DEFAULT()`, `wifi_nan_sync_config_t`, and the
`WIFI_EVENT_NAN_SYNC_STARTED`/`STOPPED` events. Shared `esp_wifi_nan_*` service
APIs support NAN-USD, but datapath APIs remain NAN-Sync-only.

Service-information fields become `ssi` and `ssi_len`;
`wifi_nan_wfa_ssi_t.proto` becomes `uint8_t`; and `ndp_resp_needed` moves into
`wifi_nan_publish_cfg_t`. Publish and subscribe configurations have explicit
USD fields, so use designated initializers to avoid uninitialized additions.

`esp_supp_dpp_init` and `esp_wifi_wps_start` no longer accept callbacks or
timeout arguments. Calling `esp_wifi_init` twice returns
`ESP_ERR_INVALID_STATE` rather than succeeding. Initialize
`wifi_action_tx_req_t.bssid`, and set `wifi_roc_req_t.allow_broadcast` when
discovery needs broadcast or multicast receive callbacks.
