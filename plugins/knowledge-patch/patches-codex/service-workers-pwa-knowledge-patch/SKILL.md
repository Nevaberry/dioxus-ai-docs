---
name: service-workers-pwa-knowledge-patch
description: Service Workers and Progressive Web Apps
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Service Workers and Progressive Web Apps Knowledge Patch

Use this skill when implementing or reviewing service worker routing, web app
manifests, PWA installation behavior, related-app detection, or Workbox window
integration. Start with the quick reference, then open the topic file that
matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/manifest-and-launch.md](references/manifest-and-launch.md) | Manifest localization, dark colors, installability, identity updates, storefront metadata, and installed-PWA link capture |
| [references/static-routing.md](references/static-routing.md) | `InstallEvent.addRoutes()`, condition composition, sources, ordering, limits, failure behavior, and cache fallback |
| [references/installation-detection.md](references/installation-detection.md) | `getInstalledRelatedApps()`, mutual verification, Android, UWP, and PWA self- or cross-origin detection |
| [references/workbox-lifecycle.md](references/workbox-lifecycle.md) | Registration timing, lifecycle event flags, `messageSW()`, and custom-router cache messages |

## Breaking and compatibility-sensitive changes

### Expect installed desktop PWAs to capture in-scope links

On Chrome 139 for Windows, macOS, and Linux, a capturable link targeting an
installed PWA's manifest scope opens in that PWA by default. It opens in a
browser tab when no PWA controls the target or the user has opted out.
ChromeOS support was still pending.

A navigation is generally capturable when it creates a new frame without
opening an auxiliary browsing context. Chrome then checks scope and user
preference before running launch handling. Do not assume every navigation or
every desktop platform is captured.

### Move storefront metadata out of the core manifest model

Treat top-level `categories`, `description`, `iarc_rating_id`, and
`screenshots` as members of the companion Manifest Application Information
specification, not the core Web Application Manifest specification.

### Require consent for identity-surface updates

The manifest is fetched and processed on every page load. User agents should
apply non-security-sensitive changes immediately, but changes to `name`,
`short_name`, `icons`, or their localized forms require presentation to the
user and express permission before application.

A changed image `src` counts as an update. An icon that is not significantly
visually different may be treated as non-security-sensitive. Locale changes
may select localized representations automatically, but those changes should
be presented the next time the installed application opens.

### Treat static routing as progressive enhancement

`InstallEvent.addRoutes()` can select a network or cache source before starting
the service worker, avoiding a worker cycle for predictable requests. Browser
availability is limited and the API is not Baseline, so do not make it the
only path on which an application depends.

## Manifest quick reference

### Localize manifest and shortcut fields with language maps

Add a `*_localized` sibling to a supported unsuffixed member. The unsuffixed
member remains the fallback.

Supported manifest members:

- `name` and `name_localized`
- `short_name` and `short_name_localized`
- `icons` and `icons_localized`

Supported shortcut members:

- `name` and `name_localized`
- `short_name` and `short_name_localized`
- `description` and `description_localized`
- `icons` and `icons_localized`

Text map values may be strings or objects containing `value` plus optional
`lang` and `dir`. The map key supplies the default language, and the
manifest-wide `dir` supplies the default direction. Localized image values are
arrays of image resources. The user agent selects the best language match.

```json
{
  "lang": "en-US",
  "dir": "ltr",
  "name": "Color Picker",
  "name_localized": {
    "de": "Farbwähler",
    "ar": { "value": "منتقي الألوان", "dir": "rtl" }
  },
  "icons": [{ "src": "/icons/default.png", "sizes": "256x256" }],
  "icons_localized": {
    "fr": [{ "src": "/icons/fr.png", "sizes": "256x256" }]
  }
}
```

### Provide dark-theme colors

`color_scheme_dark` may override only `theme_color` and `background_color`
when the operating system uses a dark theme, subject to preferences such as
accessibility settings.

```json
{
  "background_color": "#fff",
  "theme_color": "red",
  "color_scheme_dark": {
    "background_color": "#000",
    "theme_color": "hotpink"
  }
}
```

The user agent retains these colors only when it can convert the CSS color to
sRGB without external data. It can convert `lab()` and
`color(display-p3 ...)`; it ignores colors that need a custom
`@color-profile`.

### Separate specification installability from browser UX

At the specification level, every website is an installable web application.
Whether or how installation is offered is still the user agent's choice. An
installed application differs from a bookmark because the manifest members,
or their defaults, apply to its top-level traversable.

## Static routing quick reference

### Compose conditions strictly

Within a condition, the leaf members `urlPattern`, `requestMethod`,
`requestMode`, `requestDestination`, and `runningStatus` are ANDed.
`runningStatus` accepts only `"running"` or `"not-running"`.

An `or` or `not` boolean node must be the condition object's sole member. A
condition with no recognized member is invalid. URL patterns resolve against
the service worker script URL and cannot contain regular-expression groups.
Methods must be valid, non-forbidden HTTP methods.

### Choose and validate sources

Routes accept `"network"`, `"cache"`, `"fetch-event"`, a named cache object
such as `{ cacheName: "static-v3" }`, or
`"race-network-and-fetch-handler"`.

The two handler-backed sources require a `fetch` listener; otherwise
`addRoutes()` rejects with `TypeError`. Racing applies to `GET`: it races an
OK network response against the fetch handler, and a valid handler response
aborts the network request.

If a named cache does not exist, the browser falls back to the network. Cache
absence by itself does not fail the request.

### Preserve deterministic ordering and installation failure

Each `addRoutes()` call appends rules. The first matching rule chooses the
source. Across the accumulated list, the condition-count budget is 1024 and
the nesting-depth limit is 10. Invalid or over-limit additions reject
atomically.

`addRoutes()` keeps installation alive through an internal promise that is
always fulfilled. To make registration failure fail installation, explicitly
pass the returned promise to `waitUntil()`:

```js
self.addEventListener("install", event => {
  const added = event.addRoutes({
    condition: { urlPattern: "/offline/*" },
    source: { cacheName: "offline-v1" }
  });
  event.waitUntil(added);
});
```

## Installation detection quick reference

`navigator.getInstalledRelatedApps()` works on HTTPS and returns only
installed applications declared in the site's manifest and mutually verified
with the site. It considers only the first three `related_applications`
entries; it cannot enumerate arbitrary installed applications.

Results include values such as `platform`, `id`, and `url`; Android results
also expose `version`. Browsers do not implement manifest `min_version` or
`fingerprints` filtering on any platform, so do not rely on either to exclude
an older or certificate-mismatched installation.

Use the platform-specific declarations in
[references/installation-detection.md](references/installation-detection.md):

- Android installed-app detection requires declarations in both directions.
- UWP detection requires an App URI Handler and a `windows-app-web-link` file.
- Same-origin, in-scope PWA self-detection works on supported Android and
  desktop browsers.
- Cross-scope or cross-origin PWA detection remains Android-only.

## Workbox lifecycle quick reference

Attach lifecycle listeners before calling `Workbox#register()`. Registration
waits for the window `load` event unless called with `{immediate: true}`.

Use lifecycle event flags deliberately:

- `isUpdate` distinguishes first installation from an update.
- In Workbox v6+, `isExternal` marks a worker installed outside the current
  `Workbox` instance, such as by another tab.
- `wasWaitingBeforeRegister` marks a worker that was already waiting before
  `register()`, including the common repeated prompt after reload.

`messageSW()` selects a matching worker through `getSW()`, preferring a
matching waiting worker over the active worker at registration time and
otherwise waiting for a matching installing worker. Because it uses a
`MessageChannel`, its promise remains pending until the service worker replies
through `event.ports[0]`.

The default `workbox-routing` router handles `CACHE_URLS` messages and caches
only URLs matching registered routes. A separately constructed `Router` must
opt in with `addCacheListener()`.
