# React Server Components Security

The request-decoding advisories and remediation guidance are attributed to `server-components-security`.

## Treat RSC capability as exposure

Versions 19.0, 19.1.0, 19.1.1, and 19.2.0 of these packages allow unauthenticated remote code execution while decoding a crafted Server Function request:

- `react-server-dom-webpack`
- `react-server-dom-parcel`
- `react-server-dom-turbopack`

The issue is CVE-2025-55182 with CVSS 10.0. An application can be exposed merely by supporting Server Components through a framework, bundler, or plugin; application code does not need to declare a Server Function. Client-only applications and applications with no RSC-capable integration are unaffected.

## Upgrade beyond the initial RCE fixes

The initial RCE fixes were 19.0.1, 19.1.2, and 19.2.1. Later guidance added denial-of-service fixes for CVE-2025-55184, CVE-2025-67779, and CVE-2026-23864, plus a source-exposure fix for CVE-2025-55183.

Upgrade React, React DOM, and the installed RSC transport to the latest patched release together. Do not stop at the initial RCE fix, and do not treat hosting-provider mitigations as a substitute.

```sh
npm install react@latest react-dom@latest \
  react-server-dom-webpack@latest
```

Replace `react-server-dom-webpack` in the command with the transport actually installed by the application.

## Remediate frameworks and bundlers together

Affected integrations include:

- `next`
- React Router's unstable RSC APIs
- `waku`
- `@parcel/rsc`
- `@vitejs/plugin-rsc`
- `rwsdk`

Update the integration and every `react-server-dom-*` transport or RSC plugin it uses.

For Next.js, versions 13.3.x through 14.x must move to 14.2.35. Each 15.x or 16.x line needs its own latest patched release. Replace `next@14.3.0-canary.77` or later with the latest stable 14.x release.

## Preserve React Native version compatibility

A React Native application that is not in a monorepo and does not use `react-dom` needs no extra advisory-driven change beyond keeping `react` pinned.

In a React Native monorepo, update only installed `react-server-dom-webpack`, `react-server-dom-parcel`, or `react-server-dom-turbopack` packages. Do not also update `react` and `react-dom` solely for this advisory, because that can create a React Native version mismatch.
