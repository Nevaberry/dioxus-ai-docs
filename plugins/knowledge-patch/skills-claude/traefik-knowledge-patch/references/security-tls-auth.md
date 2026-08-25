# Security, TLS, and authentication

## Keep ACME accounts resolver-local

Certificate resolvers can use different account email addresses and trust
different custom CA certificates (3.2.0). This permits public and private ACME
authorities to coexist without sharing account identity or CA trust.

`certificatesDuration` supports a 30-day duration for issuers that issue that
lifetime (3.2.0). ACME propagation-check controls arrive in 3.3.0. Later ACME
configuration adds `acme.profile` and `acme.emailAddresses` for a certificate
profile and multiple contacts (3.4.0).

## Tune challenge and certificate timing

ACME HTTP challenges accept `acme.httpChallenge.delay`, and the ACME provider's
HTTP timeout is configurable (3.5.0). ACME-managed certificates can enable OCSP
stapling in the same release.

ACME also adds `CertificateTimeout` (3.7.0). Set delay and timeout values only
to accommodate the CA, DNS propagation, or network path; keep failures visible
instead of masking them with excessive waits.

## Configure TLS primitives

TLS session tickets can be disabled when ticket-based resumption is not wanted
(3.4.0). TLS supports the post-quantum-secure `X25519MLKEM768` curve (3.5.0).
Verify client compatibility before narrowing curves.

`ServersTransport` can restrict upstream cipher suites (3.7.0). Apply that
policy to backend TLS separately from client-facing TLS policy.

TLS configuration can disable fallback to the default TLS options (3.7.11).
Router TLS replaces entry-point TLS rather than merging with it, so define every
required option at the effective router layer.

## Supply backend trust

Gateway `BackendTLSPolicy` can secure backends and follows the Gateway API
channel transitions described in the Kubernetes reference. Kubernetes CRD
service TLS can load root CAs from ConfigMaps (3.4.0). Gateway API v1.5.1 allows
`BackendTLSPolicy.caCertificateRefs` to point to Secrets containing private CA
bundles (3.7.0).

Use namespaced references deliberately and review cross-namespace enforcement
before granting shared trust material.

## Diagnose certificate selection

Gateway listeners can use multiple `certificateRefs` for SNI selection
(3.7.0). Fragmented TLS ClientHello messages are supported, and a `TLSStore`
whose Secret is missing no longer takes down unrelated configuration.

Patched 3.7 behavior isolates TLS options for the same host on different entry
points, applies SNI checks to routers without host rules, and selects a
certificate deterministically when certificates share a SAN (3.7.0). Test the
specific host, entry point, and SNI combination rather than inferring behavior
from another router.

## Protect authentication boundaries

ForwardAuth can preserve the upstream `Location`, forward request bodies,
preserve the request method, log the authenticated identity, and redirect to an
`authSignInURL`. With these capabilities enabled, explicitly bound request and
response bodies and minimize forwarded headers.

`ForwardAuth.TrustForwardHeader` is deprecated (3.7.0). A global option can
disable appending to `X-Forwarded-For`; servers can drop underscore-bearing
incoming headers, and authentication middleware drops untrusted underscore
`X-*` headers. Configure these controls around a clear trusted-proxy boundary.

CONNECT bodies are discarded before ForwardAuth from 3.7.9 (3.7.11). Base
CONNECT authorization on method, destination, and trusted metadata rather than
payload content.

## Review security-sensitive extensions

Unsafe Yaegi operations and plugin syscall support expand the code a plugin can
execute. Treat both settings as privileged, audit plugin manifests and source,
and constrain the process environment before enabling them.

Keep the deployed patch release current. The detailed CVE and advisory mapping
is in [Providers and operations](providers-operations.md).
