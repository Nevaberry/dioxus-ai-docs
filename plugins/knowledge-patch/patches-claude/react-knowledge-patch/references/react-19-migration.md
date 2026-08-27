# React 19 Migration and Compatibility

## Update assumptions about generated IDs

Since `19.2.0`, the default `useId` prefix is `_r_`. React 19.0 used `:r:` and
React 19.1 used `«r»`. The new form is valid as a `view-transition-name` and
as an XML 1.0 name.

Rendered output and snapshots that expose generated IDs will change. Update
affected snapshots and code, and avoid making application logic depend on the
exact generated text.

## Add nonces to hoistable styles

Since `19.2.0`, React DOM accepts a `nonce` on hoistable styles. Supply the CSP
nonce when these styles must run under a nonce-based Content Security Policy.

## Keep pinned minor lines patched

The `news-and-versions` maintenance guidance listed the June 2026 patch
targets for projects pinned to a React 19 minor line:

- React 19.2: `19.2.7`
- React 19.1: `19.1.8`
- React 19.0: `19.0.7`

Treat these as the listed patch levels for that maintenance snapshot. Security
remediation may require a newer patched release; follow the latest-release
guidance in [Security](security.md) for RSC-capable deployments.
