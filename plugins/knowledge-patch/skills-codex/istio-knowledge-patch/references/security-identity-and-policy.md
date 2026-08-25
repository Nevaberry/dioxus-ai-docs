# Security, Identity, and Policy

Use this reference for authorization behavior, JWT validation, mTLS
credentials, certificate authorities, trust distribution, Wasm safety, and TLS
hardening.

## Contents

- [Authorization and policy evaluation](#authorization-and-policy-evaluation)
- [JWT and JWKS security](#jwt-and-jwks-security)
- [Certificate references and Gateway TLS](#certificate-references-and-gateway-tls)
- [Trust bundles, revocation, and certificate authorities](#trust-bundles-revocation-and-certificate-authorities)
- [Compliance and protocol controls](#compliance-and-protocol-controls)
- [Wasm supply-chain safeguards](#wasm-supply-chain-safeguards)

## Authorization and policy evaluation

### Fail-closed Wasm fetches deny all traffic (1.25.0)

If a Wasm image fetch fails and `failStrategy` is `FAIL_CLOSE`, Istio installs a
deny-all RBAC filter. Earlier behavior installed an allow-all filter.

### CUSTOM authorization policy inspection (1.25.0)

`istioctl x authz check` supports `AuthorizationPolicy` resources whose action
is `CUSTOM`.

### Multiple CUSTOM authorization providers (1.30.0)

A workload can use multiple `CUSTOM` authorization providers, allowing
different authentication schemes for different request paths.

### AuthorizationPolicy matcher hardening (1.30.0)

`AuthorizationPolicy` treats regex metacharacters in service-account names,
source principals, and source namespaces as literal matcher content, preventing
unintended identities from matching.

## JWT and JWKS security

### JWT rules without an issuer (1.27.0)

JWT authentication can omit `issuer` when `jwksUri` is supplied, supporting
tokens whose issuer is dynamic. An explicit JWKS URI is required when no issuer
is configured.

### Custom space-delimited JWT claims (1.28.0)

`RequestAuthentication` JWT rules can use `spaceDelimitedClaims` for custom
claims in addition to built-in `scope` and `permission`. These values are passed
to Envoy's JWT filter.

### Blocking JWKS URI address ranges (1.29.0)

JWKS fetching can block CIDRs. If any address resolved from a JWKS URI is in a
blocked range, Istio skips the fetch and substitutes a fake JWKS so
JWT-authenticated requests are rejected.

### JWKS fetch security corrections (1.30.0)

Istio no longer exposes an RSA private key through its JWKS fetch-failure
fallback. JWKS CIDR blocking is applied after DNS resolution and follows
redirects and issuer discovery, preventing those paths from bypassing blocked
ranges.

## Certificate references and Gateway TLS

### TLS server name in remote secrets (1.26.0)

`istioctl create-remote-secret` accepts `--tls-server-name`, which writes
`tls-server-name` into the generated kubeconfig so TLS validation succeeds when
its `server` is a gateway proxy hostname.

### SPIRE file-based certificate references (1.26.0)

File-based certificate references from resources such as `DestinationRule` and
`Gateway` work when SPIRE is the certificate authority.

### Multiple certificate types in Gateway resources (upgrade-1.27)

Istio and Kubernetes Gateway resources can configure multiple certificate
types, such as RSA and ECDSA, simultaneously so clients can select a supported
type.

### External SDS providers for Gateway TLS (1.27.0)

Gateway TLS configuration can use external Secret Discovery Service providers
for certificate management.

### Separate CA credentials for Gateway mTLS (1.28.0)

`ServerTLSSettings.caCertCredentialName` can reference a `Secret` or `ConfigMap`
containing CA certificates for mutual TLS.

### Gateway API frontend TLS validation (1.28.0)

Istio supports Gateway API `FrontendTLSValidation` from GEP-91.

### Gateway TLS cipher suites (1.29.0)

Set `gateway.istio.io/tls-cipher-suites` on a `Gateway` to a comma-separated
list of custom cipher suites.

## Trust bundles, revocation, and certificate authorities

### Experimental ClusterTrustBundle support (1.26.0)

Enable Kubernetes v1alpha1 `ClusterTrustBundle` support with
`values.pilot.env.ENABLE_CLUSTER_TRUST_BUNDLE_API=true`. Enable the corresponding
Kubernetes feature gates as well.

### Stable ClusterTrustBundle API (1.27.0)

On Kubernetes 1.33 and later, Istio's `ClusterTrustBundle` integration uses the
stable `certificates.k8s.io/v1beta1` API instead of `v1alpha1`.

### Certificate revocation lists with plugged-in CAs (1.27.0)

Istio watches a plugged-in CA's `ca-crl.pem`, distributes the CRL to every
namespace, and enables proxies to reject revoked certificates.

### Incomplete plugged-in CA bundles now fail (1.27.0)

Istiod validates that a `cacerts` bundle contains every required CA file and
returns an error when incomplete instead of silently falling back to the
self-signed CA.

### Configurable root-CA propagation ConfigMap (1.27.0)

`values.global.trustBundleName` sets the ConfigMap name istiod uses to propagate
its root CA, allowing control planes with overlapping namespaces to use
distinct trust-bundle ConfigMaps.

### Symlink secret watching in the node agent (1.29.0)

The Istio node agent watches secrets exposed through symlinks so changes are
detected.

### Configurable CRL distribution ConfigMap (1.29.0)

Set `values.pilot.crlConfigMapName` to select the ConfigMap istiod uses to
distribute certificate revocation lists, allowing control planes with
overlapping namespaces to use separate CRL resources.

## Compliance and protocol controls

### ENABLE_AUTO_SNI removed (1.26.0)

The deprecated `ENABLE_AUTO_SNI` flag and its code paths are removed.
Configurations must not rely on it.

### Post-quantum compliance policy (1.27.0)

The `PQC` option for `COMPLIANCE_POLICY` enforces TLS 1.3, AES-128/256-GCM
cipher suites, and `X25519MLKEM768` key exchange for mesh mTLS, Envoy downstream
and upstream TLS, and xDS. In ambient mode, configure the policy in both Pilot
and ztunnel containers.

### TLS minimum-version controls (1.30.0)

`pilot-discovery --tls-min-version` selects TLS `1.2`, the default, or `1.3`
for the istiod server and webhook.
`meshConfig.tlsDefaults.minProtocolVersion` is correctly applied to downstream
TLS contexts.

## Wasm supply-chain safeguards

### Wasm fetch limits and validation (1.30.0)

`ISTIO_WASM_MAX_BINARY_SIZE_BYTES` configures the Wasm binary-size limit. The
limit is also enforced after gzip decompression for HTTP-fetched modules.
Bearer-token realm URLs used while fetching `WasmPlugin` images are validated
to prevent SSRF.
