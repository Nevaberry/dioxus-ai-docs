# Compatibility, Security, and Release Policy

## Match the complete toolchain

Compatibility is minor-line-specific; do not treat an Angular major as having one TypeScript ceiling. Use the exact destination row (`release-policy-and-migrations`):

| Angular | Node.js alternatives | TypeScript | RxJS alternatives |
| --- | --- | --- | --- |
| `22.0.x` | `^22.22.3`, `^24.15.0`, or `^26.0.0` | `>=6.0.0 <6.1.0` | `^6.5.3` or `^7.4.0` |
| `21.0.x`–`21.2.x` | `^20.19.0`, `^22.12.0`, or `^24.0.0` | `>=5.9.0 <6.0.0` | `^6.5.3` or `^7.4.0` |
| `20.2.x`–`20.3.x` | `^20.19.0`, `^22.12.0`, or `^24.0.0` | `>=5.8.0 <6.0.0` | `^6.5.3` or `^7.4.0` |
| `20.0.x`–`20.1.x` | `^20.19.0`, `^22.12.0`, or `^24.0.0` | `>=5.8.0 <5.9.0` | `^6.5.3` or `^7.4.0` |

Angular `20.2.x` added TypeScript 5.9 support (`20.0.0`), while Angular 22 supports TypeScript 6 (`22.0.0`). Honor the narrower table ranges rather than those broad statements when selecting an exact compiler.

## Browser policy

Starting with v20, each major selects a “widely available” Baseline date near its release instead of promising a fixed number of latest browser versions:

| Angular | Baseline date |
| --- | --- |
| v20 | 2025-04-30 |
| v21 | 2025-10-20 |
| v22 | 2026-05-07 |

The set covers its core Chrome, Edge, Firefox, and Safari releases, uses a 30-month window, and targets roughly 95% of web users. Check the selected Baseline before relying on a newer platform API.

## Release, support, and migration policy

Angular targets a major every six months, one to three minors per major, and patch or prerelease builds nearly weekly. A major typically receives six months of active updates followed by 12 months of LTS. As recorded in `release-policy-and-migrations` on 2026-07-14, v22 was active; v21 and v20 were in LTS, with v20 supported through 2026-11-28; v2–v19 were unsupported.

LTS accepts newly identified security vulnerabilities and regressions caused after LTS began by third-party changes such as a new browser version. It does not receive ordinary bug fixes.

A deprecated API remains for at least the next two majors, approximately one year, and can be removed only in a major. During deprecation it receives critical and security fixes only. npm dependency updates that force application changes likewise occur only in majors; minors may widen peer ranges without forcing adoption.

The destination of `ng update` must still be supported and the source must be no more than one major behind. Cross majors one at a time, for example v10 → v11 → v12.

Developer Preview and Experimental APIs are outside ordinary versioning and deprecation guarantees and may change in a patch. Experimental work might never stabilize; Developer Preview means functional and polished, not necessarily complete migration tooling or documentation.

## Legacy Angular and CLI pairing

Before v9, framework and CLI versions were not fully synchronized. Use explicit pairs for legacy migrations:

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

## Content Security Policy

The application builder can generate a hash-based strict CSP for inline scripts (`19.0.0`). It is a Developer Preview opt-in:

```json
{
  "build": {
    "options": {
      "security": {"autoCSP": true}
    }
  }
}
```

Treat the preview status as significant when designing a long-lived deployment policy.

## URL and element security

Angular 22 tightens URL security (`22.0.0`):

- SVG animation URL attributes use the URL security context, so unsafe values are blocked.
- `object[data]` uses the resource-URL context.
- Translations cannot target `iframe src`.
- Translated form attributes and translated interpolated bindings are sanitized.

Do not bypass sanitization merely to preserve earlier behavior.

Namespaced MathML `script` elements are removed and prefixed SVG `script` hosts are rejected (`22.1.2`). Templates must not depend on either construct surviving compilation.

## Host-binding sanitization

Concrete-element host bindings pass through the applicable Angular sanitizer (`21.2.20`). Code must not depend on host bindings bypassing sanitization; review any directive that writes a URL- or HTML-sensitive host property.

## Internationalized attributes

Event attributes cannot be marked for i18n (`20.3.28`). Keep event handling outside translated attribute declarations. The possible-event-handler check applies only to property names longer than two characters, so an input named exactly `on` remains valid:

```html
<status-toggle [on]="enabled" />
```

This exception does not make actual event attributes translatable.
