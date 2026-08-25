# Security, TLS, and authentication

## Isolate ACME resolvers

ACME resolvers can use distinct account email addresses and custom CA
certificates, so private and public CA trust need not be shared (3.2.0).
`certificatesDuration` also supports a 30-day lifetime choice.

Challenge propagation checks are configurable (3.3.0). Use the controls only
when DNS or network behavior requires altered validation timing.

ACME adds `acme.profile` and `acme.emailAddresses` for certificate profiles and
multiple contact addresses (3.4.0).

Managed certificates support OCSP stapling. HTTP challenges accept
`acme.httpChallenge.delay`, and the ACME provider HTTP timeout is configurable
(3.5.0).

ACME also exposes `CertificateTimeout` (3.7.0). Coordinate challenge delay,
propagation checks, provider timeout, and certificate timeout instead of using
one setting to compensate for a different stage.

## Configure TLS behavior

TLS can disable session tickets (3.4.0) and supports the post-quantum-secure
`X25519MLKEM768` curve (3.5.0).

`ServersTransport` can restrict cipher suites used with upstream TLS. Traefik
also handles fragmented TLS ClientHello messages, and a `TLSStore` referencing
a missing Secret no longer takes down unrelated configuration (3.7.0).

Patched 3.7 behavior isolates TLS options for the same host on different entry
points, applies SNI checks to routers without host rules, and chooses
deterministically among certificates sharing a SAN (3.7.0).

TLS can disable fallback to default TLS options. Router TLS replaces entry-point
TLS rather than merging with it, so define the complete desired router policy
when overriding an entry point (3.7.11).

Gateway listeners can select among multiple certificate references, while
backend TLS policy can trust private CA bundles from Secrets. See the Kubernetes
reference for the associated API and namespace rules.

## Bound ForwardAuth traffic

ForwardAuth can log the authenticated identity through `LogUserHeader` (3.2.0)
and preserve the authorization server's `Location` header (3.3.0).

It can forward the incoming request body to the authorization server, and can
preserve the original request method when constructing the authorization
request (3.3.0 and 3.4.0). Configure `maxBodySize`; Traefik warns when the limit
is absent (3.6.0).

ForwardAuth adds `authSignInURL` for sign-in redirects and
`maxResponseBodySize` to limit authorization responses. `TrustForwardHeader` is
deprecated (3.7.0). Replace configurations that rely on trusting externally
supplied forwarding headers.

ForwardAuth passes the correct `X-Forwarded-Port` to the authorization service
(3.6.21).

CONNECT request bodies are discarded before ForwardAuth (3.7.11). Do not design
CONNECT authorization around payload inspection.

## Control forwarding and client identity

`ipStrategy` can normalize IPv6 client addresses by subnet before IP-based
middleware decisions (3.2.0).

A global setting can disable appending to `X-Forwarded-For`. The server can
remove incoming header names containing underscores, and authentication
middleware drops untrusted underscore-bearing `X-*` headers (3.7.0).

Treat forwarded headers as an explicit trust boundary. Align entry-point trust,
proxy chaining, ForwardAuth, and access logging so identity cannot be supplied
by an untrusted client.

## Review provider and plugin trust

Authenticated Docker and Swarm endpoints support HTTP Basic Authentication
(3.2.0). Protect the credentials and the endpoint's transport.

Unsafe Yaegi operations in plugin manifests (3.5.0) and plugin syscall support
(3.6.0) enlarge the code a plugin can execute. Enable either only after a trust
and isolation review; combine required plugins with `AbortOnPluginFailure` when
startup without them would be unsafe.

Ingress NGINX snippet compatibility accepts only parsed, allowlisted directives.
Use cross-namespace and allowed-response-header controls to preserve the desired
resource boundary (3.7.0).

## Maintain security fixes

Use the latest maintained patch in the chosen release line. The 3.7 line has
fixes for multiple CVEs and GHSAs through 3.7.11; see the operations reference
for the advisory-to-patch mapping.
