# React Server Components Security

## Patch request-decoding vulnerabilities

The `server-components-security` advisory covers unauthenticated request
decoding vulnerabilities in these RSC transport packages:

- `react-server-dom-webpack`
- `react-server-dom-parcel`
- `react-server-dom-turbopack`

Versions 19.0, 19.1.0, 19.1.1, and 19.2.0 allow remote code execution while
decoding a crafted Server Function request (CVE-2025-55182, CVSS 10.0).
Supporting Server Components is enough to be exposed even if application code
declares no Server Functions. Client-only applications and applications with
no RSC-capable framework, bundler, or plugin are unaffected.

The initial RCE fixes were 19.0.1, 19.1.2, and 19.2.1. Do not stop at those
versions: guidance was later revised for denial-of-service vulnerabilities
CVE-2025-55184, CVE-2025-67779, and CVE-2026-23864, plus source-exposure
CVE-2025-55183. Update React, React DOM, and the installed RSC transport to the
latest patched releases together:

```sh
npm install react@latest react-dom@latest \
  react-server-dom-webpack@latest
```

Replace the example transport with the one the project uses. A hosting
provider's mitigation is not a substitute for updating dependencies.

## Update framework and bundler integrations

Affected integrations identified by `server-components-security` include:

- `next`
- React Router's unstable RSC APIs
- `waku`
- `@parcel/rsc`
- `@vitejs/plugin-rsc`
- `rwsdk`

Update the integration and every `react-server-dom-*` transport or RSC plugin
it uses. Next.js 13.3.x through 14.x must move to 14.2.35. Each 15.x or 16.x
line needs its own latest patched release. Replace `next@14.3.0-canary.77` or
later with the latest stable 14.x release.

## Preserve React Native version compatibility

The `server-components-security` guidance has a narrower React Native rule:

- A React Native app outside a monorepo that does not use `react-dom` needs no
  extra advisory-driven change beyond keeping `react` pinned.
- In a monorepo, update only an installed `react-server-dom-webpack`,
  `react-server-dom-parcel`, or `react-server-dom-turbopack` package.
- Do not also update `react` and `react-dom` for that monorepo remediation;
  doing so can create a React Native version mismatch.
