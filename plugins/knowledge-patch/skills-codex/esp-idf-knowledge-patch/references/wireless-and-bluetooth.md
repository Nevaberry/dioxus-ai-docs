# Wireless and Bluetooth

## Classic Bluetooth and Bluedroid

### SDP configuration

In 5.4, SDP APIs are no longer gated by `CONFIG_BT_L2CAP_ENABLED`. Enable the
independent `CONFIG_BT_SDP_COMMON_ENABLED` option before calling them. The
unused `user2_ptr_len` and `user2_ptr` fields of
`esp_bluetooth_sdp_hdr_overlay_t` are deprecated.

### Removed and renamed Bluedroid APIs

In 6.0:

- Device-name functions move from `esp_bt_dev_*` to their corresponding
  `esp_bt_gap_*` or `esp_ble_gap_*` APIs.
- Replace `esp_spp_init` with `esp_spp_enhanced_init` and `esp_spp_cfg_t`.
- Replace `esp_hf_ag_devices_status_indchange` with
  `esp_hf_ag_ciev_report`.
- `ESP_BT_GAP_RSSI_*_THRLD` has no replacement.

A2DP also changes:

- Replace `ESP_A2D_MEDIA_CTRL_STOP` with `ESP_A2D_MEDIA_CTRL_SUSPEND`.
- Rename the `esp_a2d_mcc_t` codec fields to their `*_info` forms.
- Replace misspelled `ESP_A2D_SBC_CIE_ALLOC_MTHD_SRN` with
  `ESP_A2D_SBC_CIE_ALLOC_MTHD_SNR`; the old spelling remains only as a
  warning-producing alias.

## ESP-NOW

In 5.5, the send-data callback address parameter changes from
`uint8_t *mac_addr` to `esp_now_send_info_t *tx_info`.

In 6.0, replace `esp_wifi_config_espnow_rate` with
`esp_now_set_peer_rate_config`.

## Wi-Fi Records and Removed Fields

Since 5.4, `wifi_ap_record_t.bandwidth` is `wifi_bandwidth_t`, not `uint8_t`.
The `uph_id`, `ul_pw_headroom`, and `min_tx_pw_flag` fields of
`esp_wifi_htc_omc_t` are deprecated.

## Wi-Fi API Replacements

In 6.0:

- Replace DPP callbacks with `WIFI_EVENT_DPP_*` events.
- Replace `esp_rrm_send_neighbor_rep_request` with
  `esp_rrm_send_neighbor_report_request`.
- Replace antenna functions with their `esp_phy_*` equivalents.
- Collapse WPA3 extended-PSK modes to `WIFI_AUTH_WPA3_PSK`.
- Replace `ESP_IF_WIFI_STA` and `ESP_IF_WIFI_AP` with `WIFI_IF_STA` and
  `WIFI_IF_AP`.
- Replace HT bandwidth names with `WIFI_BW20` and `WIFI_BW40`.
- Replace `wifi_event_neighbor_report_t.report` with flexible member
  `n_report`.
- Obtain FTM raw reports through `esp_wifi_ftm_get_report`.

Reason-code mappings are:

| Old | Current |
| --- | --- |
| `WIFI_REASON_ASSOC_EXPIRE` | `WIFI_REASON_AUTH_EXPIRE` |
| `WIFI_REASON_NOT_AUTHED` | `WIFI_REASON_CLASS2_FRAME_FROM_NONAUTH_STA` |
| `WIFI_REASON_NOT_ASSOCED` | `WIFI_REASON_CLASS3_FRAME_FROM_NONASSOC_STA` |

## Wi-Fi NAN

NAN synchronization uses `esp_wifi_nan_sync_start`,
`esp_wifi_nan_sync_stop`, `WIFI_NAN_SYNC_CONFIG_DEFAULT()`,
`wifi_nan_sync_config_t`, and `WIFI_EVENT_NAN_SYNC_STARTED` /
`WIFI_EVENT_NAN_SYNC_STOPPED`.

Shared `esp_wifi_nan_*` service APIs also support NAN-USD, while datapath APIs
remain NAN-Sync-only.

- Service-information fields become `ssi` and `ssi_len`.
- `wifi_nan_wfa_ssi_t.proto` becomes `uint8_t`.
- `ndp_resp_needed` moves into `wifi_nan_publish_cfg_t`.
- Publish and subscribe configuration structs gain explicit USD fields; use
  designated initialization so new fields are intentional.

## Call Signatures and Off-channel Behavior

`esp_supp_dpp_init` and `esp_wifi_wps_start` no longer accept callback or
timeout arguments.

A second `esp_wifi_init` now returns `ESP_ERR_INVALID_STATE`; it no longer
succeeds without reinitialization.

Initialize `wifi_action_tx_req_t.bssid`. For discovery that needs broadcast or
multicast receive callbacks, opt in with `wifi_roc_req_t.allow_broadcast`.
