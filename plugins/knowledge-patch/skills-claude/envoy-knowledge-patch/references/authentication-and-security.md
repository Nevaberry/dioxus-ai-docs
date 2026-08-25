# Authentication and security

Use this reference for OAuth2, JWT, API keys, credentials, RBAC, request hardening, authorization-adjacent identity, and security-sensitive migrations.

## API-key identity forwarding (since 1.35.0)

API Key Auth can forward the authenticated client identity in a custom header and can remove the API key before sending the request upstream.

## Asynchronous credentials and JWK fetching (since 1.34.0)

AWS request-signing and Lambda extensions now wait while asynchronous credential providers are pending, failing only after all providers cannot retrieve credentials. The JWK fetcher sets `:scheme` from the URI rather than always using HTTP, reversible with `envoy.reloadable_features.jwt_fetcher_use_scheme_from_uri=false`.

## Authentication and metadata sources (since 1.33.0)

A new API Key Auth filter authenticates requests using API keys. RBAC adds `sourced_metadata` so a metadata matcher can name its source, and the old `metadata` field is deprecated in its favor.

## AWS credential chains (since 1.35.0)

AWS request signing can build a fully customized chain from every defined `AwsCredentialProvider`. AWS common components also add IAM Roles Anywhere support and `assume_role_credential_provider` for an additional role-assumption step before SigV4 signing.

## AWS credential selection (since 1.33.0)

The AWS request-signing filter adds `credential_provider` to select the credential source and override credential-file or `AssumeRoleWithWebIdentity` behavior.

## AWS signing controls and token rotation (since 1.37.0)

AWS request signing adds `match_included_headers` for positive header selection while excluding other non-required headers. Web-identity token file watching now picks up rotated tokens.

## Basic-auth composition and identity metadata (since 1.39.0)

`allow_missing=true` lets requests without Basic credentials continue so Basic Auth can be OR-composed with another authentication filter, while still rejecting invalid Basic credentials. `emit_dynamic_metadata=true` writes the authenticated `username` under `envoy.filters.http.basic_auth` for later RBAC or other filters.

## Deployment and credential-provider behavior (since 1.36.0)

The distroless image now runs as nonroot. The `AssumeRole` credentials provider now honors session name, session duration, and `external_id`.

## Dynamic-forward-proxy DNS and SSRF controls (since 1.39.0)

`DnsCacheConfig.resolved_address_filter` removes addresses in configured CIDR ranges from DNS results, providing DNS-layer SSRF protection. Dynamic forward-proxy subclusters can also use `sub_clusters_config.dns_cluster_config` to create `envoy.cluster.dns` clusters with explicit TTL, refresh, failure-backoff, lookup-family, and resolver controls, while `DnsCluster.dns_min_refresh_rate` floors refresh intervals derived from very short DNS TTLs.

## GCE metadata credentials (since 1.39.0)

The GCP authentication filter can fetch and inject bound access tokens, bound JWTs, or unbound access tokens from the GCE Metadata Server through the respective `Audience` fields `bound_access_token`, `bound_jwt`, and `access_token`.

## Header-mutation and RBAC hardening (since 1.38.0)

Values inserted by `query_parameter_mutations` are now URL-encoded, including formatter-derived values, under `envoy.reloadable_features.header_mutation_url_encode_query_params`. RBAC can validate repeated header values individually instead of matching their concatenation with `envoy.reloadable_features.rbac_match_headers_individually`.

## JWT authentication limits and statistics (since 1.34.0)

`jwt_max_token_size` makes the accepted JWT size limit configurable, and `stat_prefix` distinguishes multiple JWT authentication filters in one chain.

## JWT extraction without validation (since 1.37.0)

JWT authentication adds `extract_only_without_validation`, which extracts claims and forwards them as headers without verifying the token signature.

## OAuth2 client authentication and token forwarding (since 1.39.0)

The OAuth2 filter adds RFC 7523 `PRIVATE_KEY_JWT`, using the PEM private key supplied through `token_secret` to sign the client assertion. `forward_id_token` can forward a validated OIDC ID token as Bearer authorization or in a custom header that Envoy strips from incoming traffic to prevent spoofing; Authorization forwarding is mutually exclusive with bearer-token forwarding and preservation.

## OAuth2 cookie migration to AES-GCM (since 1.39.0)

OAuth2 token-cookie encryption adds an opt-in AES-256-GCM migration for CVE-2026-47775. First enable `envoy.reloadable_features.oauth2_use_gcm_encryption`, wait until every instance can read `gcm.` cookies and `oauth_legacy_cbc_decrypt` falls to zero, then disable `envoy.reloadable_features.oauth2_legacy_cbc_decrypt_compat`; reversing that order invalidates newly issued cookies, while leaving CBC fallback enabled preserves the vulnerable path.

## OAuth2 cookie protection and forwarding (since 1.35.0)

OAuth2 access, ID, and refresh tokens stored in cookies are now encrypted with the HMAC secret; set `envoy.reloadable_features.oauth2_encrypt_tokens=false` to revert temporarily. The `oauth_hmac`, `oauth_expires`, `refresh_token`, `oauth_nonce`, and `code_verifier` cookies are no longer forwarded upstream unless `envoy.reloadable_features.oauth2_cleanup_cookies=false`.

## OAuth2 defaults and CSRF state (since 1.33.0)

`use_refresh_token` now defaults to enabled, with `envoy.reloadable_features.oauth2_use_refresh_token=false` as a temporary rollback. Authorization `state` is now a base64url-encoded JSON object containing the original URL and a nonce, and the nonce uses an HMAC-signed double-submit cookie; `cookie_domain` now also applies to ID-token and refresh-token cookies.

## OAuth2 flows, cookies, and statistics (since 1.34.0)

The OAuth2 filter adds PKCE, sends a configured scope during `client_credentials` token requests, and accepts `strict`, `lax`, or `none` SameSite values for supported cookies; the default `disabled` emits no SameSite attribute. `stat_prefix` distinguishes multiple OAuth2 filters in one chain.

## OAuth2 plaintext mode and cookie behavior (since 1.36.0)

`disable_token_encryption` permits unencrypted ID and access-token storage only for trusted environments, and OAuth2-generated `401` replies now carry response-code details. Requests accepted by `pass_through_matcher` no longer lose cookies needed by later OAuth2 filters, and cookies prefixed `__Secure-` or `__Host-` now receive the `Secure` attribute.

## OAuth2 redirect, logout, and cookie controls (since 1.39.0)

`original_request_uri` can build the post-login destination from formatter values, while `allowed_redirect_domains` allow-lists exact or wildcard hosts across formatted redirects and decoded callback state to prevent open redirects. `post_logout_redirect_uri` controls or disables the OIDC logout parameter, and `use_access_token_expiry_for_id_token_cookie` derives the ID-token cookie lifetime from the token response's `expires_in` instead of the ID token's `exp` claim.

## OAuth2 redirects, logout, and expiry (since 1.35.0)

An invalid CSRF cookie during an authorization redirect is reset instead of failing the flow. `end_session_endpoint` enables RP-initiated OIDC logout when `openid` is in `auth_scopes`, while `csrf_token_expires_in` and `code_verifier_token_expires_in` configure the corresponding lifetimes and default to `600s`.

## OAuth2 routing, client authentication, and graceful failure (since 1.38.0)

The OAuth2 HTTP filter supports per-route configuration and RFC 8705 `TLS_CLIENT_AUTH`; in that mode `token_secret` is optional and ignored, and the token-endpoint cluster must use mTLS. `allow_failed_matcher` can pass failed validation upstream unauthenticated after stripping OAuth cookies and adding `x-envoy-oauth-status: failed` plus `x-envoy-oauth-failure-reason`; matcher precedence is pass-through, allow-failed, deny-redirect, then default behavior.

## OAuth2 token parameters and cookie attributes (since 1.37.0)

OAuth2 `endpoint_params` adds custom token-request body parameters. Each cookie can set `path` and `partitioned`, the latter emitting the CHIPS `Partitioned` attribute for third-party `SameSite=None` scenarios.

## RBAC and server-name matching (since 1.35.0)

HTTP and network RBAC filters now allow `FilterStateInput` in xDS matchers. A trie-based `ServerNameMatcher` is also available for server-name matching.

## SAN matching and RBAC principals (since 1.34.0)

The string-matcher API can receive matching context, initially `StreamInfo` for SAN matching. RBAC adds a more specific mTLS-validation principal and an extension point for custom principals.

## Security-sensitive request handling (since 1.33.0)

The custom-header original-IP extension no longer appends XFF automatically, restoring its earlier behavior. The CSRF filter treats `Origin: null` as missing origin information.

## Unverified-JWT signaling (since 1.39.0)

For `ExtractOnlyWithoutValidation`, `verification_status_header` names a request header that is set to `false` when an extracted JWT fails signature verification; it defaults to `x-jwt-signature-verified`. The header is absent for valid or missing tokens, and `envoy.reloadable_features.jwt_authn_add_verification_status_header=false` disables it.

## Upstream RBAC and host-selection SSRF checks (since 1.39.0)

The new upstream RBAC HTTP filter evaluates policy after selecting the upstream host but before connecting, so `upstream_ip_port` can enforce default-deny address policy for static, EDS, strict-DNS, and dynamic-forward-proxy subclusters. Custom upstream filters also gain `onHostSelected()` to inspect the chosen host and issue a local rejection before connection establishment.

