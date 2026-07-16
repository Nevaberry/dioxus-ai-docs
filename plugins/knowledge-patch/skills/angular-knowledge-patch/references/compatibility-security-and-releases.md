# Compatibility, Security, and Release Policy

Batch attribution: 19.0.0, 20.0.0, 21.0.0, 22.0.0, release-policy-and-migrations.

## Match the whole toolchain

Compatibility can change between minor lines, especially at the TypeScript ceiling. Match Node.js, TypeScript, and RxJS to the exact Angular line instead of assuming one range applies to an entire major.

| Angular | Node.js alternatives | TypeScript | RxJS alternatives |
| --- | --- | --- | --- |
| `22.0.x` | `^22.22.3`, `^24.15.0`, or `^26.0.0` | `>=6.0.0 <6.1.0` | `^6.5.3` or `^7.4.0` |
| `21.0.x`–`21.2.x` | `^20.19.0`, `^22.12.0`, or `^24.0.0` | `>=5.9.0 <6.0.0` | `^6.5.3` or `^7.4.0` |
| `20.2.x`–`20.3.x` | `^20.19.0`, `^22.12.0`, or `^24.0.0` | `>=5.8.0 <6.0.0` | `^6.5.3` or `^7.4.0` |
| `20.0.x`–`20.1.x` | `^20.19.0`, `^22.12.0`, or `^24.0.0` | `>=5.8.0 <5.9.0` | `^6.5.3` or `^7.4.0` |

Angular 20.2 added TypeScript 5.9 support. Angular 22 supports TypeScript 6.

## Browser support uses Baseline dates

Starting with Angular 20, each major selects a “widely available” Baseline date close to its release rather than promising a fixed count of latest browser versions.

| Angular | Baseline date |
| --- | --- |
| 20 | 2025-04-30 |
| 21 | 2025-10-20 |
| 22 | 2026-05-07 |

The set covers its core Chrome, Edge, Firefox, and Safari browsers, uses a 30-month window, and targets approximately 95% of web users.

## Security-sensitive bindings and translations

Angular 22 tightens URL and translated-attribute handling:

- SVG animation attributes are registered in the URL security context, so unsafe bindings to them are blocked.
- `object[data]` is a resource-URL context.
- Translations cannot target `iframe src`.
- Translated form attributes and translated interpolated bindings are sanitized.

Do not use sanitization bypasses merely to preserve behavior that these changes intentionally reject.

## Automatic strict CSP

The application builder can generate a hash-based strict Content Security Policy for inline scripts. This began as a developer-preview opt-in in Angular 19; enable it through `security.autoCSP` in builder options:

```json
{
  "projects": {
    "app": {
      "architect": {
        "build": {
          "options": {
            "security": {"autoCSP": true}
          }
        }
      }
    }
  }
}
```

## Release and support lifecycle

Angular targets:

- one major release every six months;
- one to three minors for each major;
- patch or prerelease builds almost weekly;
- approximately 18 months of support for each major: six months active and 12 months LTS.

As of 2026-07-14, Angular 22 is active, Angular 21 is in LTS, Angular 20 is in LTS through 2026-11-28, and Angular 2 through 19 are unsupported.

### LTS fix eligibility

LTS is not a stream for general bug fixes. A fix is generally considered only for:

- a newly identified security vulnerability; or
- a regression introduced after LTS began by a third-party change, such as a new browser version.

### Deprecation and dependency guarantees

A deprecated API remains for at least the next two major releases, approximately one year, and can be removed only in a major. During that period, it receives only critical and security fixes.

npm dependency updates that force application changes likewise occur only in major releases. A minor may expand supported peer-dependency ranges but does not require applications to update those peers.

Developer Preview and Experimental APIs are outside these normal versioning and deprecation guarantees and can change even in a patch. Experimental work might never stabilize. Developer Preview indicates an API intended to be functional and polished, but migration tooling or documentation can still be incomplete.

## Plan `ng update` hops

The destination release must still be supported, and the source must be no more than one major behind it. Cross-major upgrades therefore proceed one major at a time. For example, upgrade 10 → 11, then 11 → 12; do not attempt 10 → 12 directly.

Angular 22's update migration also adds `strictTemplates` to the project TypeScript configuration. Treat newly surfaced errors as required migration work rather than disabling the setting indiscriminately.

## Legacy Angular and CLI pairing

Before Angular 9, the framework and CLI were not fully synchronized, even though their major versions aligned starting with Angular 7. Choose an explicit compatible pair when migrating an old project:

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

## Removed and deprecated platform integrations

- Angular 22 removes the built-in Hammer.js integration. Applications that still need gestures must provide their own implementation.
- Angular 22 deprecates webpack support, including `@angular-devkit/build-angular` builders and `@ngtools/webpack`, as the application builder shifts toward TSGo support.

Coordinate these changes with the testing and tooling migrations in [Testing, Build Tooling, and Migrations](testing-and-tooling.md).
