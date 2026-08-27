# Networking and protocol proxies

Use this reference for listeners, sockets, TCP/UDP/QUIC behavior, PROXY protocol, tunnels, and application protocol proxies.

## TCP proxy and tunneling

### Delayed TCP connections and reset propagation (since 1.38.0)

TCP proxy configurations using `upstream_connect_mode` values other than `IMMEDIATE` must now set `max_early_data_bytes` explicitly; use `0` to retain delayed connection establishment without buffering early data. Tunneling also propagates upstream TCP resets downstream, controlled temporarily by `envoy.reloadable_features.propagate_upstream_rst_through_tunneled_tcp_proxy` and `envoy.reloadable_features.map_http_stream_reset_to_tcp_rst`.

### TCP proxy idle-timeout start (since 1.36.0)

The downstream idle timer now starts as soon as a TCP proxy connection is created, including while its upstream connection is still pending; set `envoy.reloadable_features.tcp_proxy_set_idle_timer_immediately_on_new_connection=false` to restore the old timing temporarily.

### TCP proxy retry and early receive controls (since 1.34.0)

`backoff_options` configures the TCP proxy retry strategy. A filter-state object at `envoy.tcp_proxy.receive_before_connect` lets downstream filters read before the proxy opens its upstream connection.

### TCP tunneling identity and transport metadata (since 1.36.0)

TCP proxy tunneling can generate and propagate request IDs with `request_id_extension`; `request_id_header` and `request_id_metadata_key` override the defaults `x-request-id` and `tunnel_request_id`. PROXY-protocol TLVs can obtain dynamic values from a `format_string`, and `max_downstream_connection_duration_jitter_percentage` spreads configured downstream connection expiry.

### TCP-proxy connection timing (since 1.37.0)

TCP proxy adds `upstream_connect_mode` and `max_early_data_bytes` to control when the upstream connection opens and how much early data is buffered, permitting inspection of SNI or certificate data before connecting upstream.

### TCP-proxy route, drain, and duration controls (since 1.39.0)

`envoy.reloadable_features.tcp_proxy_delay_route_selection` delays route choice until immediately before the upstream connection, according to `upstream_connect_mode`. `check_drain_close` closes downstream connections with `FlushWrite` when draining, and TCP access logs now populate `COMMON_DURATION` points `DS_CX_BEG`, `DS_CX_END`, `US_CX_BEG`, and `US_CX_END`.

## UDP proxy

### c-ares UDP-channel rotation (since 1.36.0)

The c-ares resolver's `max_udp_channel_duration` periodically recreates the UDP channel to avoid stale socket state and distribute queries across UDP ports.

### Tap and UDP sink behavior (since 1.35.0)

Transport tap adds a counter for streaming and buffered traces, and streamed taps can emit messages according to the configured size. The UDP sink now accepts a single message larger than 64 KB.

### UDP external authorization (since 1.39.0)

The UDP proxy adds an `ext_authz` session filter that calls the gRPC Authorization API when a new UDP session is created.

### UDP proxy routing and retry backoff (since 1.33.0)

Session filters can select a cluster through per-session state key `envoy.udp_proxy.cluster`; static and dynamic clusters can coexist, with `envoy.upstream.dynamic_host` distinguishing dynamic-host sessions. `backoff_options` now configures retries when UDP is tunneled over HTTP.

## QUIC and HTTP/3 transport

### HTTP/2 and QUIC resource tuning (since 1.37.0)

`enable_huffman_encoding` controls HTTP/2 header Huffman encoding. QUIC `max_sessions_per_event_loop` caps new sessions per event-loop iteration and defaults to the prior hard-coded value of `16`.

### HTTP/3 QPACK control (since 1.34.0)

`envoy_v3_api_field_extensions.upstreams.http.v3.Http3ProtocolOptions.disable_qpack` experimentally disables QPACK compression.

### HTTP/3 validation and flow control (since 1.35.0)

Envoy validates HTTP/3 pseudo-headers by default; `envoy.restart_features.validate_http3_pseudo_headers=false` disables it. Experimental `disable_connection_flow_control_for_streams` lets multiplexed streams make progress independently without connection-level flow control.

### Proxy buffering and HTTP/3 connection behavior (since 1.36.0)

The generic-proxy codec now disconnects when its buffer, sized to the connection buffer limit, is exceeded; set `envoy.reloadable_features.generic_proxy_codec_buffer_limit=false` to revert. Upstream HTTP/3 Happy Eyeballs is now disabled through `envoy.reloadable_features.http3_happy_eyeballs`, while Envoy Mobile drains connections on network changes independently of DNS refresh unless `envoy.reloadable_features.decouple_explicit_drain_pools_and_dns_refresh=false`.

### QUIC key logging and session resumption (since 1.39.0)

QUIC can emit NSS TLS key-log lines with the same IP-list filtering as TCP TLS when `key_log` is configured and `envoy.restart_features.quic_keylog_support=true`. It can also resume sessions across instances from configured `session_ticket_keys` when `envoy.reloadable_features.quic_session_ticket_support=true`; both guards default to disabled.

### QUIC SCONE support (since 1.38.0)

`QuicProtocolOptions.enable_scone` enables SCONE, while Envoy Mobile adds `EngineBuilder.enableScone()` and reports SCONE bandwidth and timestamp data through `scone_max_kbps` and `scone_timestamp_ms`.

### QUIC-LB connection IDs (since 1.34.0)

A new extension provides draft QUIC-LB connection-ID generation.

### QUIC-LB server identifiers (since 1.36.0)

QUIC-LB configuration can now use a base64-encoded server ID.

## Listeners, sockets, and namespaces

### Admin and listener-update APIs (since 1.38.0)

The `/clusters` endpoint accepts an RE2 `filter` query parameter, compatible with text or JSON `format`, to select clusters by name. `ListenerManager` adds `ListenerUpdateCallbacks`, paralleling cluster-update callbacks for extension code.

### Directional listener draining (since 1.34.0)

The admin `/drain_listeners` endpoint can combine its `inbound_only` and graceful query parameters, enabling graceful draining limited to inbound listeners.

### Downstream transport controls (since 1.35.0)

The PostgreSQL proxy can require downstream SSL. Listener socket addresses add `network_namespace_filepath` for opening the listener in a specified network namespace.

### io_uring flow-control settings (since 1.39.0)

The io_uring socket interface adds `write_high_watermark_bytes` and `write_low_watermark_bytes`, with existing deployments now applying write backpressure by default at 128 KiB and resuming at 16 KiB. Linux 6.0+ also supports multishot reads using a kernel buffer ring.

### Linux worker and socket locality (since 1.39.0)

`enable_worker_cpu_affinity` pins Linux worker threads to CPUs in the process affinity mask. With affinity and reuse-port enabled, listener `cpu_locality_balance` can steer connections to the worker on the receiving CPU; a separate sockmap socket interface can accelerate same-host TCP on Linux 4.18+ while falling back to normal TCP for remote peers.

### Listener keepalive controls (since 1.37.0)

Primary and additional listener addresses accept `tcp_keepalive`; additional addresses inherit the listener setting unless overridden. Setting any keepalive field to `0` disables keepalive for the applicable address.

### Listener socket options and file-backed SDS secrets (since 1.34.0)

Socket options attached only to an additional listener address are now applied even when the listener itself has no `socket_options`. SDS now watches file-backed `GenericSecret` resources for changes.

### Network-namespace matching (since 1.36.0)

`NetworkNamespaceInput` exposes a listener socket's `network_namespace_filepath` to `filter_chain_matcher` and network or HTTP RBAC matchers; it yields an empty value on non-Linux platforms, causing default-filter-chain selection. The TLS inspector also publishes dynamic metadata when `ClientHello` parsing fails.

### Transport-socket and composite cluster selection (since 1.37.0)

Cluster `transport_socket_matcher` uses the xDS matcher framework to select a named entry from `transport_socket_matches` using endpoint metadata, locality metadata, or transport-socket filter state. The new composite cluster selects successive sub-clusters by retry attempt and fails once attempts exceed its configured cluster list.

### WebSocket response handling and timeouts (since 1.36.0)

WebSocket handshake `4xx` and `5xx` responses now pass through the filter chain, and route plus per-try timeouts apply while waiting for an upgrade response. Set `envoy.reloadable_features.websocket_allow_4xx_5xx_through_filter_chain=false` or `envoy.reloadable_features.websocket_enable_timeout_on_upgrade_response=false` to disable the respective behavior.

## PROXY protocol

### Proxy Protocol v2 custom TLVs (since 1.34.0)

Upstream transport sockets can add custom TLVs from endpoint typed metadata in `envoy.transport_sockets.proxy_protocol` or from `ProxyProtocolConfig.added_tlvs`, with host entries overriding configuration entries of the same type. TCP proxy's `proxy_protocol_tlvs` adds TLVs to the Proxy Protocol state that is emitted in the upstream v2 header.

### PROXY-protocol binary TLVs (since 1.39.0)

`encoding: BASE64` stores a PROXY-protocol TLV's raw bytes as base64 in dynamic metadata or filter state. The default continues to sanitize the value as UTF-8.

### PROXY-protocol TLV handling (since 1.37.0)

Duplicate PROXY protocol v2 TLVs with the same key are now retained unless `envoy.reloadable_features.proxy_protocol_allow_duplicate_tlvs=false`. `tlv_location=FILTER_STATE` stores TLVs under `envoy.network.proxy_protocol.tlv`, where a value is addressable as `%FILTER_STATE(envoy.network.proxy_protocol.tlv:FIELD:key)%`; the default remains `DYNAMIC_METADATA`.

### TCP proxy logging and PROXY-protocol TLVs (since 1.38.0)

TCP proxy can emit a log entry when a connection is accepted. `proxy_protocol_tlv_merge_policy` controls how configured TLVs combine with existing PROXY-protocol state through `ADD_IF_ABSENT`, `OVERWRITE_BY_TYPE_IF_EXISTS_OR_ADD`, or `APPEND_IF_EXISTS_OR_ADD`.

## Redis, PostgreSQL, and MySQL

### Expanded Redis command set (since 1.36.0)

The Redis proxy adds `COPY`, `RPOPLPUSH`, `SMOVE`, `SUNION`, `SDIFF`, `SINTER`, `SINTERSTORE`, `ZUNIONSTORE`, `ZINTERSTORE`, `PFMERGE`, `GEORADIUS`, `GEORADIUSBYMEMBER`, `RENAME`, `SORT`, `SORT_RO`, `ZMSCORE`, `SDIFFSTORE`, `MSETNX`, `SUBSTR`, `ZRANGESTORE`, `ZUNION`, `ZDIFF`, `SUNIONSTORE`, `SMISMEMBER`, `HRANDFIELD`, `GEOSEARCHSTORE`, `ZDIFFSTORE`, `ZINTER`, `ZRANDMEMBER`, `BITOP`, `LPOS`, and `RENAMENX`.

### PostgreSQL connection inspection (since 1.37.0)

The new Postgres Inspector listener filter detects PostgreSQL connections, extracts metadata, and enables SNI-based routing for PostgreSQL traffic.

### Redis 7.4 hash-field expiry (since 1.39.0)

The Redis proxy adds `HEXPIRE`, `HEXPIREAT`, `HPEXPIRE`, `HPEXPIREAT`, `HPERSIST`, `HTTL`, `HPTTL`, `HEXPIRETIME`, and `HPEXPIRETIME`. Commands declared through `custom_commands` now also work inside `MULTI`/`EXEC` transactions.

### Redis command support (since 1.33.0)

The Redis proxy now supports `KEYS`, `SELECT`, and `UNWATCH`.

### Valkey zone-aware routing and Redis commands (since 1.38.0)

Redis Cluster proxy adds `LOCAL_ZONE_AFFINITY` and `LOCAL_ZONE_AFFINITY_REPLICAS_AND_PRIMARY` read policies plus `enable_zone_discovery` for same-zone routing; this currently works only with Valkey. The proxy also supports `BITFIELD_RO`.

## Reverse tunnels and connection management

### Connection-pressure controls (since 1.38.0)

Listener and cluster `per_connection_buffer_high_watermark_timeout` close connections that stay above their buffer high watermark, with the timeout disabled by default. `envoy.overload_actions.close_idle_http_connections` can shed idle downstream HTTP connections, currently only for HTTP/3, and the CPU-utilization monitor now detects cgroup v1 or v2 automatically.

### Experimental reverse tunnels (since 1.36.0)

Envoy can establish persistent reverse tunnels from downstream Envoy instances to upstream instances that cannot directly reach them, including deployments behind NAT or firewalls; the feature remains experimental.

### Graceful reverse-tunnel draining (since 1.39.0)

`enable_drain_with_goaway` makes a reverse-tunnel initiator replace a tunnel when its peer sends GOAWAY while allowing in-flight streams to finish. Reverse-connection clusters can also opt into a drain-aware upstream HTTP/2 codec through `typed_extension_protocol_options`, allowing peers to fail over before existing tunnels close.

### Reverse-tunnel cluster validation (since 1.37.0)

Reverse-tunnel configuration adds `required_cluster_name`; an initiation whose `x-envoy-reverse-tunnel-upstream-cluster-name` does not match is rejected with `400 Bad Request`.

### Reverse-tunnel tenant isolation (since 1.38.0)

`enable_tenant_isolation` scopes cached reverse-tunnel sockets by `<tenant>@<node>` and `<tenant>@<cluster>` and rejects handshake components that already contain `@`.

