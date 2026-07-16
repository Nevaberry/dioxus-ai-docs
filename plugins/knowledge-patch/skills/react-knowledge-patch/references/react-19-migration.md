# React 19 Migration and Compatibility

## Generated `useId` values

The default generated prefix changed across React 19 patch lines:

| Release | Prefix |
|---|---|
| 19.0 | `:r:` |
| 19.1 | `«r»` |
| 19.2.0 | `_r_` |

The `_r_` form is valid both as a CSS `view-transition-name` value and as an XML 1.0 name. Server-rendered output, tests, and snapshots that expose generated IDs will change.

Treat `useId` values as opaque. Update snapshots where the change is expected, and remove application logic that parses or depends on a generated prefix.

## CSP nonces for hoistable styles

React DOM accepts a `nonce` on hoistable styles, allowing them to pass a nonce-based Content Security Policy.

## Maintained React 19 patch levels

For projects intentionally pinned to a React 19 minor line, the June 2026 listed patch targets are:

| Minor line | Patch target |
|---|---|
| 19.2 | `19.2.7` |
| 19.1 | `19.1.8` |
| 19.0 | `19.0.7` |

Security remediation can require a newer release than an application's current pin. Update `react`, `react-dom`, and any RSC transport coherently; see [Security](security.md) for the RSC-specific rules and the React Native monorepo exception.
