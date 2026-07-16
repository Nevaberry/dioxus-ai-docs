# Server operations

## Listener-port remapping

Global `http_port` and `https_port` change Caddy's internal listener ports. They do not change the ports clients use. Public traffic and ACME challenges still need forwarding from ports 80 and 443 when the internal ports are remapped.

```caddyfile
{
	http_port 8080
	https_port 8443
}
```

Do not publish only 8080/8443 and expect normal URLs or HTTP-01/TLS-ALPN-01 validation to discover those ports automatically.

## Which servers global options affect

A global `servers :80` block applies only if a site block produces a port-80 server during Caddyfile adaptation. The redirect listener created later by Automatic HTTPS is not affected.

Add an explicit, even empty, HTTP site when port-80 options such as `name` must apply:

```caddyfile
{
	servers :80 {
		name http
	}
}
http:// {
}
```

Inspect adapted JSON whenever a global `servers` selector and Automatic HTTPS both influence listener creation.

## HTTP timeouts and TCP keepalive

HTTP servers default `ReadHeaderTimeout` to one minute since 2.9.0. Slow clients therefore no longer get an unlimited interval to finish request headers unless configuration overrides the default.

As of 2.10.1, `keepalive_interval` is applied to accepted sockets through Go's keepalive configuration. A negative interval disables TCP keepalives. Reverse-proxy transports use the same mechanism for probe intervals.

The 2.11 line adds `keepalive_idle` and `keepalive_count`, allowing the idle time and probe count to be tuned alongside the interval. Coordinate all three settings with load balancers and operating-system limits.

## QUIC 0-RTT

IP matchers reject QUIC 0-RTT requests since 2.9.0, and proxied early-data requests carry `Early-Data`. The 2.11 line adds a server option to disable QUIC 0-RTT when replayable early data is inappropriate.

Disabling 0-RTT trades repeat-connection latency for simpler replay safety. Keep it disabled for endpoints where idempotency cannot be guaranteed.

## HTTP protocol selection

`protocols` accepts `h1`, `h2`, `h2c`, and `h3`. Enabling HTTP/2 or H2C necessarily enables HTTP/1.1. HTTP/1.1 and HTTP/3 may otherwise be selected independently.

H2C has feature limitations and is discouraged unless a specific cleartext HTTP/2 integration requires it. Confirm adapted configuration instead of assuming the list maps one-to-one to enabled protocol stacks.

## HTTP/1 full duplex

Experimental `enable_full_duplex` lets a handler write an HTTP/1 response while it continues reading the request body. Without it, Go consumes the unread body before writing the response. HTTP/2 and later protocols are already full-duplex.

```caddyfile
{
	servers {
		enable_full_duplex
	}
}
```

Older HTTP/1 clients can deadlock with this behavior. Test every relevant client and intermediary before enabling it.

## Plain HTTP received on a TLS listener

Listener wrappers run in declaration order. Put `http_redirect` before the `tls` marker to detect plaintext HTTP received on an HTTPS listener and redirect it.

```caddyfile
{
	servers {
		listener_wrappers {
			http_redirect
			tls
		}
	}
}
```

This is especially useful when HTTPS uses a non-standard port and a browser initially attempts plaintext HTTP to that port.

## PROXY protocol trust boundary

The built-in `proxy_protocol` listener wrapper must appear before `tls` because it parses a plaintext connection prefix. Its metadata replaces the immediate peer address before request matchers and `trusted_proxies` run.

Restrict which peers may supply that metadata with `allow` and `deny`, and set an explicit fallback policy. Otherwise an untrusted sender may forge the client address used by later authorization or logging.

```caddyfile
{
	servers {
		listener_wrappers {
			proxy_protocol {
				allow 10.0.0.0/8
				fallback_policy reject
			}
			tls
		}
	}
}
```

Forwarded HTTP headers have a separate trust policy; see [Reverse proxy](reverse-proxy.md).

## Socket activation

Since 2.9.0, Caddy can inherit passed file descriptors for socket activation. The 2.11 line adds named-socket support, allowing activated listeners to be associated by name rather than only descriptor position.

Keep the service manager's descriptor names and the Caddy configuration synchronized, and verify both fresh starts and reloads.

## Staged shutdown

`shutdown_delay` keeps the server operating normally before the grace period starts. During the delay, `{http.shutting_down}` becomes `true` and `{http.time_until_shutdown}` reports the remaining time, allowing health checks to remove the instance from rotation.

After the delay, `grace_period` stops new work and bounds graceful completion. Without a configured grace period, existing connections may finish indefinitely.

```caddyfile
{
	shutdown_delay 30s
	grace_period 10s
}
```

Set the external load balancer's health-check and draining intervals so removal completes before the grace period starts.

## Reload behavior

`SIGUSR1` reloads the original configuration only when both conditions hold:

- Caddy was started with a configuration file; and
- that configuration has not subsequently been changed through the admin API.

This prevents a signal reload from unexpectedly overwriting newer API-managed state. Choose either file-owned or API-owned configuration as the operational source of truth.

## Admin endpoint and origins

`admin off` disables the endpoint and also makes `caddy reload` unavailable.

A non-wildcard admin listener validates `Host` against allowed origins by default; a wildcard listener does not. `enforce_origin` additionally validates `Origin` and handles CORS preflight requests for browser access.

```caddyfile
{
	admin :2019 {
		origins localhost
		enforce_origin
	}
}
```

Since 2.11.1, browser requests attempted with `no-cors` mode are blocked. Version 2.11.3 canonicalizes remote-admin array indices and path boundaries. Avoid exposing the admin listener to untrusted networks even with origin validation.

## Storage cleaning

Certificate storage is cleaned once during process startup and again at `storage_clean_interval` boundaries. If a scan takes at least half of the configured interval, the next scheduled scan is skipped.

Use a longer interval for large, remote, or expensive shared stores. Since 2.9.0, TLS storage cleaning can be disabled and the pre-operation storage check is configurable, but doing so makes external monitoring and cleanup essential.

## Automatic process memory limit

Since 2.10.0, the `caddy run` path sets `GOMEMLIMIT` automatically. Other CLI subcommands do not. A service that embeds Caddy or starts it through a different command path must arrange its own memory-limit policy.

## Named filesystem modules

The global `filesystem <name> <module>` option can instantiate multiple plugin-backed filesystems, including multiple instances of the same module. A site selects an instance with `fs <name>` before `file_server`.

This affects content serving only; it does not replace the global certificate-storage module.

```caddyfile
{
	filesystem assets example_module {
		# module-specific options
	}
}

example.com {
	fs assets
	file_server
}
```

Module names and configuration are plugin-specific. Confirm that the deployed binary contains the selected module.
