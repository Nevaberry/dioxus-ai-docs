# React 19 Migration and Compatibility

Output and DOM compatibility changes below are attributed to `19.2.0`; the June patch-level snapshot is from `news-and-versions`.

## Update expectations for generated IDs

The default `useId` prefix changed from `:r:` in React 19.0 and `«r»` in React 19.1 to `_r_`. The new form is valid as a `view-transition-name` and as an XML 1.0 name.

Rendered output and snapshots that expose generated IDs will change. Update those expectations, and avoid application logic that depends on the exact generated text.

## Add CSP nonces to hoistable styles

React DOM permits a `nonce` on hoistable styles, allowing those styles to work under a nonce-based Content Security Policy.

## Interpret listed React 19 patch levels carefully

The June 2026 release snapshot listed `19.2.7`, `19.1.8`, and `19.0.7` as the patch targets for projects pinned to the corresponding React 19 minor lines.

Treat those values as the recorded June 2026 levels, not as a substitute for security guidance to install the latest patched release available for the selected minor line.
