# Security, authentication, and TLS

Use this reference for TLS identity and policy, OAuth2, authorization, credentials, JWTs, and request-hardening controls.

## TLS, certificates, and trust

### Empty trusted-CA rejection (since 1.35.0)

TLS configuration now rejects an empty trusted-CA file or inline value instead of accepting it and validating any certificate chain. The temporary rollback is `envoy.reloadable_features.reject_empty_trusted_ca_file=false`.

### HTTP virtual-host, cookie, and client-certificate matching (since 1.37.0)

`RouteConfiguration.vhost_header` selects an alternate header for virtual-host matching, and route matches can inspect individual cookies structurally. `HttpConnectionManager.forward_client_cert_matcher` selects XFCC handling per request, falling back to the static client-certificate forwarding settings when no action matches.

### MySQL TLS termination and authentication (since 1.39.0)

The MySQL proxy can terminate downstream TLS through the STARTTLS transport socket and mediate MySQL 8 `caching_sha2_password` full authentication using RSA public-key exchange. Its `downstream_ssl` mode is `DISABLE`, `REQUIRE`, or `ALLOW`.

### New access-log and certificate metrics (since 1.35.0)

`ExtAuthzLoggingInfo` exposes `grpc_status`; TCP-tunneling access logs add `%BYTES_RECEIVED%`, `%BYTES_SENT%`, `%UPSTREAM_HEADER_BYTES_SENT%`, `%UPSTREAM_HEADER_BYTES_RECEIVED%`, `%UPSTREAM_WIRE_BYTES_SENT%`, and `%UPSTREAM_WIRE_BYTES_RECEIVED%`. TLS and CA certificate expiry epochs are emitted below `cluster.<cluster_name>.ssl.certificate.<cert_name>.` and `listener.<address>.ssl.certificate.<cert_name>.`.

### SAN matching and RBAC principals (since 1.34.0)

The string-matcher API can receive matching context, initially `StreamInfo` for SAN matching. RBAC adds a more specific mTLS-validation principal and an extension point for custom principals.

### TLS builds and RSA key usage (since 1.38.0)

FIPS builds must replace `--define=boringssl=fips` with `--config=boringssl-fips`; Envoy can also be built against OpenSSL with `--config=openssl`, although that disables HTTP/3 and the resulting build is not covered by Envoy's security policy, and published contrib binaries now report versions ending in `-contrib`. `enforce_rsa_key_usage` now defaults to `true`, making a present but incompatible certificate `keyUsage` extension fail the handshake.

### TLS certificate and upstream-SNI controls (since 1.33.0)

TLS servers now support P-384 and P-521 certificate curves. Upstream TLS can set SNI to the configured hostname and validate certificate SANs against the actual SNI sent, and IP SAN operations now work even when the host OS does not support that IP version.

### TLS certificate selection, compression, and SPIFFE (since 1.38.0)

Upstream TLS can fetch certificates on demand through SDS using the on-demand certificate selector, and active health checks now wait for required upstream TLS SDS secrets unless `envoy.reloadable_features.health_check_after_cluster_warming=false`; SPIFFE validation can select a workload trust domain from per-connection filter state and watch Kubernetes-style atomic file updates through `watched_directory`. Certificate compression adds Brotli for QUIC and Brotli plus zlib for TCP TLS; `envoy.reloadable_features.tls_certificate_compression_brotli=false` restores zlib-only QUIC and no TCP compression.

### TLS certificate-compression default (since 1.39.0)

`envoy.reloadable_features.tls_certificate_compression_brotli` now defaults to disabled, so QUIC uses zlib-only certificate compression and TCP TLS uses none. Set the guard to `true` to restore Brotli support introduced in 1.38.

### TLS ClientHello fingerprinting (since 1.35.0)

The TLS inspector's `enable_ja4_fingerprinting` option computes a JA4 fingerprint from the ClientHello.

### TLS compliance, groups, and CA-list suppression (since 1.39.0)

TLS compliance policy accepts `CNSA1_202603` and `CNSA2_202603`. `%DOWNSTREAM_TLS_GROUP%` and `%UPSTREAM_TLS_GROUP%` expose the negotiated key-exchange group, while `CertificateValidationContext.suppress_client_ca_list` omits trusted CA names from `CertificateRequest` without changing validation, including with the SPIFFE validator.

### TLS identity attributes and logging (since 1.39.0)

CEL adds `connection.peer_certificate_valid` to distinguish presented-and-validated certificates from untrusted certificates accepted by optional mTLS, plus `upstream.server_name` for the established upstream SNI. The same upstream SNI is available to substitution formatting as `%UPSTREAM_SERVER_NAME%`.

### TLS identity exposure (since 1.38.0)

`%DOWNSTREAM_PEER_ISSUER_FINGERPRINT_256%` and `%DOWNSTREAM_PEER_ISSUER_SERIAL%` expose the verified issuer certificate, and the Go HTTP filter adds `DownstreamSslConnection()` for downstream TLS details. Attributes add PEM certificates as `connection.peer_certificate` and `upstream.peer_certificate`, while transport-failure formatters now include CRL distribution points in CRL validation errors.

### TLS inspection, certificate delivery, and diagnostics (since 1.37.0)

TLS Inspector can cap the accepted ClientHello size, and downstream TLS can fetch certificates on demand through SDS with the on-demand certificate selector. SNI and transport-failure reasons are now available for more pre-handshake failures, certificate-validation log reasons are more specific, and SDS recovers automatically when certificate files missing at initial load later appear.

### TLS policy and SPIFFE trust bundles (since 1.34.0)

TLS configuration can enforce a named compliance policy such as FIPS. The SPIFFE certificate validator adds a `trust_bundles` `DataSource` mapping, which takes precedence over `trust_domains` when both are configured.

## OAuth2 and cookies

### OAuth2 client authentication and token forwarding (since 1.39.0)

The OAuth2 filter adds RFC 7523 `PRIVATE_KEY_JWT`, using the PEM private key supplied through `token_secret` to sign the client assertion. `forward_id_token` can forward a validated OIDC ID token as Bearer authorization or in a custom header that Envoy strips from incoming traffic to prevent spoofing; Authorization forwarding is mutually exclusive with bearer-token forwarding and preservation.

### OAuth2 cookie migration to AES-GCM (since 1.39.0)

OAuth2 token-cookie encryption adds an opt-in AES-256-GCM migration for CVE-2026-47775. First enable `envoy.reloadable_features.oauth2_use_gcm_encryption`, wait until every instance can read `gcm.` cookies and `oauth_legacy_cbc_decrypt` falls to zero, then disable `envoy.reloadable_features.oauth2_legacy_cbc_decrypt_compat`; reversing that order invalidates newly issued cookies, while leaving CBC fallback enabled preserves the vulnerable path.

### OAuth2 cookie protection and forwarding (since 1.35.0)

OAuth2 access, ID, and refresh tokens stored in cookies are now encrypted with the HMAC secret; set `envoy.reloadable_features.oauth2_encrypt_tokens=false` to revert temporarily. The `oauth_hmac`, `oauth_expires`, `refresh_token`, `oauth_nonce`, and `code_verifier` cookies are no longer forwarded upstream unless `envoy.reloadable_features.oauth2_cleanup_cookies=false`.

### OAuth2 defaults and CSRF state (since 1.33.0)

`use_refresh_token` now defaults to enabled, with `envoy.reloadable_features.oauth2_use_refresh_token=false` as a temporary rollback. Authorization `state` is now a base64url-encoded JSON object containing the original URL and a nonce, and the nonce uses an HMAC-signed double-submit cookie; `cookie_domain` now also applies to ID-token and refresh-token cookies.

### OAuth2 flows, cookies, and statistics (since 1.34.0)

The OAuth2 filter adds PKCE, sends a configured scope during `client_credentials` token requests, and accepts `strict`, `lax`, or `none` SameSite values for supported cookies; the default `disabled` emits no SameSite attribute. `stat_prefix` distinguishes multiple OAuth2 filters in one chain.

### OAuth2 plaintext mode and cookie behavior (since 1.36.0)

`disable_token_encryption` permits unencrypted ID and access-token storage only for trusted environments, and OAuth2-generated `401` replies now carry response-code details. Requests accepted by `pass_through_matcher` no longer lose cookies needed by later OAuth2 filters, and cookies prefixed `__Secure-` or `__Host-` now receive the `Secure` attribute.

### OAuth2 redirect, logout, and cookie controls (since 1.39.0)

`original_request_uri` can build the post-login destination from formatter values, while `allowed_redirect_domains` allow-lists exact or wildcard hosts across formatted redirects and decoded callback state to prevent open redirects. `post_logout_redirect_uri` controls or disables the OIDC logout parameter, and `use_access_token_expiry_for_id_token_cookie` derives the ID-token cookie lifetime from the token response's `expires_in` instead of the ID token's `exp` claim.

### OAuth2 redirects, logout, and expiry (since 1.35.0)

An invalid CSRF cookie during an authorization redirect is reset instead of failing the flow. `end_session_endpoint` enables RP-initiated OIDC logout when `openid` is in `auth_scopes`, while `csrf_token_expires_in` and `code_verifier_token_expires_in` configure the corresponding lifetimes and default to `600s`.

### OAuth2 routing, client authentication, and graceful failure (since 1.38.0)

The OAuth2 HTTP filter supports per-route configuration and RFC 8705 `TLS_CLIENT_AUTH`; in that mode `token_secret` is optional and ignored, and the token-endpoint cluster must use mTLS. `allow_failed_matcher` can pass failed validation upstream unauthenticated after stripping OAuth cookies and adding `x-envoy-oauth-status: failed` plus `x-envoy-oauth-failure-reason`; matcher precedence is pass-through, allow-failed, deny-redirect, then default behavior.

### OAuth2 token parameters and cookie attributes (since 1.37.0)

OAuth2 `endpoint_params` adds custom token-request body parameters. Each cookie can set `path` and `partitioned`, the latter emitting the CHIPS `Partitioned` attribute for third-party `SameSite=None` scenarios.

## Authorization, RBAC, and request identity

### API-key identity forwarding (since 1.35.0)

API Key Auth can forward the authenticated client identity in a custom header and can remove the API key before sending the request upstream.

### Authentication and metadata sources (since 1.33.0)

A new API Key Auth filter authenticates requests using API keys. RBAC adds `sourced_metadata` so a metadata matcher can name its source, and the old `metadata` field is deprecated in its favor.

### Basic-auth composition and identity metadata (since 1.39.0)

`allow_missing=true` lets requests without Basic credentials continue so Basic Auth can be OR-composed with another authentication filter, while still rejecting invalid Basic credentials. `emit_dynamic_metadata=true` writes the authenticated `username` under `envoy.filters.http.basic_auth` for later RBAC or other filters.

### External-authorization enablement (since 1.34.0)

Ext-authz configuration now accepts `disabled: false`, allowing a filter marked default-disabled for a filter chain to be enabled.

### External-authorization responses and limits (since 1.37.0)

HTTP ext-authz now honors the configured `retry_policy.retry_on`, propagates response headers through `allowed_client_headers` on denial and `allowed_client_headers_on_success` on success, and validates header limits after mutations. `enforce_response_header_limits` controls dropping response headers once count or size limits are reached, `error_response` lets the service return a custom status, headers, and body for internal errors, and gRPC failures now honor `status_on_error`.

### External-authorization routing and denial controls (since 1.36.0)

HTTP `ext_authz` per-route `check_settings.grpc_service` can select a different gRPC authorization backend, HTTP authorization calls accept a `retry_policy`, and `max_denied_response_body_bytes` truncates oversized denial bodies. The network filter's `send_tls_alert_on_denial` sends TLS `access_denied(49)` before close, and an authorization response is rejected if its mutations push the request header count above the configured limit.

### External-authorization shadowing and request controls (since 1.38.0)

HTTP ext-authz adds `shadow_mode`, which always lets the request continue and stores a `ShadowDecision` under `<filter-name>.shadow`, normally `envoy.filters.http.ext_authz.shadow`; `path_override` can replace the authorization request path but is mutually exclusive with `path_prefix`. Logging info adds `requestProcessingEffect()` and `failedOpen()`, denied-response headers now reach the client, and HTTP authorization failures honor `status_on_error`.

### Header-mutation and RBAC hardening (since 1.38.0)

Values inserted by `query_parameter_mutations` are now URL-encoded, including formatter-derived values, under `envoy.reloadable_features.header_mutation_url_encode_query_params`. RBAC can validate repeated header values individually instead of matching their concatenation with `envoy.reloadable_features.rbac_match_headers_individually`.

### Network ext-authz metadata (since 1.37.0)

The network ext-authz filter adds `metadata_context_namespaces` and `typed_metadata_context_namespaces`, allowing connection metadata such as PROXY-protocol TLVs to be included in authorization checks.

### RBAC and server-name matching (since 1.35.0)

HTTP and network RBAC filters now allow `FilterStateInput` in xDS matchers. A trie-based `ServerNameMatcher` is also available for server-name matching.

### Security-sensitive request handling (since 1.33.0)

The custom-header original-IP extension no longer appends XFF automatically, restoring its earlier behavior. The CSRF filter treats `Origin: null` as missing origin information.

### Upstream RBAC and host-selection SSRF checks (since 1.39.0)

The new upstream RBAC HTTP filter evaluates policy after selecting the upstream host but before connecting, so `upstream_ip_port` can enforce default-deny address policy for static, EDS, strict-DNS, and dynamic-forward-proxy subclusters. Custom upstream filters also gain `onHostSelected()` to inspect the chosen host and issue a local rejection before connection establishment.

## JWT and API authentication

### Asynchronous credentials and JWK fetching (since 1.34.0)

AWS request-signing and Lambda extensions now wait while asynchronous credential providers are pending, failing only after all providers cannot retrieve credentials. The JWK fetcher sets `:scheme` from the URI rather than always using HTTP, reversible with `envoy.reloadable_features.jwt_fetcher_use_scheme_from_uri=false`.

### JWT authentication limits and statistics (since 1.34.0)

`jwt_max_token_size` makes the accepted JWT size limit configurable, and `stat_prefix` distinguishes multiple JWT authentication filters in one chain.

### JWT extraction without validation (since 1.37.0)

JWT authentication adds `extract_only_without_validation`, which extracts claims and forwards them as headers without verifying the token signature.

### Unverified-JWT signaling (since 1.39.0)

For `ExtractOnlyWithoutValidation`, `verification_status_header` names a request header that is set to `false` when an extracted JWT fails signature verification; it defaults to `x-jwt-signature-verified`. The header is absent for valid or missing tokens, and `envoy.reloadable_features.jwt_authn_add_verification_status_header=false` disables it.

## Cloud credentials and request signing

### AWS credential chains (since 1.35.0)

AWS request signing can build a fully customized chain from every defined `AwsCredentialProvider`. AWS common components also add IAM Roles Anywhere support and `assume_role_credential_provider` for an additional role-assumption step before SigV4 signing.

### AWS credential selection (since 1.33.0)

The AWS request-signing filter adds `credential_provider` to select the credential source and override credential-file or `AssumeRoleWithWebIdentity` behavior.

### AWS signing controls and token rotation (since 1.37.0)

AWS request signing adds `match_included_headers` for positive header selection while excluding other non-required headers. Web-identity token file watching now picks up rotated tokens.

### GCE metadata credentials (since 1.39.0)

The GCP authentication filter can fetch and inject bound access tokens, bound JWTs, or unbound access tokens from the GCE Metadata Server through the respective `Audience` fields `bound_access_token`, `bound_jwt`, and `access_token`.

### Redis commands and AWS authentication (since 1.35.0)

The Redis proxy adds `SCAN`, `INFO`, and `ROLE` command support and can authenticate to Redis with AWS IAM.

### Redis proxy commands and credentials (since 1.37.0)

The Redis proxy adds `HELLO` and `OBJECT`, and it can use separate credentials for each upstream Redis cluster.

## Security-sensitive identity and forwarding

### Original host preservation (since 1.35.0)

The router filter records the host value from before its mutation in `x-envoy-original-host`.

