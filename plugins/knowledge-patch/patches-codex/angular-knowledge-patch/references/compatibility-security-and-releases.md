# Compatibility, Security, and Release Policy

## Toolchain compatibility

Match Node.js, TypeScript, and RxJS to the exact Angular minor line; the
TypeScript ceiling can change within a major. (`release-policy-and-migrations`)

| Angular | Node.js alternatives | TypeScript | RxJS alternatives |
| --- | --- | --- | --- |
| `22.0.x` | `^22.22.3`, `^24.15.0`, or `^26.0.0` | `>=6.0.0 <6.1.0` | `^6.5.3` or `^7.4.0` |
| `21.0.x`–`21.2.x` | `^20.19.0`, `^22.12.0`, or `^24.0.0` | `>=5.9.0 <6.0.0` | `^6.5.3` or `^7.4.0` |
| `20.2.x`–`20.3.x` | `^20.19.0`, `^22.12.0`, or `^24.0.0` | `>=5.8.0 <6.0.0` | `^6.5.3` or `^7.4.0` |
| `20.0.x`–`20.1.x` | `^20.19.0`, `^22.12.0`, or `^24.0.0` | `>=5.8.0 <5.9.0` | `^6.5.3` or `^7.4.0` |

Angular 20.2 added TypeScript 5.9 support (`20.0.0`). Angular 22 supports
TypeScript 6 (`22.0.0`).

## Browser policy

Starting with v20, each major pins a “widely available” Baseline date instead of
promising a fixed count of latest browsers. The selected Baseline uses a
30-month window across its core Chrome, Edge, Firefox, and Safari versions and
targets about 95% of web users. The dates are 2025-04-30 for v20, 2025-10-20 for
v21, and 2026-05-07 for v22. (`release-policy-and-migrations`)

## Release and support lifecycle

Angular targets a major every six months, one to three minors per major, and
patch or prerelease builds almost weekly. A major is normally supported for 18
months: six months active and 12 months LTS. As of 2026-07-14, v22 is active,
v21 is in LTS, v20 is in LTS through 2026-11-28, and v2–v19 are unsupported.
(`release-policy-and-migrations`)

LTS accepts only newly identified security vulnerabilities or regressions
introduced after LTS began by third-party changes such as a new browser version;
it does not receive general bug fixes. (`release-policy-and-migrations`)

A deprecated API remains for at least the next two major releases—about one
year—and can be removed only in a major. During that window it receives only
critical and security fixes. npm dependency upgrades that force application
changes also occur only in majors; minors may broaden peer ranges without
requiring an update. (`release-policy-and-migrations`)

Developer Preview and Experimental APIs sit outside the normal versioning and
deprecation guarantees and may change even in a patch. Experimental APIs might
never stabilize; Developer Preview means functional and polished, but migration
tooling or documentation can remain incomplete. (`release-policy-and-migrations`)

## Upgrade paths

The destination must still be supported and the source must be within one major
of it. Cross-major upgrades proceed one major at a time; for example, v10 to v12
must run v10 → v11 and then v11 → v12. (`release-policy-and-migrations`)

Before v9, Angular and Angular CLI were not fully synchronized, although their
major versions aligned starting with v7. Use explicit legacy pairings rather
than deriving a CLI version mechanically. (`release-policy-and-migrations`)

| Angular | Compatible Angular CLI |
| --- | --- |
| `8.2.x` | `8.2.x` or `8.3.x` |
| `8.0.x`–`8.1.x` | `8.0.x` or `8.1.x` |
| `7.2.x` | `7.2.x` or `7.3.x` |
| `7.0.x`–`7.1.x` | `7.0.x` or `7.1.x` |
| `6.1.x` | `6.1.x` or `6.2.x` |
| `6.0.x` | `6.0.x` |
| `5.2.x` | `1.6.x` or `1.7.x` |
| `5.0.x`–`5.1.x` | `1.5.x` |
| `4.2.x`–`4.4.x` | `1.3.x` or `1.4.x` |
| `4.0.x`–`4.1.x` | `1.0.x`, `1.1.x`, or `1.2.x` |
| `2.x` | not specified |

## Content Security Policy and sanitization

The application builder can generate a hash-based strict CSP for inline scripts
with the developer-preview `security.autoCSP` option (`19.0.0`):

```json
{"security":{"autoCSP":true}}
```

Angular 22 tightens URL and translation security (`22.0.0`):

- SVG animation attributes use the URL security context, so unsafe bindings are
  blocked.
- `object[data]` uses the resource-URL context.
- Translations cannot target `iframe src`.
- Translated form attributes and translated interpolated bindings are sanitized.

Concrete-host bindings now pass through the applicable sanitizer; do not depend
on a host binding bypassing sanitization (`21.2.20`). Event attributes marked for
i18n are rejected, so translated declarations must not contain event handling
(`20.3.28`).

The compiler removes namespaced MathML `script` elements and rejects prefixed
SVG `script` hosts (`22.1.2`).

## HTTP behavior hardening

`HttpHeaders.delete(name, value)` deletes only exact value matches; a partial
match is retained. Materializing a cloned headers object does not compromise its
immutability, so continue assigning the result of every later operation. Root
HTTP interceptors also run in the terminal request chain. (`21.2.20`)

```ts
const headers = new HttpHeaders({'X-Mode': ['prod', 'production']});
const next = headers.delete('X-Mode', 'prod');
// next.getAll('X-Mode') is ['production']
```

JSON responses are always decoded as UTF-8 regardless of other response
metadata (`22.1.2`).

## Locale data

The CLDR data changed from v41 to v47, so currency, date, and other
locale-sensitive formatting can change after an Angular 21 upgrade (`21.0.0`).
