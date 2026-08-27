# TLS and PKI

## Handshake matching and certificate selection

Since 2.9.0, the Caddyfile can express TLS handshake matchers, TLS connection policies, and certificate-selection policies that previously required JSON. This includes an `sni_regexp` matcher. Selected TLS matchers can resolve runtime placeholders.

Order connection policies deliberately: a broad policy placed before a narrow one may consume a handshake that was intended for the narrow policy. Validate the adapted JSON when combining SNI, client-authentication, protocol, or certificate-selection conditions.

The `tls.context` module added in 2.9.0 lets extension modules customize TLS connection context.

## SNI defaults and fallbacks

`default_sni` supplies a name only when a client sends no SNI. By contrast, experimental `fallback_sni` replaces client SNI only when the offered name matches no cached certificate.

The fallback name must have a certificate managed by Caddy. This is mainly useful behind a CDN or other intermediary that can connect to a stable origin hostname. It is not a substitute for authorizing arbitrary names.

## Binding HTTP Host to TLS SNI

`strict_sni_host` returns HTTP 421 when an HTTPS request's `Host` differs from the ClientHello SNI. This prevents domain-fronting from bypassing host-based policy.

Caddy enables strict SNI/Host binding automatically when TLS client authentication is configured. `insecure_off` is the explicit escape hatch for a proxy design that intentionally permits domain fronting; use it only after confirming that authorization cannot be bypassed through a different Host value.

## Client certificate authentication

### Default modes and trust pools

Providing a `client_auth` trust pool changes the default mode to `require_and_verify`. Without a pool, the default mode is only `require`, which requests a certificate but does not establish a configured trust anchor.

Standard modular trust pools can obtain certificates from:

- PEM files;
- inline base64-encoded DER;
- a configured PKI root or intermediate;
- PEM objects stored at Caddy storage keys; or
- HTTP endpoints.

Multiple certificate sources can be supplied.

```caddyfile
example.com {
	tls {
		client_auth {
			trust_pool file /etc/caddy/client-ca.pem
		}
	}
}
```

The Caddyfile can configure the custom `client_auth` leaf verifier since 2.10.0. This makes leaf-certificate-specific verification available without switching to JSON.

Since 2.11.1, a missing or malformed client-auth CA file fails provisioning. It no longer silently disables client authentication.

## Managed certificate renewal

### Window versus scan cadence

The 2.11 line adds global Caddyfile `renewal_window_ratio`. Internal PKI authorities can independently set `maintenance_interval` and `renewal_window_ratio`.

`renew_interval` controls how often Caddy scans managed certificates; it does not define the renewal window. `ocsp_interval` separately controls OCSP staple checks. Keep these three concepts distinct when tuning background work.

### Requested certificate lifetime

Experimental `cert_lifetime` asks an ACME CA for a specific `notAfter` value. The CA may ignore or reject the request; the default `0` leaves lifetime selection to the CA.

Experimental ACME profile selection is covered in [Automatic HTTPS and ECH](automatic-https-and-ech.md). Profiles can request CA-defined properties that a CSR cannot express.

### OCSP in restricted networks

`ocsp_stapling off` disables stapling when responders cannot be reached. Prefer fixing network reachability where possible; disabling stapling changes what clients can learn about certificate status.

## Private-key reuse

Managed renewals create a new private key by default. The TLS directive's `reuse_private_keys` option retains it for deployments that require key pinning, but this increases the lifetime and impact of a compromised key and is explicitly discouraged for normal deployments.

## Handshake-time certificate managers

`get_certificate` delegates selection to a certificate manager during the TLS handshake and implies on-demand loading, not Caddy-managed issuance.

The built-in HTTP manager sends ClientHello details to a URL as query parameters. It requires a `200` response containing the full PEM certificate chain and private key. Because the handshake waits for that response and the endpoint handles private key material, prefer a local, authenticated, low-latency endpoint.

```caddyfile
https:// {
	tls {
		get_certificate http http://localhost:9007/certs
	}
}
```

Apply global On-Demand TLS authorization separately when Caddy is also permitted to issue certificates dynamically.

## Internal PKI

### Default authority and custom key hierarchy

The default PKI authority ID is `local`. Without supplied material, Caddy generates and manages the local authority.

A deployment can instead load PEM root and intermediate certificate/key pairs. The intermediate certificate must expire before the root.

```caddyfile
{
	pki {
		ca local {
			root {
				cert /etc/caddy/root.pem
				key /etc/caddy/root.key
			}
			intermediate {
				cert /etc/caddy/intermediate.pem
				key /etc/caddy/intermediate.key
			}
		}
	}
}
```

In the 2.11 line, an internal authority can issue through a chain containing multiple intermediate certificates.

### Internal leaf lifetime

Internally issued leaf certificates default to a 12-hour lifetime and must expire before the default seven-day intermediate. Account for that short lifetime when clients cache certificates or when an authority is intermittently unavailable.

The internal issuer's `sign_with_root` bypasses the intermediate for rare clients that cannot validate ordinary chains. It weakens normal key separation and is not recommended otherwise.

## System and combined CA pools

Later 2.11 releases add `system` and `combined` TLS CA-pool modules. `system` uses the platform trust store alone. `combined` joins that store with another configured pool, which is useful when public or enterprise roots and a private application CA must both be accepted.

Do not assume the system pool is identical across containers, hosts, and operating systems.

## TLS storage controls

Since 2.9.0, CertMagic's `DisableStorageCheck` is configurable and TLS storage cleaning can be disabled. Disabling the capacity/writability check or cleaning transfers responsibility for storage health and stale assets to the operator.

The deprecated TLS JSON fields `rate_limit` and `burst` were removed in 2.9.0. Delete them before loading a pre-2.9 configuration.

Storage cleaning cadence and shared storage behavior are covered in [Server operations](server-operations.md) and [Automatic HTTPS and ECH](automatic-https-and-ech.md).

## TLS secret logging

`insecure_secrets_log` writes TLS secrets in NSS key-log format for packet decryption in tools such as Wireshark.

```caddyfile
example.com {
	tls {
		insecure_secrets_log /secure/debug/caddy.keys
	}
}
```

Anyone who obtains the file can decrypt captured connections. Enable it only for tightly controlled troubleshooting, restrict its filesystem permissions, rotate it, and remove it immediately afterward.
