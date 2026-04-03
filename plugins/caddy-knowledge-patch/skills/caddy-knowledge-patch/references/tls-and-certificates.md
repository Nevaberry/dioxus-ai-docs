# TLS and Certificates

TLS, ACME, and certificate management changes since Caddy 2.8.0.

## ZeroSSL Requires Email (2.8.0, Breaking)

ZeroSSL is only added as a default issuer if you provide an email address. Without `email`, only Let's Encrypt is used:

```
{
    email you@example.com
}
```

## On-Demand TLS `permission` Module (2.8.0)

In JSON config, the `ask` endpoint is deprecated in favor of a pluggable `permission` module. In Caddyfile, `ask` still works, plus new `permission` subdirective:

```
{
    on_demand_tls {
        ask https://auth.example.com/check
        # OR
        permission <module>
    }
}
```

## `force_automate` (2.9.0, Experimental)

Override wildcard certificate preference to force individual certificates per domain:

```
example.com {
    tls force_automate
}
```

## Encrypted ClientHello — ECH (2.10.0, Major)

Major privacy feature: encrypts the domain name in the TLS ClientHello message. Requires a DNS provider module (e.g., `xcaddy build --with github.com/caddy-dns/cloudflare`):

```
{
    dns cloudflare {env.CLOUDFLARE_API_KEY}
    ech ech.example.net
}

example.com {
    respond "Hello!"
}
```

All sites are protected behind the public name (`ech.example.net`). Caddy auto-generates ECH configs and publishes HTTPS DNS records. The public name must point to your server.

### ECH Key Rotation (2.11.1)

ECH keys are now rotated automatically (previously static).

## Global `dns` Option (2.10.0)

Configure a DNS provider once globally for all features that need it (ACME DNS challenges, ECH, etc.):

```
{
    dns cloudflare {env.CLOUDFLARE_API_KEY}
}
```

## Wildcards by Default (2.10.0, Major)

Caddy now uses wildcard certificates for subdomains instead of issuing individual certificates. Override with `tls force_automate`. The old `auto_https prefer_wildcard` option is removed.

## Post-Quantum Key Exchange (2.10.0)

`X25519MLKEM768` is now included as a default cryptographic group. No configuration needed — all TLS connections automatically negotiate post-quantum key exchange when supported.

## ACME Profiles (2.10.0, Experimental)

Support for ACME profiles (e.g., Let's Encrypt 6-day short-lived certificates). May become the default in future versions.

## `tls_resolvers` Global Option (2.11.2)

Control which DNS resolvers are used for the ACME DNS challenge:

```
{
    tls_resolvers 1.1.1.1 8.8.8.8
}
```

## Security: `forward_auth` Identity Injection Fix (2.11.2)

`copy_headers` in `forward_auth` now strips client-supplied identity headers before copying auth response headers. This prevents privilege escalation where a client could inject identity headers that bypass authentication.

## Security: `vars_regexp` Double-Expansion (2.11.2)

Fixed a placeholder double-expansion vulnerability in `vars_regexp` that could leak secrets in unusual configurations.
