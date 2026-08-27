# TLS, QUIC, and networking

Use this reference for TLS policy and certificates, QUIC, listeners, TCP and UDP proxying, PROXY protocol, sockets, namespaces, and connection transport.

## c-ares UDP-channel rotation (since 1.36.0)

The c-ares resolver's `max_udp_channel_duration` periodically recreates the UDP channel to avoid stale socket state and distribute queries across UDP ports.

## Delayed TCP connections and reset propagation (since 1.38.0)

TCP proxy configurations using `upstream_connect_mode` values other than `IMMEDIATE` must now set `max_early_data_bytes` explicitly; use `0` to retain delayed connection establishment without buffering early data. Tunneling also propagates upstream TCP resets downstream, controlled temporarily by `envoy.reloadable_features.propagate_upstream_rst_through_tunneled_tcp_proxy` and `envoy.reloadable_features.map_http_stream_reset_to_tcp_rst`.

## Directional listener draining (since 1.34.0)

The admin `/drain_listeners` endpoint can combine its `inbound_only` and graceful query parameters, enabling graceful draining limited to inbound listeners.

## Downstream transport controls (since 1.35.0)

The PostgreSQL proxy can require downstream SSL. Listener socket addresses add `network_namespace_filepath` for opening the listener in a specified network namespace.

## Empty trusted-CA rejection (since 1.35.0)

TLS configuration now rejects an empty trusted-CA file or inline value instead of accepting it and validating any certificate chain. The temporary rollback is `envoy.reloadable_features.reject_empty_trusted_ca_file=false`.

## Experimental reverse tunnels (since 1.36.0)

Envoy can establish persistent reverse tunnels from downstream Envoy instances to upstream instances that cannot directly reach them, including deployments behind NAT or firewalls; the feature remains experimental.

## Fair-share bandwidth and connection jitter (since 1.39.0)

The new HTTP bandwidth-share filter fairly divides request and response bandwidth among weighted tenants with filter-chain or per-route limits. `HttpConnectionManager.drain_timeout_jitter` and `HttpProtocolOptions.max_connection_duration_jitter` randomize drain and maximum-duration deadlines to stagger reconnects.

## HTTP virtual-host, cookie, and client-certificate matching (since 1.37.0)

`RouteConfiguration.vhost_header` selects an alternate header for virtual-host matching, and route matches can inspect individual cookies structurally. `HttpConnectionManager.forward_client_cert_matcher` selects XFCC handling per request, falling back to the static client-certificate forwarding settings when no action matches.

## HTTP/1.1 proxy CONNECT formatting (since 1.36.0)

The HTTP/1.1 proxy transport socket now sends RFC 9110 `CONNECT` requests with a `Host` header by default and prefers `hostname:port` over `IP:port` when endpoint metadata provides a hostname. Set `envoy.reloadable_features.http_11_proxy_connect_legacy_format=true` to temporarily restore the headerless format.

## HTTP/2 and QUIC resource tuning (since 1.37.0)

`enable_huffman_encoding` controls HTTP/2 header Huffman encoding. QUIC `max_sessions_per_event_loop` caps new sessions per event-loop iteration and defaults to the prior hard-coded value of `16`.

## Linux worker and socket locality (since 1.39.0)

`enable_worker_cpu_affinity` pins Linux worker threads to CPUs in the process affinity mask. With affinity and reuse-port enabled, listener `cpu_locality_balance` can steer connections to the worker on the receiving CPU; a separate sockmap socket interface can accelerate same-host TCP on Linux 4.18+ while falling back to normal TCP for remote peers.

## Listener keepalive controls (since 1.37.0)

Primary and additional listener addresses accept `tcp_keepalive`; additional addresses inherit the listener setting unless overridden. Setting any keepalive field to `0` disables keepalive for the applicable address.

## Listener socket options and file-backed SDS secrets (since 1.34.0)

Socket options attached only to an additional listener address are now applied even when the listener itself has no `socket_options`. SDS now watches file-backed `GenericSecret` resources for changes.

## Mandatory RSA key-usage and TLS-version checks (since 1.39.0)

`enforce_rsa_key_usage` is now deprecated and ignored: peer certificates always have their `keyUsage` extension enforced, even when configuration says `false`. TLS Inspector also rejects ClientHello versions outside TLS 1.0–1.3 unless `envoy.reloadable_features.tls_inspector_enforce_client_tls_version=false` temporarily restores the old behavior.

## Network-namespace and post-handshake filter state (since 1.37.0)

Connections accepted on a listener with `network_namespace_filepath` now expose read-only `envoy.network.network_namespace` filter state, and a shared filter-state extension can override the upstream bind-address Linux namespace. The Set Filter State network filter also adds `on_downstream_tls_handshake`, allowing values such as peer-certificate SANs to be populated only after TLS completes.

## Network-namespace matching (since 1.36.0)

`NetworkNamespaceInput` exposes a listener socket's `network_namespace_filepath` to `filter_chain_matcher` and network or HTTP RBAC matchers; it yields an empty value on non-Linux platforms, causing default-filter-chain selection. The TLS inspector also publishes dynamic metadata when `ClientHello` parsing fails.

## Proxy buffering and HTTP/3 connection behavior (since 1.36.0)

The generic-proxy codec now disconnects when its buffer, sized to the connection buffer limit, is exceeded; set `envoy.reloadable_features.generic_proxy_codec_buffer_limit=false` to revert. Upstream HTTP/3 Happy Eyeballs is now disabled through `envoy.reloadable_features.http3_happy_eyeballs`, while Envoy Mobile drains connections on network changes independently of DNS refresh unless `envoy.reloadable_features.decouple_explicit_drain_pools_and_dns_refresh=false`.

## Proxy Protocol v2 custom TLVs (since 1.34.0)

Upstream transport sockets can add custom TLVs from endpoint typed metadata in `envoy.transport_sockets.proxy_protocol` or from `ProxyProtocolConfig.added_tlvs`, with host entries overriding configuration entries of the same type. TCP proxy's `proxy_protocol_tlvs` adds TLVs to the Proxy Protocol state that is emitted in the upstream v2 header.

## PROXY-protocol binary TLVs (since 1.39.0)

`encoding: BASE64` stores a PROXY-protocol TLV's raw bytes as base64 in dynamic metadata or filter state. The default continues to sanitize the value as UTF-8.

## PROXY-protocol TLV handling (since 1.37.0)

Duplicate PROXY protocol v2 TLVs with the same key are now retained unless `envoy.reloadable_features.proxy_protocol_allow_duplicate_tlvs=false`. `tlv_location=FILTER_STATE` stores TLVs under `envoy.network.proxy_protocol.tlv`, where a value is addressable as `%FILTER_STATE(envoy.network.proxy_protocol.tlv:FIELD:key)%`; the default remains `DYNAMIC_METADATA`.

## QUIC key logging and session resumption (since 1.39.0)

QUIC can emit NSS TLS key-log lines with the same IP-list filtering as TCP TLS when `key_log` is configured and `envoy.restart_features.quic_keylog_support=true`. It can also resume sessions across instances from configured `session_ticket_keys` when `envoy.reloadable_features.quic_session_ticket_support=true`; both guards default to disabled.

## QUIC SCONE support (since 1.38.0)

`QuicProtocolOptions.enable_scone` enables SCONE, while Envoy Mobile adds `EngineBuilder.enableScone()` and reports SCONE bandwidth and timestamp data through `scone_max_kbps` and `scone_timestamp_ms`.

## QUIC-LB connection IDs (since 1.34.0)

A new extension provides draft QUIC-LB connection-ID generation.

## QUIC-LB server identifiers (since 1.36.0)

QUIC-LB configuration can now use a base64-encoded server ID.

## Socket and network-filter extension points (since 1.34.0)

The default socket interface gains an `io_uring` option. `ExtensionWithMatcher` can wrap network filters with only `SkipFilter` supported; when enabled, `envoy.reloadable_features.connection_close_through_filter_manager` lets a network filter prevent connection close, and the guard defaults to false.

## TCP proxy idle-timeout start (since 1.36.0)

The downstream idle timer now starts as soon as a TCP proxy connection is created, including while its upstream connection is still pending; set `envoy.reloadable_features.tcp_proxy_set_idle_timer_immediately_on_new_connection=false` to restore the old timing temporarily.

## TCP tunneling identity and transport metadata (since 1.36.0)

TCP proxy tunneling can generate and propagate request IDs with `request_id_extension`; `request_id_header` and `request_id_metadata_key` override the defaults `x-request-id` and `tunnel_request_id`. PROXY-protocol TLVs can obtain dynamic values from a `format_string`, and `max_downstream_connection_duration_jitter_percentage` spreads configured downstream connection expiry.

## TCP-proxy connection timing (since 1.37.0)

TCP proxy adds `upstream_connect_mode` and `max_early_data_bytes` to control when the upstream connection opens and how much early data is buffered, permitting inspection of SNI or certificate data before connecting upstream.

## TCP-proxy route, drain, and duration controls (since 1.39.0)

`envoy.reloadable_features.tcp_proxy_delay_route_selection` delays route choice until immediately before the upstream connection, according to `upstream_connect_mode`. `check_drain_close` closes downstream connections with `FlushWrite` when draining, and TCP access logs now populate `COMMON_DURATION` points `DS_CX_BEG`, `DS_CX_END`, `US_CX_BEG`, and `US_CX_END`.

## TLS builds and RSA key usage (since 1.38.0)

FIPS builds must replace `--define=boringssl=fips` with `--config=boringssl-fips`; Envoy can also be built against OpenSSL with `--config=openssl`, although that disables HTTP/3 and the resulting build is not covered by Envoy's security policy, and published contrib binaries now report versions ending in `-contrib`. `enforce_rsa_key_usage` now defaults to `true`, making a present but incompatible certificate `keyUsage` extension fail the handshake.

## TLS certificate and upstream-SNI controls (since 1.33.0)

TLS servers now support P-384 and P-521 certificate curves. Upstream TLS can set SNI to the configured hostname and validate certificate SANs against the actual SNI sent, and IP SAN operations now work even when the host OS does not support that IP version.

## TLS certificate selection, compression, and SPIFFE (since 1.38.0)

Upstream TLS can fetch certificates on demand through SDS using the on-demand certificate selector, and active health checks now wait for required upstream TLS SDS secrets unless `envoy.reloadable_features.health_check_after_cluster_warming=false`; SPIFFE validation can select a workload trust domain from per-connection filter state and watch Kubernetes-style atomic file updates through `watched_directory`. Certificate compression adds Brotli for QUIC and Brotli plus zlib for TCP TLS; `envoy.reloadable_features.tls_certificate_compression_brotli=false` restores zlib-only QUIC and no TCP compression.

## TLS certificate-compression default (since 1.39.0)

`envoy.reloadable_features.tls_certificate_compression_brotli` now defaults to disabled, so QUIC uses zlib-only certificate compression and TCP TLS uses none. Set the guard to `true` to restore Brotli support introduced in 1.38.

## TLS ClientHello fingerprinting (since 1.35.0)

The TLS inspector's `enable_ja4_fingerprinting` option computes a JA4 fingerprint from the ClientHello.

## TLS compliance, groups, and CA-list suppression (since 1.39.0)

TLS compliance policy accepts `CNSA1_202603` and `CNSA2_202603`. `%DOWNSTREAM_TLS_GROUP%` and `%UPSTREAM_TLS_GROUP%` expose the negotiated key-exchange group, while `CertificateValidationContext.suppress_client_ca_list` omits trusted CA names from `CertificateRequest` without changing validation, including with the SPIFFE validator.

## TLS identity exposure (since 1.38.0)

`%DOWNSTREAM_PEER_ISSUER_FINGERPRINT_256%` and `%DOWNSTREAM_PEER_ISSUER_SERIAL%` expose the verified issuer certificate, and the Go HTTP filter adds `DownstreamSslConnection()` for downstream TLS details. Attributes add PEM certificates as `connection.peer_certificate` and `upstream.peer_certificate`, while transport-failure formatters now include CRL distribution points in CRL validation errors.

## TLS inspection, certificate delivery, and diagnostics (since 1.37.0)

TLS Inspector can cap the accepted ClientHello size, and downstream TLS can fetch certificates on demand through SDS with the on-demand certificate selector. SNI and transport-failure reasons are now available for more pre-handshake failures, certificate-validation log reasons are more specific, and SDS recovers automatically when certificate files missing at initial load later appear.

## TLS policy and SPIFFE trust bundles (since 1.34.0)

TLS configuration can enforce a named compliance policy such as FIPS. The SPIFFE certificate validator adds a `trust_bundles` `DataSource` mapping, which takes precedence over `trust_domains` when both are configured.

## Transport-socket and composite cluster selection (since 1.37.0)

Cluster `transport_socket_matcher` uses the xDS matcher framework to select a named entry from `transport_socket_matches` using endpoint metadata, locality metadata, or transport-socket filter state. The new composite cluster selects successive sub-clusters by retry attempt and fails once attempts exceed its configured cluster list.

## WebSocket response handling and timeouts (since 1.36.0)

WebSocket handshake `4xx` and `5xx` responses now pass through the filter chain, and route plus per-try timeouts apply while waiting for an upgrade response. Set `envoy.reloadable_features.websocket_allow_4xx_5xx_through_filter_chain=false` or `envoy.reloadable_features.websocket_enable_timeout_on_upgrade_response=false` to disable the respective behavior.

