# External processing and authorization

Use this reference for HTTP and network external processing, external authorization, processor lifecycle, failure handling, and response mutation.

## External processing transport and sampling (since 1.33.0)

The `ext_proc` filter can now exchange external-processing messages over HTTP. Its generated tracing spans no longer default to always sampled; they inherit the parent span's decision.

## External-authorization enablement (since 1.34.0)

Ext-authz configuration now accepts `disabled: false`, allowing a filter marked default-disabled for a filter chain to be enabled.

## External-authorization responses and limits (since 1.37.0)

HTTP ext-authz now honors the configured `retry_policy.retry_on`, propagates response headers through `allowed_client_headers` on denial and `allowed_client_headers_on_success` on success, and validates header limits after mutations. `enforce_response_header_limits` controls dropping response headers once count or size limits are reached, `error_response` lets the service return a custom status, headers, and body for internal errors, and gRPC failures now honor `status_on_error`.

## External-authorization routing and denial controls (since 1.36.0)

HTTP `ext_authz` per-route `check_settings.grpc_service` can select a different gRPC authorization backend, HTTP authorization calls accept a `retry_policy`, and `max_denied_response_body_bytes` truncates oversized denial bodies. The network filter's `send_tls_alert_on_denial` sends TLS `access_denied(49)` before close, and an authorization response is rejected if its mutations push the request header count above the configured limit.

## External-authorization shadowing and request controls (since 1.38.0)

HTTP ext-authz adds `shadow_mode`, which always lets the request continue and stores a `ShadowDecision` under `<filter-name>.shadow`, normally `envoy.filters.http.ext_authz.shadow`; `path_override` can replace the authorization request path but is mutually exclusive with `path_prefix`. Logging info adds `requestProcessingEffect()` and `failedOpen()`, denied-response headers now reach the client, and HTTP authorization failures honor `status_on_error`.

## External-processing composition and headers (since 1.38.0)

Multiple ext-proc filters can coexist in one chain under `envoy.reloadable_features.ext_proc_inject_data_with_state_update`, and `allow_content_length_header` lets the original `Content-Length` survive or be changed by the processor. `ExtProcLoggingInfo` adds `received_immediate_response`, while `processing_effect_lib` moves from `extensions/filters/http/ext_proc` to `extensions/filters/common/processing_effect`.

## External-processing failure and request controls (since 1.36.0)

`ext_proc` once again permits `failure_mode_allow` with `FULL_DUPLEX_STREAMED`; fail-open saves the processor's actual gRPC failure status in filter state. `status_on_error` replaces the fixed downstream `500`, and the per-route-capable `ProcessingRequestModifier` extension can alter a `ProcessingRequest` before transmission.

## External-processing failure policy (since 1.35.0)

A spurious `ext_proc` response now follows `failure_mode_allow` for fail-open versus fail-close behavior; `envoy.reloadable_features.ext_proc_fail_close_spurious_resp=false` restores the old handling temporarily. Routes can now override `failure_mode_allow`.

## External-processing lifecycle and responses (since 1.37.0)

Ext-proc closes its gRPC stream once no further processing is needed outside buffered modes; disable this with `envoy.reloadable_features.ext_proc_stream_close_optimization=false`. It also adds `StreamedImmediateResponse`, cluster-metadata forwarding, response-attribute remapping through `MappedAttributeBuilder`, and per-event mutation effects in `ExtProcLoggingInfo.processingEffects`.

## External-processing override and body modes (since 1.34.0)

For `ext_proc` mode overrides, an unset headers or trailers mode (`DEFAULT`) leaves the filter's configured processing mode unchanged, and `request_header_mode` is ignored when checking `allowed_override_modes`. The filter also adds the `FULL_DUPLEX_STREAMED` body mode.

## External-processing shutdown, local replies, and filter state (since 1.34.0)

Graceful gRPC side-stream half-close is opt-in with `envoy.reloadable_features.ext_proc_graceful_grpc_close=true`; its remote-close timeout defaults to one second and is controlled by `envoy.filters.http.ext_proc.remote_close_timeout_milliseconds`. Local replies are no longer sent to the processor by default, with `envoy_reloadable_features_skip_ext_proc_on_local_reply=false` as a rollback, and an extension can save the processor response to filter state.

## External-processing startup failures (since 1.39.0)

If the HTTP ext-proc filter cannot create its gRPC client, it now reports `INTERNAL` and obeys `failure_mode_allow` instead of silently ignoring the error. `envoy.reloadable_features.ext_proc_report_client_creation_error=false` restores the old behavior temporarily.

## Network ext-authz metadata (since 1.37.0)

The network ext-authz filter adds `metadata_context_namespaces` and `typed_metadata_context_namespaces`, allowing connection metadata such as PROXY-protocol TLVs to be included in authorization checks.

## Network external-processing controls (since 1.39.0)

A network external processor can set `ProcessingResponse.close_stream_to_ext_proc_server` to close its gRPC stream early and let later traffic bypass the filter. `receiving_namespaces` also permits untyped dynamic metadata to flow back from the processor.

## UDP external authorization (since 1.39.0)

The UDP proxy adds an `ext_authz` session filter that calls the gRPC Authorization API when a new UDP session is created.

