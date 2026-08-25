# Bluetooth

Use these notes when migrating Bluetooth host, controller, profile, Mesh, Classic, LE Audio, ISO, or security code.

## Host, HCI, connections, and security

### Bluetooth HCI devicetree — `migration-4.0`

`bt-hci-bus` and `bt-hci-quirks` values are now lower-case strings without the `BT_HCI_BUS_` or `BT_HCI_QUIRK_` prefix. `BT_SPI` is selected from devicetree compatibles and should be removed from board defconfigs.

### Bluetooth advertiser resumption — `migration-4.0`

`BT_LE_ADV_OPT_CONNECTABLE`, `BT_LE_ADV_OPT_ONE_TIME`, and `BT_LE_ADV_CONN` are deprecated because connectability was coupled to automatic restart. Extended advertising never auto-resumes: use `BT_LE_ADV_FAST_2` in place of the `BT_LE_ADV_CONN` shorthand, or replace custom `BT_LE_ADV_OPT_CONNECTABLE` with `BT_LE_ADV_OPT_CONN` and remove `BT_LE_ADV_OPT_ONE_TIME`.

For legacy advertising that did not resume, replace the connectable/one-time combination with `BT_LE_ADV_OPT_CONN`. Applications that relied on automatic legacy resumption must now restart advertising themselves; new connectable shorthands are `BT_LE_ADV_CONN_FAST_1` and `BT_LE_ADV_CONN_FAST_2`.

### Bluetooth host contracts — `4.0.0`

`bt_tbs_client_register_cb()` now allows multiple listeners and may fail, while an ATT timeout now disconnects the peer. `CONFIG_BT_CONN_CHECK_NULL_BEFORE_CREATE` makes the LE create APIs reject a non-NULL connection pointer, and `CONFIG_BT_CONN_TX_NOTIFY_WQ` moves TX notification processing off the system workqueue.

### Bluetooth-backed entropy timing — `migration-4.1`

The Bluetooth HCI entropy driver now requests and parses random data directly, so applications can obtain entropy before a Bluetooth connection is ready.

### Bluetooth controller declaration — `migration-4.1`

`BT_CTLR` is deprecated in favor of `HAS_BT_CTLR`. Kconfig options for local link layers, including HCI drivers and the upstream controller, should select `HAS_BT_CTLR`.

### Bluetooth ACL buffers and pairing — `migration-4.1`

`CONFIG_BT_BUF_ACL_RX_COUNT` is deprecated; the base count is now `CONFIG_BT_MAX_CONN + 1`, and extra buffers are configured with `CONFIG_BT_BUF_ACL_RX_COUNT_EXTRA`. LE legacy pairing is no longer enabled by default; applications that still require it must disable `CONFIG_BT_SMP_SC_PAIR_ONLY`.

The prompt for internal-only `CONFIG_BT_ECC` is removed, so its internal users must select it themselves.

### Bluetooth HCI and automatic connections — `4.1.0`

The legacy Bluetooth HCI driver API is removed in favor of an API based on Zephyr's normal driver model. `bt_le_set_auto_conn()` is deprecated; applications should reconnect from the `bt_conn_cb.disconnected` callback instead.

### Bluetooth HCI buffers and commands — `migration-4.2`

HCI driver buffers now carry their H:4 type prefix in the payload; `bt_buf_set_type()` and `bt_buf_get_type()` are deprecated and may be called only once per buffer. Replace parameterized `bt_hci_cmd_create()` with argument-free `bt_hci_cmd_alloc()`, since send functions now encode the command header.

### Bluetooth ISO and managed CCC data — `migration-4.2`

Applications must explicitly create and remove ISO data paths with `bt_iso_setup_data_path()` and `bt_iso_remove_data_path()`. Replace `BT_ISO_CHAN_TYPE_CONNECTED` checks with central/peripheral checks using `BT_ISO_CHAN_TYPE_CENTRAL` and `BT_ISO_CHAN_TYPE_PERIPHERAL`.

Rename `_bt_gatt_ccc` to `bt_gatt_ccc_managed_user_data` and `BT_GATT_CCC_INITIALIZER` to `BT_GATT_CCC_MANAGED_USER_DATA_INIT`. Channel-sounding antenna constants now encode both antenna selections as `BT_LE_CS_TONE_ANTENNA_CONFIGURATION_A<number>_B<number>`.

### Bluetooth channel-sounding modes — `migration-4.3`

`bt_le_cs_test_param` and `bt_le_cs_create_config_params` now provide main and sub mode as one parameter, and `bt_conn_le_cs_config` reports them together. Replace `bt_conn_le_cs_main_mode` and `bt_conn_le_cs_sub_mode` with `bt_conn_le_cs_mode`.

### Bluetooth controller names — `migration-4.3`

Rename `CONFIG_BT_CTRL_ADV_ADI_IN_SCAN_RSP` to `CONFIG_BT_CTLR_ADV_ADI_IN_SCAN_RSP`. The misspelled `bt_hci_vs_fata_error_cpu_data_cortex_m` becomes `bt_hci_vs_fatal_error_cpu_data_cortex_m` and now includes the program counter.

### Bluetooth host configuration — `4.3.0`

Replace deprecated `bt_hci_bus` use with `BT_DT_HCI_BUS_GET`. `CONFIG_BT_AUTO_PHY_UPDATE` is replaced by separate `CONFIG_BT_AUTO_PHY_CENTRAL_*` and `CONFIG_BT_AUTO_PHY_PERIPHERAL_*` choices for role-specific automatic PHY preferences.

### Bluetooth connection security — `migration-4.4`

Legacy LE passkey-entry pairing no longer grants MITM authentication, and persisted bonds created that way are downgraded when loaded. `bt_iso_chan.required_sec_level` and `bt_iso_server.sec_level` are removed; secure the ACL with `bt_conn_set_security()` before `bt_iso_chan_connect()`.

### Bluetooth host configuration — `migration-4.4`

Use `bt_conn_le_info.interval_us` instead of the deprecated 1.25-ms-unit `interval`, and rename the `CONFIG_DEVICE_*_GATT_WRITABLE_*` options to their `CONFIG_BT_DEVICE_*` forms. The host no longer selects `CONFIG_POLL`, so applications using `k_poll` must enable it themselves.

### GATT notification permissions — `4.4.2`

When notify or indicate is passed a characteristic declaration, Bluetooth GATT now checks the characteristic value's permissions rather than the declaration's permissions.

## LE Audio and media profiles

### Bluetooth Audio runtime registration — `migration-4.0`

The Unicast Server must call `bt_bap_unicast_server_register()` with `bt_bap_unicast_server_register_param` before its first callback registration; the ASE Kconfigs are now maximums named `CONFIG_BT_ASCS_MAX_ASE_SRC_COUNT` and `CONFIG_BT_ASCS_MAX_ASE_SNK_COUNT`, and `bt_bap_unicast_server_unregister()` permits later teardown. Scan Delegator/BASS likewise move to `bt_bap_scan_delegator_register()`/`unregister()`—the old callback-only registration API is removed—and TBS/GTBS bearers use `bt_tbs_register_bearer()`/`bt_tbs_unregister_bearer()`.

### Bluetooth Audio API and security changes — `migration-4.0`

VCP Volume Renderer state/flags callbacks gain a connection parameter, while Unicast Client callback structures are no longer `const` and multiple registrations are allowed. CSIP coordinator lock/release now require `CONFIG_BT_BONDABLE` and bonded members.

Rename the `bt_audio_codec_qos` family to `bt_bap_qos_cfg` and `BT_AUDIO_CODEC_QOS*` constants to `BT_BAP_QOS_CFG*`. Applications must generate broadcast IDs themselves because `bt_cap_initiator_broadcast_get_id()` and `bt_bap_broadcast_source_get_id()` are removed; use `BT_ISO_BROADCAST_CODE_SIZE` instead of removed `BT_AUDIO_BROADCAST_CODE_SIZE`.

### Bluetooth Audio runtime dependencies — `migration-4.1`

LE Audio options no longer automatically enable `CONFIG_BT_GATT_CLIENT`, `CONFIG_BT_GATT_AUTO_DISCOVER_CCC`, `CONFIG_BT_GATT_AUTO_UPDATE_MTU`, `CONFIG_BT_EXT_ADV`, `CONFIG_BT_PER_ADV_SYNC`, `CONFIG_BT_ISO_BROADCASTER`, `CONFIG_BT_ISO_SYNC_RECEIVER`, `CONFIG_BT_PAC_SNK`, or `CONFIG_BT_PAC_SRC`; enable the ones the application uses.

PACS must be registered at runtime with `bt_pacs_register()` before use and before `bt_ascs_register()`. AICS, ASCS, CSIP, HAS, MCS, PACS, TBS, VCP, and VOCS now depend on `CONFIG_BT_SMP`, which may also need explicit selection.

### Bluetooth broadcast, connection, and Mesh hooks — `4.1.0`

Broadcast sources gain `bt_bap_broadcast_source_register_cb()` and `bt_bap_broadcast_source_unregister_cb()`, while CAP commanders can distribute a broadcast code with `bt_cap_commander_distribute_broadcast_code()`. Other additions include the in-progress `bt_ccp` API and the `bt_mesh_health_cli::update` callback for refreshing periodically published Health Client messages.

### Bluetooth Audio and HFP changes — `migration-4.2`

Rename `CONFIG_BT_CSIP_SET_MEMBER_NOTIFIABLE` to `CONFIG_BT_CSIP_SET_MEMBER_SIRK_NOTIFIABLE` and `BT_AUDIO_CONTEXT_TYPE_PROHIBITED` to `BT_AUDIO_CONTEXT_TYPE_NONE`; replace `bt_csip_set_member_get_sirk()` with `bt_csip_set_member_get_info()`. The HFP AG `sco_disconnected` callback now receives `struct bt_conn *sco_conn` and a `uint8_t reason`.

### Bluetooth LE Audio group control — `4.2.0`

CAP gains `bt_cap_unicast_group_create()`, `bt_cap_unicast_group_reconfig()`, `bt_cap_unicast_group_add_streams()`, and `bt_cap_unicast_group_delete()` plus stream iteration; BAP gains `bt_bap_unicast_group_foreach_stream()`. CSIP Set Members can change size and rank with `bt_csip_set_member_set_size_and_rank()`.

### Bluetooth Audio codec configuration — `migration-4.3`

`bt_audio_codec_cfg` must explicitly set target latency and PHY; use `BT_AUDIO_CODEC_CFG_TARGET_LATENCY_BALANCED` and `BT_AUDIO_CODEC_CFG_TARGET_PHY_2M` for the old behavior, or use `BT_AUDIO_CODEC_CFG`, which defaults to them.

### Bluetooth Audio roles and PA state — `migration-4.3`

GMAP's BGS role now also requires `CONFIG_BT_BAP_BROADCAST_ASSISTANT`. A standalone BAP Scan Delegator must update periodic-advertising synchronization with `bt_bap_scan_delegator_set_pa_state()`; this remains automatic when paired with a BAP Broadcast Sink.

### Bluetooth Audio discovery and iteration — `migration-4.4`

`bt_bap_broadcast_assistant_discover()` no longer reads remote BASS receive states; call `bt_bap_broadcast_assistant_read_recv_state()` explicitly. Audio foreach callbacks now return `true` to continue and `false` to stop, and may return an error when iteration stops early.

### Bluetooth Audio configuration — `migration-4.4`

`CONFIG_BT_AUDIO` now depends on `CONFIG_UTF8`, and `bt_tbs_set_uri_scheme_list()` takes one comma-separated string such as `"tel,skype"` instead of an array. `CONFIG_BT_TBS_SUPPORTED_FEATURES` is removed; use `BT_TBS_FEATURE_HOLD` and `BT_TBS_FEATURE_JOIN`.

## Mesh

### Bluetooth PAST and Mesh workqueues — `4.0.0`

Controller-side Periodic Advertising Sync Transfer roles are enabled with `CONFIG_BT_CTLR_SYNC_TRANSFER_SENDER` and `CONFIG_BT_CTLR_SYNC_TRANSFER_RECEIVER`. Bluetooth Mesh now uses its own workqueue; enable `CONFIG_BT_MESH_WORKQ_SYS` only to retain the old system-workqueue behavior.

### Bluetooth Mesh PSA migration — `migration-4.1`

`CONFIG_BT_MESH_USES_TINYCRYPT` is deprecated; platforms without TF-M now default to `CONFIG_BT_MESH_USES_MBEDTLS_PSA`. TinyCrypt stores Mesh keys incompatibly with `CONFIG_BT_MESH_USES_MBEDTLS_PSA` and `CONFIG_BT_MESH_USES_TFM_PSA`, so a provisioned device must be unprovisioned before an in-place switch and reprovisioned afterward; Mesh DFU should use `BT_MESH_DFU_EFFECT_UNPROV`.

With `CONFIG_BT_SETTINGS` and `CONFIG_BT_MESH_USES_MBEDTLS_PSA`, explicitly enable `CONFIG_SECURE_STORAGE`.

### Bluetooth HCI, Mesh, and passkeys — `migration-4.3`

Use `ipc` instead of the removed `ipm` value for the `bt-hci-bus` property. Mesh provider choices `CONFIG_BT_MESH_USES_MBEDTLS_PSA` and `CONFIG_BT_MESH_USES_TFM_PSA` are removed in favor of automatic selection through `CONFIG_PSA_CRYPTO`.

`CONFIG_BT_FIXED_PASSKEY` is deprecated; enable `CONFIG_BT_APP_PASSKEY` and return a passkey, or `BT_PASSKEY_RAND`, from `bt_conn_auth_cb.app_passkey`.

### Bluetooth Mesh provisioning and key sync — `4.4.0`

Use `bt_mesh_input_numeric()` and the `output_numeric` callback in `bt_mesh_prov` for numeric OOB provisioning in place of the deprecated `bt_mesh_input_number()` and `output_number`. Default-enabled `CONFIG_BT_MESH_CDB_KEY_SYNC` keeps Configuration Database subnet and application keys synchronized with local storage.

## Classic and other profiles

### Bluetooth Device Information strings — `migration-4.1`

Replace `CONFIG_BT_DIS_MODEL` and `CONFIG_BT_DIS_MANUF` with `CONFIG_BT_DIS_MODEL_NUMBER_STR` and `CONFIG_BT_DIS_MANUF_NAME_STR`.

### Bluetooth Device Information presence controls — `4.1.0`

`CONFIG_BT_DIS_MODEL_NUMBER` and `CONFIG_BT_DIS_MANUF_NAME` independently control whether the Model Number String and Manufacturer Name String characteristics are present in DIS.

### Bluetooth buffers and Classic bond operations — `4.2.0`

`CONFIG_BT_CONN_TX_MAX` is deprecated; the pending connection TX count now follows `CONFIG_BT_BUF_ACL_TX_COUNT`. `bt_unpair()` and `bt_foreach_bond()` no longer cover Classic bonds, so use `bt_br_unpair()` and `bt_br_foreach_bond()`; `bt_br_set_discoverable()` also gains a `limited` argument.

### Bluetooth Classic and LE capabilities — `4.2.0`

The Classic stack adds HFP Audio Gateway and Hands-Free roles, configurable codec negotiation and call features, L2CAP retransmission/flow-control modes, and L2CAP echo request/response APIs. LE Connection Subrating is no longer experimental.

### Bluetooth callbacks and Alert Notification Service — `4.4.0`

Applications can unregister GATT and periodic-advertising-sync callbacks with `bt_gatt_cb_unregister()` and `bt_le_per_adv_sync_cb_unregister()`; for unicast ISO channels, `bt_iso_chan_ops.disconnected` now always precedes `bt_conn_cb.disconnected`. `CONFIG_BT_ANS` introduces the Alert Notification Service, and `CONFIG_BT_CTLR_ADV_AUX_SET`, `CONFIG_BT_CTLR_ADV_SYNC_SET`, and `CONFIG_BT_CTLR_ADV_DATA_BUF_MAX` no longer require `CONFIG_BT_CTLR_ADVANCED_FEATURES`.
