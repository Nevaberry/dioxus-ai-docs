# Automatic HTTPS and ECH

## What activates Automatic HTTPS

Automatic HTTPS is activated when Caddy can derive a hostname or IP from one of these sources:

- a Caddyfile site address;
- a host matcher on a top-level JSON route;
- the `--domain` or `--from` command input; or
- the `automate` certificate loader.

It is not activated when no hostname or IP is present, when a site address explicitly uses `http://`, or when a server listens only on the HTTP port. A manually loaded certificate suppresses certificate automation for that name unless `ignore_loaded_certificates` is enabled.

Automatic HTTPS augments explicit routing; it does not replace user routes.

## Redirect ordering

When a server already listens on the HTTP port, generated HTTP-to-HTTPS redirects are inserted:

1. after user routes that have host matchers; and
2. before a user catch-all route.

This allows an explicit host route to take precedence while preserving redirects ahead of a generic fallback. Inspect adapted JSON when route order is security-sensitive.

The global `servers :80` block affects only a server that exists during Caddyfile adaptation; an Automatic HTTPS redirect listener created later is not retroactively changed. See [Server operations](server-operations.md) for the empty-HTTP-site technique.

## Wildcard selection and forced automation

In 2.9.0, the experimental `auto_https prefer_wildcard` option could prefer a matching wildcard certificate, while experimental `force_automate` could force a name into automation.

Since 2.10.0, Caddy automatically prefers a managed wildcard certificate when it covers a configured subdomain. The experimental `prefer_wildcard` option is removed. Use site-level `tls force_automate` when the literal hostname must get its own certificate:

```caddyfile
foo.example.com {
	tls force_automate
}
```

When an IP address has no explicit automation policy, Caddy selects the internal issuer (since 2.9.0).

## Local HTTPS and trust distribution

Local HTTPS uses Caddy's internal CA rather than ACME or DNS validation. The default local root and intermediate are stored under `pki/authorities/local` in Caddy's data storage. Every client must trust the root.

Automatic root installation can be disabled with the global Caddyfile option `skip_install_trust` or JSON `"install_trust": false`. Installation or removal can also be performed explicitly:

```sh
caddy trust
caddy untrust
```

Automatic trust installation is not reliable in containers or under unprivileged service accounts. Distribute the root into every relevant application, operating-system, container, and device trust store.

## ACME challenge selection

HTTP-01 and TLS-ALPN-01 are enabled by default. When more than one challenge is available, Caddy initially chooses randomly, learns which type succeeds, and falls back to another type on failure.

Enabling DNS-01 disables the other challenge types by default. If the selected challenge type conflicts with ingress topology, configure challenge behavior explicitly rather than relying on fallback.

## DNS challenge configuration

### Global provider

Since 2.10.0, the global `dns` option sets a default DNS module for ACME DNS challenges, ECH publication, and other TLS operations. The JSON counterpart is the `dns` field of the TLS app.

```caddyfile
{
	dns cloudflare {env.CLOUDFLARE_API_KEY}
}
```

A site-specific `acme_dns` value overrides the global provider. Caddy 2.10.2 fixes a critical 2.10.1 regression in adaptation of the global `acme_dns` option; use at least 2.10.2 when depending on it.

### Delegating the challenge name

`_acme-challenge` may be delegated with a CNAME into a zone handled by a supported DNS module. This is useful when the original zone lacks a usable API. Configure the site-specific `dns_challenge_override_domain` for that delegation.

Later 2.11 releases expand placeholders in the DNS challenge `override_domain` and in ACME credential values.

### Global resolvers

Since 2.11.2, global `tls_resolvers` selects DNS resolvers used for ACME DNS challenges across all sites. This is separate from selecting the DNS provider that writes challenge records.

### Distributed solving

The 2.11 line can disable distributed ACME challenge solving except for HTTP-01. Use this when shared storage should not coordinate non-HTTP challenge ownership, while remembering that HTTP-01 retains its required coordination behavior.

## Experimental ACME profiles

Since 2.10.0, issuers can opt into experimental ACME profiles. A profile lets a CA expose certificate properties, such as a short lifetime, that a CSR alone cannot request. Profile selection remains opt-in in the 2.10 line; upgrading does not enable one automatically.

## On-Demand TLS authorization

On-Demand TLS obtains a missing certificate while the first TLS handshake waits, caches it, and renews it in the background. Enabling On-Demand TLS in a site's automation policy is not sufficient: a global restriction must also be configured in the JSON automation object or the Caddyfile `on_demand_tls` option.

Normally, configure an `ask` HTTP endpoint that authorizes the requested SNI against application state. The restriction is global, not scoped per site or domain. The endpoint must therefore make the complete authorization decision for every possible name.

Certificate issuance directly delays the first handshake. A slow authorization endpoint or issuer adds to that delay, so keep `ask` local or low-latency and bound its work.

## Issuance and renewal failures

Issuance and renewal normally happen in the background, allowing startup to complete before certificates are ready. On failure Caddy:

1. retries briefly;
2. tries other enabled challenge types;
3. moves to the next issuer, with Let's Encrypt followed by ZeroSSL as defaults; and
4. after all issuers fail, backs off with at most one day between attempts for up to 30 days.

Let's Encrypt retries use its staging service to reduce production rate-limit pressure. Caddy also limits ACME work to 10 attempts per account per 10 seconds.

A configuration change aborts in-flight certificate tasks. Batch frequent reloads during initial issuance or renewal; otherwise each reload can repeatedly cancel progress.

## Shared certificate storage

With default storage, `$HOME` must be writable and persistent. Multiple instances using the same storage share certificate assets and coordinate certificate management as a cluster. Before ACME operations, Caddy checks that storage is writable and has sufficient capacity.

Do not point clustered instances at merely similar local paths; they need the same consistency-capable storage. Preserve it across container or VM replacement.

## Encrypted ClientHello

### Enabling ECH

Since 2.10.0, the global `ech` option makes Caddy generate, publish, and serve ECH configurations. It requires a DNS provider module. The public name must resolve to Caddy and receives its own certificate.

```caddyfile
{
	dns cloudflare {env.CLOUDFLARE_API_KEY}
	ech ech.example.net
}

example.com {
	respond "Hello there!"
}
```

Caddy creates or augments HTTPS records for the protected site names, not for the public name. It does not automatically publish ECH for CNAME'd protected domains, and a protected domain must already have a record in its zone. Clients need encrypted DNS as well; otherwise DNS lookup can disclose the name before TLS hides SNI.

### Rotation and protocol propagation

ECH keys rotate automatically in the 2.11 line. HTTP logs and placeholders can expose ECH status. Later 2.11 fixes propagate ECH keys to QUIC listeners and correctly retry failed rotations.

### Verifying ECH

An `encrypted_client_hello` extension alone is not proof that ECH succeeded because browsers send GREASE values. In a packet capture, verify that ClientHello SNI contains the configured public name instead of the protected site name.

Testing may require secure DNS, cleared DNS caches, and a fresh connection. Reusing an existing connection can mask a configuration change.

### Stored ECH state

ECH state is stored at `ech/configs/<random-config-id>` in the configured data storage. Its metadata sidecar prevents DNS publication on every reload.

Deleting the stored configuration safely forces reconstruction but can reset the key-rotation schedule. Clearing only publication metadata forces publication-related work without the broader key reset. Back up shared state and distinguish those recovery actions.

## Post-quantum default

Since 2.10.0, TLS enables the standardized `x25519mlkem768` hybrid post-quantum key-exchange group by default. No Caddy configuration is required; only pin an explicit curve list if a documented interoperability constraint requires it.
