---
name: service-workers-pwa-knowledge-patch
description: Service Workers and Progressive Web Apps
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Service Workers and Progressive Web Apps

Use this skill when implementing or reviewing service-worker static routing,
web app manifests, installed-app detection, installed-PWA navigation, or
Workbox window integration.

Treat browser and platform support as part of the design. Manifest standards,
service-worker APIs, installed-app relationships, and Workbox helpers do not
share one support matrix.

## Reference index

| Reference | Topics |
| --- | --- |
| [Manifest and navigation](references/manifest-and-navigation.md) | Default PWA link capture, manifest localization and dark colors, installability, update consent, storefront metadata |
| [Static routing](references/static-routing.md) | `InstallEvent.addRoutes()`, conditions, sources, ordering, limits, install failure, cache fallback |
| [Installation detection](references/installation-detection.md) | `getInstalledRelatedApps()`, Android, UWP, same-scope and cross-origin PWA detection |
| [Workbox lifecycle](references/workbox-lifecycle.md) | Registration timing, lifecycle event flags, `messageSW()`, custom-router cache messages |

## Compatibility changes and broken assumptions

### Installed desktop PWAs may capture links automatically

In Chrome 139 on Windows, macOS, and Linux, an in-scope capturable link opens
in an installed PWA by default. Do not assume every ordinary link navigation
remains in a browser tab.

Capture applies after Chrome determines that navigation creates a new frame
without an auxiliary browsing context, checks manifest scope, and honors the
user's opt-out preference. It falls back to a tab when no controlling PWA is
available or the user opted out. Do not assume the same behavior on ChromeOS.

### Specification-level installability is not an install prompt guarantee

The Web App Manifest specification treats every website as an installable web
application. The user agent still decides whether and how to offer
installation. Keep product-facing installation logic separate from the
specification's installability definition.

### Identity updates are consent-sensitive

Although a manifest is fetched and processed on each page load, changes to
`name`, `short_name`, `icons`, and their localized forms should require express
permission before being applied. Apply other non-security-sensitive changes
immediately, but do not design identity changes as silent updates.

A changed icon `src` counts as an update. A visually insignificant icon change
may be treated as non-security-sensitive. Locale selection may switch the
localized identity automatically, but the change should be presented when the
application next opens.

### Storefront members moved out of the core manifest specification

Look to the Manifest Application Information companion specification for
`categories`, `description`, `iarc_rating_id`, and `screenshots`. Do not treat
their absence from the core draft as removal from the broader manifest model.

### Static routing needs a feature fallback

`InstallEvent.addRoutes()` has limited availability and is not Baseline.
Feature-test it and preserve normal service-worker or network behavior where
it is unavailable.

## Manifest quick reference

### Localize identity and shortcut metadata with language maps

Add sibling `*_localized` language maps to:

- top-level `name`, `short_name`, and `icons`;
- shortcut `name`, `short_name`, `description`, and `icons`.

Keep the unsuffixed member as the fallback. A localized text entry may be a
plain string or an object containing `value` plus optional `lang` and `dir`.
Object defaults come from the language-map key and manifest-wide `dir`.
Localized image entries are arrays of image resources.

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

Expect the user agent to choose the best language match.

### Supply dark theme colors

Use `color_scheme_dark` only to override `theme_color` and
`background_color`:

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

The override follows the operating-system dark theme subject to user
preferences such as accessibility settings. Color values survive processing
only when they can be converted to sRGB without external data. `lab()` and
`color(display-p3 ...)` are convertible; a custom profile requiring
`@color-profile` is ignored.

## Static routing quick reference

Register predictable routes during `install` so network and cache sources can
be selected without starting the worker.

```js
self.addEventListener("install", event => {
  const added = event.addRoutes([
    {
      condition: { urlPattern: "/static/*" },
      source: { cacheName: "static-v3" }
    },
    {
      condition: { urlPattern: "/api/*", requestMethod: "GET" },
      source: "race-network-and-fetch-handler"
    }
  ]);
  event.waitUntil(added);
});
```

Choose sources deliberately:

| Source | Use |
| --- | --- |
| `"network"` | Send a matched request to the network |
| `"cache"` | Use the general cache route source |
| `{ cacheName }` | Select one named cache; a missing cache falls back to network |
| `"fetch-event"` | Dispatch to the worker's fetch handler |
| `"race-network-and-fetch-handler"` | Race an OK network response with a fetch-handler response for `GET` |

Install a `fetch` listener before using either handler-backed source or
`addRoutes()` rejects with `TypeError`.

Leaf conditions are ANDed. An `or` or `not` boolean node must be the condition
object's sole member. Respect first-match ordering, the accumulated
1024-condition budget, and maximum nesting depth 10.

Pass the returned promise to `waitUntil()` when an invalid or over-limit route
must fail installation. Calling `addRoutes()` keeps installation alive through
a separate always-fulfilled internal promise, so route rejection alone does
not otherwise fail the install.

## Installation detection quick reference

Call `navigator.getInstalledRelatedApps()` only in HTTPS contexts and treat an
empty result as normal:

```js
const related = await navigator.getInstalledRelatedApps?.() ?? [];
```

The query is not an installed-app enumerator. It considers only the first
three manifest `related_applications` entries, and returns only installed apps
that are declared by the site and mutually verified.

Select the relationship recipe by target:

| Target | Required relationship |
| --- | --- |
| Android app | App declares the website with Digital Asset Links; site declares the `play` package ID |
| Windows UWP | Package registers an App URI Handler; site publishes `windows-app-web-link` and declares the PFN plus `!App` |
| Same-scope PWA | Site declares its own `webapp` manifest URL and app ID |
| Cross-scope or cross-origin PWA | Android-only reciprocal WebAPK query relationship |

Do not depend on manifest `min_version` or `fingerprints` filters: browsers do
not implement them for these queries. Verify returned details in application
logic when version or certificate identity matters.

Desktop self-detection requires the page to share the PWA origin and be inside
manifest scope. The `webapp` entry's `id` is required on desktop, while Android
does not require it. Read the full platform recipes before editing declarations.

## Workbox lifecycle quick reference

Attach lifecycle listeners before `register()`. Registration normally waits
for the window `load` event; pass `{immediate: true}` to register sooner.

```js
const wb = new Workbox("/sw.js");
wb.addEventListener("waiting", event => showUpdatePrompt(event));
await wb.register({immediate: true});
```

Interpret event flags instead of treating every event as a fresh update:

- `isUpdate` distinguishes initial installation from an update.
- `isExternal` identifies a worker installed outside this `Workbox` instance.
- `wasWaitingBeforeRegister` means the worker was already waiting before
  registration, including the common reload case.

`messageSW()` selects a matching waiting worker before an active worker at
registration time; otherwise it waits for a matching installing worker. Its
promise resolves only when the worker replies through `event.ports[0]`.

```js
addEventListener("message", event => {
  if (event.data.type === "GET_VERSION") {
    event.ports[0].postMessage("2.0.0");
  }
});
```

The default `workbox-routing` router handles `CACHE_URLS` messages and caches
only URLs matching registered routes. For a separately constructed `Router`,
call `addCacheListener()` explicitly.

## Review checklist

- Check browser, operating-system, and library support independently.
- Keep unsuffixed manifest members as localization fallbacks.
- Require consent for visible identity changes.
- Feature-test static routing and preserve a fallback request path.
- Validate route condition shape, source prerequisites, order, and quotas.
- Use `waitUntil(addRoutesPromise)` when route failure must fail installation.
- Configure installed-app declarations and verification in both directions.
- Do not use installed-related-app results as arbitrary app enumeration.
- Register Workbox listeners before registration.
- Make every `messageSW()` request produce an explicit port reply.
