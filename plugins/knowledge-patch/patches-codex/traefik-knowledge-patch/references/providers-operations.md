# Providers and operations

## Use systemd socket activation

Systemd can own listening sockets and pass them to Traefik (3.1.0). Coordinate
socket units, service units, and Traefik entry points so only one component
binds each address. Socket activation also supports UDP routing (3.4.0).

## Connect infrastructure providers

Docker and Swarm providers support HTTP Basic Authentication for protected
provider endpoints (3.2.0). Store endpoint credentials outside committed
configuration.

The Nomad provider can watch catalog changes instead of polling, enabling
event-driven configuration refreshes (3.2.0).

Docker, ECS, Docker Swarm, Consul Catalog, and Nomad label providers can set
backend server URLs directly through labels (3.4.0). Validate label ownership
because labels can now determine full upstream URLs.

ECS supports IPv6 endpoint discovery, while Docker can discover containers that
are not currently running (3.6.0). Account for readiness separately from
discovery.

Docker and Swarm providers negotiate the Docker API version automatically
(3.7.0), reducing the need to pin a provider-side API version.

## Configure the HTTP provider safely

HTTP-provider requests include a `Host` header, allowing host-routed endpoints
to serve dynamic configuration correctly (3.3.0).

The provider's `maxResponseBodySize` bounds downloaded configuration responses
(3.7.0). Set it to limit memory and trust exposure without blocking legitimate
configuration payloads.

## Bound protocol resources

The server's maximum incoming request-header size is configurable (3.2.0).
Choose a limit that accommodates required headers while constraining oversized
requests.

HTTP/2 servers expose HPACK table-size controls for tuning header compression
(3.6.0). Treat these as capacity and interoperability settings rather than
application routing policy.

FastProxy rejects CONNECT requests. Use the regular proxy path for CONNECT
tunnels (3.7.11). Starting in 3.7.9, Traefik defers CONNECT payloads until the
backend accepts the tunnel, discards CONNECT bodies before ForwardAuth, and
does not return CONNECT requests to the connection pool.

## Control plugin failure and authority

`AbortOnPluginFailure` makes startup fail when a plugin cannot load rather than
continuing without it (3.3.0). Enable it where the plugin is required for
correctness or security.

Plugin manifests can permit unsafe Yaegi operations (3.5.0), and plugins can
use syscalls (3.6.0). Both capabilities expand executable authority. Review the
manifest, code, provenance, and runtime isolation before enabling them.

## Maintain provider integrations

Authentication middleware warns when `maxBodySize` is unset (3.6.0). Treat the
warning as a prompt to make body-forwarding limits explicit.

Traefik's Redis integration requires Redis keyspace notifications for update
notifications. Enable them before relying on Redis-driven refresh behavior
(3.7.11).

## Select a maintained patch release

The 3.7 line accumulated security corrections after its initial release
(3.7.0):

- 3.7.5 fixes CVE-2026-54761 and CVE-2026-54762.
- 3.7.6 fixes CVE-2026-54763 through CVE-2026-54765.
- 3.7.7 fixes three additional advisories.
- 3.7.8 fixes GHSA-8rxv-jg7p-wvg3.
- 3.7.9 fixes GHSA-3ccp-42pg-hgv6.
- 3.7.10 fixes GHSA-fgjj-px3w-67xx, GHSA-62fc-8686-hfmq, and
  GHSA-6765-c87h-8mrf.

Deployments staying on that line should move to 3.7.11 rather than an earlier
patch (3.7.11).
