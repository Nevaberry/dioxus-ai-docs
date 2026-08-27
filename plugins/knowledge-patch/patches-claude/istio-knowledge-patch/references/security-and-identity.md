# Security, identity, and certificates

Use this reference for authentication, authorization, certificate sources,
control-plane TLS, and extension-fetch hardening. Treat compatibility escape
hatches that disable authentication as temporary measures.

## AuthorizationPolicy behavior

- (`1.25.0`) Multiple port-level `STRICT` rules in an ambient
  `PeerAuthentication` now enforce strict mTLS rather than combining into an
  effectively permissive policy.
- (`1.25.0`) `istioctl x authz check` understands `AuthorizationPolicy` objects
  whose action is `CUSTOM`.
- (`upgrade-1.29`) Experimental ztunnel dry-run authorization is enabled with
  `AMBIENT_ENABLE_DRY_RUN_AUTHORIZATION_POLICY=true` on istiod. Enable it only
  after every connected ztunnel is at least 1.29; older ztunnels fully enforce
  the policy.
- (`1.30.0`) A workload may use multiple `CUSTOM` authorization providers, for
  example to apply different authentication schemes to different paths.
- (`1.30.0`) Regex metacharacters in AuthorizationPolicy service-account names,
  source principals, and source namespaces are treated literally, avoiding
  unintended identity matches.

## Debug endpoint authorization

- (`upgrade-1.29`) Debug endpoint authorization is enabled by default.
  Non-system namespaces can access only `config_dump`, `ndsz`, and `edsz`, and
  only for proxies in their own namespace. Kiali and custom monitoring clients
  may need updated permissions. `ENABLE_DEBUG_ENDPOINT_AUTH=false` restores
  unrestricted behavior.
- (`upgrade-1.30`) Authentication also applies to plaintext `syncz` and
  `config_dump` xDS endpoints on port 15010, affecting
  `istioctl --plaintext` and custom xDS clients.
- (`1.30.0`) With `ENABLE_DEBUG_ENDPOINT_AUTH=true`, set
  `DEBUG_ENDPOINT_AUTH_ALLOWED_NAMESPACES` to a comma-separated namespace
  allowlist. The system namespace is always authorized.

## JWT authentication and JWKS fetching

- (`1.27.0`) A JWT rule may omit `issuer` only when it supplies an explicit
  `jwksUri`, supporting dynamic token issuers without ambiguous key discovery.
- (`1.28.0`) `RequestAuthentication` supports custom
  `spaceDelimitedClaims` in addition to built-in `scope` and `permission`; the
  configured values are passed correctly to Envoy's JWT filter.
- (`1.29.0`) JWKS fetching can block CIDRs. If any address resolved for the URI
  is blocked, Istio skips the fetch and substitutes a fake JWKS so
  JWT-authenticated requests fail closed.
- (`1.30.0`) The failed-fetch JWKS fallback no longer exposes an RSA private
  key. CIDR blocking occurs after DNS resolution and follows redirects and
  issuer discovery, so those paths cannot bypass the blocked ranges.

## Wasm extension safety

- (`1.25.0`) A Wasm image fetch failure with `failStrategy: FAIL_CLOSE` installs
  a deny-all RBAC filter, not an allow-all filter.
- (`1.30.0`) `ISTIO_WASM_MAX_BINARY_SIZE_BYTES` sets the Wasm binary limit. The
  limit is enforced after gzip decompression for HTTP-fetched modules.
- (`1.30.0`) Bearer-token realm URLs encountered while fetching `WasmPlugin`
  images are validated to prevent server-side request forgery.

## Certificate references

- (`1.26.0`) A `DestinationRule` in `SIMPLE` TLS mode can reference a
  `ConfigMap` as well as a `Secret`, which permits CA-only material outside a
  Secret.
- (`1.26.0`) File-based certificate references in `DestinationRule`, `Gateway`,
  and similar resources work when SPIRE is the certificate authority.
- (`1.27.0`) Gateway TLS configuration supports external Secret Discovery
  Service providers.
- (`1.28.0`) `ServerTLSSettings.caCertCredentialName` can reference a `Secret`
  or `ConfigMap` containing CA certificates for mutual TLS.
- (`upgrade-1.27`) Istio and Kubernetes Gateway resources can present multiple
  certificate types, including RSA and ECDSA, so clients negotiate a supported
  type.
- (`1.26.0`) `istioctl create-remote-secret --tls-server-name <name>` writes
  `tls-server-name` into the kubeconfig, allowing certificate validation when
  the kubeconfig server is a gateway proxy hostname.

## Cluster trust bundles and CA propagation

- (`1.26.0`) Experimental Kubernetes v1alpha1 `ClusterTrustBundle` support
  requires `values.pilot.env.ENABLE_CLUSTER_TRUST_BUNDLE_API=true` and the
  matching Kubernetes feature gates.
- (`1.27.0`) On Kubernetes 1.33 and later, the integration uses stable
  `certificates.k8s.io/v1beta1` rather than `v1alpha1`.
- (`1.27.0`) Istiod validates that a `cacerts` bundle contains every required
  CA file and returns an error for an incomplete bundle instead of silently
  using its self-signed CA.
- (`1.27.0`) With a plugged-in CA, istiod watches `ca-crl.pem`, distributes the
  certificate revocation list to every namespace, and configures proxies to
  reject revoked certificates.
- (`1.27.0`) `values.global.trustBundleName` selects the ConfigMap used to
  propagate the root CA, allowing overlapping control planes to use separate
  trust-bundle objects.
- (`1.29.0`) `values.pilot.crlConfigMapName` selects the CRL distribution
  ConfigMap, likewise separating control planes that share namespaces.
- (`1.29.0`) The node agent watches certificate secrets exposed through
  symlinks and detects changes to their targets.

## TLS policy and gateway identity

- (`1.27.0`) `COMPLIANCE_POLICY=PQC` requires TLS 1.3,
  AES-128/256-GCM cipher suites, and `X25519MLKEM768` key exchange for mesh mTLS,
  upstream and downstream Envoy TLS, and xDS. In ambient mode, set the policy
  in both pilot and ztunnel containers.
- (`1.29.0`) `gateway.istio.io/tls-cipher-suites` accepts a comma-separated list
  of cipher suites on a Gateway.
- (`1.30.0`) `pilot-discovery --tls-min-version` selects TLS `1.2`, the default,
  or `1.3` for the istiod server and webhook.
- (`1.30.0`) `meshConfig.tlsDefaults.minProtocolVersion` is correctly applied
  to downstream TLS contexts.
- (`1.30.0`) Set
  `ambient.istio.io/xfcc-include-client-identity: "true"` on a waypoint Gateway
  or GatewayClass to replace the inbound XFCC value with one derived from the
  source workload's ztunnel-provided SPIFFE identity.

