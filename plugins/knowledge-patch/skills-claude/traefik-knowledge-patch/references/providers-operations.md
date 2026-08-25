# Providers and operations

## Use systemd socket activation

Systemd can own listening sockets and pass them to Traefik (3.1.0). Socket
activation also covers UDP routing (3.4.0). Keep socket unit addresses and
Traefik entry points aligned, and test process restarts without recreating the
socket.

## Connect Docker and Swarm safely

Docker and Swarm providers support HTTP Basic Authentication for protected
provider endpoints (3.2.0). Docker and Swarm later auto-negotiate the Docker API
version (3.7.0), reducing dependence on a manually pinned API version.

The Docker provider can discover containers that are not running (3.6.0).
Account for container state in constraints so stopped workloads do not produce
unwanted routes. The ECS provider supports IPv6 (3.6.0).

## Configure label providers

Docker, ECS, Docker Swarm, Consul Catalog, and Nomad can set backend server URLs
directly through labels (3.4.0). Validate label ownership because it controls
the full upstream URL rather than only host and port fragments.

Consul, Consul Catalog, and Nomad log their provider namespace at startup
(3.6.0). Include startup logs in diagnostics when namespace scoping produces
unexpected discovery.

## Watch Nomad events

The Nomad provider can watch catalog changes rather than poll for them (3.2.0).
Choose the event-driven mode when prompt updates matter, and retain monitoring
for a stalled watch.

## Bound HTTP provider behavior

Requests from the HTTP provider include a `Host` header, allowing host-routed
configuration endpoints to respond correctly (3.3.0). The provider also has
`maxResponseBodySize` to bound the downloaded dynamic configuration (3.7.0).
Set the limit above the legitimate configuration size but below an unacceptable
memory or transfer cost.

## Control server protocol resources

The server maximum request-header size is configurable (3.2.0). HTTP/2 servers
also expose HPACK table-size controls (3.6.0). Treat both as resource and
compatibility limits: test expected clients before tightening them.

## Fail closed on plugin loading

`AbortOnPluginFailure` stops startup if a plugin cannot load instead of silently
continuing without it (3.3.0). Prefer it when plugin behavior is required for
security or correctness.

Plugin manifests can enable unsafe operations in the Yaegi interpreter
(3.5.0), and plugins can use syscalls (3.6.0). Both broaden the plugin's
effective authority. Review the manifest and source, minimize host access, and
treat enabling either capability as a trust decision.

## Configure Redis notifications

Traefik's Redis integration requires Redis keyspace notifications (3.7.11).
Enable them before depending on notification-driven updates and monitor the
event path after Redis configuration changes.

## Apply patch-line security updates

Do not remain on an initial 3.7 image. The 3.7.5 patch addresses
CVE-2026-54761 and CVE-2026-54762; 3.7.6 addresses CVE-2026-54763 through
CVE-2026-54765; and 3.7.7 addresses three additional advisories (3.7.0).

Later fixes supersede the earlier recommendation: 3.7.8 addresses
GHSA-8rxv-jg7p-wvg3, 3.7.9 addresses GHSA-3ccp-42pg-hgv6, and 3.7.10 addresses
GHSA-fgjj-px3w-67xx, GHSA-62fc-8686-hfmq, and GHSA-6765-c87h-8mrf. Deployments
staying on the 3.7 line should move to 3.7.11 rather than an earlier patch
(3.7.11).
