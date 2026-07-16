# Operations And Migration

Use this reference for provider connectivity, runtime integration, plugin trust,
upgrade checks, and patch-line maintenance.

## Provider connectivity and discovery

- Docker and Swarm providers support HTTP Basic Authentication when connecting
  to a protected endpoint (since 3.2.0).
- Nomad can watch catalog events instead of polling for configuration changes
  (since 3.2.0).
- Requests from the HTTP provider include a `Host` header, allowing host-routed
  configuration endpoints to respond correctly (since 3.3.0).
- Docker, ECS, Docker Swarm, Consul Catalog, and Nomad can configure backend
  server URLs directly through provider labels (since 3.4.0).
- ECS supports IPv6, and Docker can discover containers that are not running
  (since 3.6.0).
- Consul, Consul Catalog, and Nomad log their provider namespace at startup
  (since 3.6.0).
- HTTP provider `maxResponseBodySize` bounds downloaded dynamic configuration
  (since 3.7.0).
- Docker and Swarm providers automatically negotiate the Docker API version
  (since 3.7.0).

## Runtime and socket activation

- Traefik supports systemd socket activation for systemd-owned listening sockets
  (since 3.1.0).
- Socket activation also supports UDP routing (since 3.4.0).

## Plugin failure and trust controls

- `AbortOnPluginFailure` terminates startup when a plugin fails to load instead
  of continuing without it (since 3.3.0).
- Plugin manifests can enable unsafe operations in the Yaegi interpreter (since
  3.5.0). Treat that flag as part of the plugin's trust boundary.
- Plugins can use syscalls (since 3.6.0), extending them to OS-level
  integrations and increasing the importance of plugin review.

## Security and patch maintenance

- The 3.7 line received several security fixes. Version 3.7.5 addresses
  CVE-2026-54761 and CVE-2026-54762; 3.7.6 addresses CVE-2026-54763 through
  CVE-2026-54765; and 3.7.7 addresses three more advisories. For deployments on
  that line, upgrade to 3.7.7 rather than remaining on 3.7.0.
