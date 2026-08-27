# Upgrades, builds, and operations

Use this reference for upgrade preparation, removed compatibility paths, source builds, process controls, admin behavior, and file-watching changes.

## Admin and listener-update APIs (since 1.38.0)

The `/clusters` endpoint accepts an RE2 `filter` query parameter, compatible with text or JSON `format`, to select clusters by name. `ListenerManager` adds `ListenerUpdateCallbacks`, paralleling cluster-update callbacks for extension code.

## Admin and log-file controls (since 1.37.0)

Admin `allow_paths` restricts the interface to endpoints matching configured string matchers and returns `403` for all others. Envoy also adds `/memory/tcmalloc` and `--file-flush-min-size-kb <integer>` for TCMalloc diagnostics and minimum log-file flush size.

## Admin and process-log diagnostics (since 1.39.0)

With TCMalloc, `/peak_heap_dump` emits the peak heap profile. `--log-stacktrace-single-entry` keeps a whole stack trace in one log event, `%N` adds the Envoy version to spdlog patterns, and gRPC access logging exposes `grpc_entries_flushed` and `grpc_entries_flush_failed` delivery counters.

## Bazel 8 source builds and DLB availability (since 1.39.0)

Envoy source builds now use Bazel 8 while retaining WORKSPACE mode through `--enable_workspace --noenable_bzlmod`; external-repository runfiles consequently move directly under the runfiles root. The `envoy.network.connection_balance.dlb` contrib extension is disabled at the Bazel layer on every platform.

## Container-aware worker concurrency (since 1.37.0)

On Linux, when `--concurrency` is unset, Envoy now sizes worker threads from the minimum of hardware threads, CPU affinity, and cgroup CPU limits, using conservative floor rounding. Set `ENVOY_CGROUP_CPU_DETECTION=false` to restore hardware-thread and affinity-based sizing.

## DNS-cluster and AWS IAM deprecations (since 1.33.0)

DNS fields directly on strict- or logical-DNS `Cluster` configurations are deprecated; use the `cluster_type` extension with a `DnsCluster` typed config. The `aws_iam` extension is deprecated and scheduled for removal no later than Envoy 1.35.

## In-place watched-directory updates (since 1.39.0)

`WatchedDirectory.watch_modify=true` subscribes to in-place `IN_MODIFY` events as well as atomic `IN_MOVED_TO` replacements. This lets direct certificate-file writes trigger SDS rotation; the default remains rename-only watching.

## io_uring flow-control settings (since 1.39.0)

The io_uring socket interface adds `write_high_watermark_bytes` and `write_low_watermark_bytes`, with existing deployments now applying write backpressure by default at 128 KiB and resuming at 16 KiB. Linux 6.0+ also supports multishot reads using a kernel buffer ring.

## Process limits and build configuration (since 1.35.0)

Envoy now raises its soft file-descriptor limit to the hard limit unless `envoy_restart_features_raise_file_limits` disables this behavior. Source builds use C++20; `--config=clang` selects Clang with `libc++`, `--config=gcc` selects GCC with `libstdc++`, and the old `clang-libstdc++` setup is removed.

## Removed authentication and HTTP filters (since 1.35.0)

The `grpc_credentials/aws_iam` extension has been deleted, so configurations that still reference it fail to load. The contrib Squash HTTP filter has also been removed.

## Removed compatibility controls (since 1.34.0)

Envoy removed the legacy paths and runtime controls `envoy.reloadable_features.consistent_header_validation`, `envoy.reloadable_features.sanitize_http2_headers_without_nghttp2`, `envoy.reloadable_features.upstream_remote_address_use_connection`, `envoy.reloadable_features.xdstp_path_avoid_colon_encoding`, and `envoy.reloadable_features.strict_duration_validation`. It also removed `envoy.reloadable_features.allow_slot_destroy_on_worker_threads`, `envoy.reloadable_features.reject_invalid_yaml`, `envoy.reloadable_features.dns_details`, `envoy.reloadable_features.no_timer_based_rate_limit_token_bucket`, and `envoy.reloadable_features.dns_nodata_noname_is_success`.

## Removed compatibility controls (since 1.35.0)

Envoy removed the legacy paths and guards `envoy.reloadable_features.switch_protocol_websocket_handshake`, `envoy.reloadable_features.http2_no_protocol_error_upon_clean_close`, `envoy.reloadable_features.sanitize_sni_in_access_log`, `envoy.reloadable_features.quic_connect_client_udp_sockets`, `envoy.reloadable_features.quic_support_certificate_compression`, `envoy.reloadable_features.internal_authority_header_validator`, `envoy_reloadable_features_filter_access_loggers_first`, and `envoy.reloadable_features.tcp_tunneling_send_downstream_fin_on_upstream_trailers`. It also removed `envoy_reloadable_features_boolean_to_string_fix`, `envoy.reloadable_features.logging_with_fast_json_formatter`, `envoy.reloadable_features.use_route_host_mutation_for_auto_sni_san`, `envoy.reloadable_features.ext_proc_timeout_error`, `envoy.reloadable_features.extend_h3_accept_untrusted`, `envoy.reloadable_features.lua_flow_control_while_http_call`, and `envoy.reloadable_features.envoy_reloadable_features_http1_use_balsa_parser`.

## Removed compatibility controls (since 1.37.0)

Envoy removed the legacy paths for `envoy.reloadable_features.http1_balsa_disallow_lone_cr_in_chunk_extension`, `envoy.reloadable_features.jwt_fetcher_use_scheme_from_uri`, `envoy.reloadable_features.tcp_proxy_retry_on_different_event_loop`, `envoy.reloadable_features.http1_balsa_delay_reset`, `envoy.reloadable_features.http1_balsa_allow_cr_or_lf_at_request_start`, `envoy.reloadable_features.http3_remove_empty_cookie`, `envoy.reloadable_features.original_src_fix_port_exhaustion`, `envoy.reloadable_features.http2_propagate_reset_events`, `envoy.reloadable_features.report_load_with_rq_issued`, `envoy_restart_features_use_eds_cache_for_ads`, `envoy.restart_features.skip_backing_cluster_check_for_sds`, and `envoy.reloadable_features.router_filter_resetall_on_local_reply`.

## Removed compatibility controls (since 1.38.0)

`envoy.reloadable_features.oauth2_encrypt_tokens` is removed; token cookies remain encrypted unless the OAuth2 filter sets `disable_token_encryption`. `envoy.reloadable_features.tcp_proxy_set_idle_timer_immediately_on_new_connection` and its legacy TCP-proxy behavior are also removed.

## Removed extensions and compatibility switches (since 1.33.0)

The deprecated OpenCensus tracing extension was removed. Envoy also removed these runtime controls and their legacy paths: `envoy_reloadable_features_send_local_reply_when_no_buffer_and_upstream_request`, `envoy.reloadable_features.edf_lb_host_scheduler_init_fix`, `envoy.reloadable_features.edf_lb_locality_scheduler_init_fix`, `envoy.reloadable_features.validate_grpc_header_before_log_grpc_status`, `envoy.reloadable_features.http_route_connect_proxy_by_default`, `envoy.reloadable_features.defer_processing_backedup_streams`, `envoy.reloadable_features.dns_reresolve_on_eai_again`, `envoy.restart_features.sanitize_te`, `envoy.restart_features.quic_handle_certs_with_shared_tls_code`, `envoy.restart_features.allow_client_socket_creation_failure`, `envoy.reloadable_features.use_http_client_to_fetch_aws_credentials`, and `envoy.reloadable_features.exclude_host_in_eds_status_draining`.

## Removed runtime fallbacks (since 1.36.0)

Envoy removed these guards and their legacy paths: `envoy.reloadable_features.shadow_policy_inherit_trace_sampling`, `envoy.reloadable_features.prefer_ipv6_dns_on_macos`, `envoy.reloadable_features.avoid_dfp_cluster_removal_on_cds_update`, `envoy.reloadable_features.oauth2_use_refresh_token`, `envoy.reloadable_features.explicit_internal_address_config`, `envoy.reloadable_features.dfp_fail_on_empty_host_header`, `envoy.reloadable_features.prefer_quic_client_udp_gro`, `envoy.reloadable_features.enable_udp_proxy_outlier_detection`, `envoy.reloadable_features.xds_prevent_resource_copy`, `envoy.reloadable_features.normalize_rds_provider_config`, `envoy.reloadable_features.local_reply_traverses_filter_chain_after_1xx`, `envoy.reloadable_features.report_stream_reset_error_code`, `envoy.reloadable_features.streaming_shadow`, `envoy.reloadable_features.http3_remove_empty_trailers`, `envoy.reloadable_features.enable_include_histograms`, `envoy.reloadable_features.udp_socket_apply_aggregated_read_limit`, `envoy.reloadable_features.proxy_status_mapping_more_core_response_flags`, `envoy.reloadable_features.allow_alt_svc_for_ips`, `envoy.reloadable_features.filter_chain_aborted_can_not_continue`, `envoy.reloadable_features.use_filter_manager_state_for_downstream_end_stream`, `envoy.reloadable_features.wait_for_first_byte_before_balsa_msg_done`, `envoy.reloadable_features.mmdb_files_reload_enabled`, `envoy.reloadable_features.use_typed_metadata_in_proxy_protocol_listener`, `envoy.reloadable_features.getaddrinfo_num_retries`, `envoy.reloadable_features.proxy_ssl_port`, `envoy.reloadable_features.gcp_authn_use_fixed_url`, `envoy.reloadable_features.jwt_authn_remove_jwt_from_query_params`, `envoy.reloadable_features.jwt_authn_validate_uri`, `envoy.restart_features.fix_dispatcher_approximate_now`, `envoy.reloadable_features.use_config_in_happy_eyeballs`, and `envoy.reloadable_features.proxy_104`.

## TCMalloc management and shrink-heap controls (since 1.38.0)

Envoy now uses TCMalloc background actions instead of its timer-based release path, removing `tcmalloc.released_by_timer`; `MemoryAllocatorManager` adds `soft_memory_limit_bytes`, `max_per_cpu_cache_size_bytes`, and `max_unfreed_memory_bytes`. The `envoy.overload_actions.shrink_heap` action accepts `ShrinkHeapConfig` with `timer_interval` (minimum `1s`, default `10s`) and `max_unfreed_memory_bytes` (default `100MB`).

## Validation-mode bootstrap extensions (since 1.38.0)

`--mode validate` now creates bootstrap extensions, so their own configuration is validated and the providers or singletons they register are available to dependent configuration.

