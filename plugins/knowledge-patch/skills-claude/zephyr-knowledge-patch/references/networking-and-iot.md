# Networking and IoT Protocols

Entries are grouped by developer task and alphabetized by topic. The
parenthetical identifier records the exact source batch for each item.

## Blob-free Wi-Fi builds (migration-4.1)

Replace vendor-specific `CONFIG_NXP_WIFI_BUILD_ONLY_MODE` and `CONFIG_NRF_WIFI_BUILD_ONLY_MODE` with the common `CONFIG_BUILD_ONLY_NO_BLOBS`.

## Cellular and hashing contracts (migration-4.3)

`cellular_access_technology` values are redefined and `cellular_registration_status` values extended to align with 3GPP TS 27.007. Hash packets now require constant input, affecting out-of-tree backends that performed hashing in place.

## CoAP and DHCP capabilities (4.0.0)

CoAP now supports the No Response option. DHCPv4 clients can retain multiple DNS servers, while the server can send DNS and Router options and use an application callback to assign custom addresses.

## CoAP block and retransmission APIs (migration-4.0)

The `block_number` output of `coap_get_block1_option()` and `coap_get_block2_option()` is now `uint32_t *`, and `coap_get_block2_option()` adds a `bool *has_more` output. With `CONFIG_COAP_RANDOMIZE_ACK_TIMEOUT`, `struct coap_transmission_parameters` also contains `ack_random_percent`.

## CoAP cancellation and LwM2M socket setup (4.1.0)

Clients can cancel a CoAP request with `coap_client_cancel_request()`. LwM2M pull transfers gain `lwm2m_pull_context_set_sockopt_callback()` for applying socket options to their connection.

## CoAP client ownership (migration-4.3)

`coap_client_response_cb_t` now receives its arguments through a `coap_client_response_data` pointer. `coap_client_request.path` and `.options` are embedded arrays rather than transient pointers, sized by `CONFIG_COAP_CLIENT_MAX_PATH_LENGTH` and `CONFIG_COAP_CLIENT_MAX_EXTRA_OPTIONS`.

## CoAP resource metadata (migration-4.4)

Move `.well-known/core` attributes from `coap_resource.user_data` to the new `coap_resource.metadata` pointer, leaving `user_data` for the application. `COAP_RESPONSE_CODE_OK` is removed because CoAP has no registered 2.00 response code.

## Connection idling and DNS (4.3.0)

Connection Manager can set and query per-interface idle timeouts and reports `NET_EVENT_CONN_IF_IDLE_TIMEOUT`. DNS resolution adds CNAME, TXT, and SRV query types plus APIs to enable packet forwarding and remove configured server addresses.

## DHCP and LwM2M controls (4.4.0)

DHCPv4 servers can install an address validator with `net_dhcpv4_server_set_address_validator_cb()`. LwM2M adds `CONFIG_LWM2M_SEND_SCHEDULER`, the IPSO magnetometer object through `CONFIG_LWM2M_IPSO_MAGNETOMETER`, and `lwm2m_cache_free_slots_get()`.

## DHCPv6 DNS and mDNS probing (4.1.0)

`CONFIG_NET_DHCPV6_OPTION_DNS_ADDRESS` adds DHCPv6 DNS-address option support. `CONFIG_MDNS_RESPONDER_PROBE` enables probing by the mDNS responder.

## Ethernet API migrations (migration-4.2)

Rename DSA roles from `ETHERNET_DSA_MASTER_PORT`/`ETHERNET_DSA_SLAVE_PORT` to `ETHERNET_DSA_CONDUIT_PORT`/`ETHERNET_DSA_USER_PORT`, and remove `_T` from the `LINK_*BASE_T` and `ETHERNET_LINK_*BASE_T` speed constants. Link, duplex, and autonegotiation configuration requests are removed; obtain the PHY with `net_eth_get_phy()` and call `phy_configure_link()`, whose new `flags` argument should be `0` for the old behavior.

## Ethernet bridging (migration-4.0)

Bridge shell operations move under `net bridge`. Bridging now uses a separate virtual network interface while member Ethernet interfaces remain normally usable; `eth_bridge_iface_allow_tx()` and bridge listener add/remove are gone, and `eth_bridge_iface_add()`/`remove()` now take the bridge network-interface pointer first.

## Ethernet bus width and PHY advertisement (migration-4.3)

Remove the obsolete Xilinx GEM `amba-ahb-dbus-width` property because the driver discovers it at runtime. `nxp,enet-mac` and `xlnx,gem` no longer constrain PHY speed and duplex during initialization; use the PHY's `default-speeds` property when the MAC supports only a subset of advertised PHY speeds.

## Ethernet initialization and offload (migration-4.4)

`CONFIG_ETH_INIT_PRIORITY` now defaults to 60 and supplies the PHY, MDIO, and applicable PTP defaults. Checksum-capable out-of-tree drivers must select `CONFIG_NET_CHECKSUM_OFFLOAD_SUPPORTED`; applications enable the feature with `CONFIG_NET_CHECKSUM_OFFLOAD`.

## Ethernet MAC provisioning (migration-4.4)

Drivers adopting `net_eth_mac_config` now obtain MAC addresses from a child of `nvmem-layout`; SAM GMAC's `CONFIG_ETH_SAM_GMAC_MAC_I2C_*` options and `mac-eeprom` property are removed. On STM32, `zephyr,random-mac-address` now generates all six bytes and `local-mac-address` is used as written, rather than retaining an ST OUI.

## Ethernet PHY bindings (migration-4.4)

The `ethernet-phy` `fixed-link` property is removed; use an `ethernet-phy-fixed-link` node with `default-speeds`. `microchip,ksz8081` reset GPIOs now use active-low semantics, `microchip,lan865x` must point `phy-handle` at its PHY node, and removal of `CONFIG_NET_DSA_DEPRECATED` also removes the unmigrated KSZ8463, KSZ8794, and KSZ8863 drivers.

## Ethernet reset and checksum properties (migration-4.3)

An active-low `microchip,vsc8541` reset must now carry `GPIO_ACTIVE_LOW` in `reset-gpios`. Xilinx GEM checksum offload now defaults on and replaces `rx-checksum-offload` and `tx-checksum-offload` with opt-out properties `disable-rx-checksum-offload` and `disable-tx-checksum-offload`; QEMU targets always disable it.

## Extensible Ethernet protocol handling (4.1.0)

`NET_L3_REGISTER` lets applications register handlers for Ethernet protocol types without modifying the Zephyr network core. Ethernet also gains `CONFIG_NET_L2_ETHERNET_RESERVE_HEADER`.

## FlexRAM, Ethos-U, and modem configuration (migration-4.2)

Include the NXP FlexRAM API from `<zephyr/drivers/misc/flexram/nxp_flexram.h>` and replace `memc_flexram_*` APIs and Kconfigs with `flexram_*`. Rename `CONFIG_ARM_ETHOS_U*` to `CONFIG_ETHOS_U*`, and replace removed `CONFIG_MODEM_CELLULAR_CMUX_MAX_FRAME_SIZE` with the separate `CONFIG_MODEM_CMUX_WORK_BUFFER_SIZE` and `CONFIG_MODEM_CMUX_MTU` settings.

## HTTP and ICMP contracts (migration-4.4)

`net_icmp_handler_t` now returns `net_verdict`. Dynamic HTTP handlers use `http_transaction_status` and the renamed `HTTP_SERVER_TRANSACTION_ABORTED`/`HTTP_SERVER_REQUEST_DATA_MORE`/`HTTP_SERVER_REQUEST_DATA_FINAL` values, and must handle `HTTP_SERVER_TRANSACTION_COMPLETE` to reset state after a response is fully sent.

## HTTP dynamic methods and diagnostics (4.1.0)

Dynamic HTTP resources now accept PUT, PATCH, and DELETE in addition to the existing methods. Servers can report failure reasons with `CONFIG_HTTP_SERVER_REPORT_FAILURE_REASON` and use ALPN for TLS with `CONFIG_HTTP_SERVER_TLS_USE_ALPN`.

## HTTP request contexts and fallback resources (migration-4.1)

Dynamic-resource callbacks now receive request data, length, and headers through `http_request_ctx`; use it rather than `http_client_ctx` so concurrent HTTP/2 streams do not share request headers incorrectly. WebSocket resource callbacks gain the same request context for inspecting upgrade headers.

`HTTP_SERVICE_DEFINE` and `HTTPS_SERVICE_DEFINE` gain a final fallback-resource argument. Pass `NULL` to preserve the prior no-fallback behavior.

## HTTP server and client contracts (migration-4.2)

HTTP service definitions now honor their `_concurrent` and `_backlog` values, so existing `HTTP_SERVICE_DEFINE*` and `HTTPS_SERVICE_DEFINE*` arguments must be sized deliberately. An `http_response_cb_t` callback now returns `int`; return `0` to continue with the old behavior or a nonzero value to abort the connection.

## HTTP server application surface (4.0.0)

Applications can inspect request headers, set response headers and status codes, serve static filesystem resources, and omit a local host when creating a server instance; dynamic-resource callbacks have a new format for incremental requests and replies.

## HTTP, socket, and ICMP contracts (migration-4.3)

HTTP service macros now honor their `_config` argument, so every `HTTP_SERVICE_DEFINE*` and `HTTPS_SERVICE_DEFINE*` must pass an applicable value. `socklen_t` is now always the 32-bit `uint32_t`, and `net_icmp_init_ctx()` gains an `AF_INET` or `AF_INET6` family argument.

## IPv4, OpenThread, and traffic-class configuration (migration-4.1)

New IPv4 addresses now get their default mask from `CONFIG_NET_IPV4_DEFAULT_NETMASK`; applications can still override it with `net_if_ipv4_set_netmask_by_addr()`. `CONFIG_NET_L2_OPENTHREAD` no longer implies NVS, so explicitly enable `CONFIG_NVS` or `CONFIG_ZMS`; rename `CONFIG_NET_TC_SKIP_FOR_HIGH_PRIO` to `CONFIG_NET_TC_TX_SKIP_FOR_HIGH_PRIO`.

## LoRa asynchronous receive context (migration-4.1)

`lora_recv_async()` and `lora_recv_cb` gain a `void *user_data` argument. Pass `NULL` to retain context-free behavior.

## LoRa channel activity and duty cycling (4.4.0)

The LoRa API adds `lora_airtime`, synchronous/asynchronous Channel Activity Detection through `lora_cad()` and `lora_cad_async()`, and hardware wake-on-radio through `lora_recv_duty_cycle()`; CAD and listen-before-talk parameters live in `lora_modem_config`.

## LwM2M accelerometer resources (migration-4.2)

Applications enabling the optional Accelerometer object's Y, Z, minimum-range, or maximum-range resources must now provide read buffers for them.

## LwM2M location and certificate behavior (4.0.0)

Applications using the optional Location altitude, radius, or speed resources must now provide a read buffer. Certificate-based connections can verify the X.509 hostname when the URI contains a valid name, and the DTLS cipher list gains `TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8`.

## LwM2M sizing and observation behavior (4.2.0)

`CONFIG_LWM2M_ENGINE_MESSAGE_HEADER_SIZE` is removed; include the former 48-byte header headroom in `CONFIG_LWM2M_COAP_MAX_MSG_SIZE` and ensure `CONFIG_LWM2M_COAP_BLOCK_SIZE` still fits. `CONFIG_LWM2M_SERVER_BOOTSTRAP_ON_FAIL` adds fallback bootstrap, and numerical observations now honor Greater Than, Less Than, and Step attributes when `CONFIG_LWM2M_MAX_NOTIFIED_NUMERICAL_RES_TRACKED` is sized appropriately.

## MCTP over I3C (4.4.0)

MCTP gains `zephyr,mctp-i3c-controller`, `zephyr,mctp-i3c-endpoint`, and `zephyr,mctp-i3c-target` bindings, with new I2C and I3C endpoint/owner samples plus a USB endpoint sample.

## Modbus serial settings (migration-4.2)

Rename `modbus_serial_param.client_stop_bits` to `stop_bits`. Nonstandard stop-bit settings are disabled unless `CONFIG_MODBUS_NONCOMPLIANT_SERIAL_MODE` is enabled.

## Modem and LoRaWAN symbols (migration-4.4)

HL78XX timing symbols gain an `_MS` suffix and the default startup time changes from 1000 ms to 120 ms. All `CONFIG_LORAMAC_REGION_*` symbols become `CONFIG_LORAWAN_REGION_*`.

## Modem configuration (migration-4.3)

Rename `CONFIG_MODEM_AT_SHELL_USER_PIPE` to `CONFIG_MODEM_AT_USER_PIPE`. Rename `CONFIG_MODEM_CMUX_WORK_BUFFER_SIZE` to `CONFIG_MODEM_CMUX_WORK_BUFFER_SIZE_EXTRA`; its value is only the extra space beyond `CONFIG_MODEM_CMUX_MTU + 7`.

## MQTT 5 and socket controls (4.2.0)

Full MQTT 5.0 support is selected with `CONFIG_MQTT_VERSION_5_0`, and `mqtt_transport.if_name` binds a transport to an interface. Internet raw sockets use `CONFIG_NET_SOCKETS_INET_RAW`; new socket controls include `IP_MULTICAST_LOOP`, `IPV6_MULTICAST_LOOP`, and `TLS_CERT_VERIFY_RESULT`, while offloaded stacks can enable DNS through `socket_offload_dns_enable()`.

## MQTT disconnect and raw packet sockets (migration-4.2)

`mqtt_disconnect()` gains an optional parameter for MQTT 5.0; MQTT 3.1.1 callers must pass `NULL`. `AF_PACKET/SOCK_RAW/IPPROTO_RAW` is no longer valid; use `AF_PACKET/SOCK_DGRAM/ETH_P_ALL` for link-layer packets or an `AF_INET`/`AF_INET6` raw IP socket as appropriate.

## MQTT shell topics (migration-4.3)

The MQTT shell topics change from `<device_id>_rx` and `<device_id>_tx` to `<device_id>/sh/rx` and `<device_id>/sh/tx`. Set `SHELL_MQTT_TOPIC_RX_ID` and `SHELL_MQTT_TOPIC_TX_ID` to retain custom or legacy suffixes.

## MQTT-SN gateway discovery (4.1.0)

MQTT-SN adds Gateway Advertisement and Discovery support through `mqtt_sn_add_gw()` and `mqtt_sn_search()`.

## Network buffers and socket services (migration-4.0)

Include network buffers with `<zephyr/net_buf.h>` instead of `<zephyr/net/buf.h>`. Remove the ignored `work_q` argument from `NET_SOCKET_SERVICE_SYNC_DEFINE` and `_STATIC`; socket-service callbacks now receive `struct net_socket_service_event *pev` instead of `struct k_work *work`. Replace deprecated `CONFIG_NET_SOCKETS_POLL_MAX` with `CONFIG_ZVFS_POLL_MAX`.

## Network client and server capabilities (4.4.0)

CoAP clients gain multicast through `CONFIG_COAP_CLIENT_MULTICAST`, `CONFIG_FTP_CLIENT` adds an FTP client, and `CONFIG_OPENTHREAD_ZEPHYR_BORDER_ROUTER_NAT64_TRANSLATOR` enables the Zephyr NAT64 translator. A single DTLS server socket can now serve parallel clients, and `CONFIG_NET_SOCKETS_TLS_CONNECT_TIMEOUT` bounds secure-socket connection setup.

## Network monitoring, time sync, and shell commands (4.0.0)

The networking stack gains a Prometheus metrics library and optional periodic SNTP resynchronization. New operational commands include `net dhcpv4 client`, `net dhcpv6 client`, `net virtual`, and `net cm`, and `net ipv4`/`net ipv6` remain available without the native IP stack.

## Network service capabilities (4.2.0)

`COAPS_SERVICE_DEFINE` adds secure CoAP services, `CONFIG_HTTP_SERVER_COMPRESSION` enables HTTP response compression, and `CONFIG_NET_DHCPV4_INIT_REBOOT` enables DHCPv4 INIT-REBOOT. SNTP also gains the asynchronous `sntp_init_async()`, `sntp_send_async()`, `sntp_read_async()`, and `sntp_close_async()` lifecycle.

## Network-management events and DNS sources (migration-4.2)

`net_mgmt_event_handler_t` and `net_mgmt_request_handler_t` now receive a `uint64_t` event value; use `NET_MGMT_LAYER_CODE` and `NET_MGMT_GET_COMMAND` to decode it. Management sockets replace the oversized QAV request constants with `SO_NET_MGMT_ETHERNET_SET_QAV_PARAM` and `SO_NET_MGMT_ETHERNET_GET_QAV_PARAM`.

`dns_resolve_reconfigure()` and `dns_resolve_reconfigure_with_interfaces()` gain a required source argument such as `DNS_SOURCE_DHCPV4`.

## Networking namespace split (migration-4.4)

Zephyr networking names from `net_ip.h` and `socket.h` now use `net_`, `NET_`, or `ZSOCK_` prefixes; `net_compat.h` temporarily supplies old names. POSIX applications should include headers such as `<sys/socket.h>` directly because Zephyr networking headers no longer provide those symbols transitively.

## OCPP 1.6 charge points (4.3.0)

`CONFIG_OCPP` adds an OCPP 1.6 Charge Point library over WebSocket, including core authorization, transaction-management, and meter-value operations for EV charging stations.

## OpenThread and Wi-Fi integration (4.3.0)

OpenThread adds Zephyr border-router, DHCPv6 prefix-delegation, multiple-instance, radio-coexistence, RCP-restoration, SRP fast-start, and TREL DNS-SD controls. The WPA supplicant integration gains background-scan configuration and multiple virtual interfaces.

## OpenThread module API (migration-4.2)

OpenThread is moved out of Zephyr's networking L2 into a standalone module that can run without Zephyr L2 or its IEEE 802.15.4 shim. Replace `openthread_api_mutex_*` with `openthread_mutex_*`, `openthread_start()` with `openthread_run()`, and the `openthread_state_changed_cb*` types and registration calls with their `openthread_state_changed_callback*` forms.

New code should initialize and control the stack through `openthread_init()`, `openthread_run()`, `openthread_stop()`, and `openthread_set_receive_cb()` rather than accessing deprecated `openthread_context` fields. Existing `CONFIG_NET_L2_OPENTHREAD` applications use the module as their backend, while OpenThread Kconfigs now live under `modules/openthread/Kconfig`.

## OpenThread PSA migration (migration-4.4)

Rename `CONFIG_OPENTHREAD_MBEDTLS_CHOICE` to `CONFIG_OPENTHREAD_SECURITY_DEFAULT_CONFIG` and `CONFIG_CUSTOM_OPENTHREAD_SECURITY` to `CONFIG_OPENTHREAD_SECURITY_CUSTOM_CONFIG`. `CONFIG_OPENTHREAD_CRYPTO_LEGACY_MBEDTLS_CONFIG` is removed and PSA is now the only supported and default crypto path; non-TF-M default configurations imply `CONFIG_SECURE_STORAGE` and therefore require a Settings, ZMS, or custom backend.

## OpenThread wake-up and message management (4.1.0)

OpenThread gains Wake-up Coordinator and Wake-up End Device roles through `CONFIG_OPENTHREAD_WAKEUP_COORDINATOR` and `CONFIG_OPENTHREAD_WAKEUP_END_DEVICE`. It also adds `CONFIG_OPENTHREAD_PLATFORM_MESSAGE_MANAGEMENT` and `CONFIG_OPENTHREAD_TCAT_MULTIRADIO_CAPABILITIES`.

## Path MTU and socket controls (4.1.0)

Enable IPv4 or IPv6 path-MTU handling with `CONFIG_NET_IPV4_PMTU` or `CONFIG_NET_IPV6_PMTU`. Socket support expands with `IP_LOCAL_PORT_RANGE`, `IP_MULTICAST_IF`, `IPV6_MULTICAST_IF`, `IP_MTU`, and `IPV6_MTU`.

## POSIX socket names (4.1.0)

`CONFIG_NET_SOCKETS_POSIX_NAMES` is removed. Enable `CONFIG_POSIX_API` to call the POSIX socket names, or use the `zsock_`-prefixed APIs when POSIX cannot be enabled.

## Prometheus metric declarations (migration-4.1)

Prometheus counters, gauges, histograms, and summaries no longer require a separate `struct prometheus_metric`; the corresponding `PROMETHEUS_*_DEFINE` macro prototypes have changed.

## Prometheus network statistics (4.1.0)

`CONFIG_NET_STATISTICS_VIA_PROMETHEUS` exports Zephyr network statistics through the Prometheus metrics facilities.

## Protocol helper APIs (4.3.0)

MQTT-SN gains APIs to predefine topics, define short topics, and update Will topics and messages. LwM2M adds `lwm2m_set_cache_filter()` for cache filtering, while `CONFIG_NET_CONFIG_CLOCK_SNTP_SET_RTC` lets network time synchronization update the RTC.

## PTP rate adjustment (migration-4.3)

`ptp_clock_rate_adjust()` now adjusts the rate ratio relative to nominal frequency rather than the current frequency. Out-of-tree PTP clock drivers must update their implementation for the new PI-servo semantics.

## Routed-packet hop limits (4.4.2)

The routing path now decrements IPv4 TTL and IPv6 hop limit on forwarded packets. Gateways and tests using `net_route_packet_if()` should no longer expect forwarded packets to retain their incoming value.

## Secure socket configuration (migration-4.4)

The protocol passed to `zsock_socket()` for a secure socket is now enforced as the minimum TLS version. `NET_SOCKETS_SOCKOPT_TLS` no longer selects crypto settings, so applications must explicitly choose a TLS version and ciphersuites, optionally through `CONFIG_MBEDTLS_CIPHERSUITE_TLS_*` helpers.

## Selective Ethernet statistics (4.4.0)

`ethernet_stats_type` and the optional `get_stats_type` callback in `ethernet_api` let callers request common, vendor, or all statistics without forcing drivers to query expensive vendor firmware data.

## Silabs Gecko Ethernet properties (migration-4.1)

Gecko Ethernet properties `location-phy_mdc`, `location-phy_mdio`, `location-phy_pwr_enable`, `location-phy_reset`, and `location-phy_interrupt` become fully hyphenated `location-phy-*` names. The `location-rmii_*` properties for refclk, CRS/DV, TXD0/1, TX enable, RXD0/1, and RX error move to the corresponding `location-phy-*` names.

## STM32 Ethernet PHY configuration (migration-4.2)

STM32 Ethernet no longer uses `ETH_STM32_HAL_MII`; select the interface with the devicetree `phy-connection-type` property and provide a required `phy-handle`. The old STM32 PHY address, carrier-check, autonegotiation, speed, and duplex Kconfigs are removed because those settings now belong to the Ethernet PHY API.

## TCP backlog and socket metadata (4.3.0)

`zsock_listen()` now enforces its `backlog` as the limit on pending connections. New socket controls expose received IPv4 TTL and IPv6 packet information and hop limits through `IP_RECVTTL`, `IPV6_PKTINFO`, `IPV6_RECVHOPLIMIT`, and `IPV6_HOPLIMIT`.

## Wi-Fi and OpenThread facilities (4.0.0)

The Wi-Fi stack adds Easy Connect/DPP, a credentials library, enterprise station support, and sample snippets; its shell gains regulatory-domain, WPS, and 802.11r controls. The OpenThread port adds NAT64 callbacks, `CONFIG_IEEE802154_SELECTIVE_TXCHANNEL`, and configuration for NAT64 CIDR, stored-frame-counter headroom, RX sensitivity, and CSL request timing.

## Wi-Fi channel bands (migration-4.4)

`wifi_channel_info` gains `band`; 2.4- and 5-GHz channels can leave it `WIFI_FREQ_BAND_UNKNOWN`, but overlapping 6-GHz channel numbers require `WIFI_FREQ_BAND_6_GHZ`. Recompile callers so the `net_mgmt` structure size matches.

## WireGuard and Wi-Fi peer-to-peer (4.4.0)

`CONFIG_WIREGUARD` adds WireGuard VPN support, while `wifi_mgmt_p2p` adds Wi-Fi Direct discovery and connections without an access point. WPA supplicant can also opt into otherwise-disabled WEP support with `CONFIG_WIFI_NM_WPA_SUPPLICANT_WEP`.

## zperf and Wi-Fi shell options (migration-4.2)

`CONFIG_NET_ZPERF` no longer enables its server; add `CONFIG_NET_ZPERF_SERVER` for server commands. Wi-Fi interface-related options change as follows: `wifi connect` and `wifi ap enable` use `-g` instead of `-i`, `wifi twt setup` uses `-p`, `wifi ap config` uses `-t`, and `wifi mode`, `wifi channel`, and `wifi packet_filter` use `--iface` instead of `--if-index`.
