# React Server Components Security

## Exposure test

The request decoder in these packages was vulnerable to unauthenticated remote code execution when processing a crafted Server Function request:

- `react-server-dom-webpack`;
- `react-server-dom-parcel`; and
- `react-server-dom-turbopack`.

Affected versions include 19.0, 19.1.0, 19.1.1, and 19.2.0. The issue is CVE-2025-55182 with a CVSS score of 10.0.

An application is exposed when its framework, bundler, or plugin supports React Server Components, even if application code declares no Server Functions. The vulnerable decoding path is enough.

Client-only applications and applications with no RSC-capable framework, bundler, or plugin are unaffected.

## Complete remediation

The initial remote-code-execution fixes were 19.0.1, 19.1.2, and 19.2.1. Do not stop at those versions. Upgrade guidance was revised after these additional issues:

- denial of service: CVE-2025-55184;
- denial of service: CVE-2025-67779;
- denial of service: CVE-2026-23864; and
- source exposure: CVE-2025-55183.

Upgrade React, React DOM, and the installed RSC transport to the latest patched release together:

```sh
npm install react@latest react-dom@latest \
  react-server-dom-webpack@latest
```

Replace `react-server-dom-webpack` in the command with the installed Parcel or Turbopack transport when applicable.

Hosting-provider mitigations are defense in depth, not a substitute for dependency upgrades.

## Framework and bundler integrations

Affected integrations include:

- `next`;
- React Router's unstable RSC APIs;
- `waku`;
- `@parcel/rsc`;
- `@vitejs/plugin-rsc`; and
- `rwsdk`.

Update both the integration and every RSC transport or RSC plugin it installs or uses.

For Next.js:

- versions 13.3.x through 14.x must move to 14.2.35;
- each 15.x or 16.x line must move to its own latest patched release; and
- `next@14.3.0-canary.77` or later should be replaced with the latest stable 14.x release.

## React Native exception

Avoid applying the web remediation mechanically to React Native:

- A React Native application outside a monorepo that does not use `react-dom` needs no extra advisory-driven change beyond keeping its `react` version pinned.
- In a monorepo, update only any installed `react-server-dom-webpack`, `react-server-dom-parcel`, or `react-server-dom-turbopack` package.
- Do not also update `react` and `react-dom` in that monorepo solely for this advisory; doing so can create a React Native version mismatch.
