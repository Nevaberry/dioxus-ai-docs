# Manifest and Navigation

## Installed PWA link capture

Starting with Chrome 139 on Windows, macOS, and Linux, an installed PWA
captures a capturable link by default when its target is within the PWA's
manifest scope (batch `chrome-139-pwa-navigation`).

A navigation is generally capturable when it creates a new frame without
opening an auxiliary browsing context. Chrome then checks scope and user
preference before applying the Launch Handling Algorithm. The target opens in
the PWA unless the user opted out. It falls back to a browser tab when there is
no controlling PWA or the user opted out. ChromeOS support was still pending.

Account for this behavior when navigation is expected to remain in a tab, and
do not generalize the desktop behavior to every platform.

## Localized manifest members

The Web App Manifest draft adds language maps for identity metadata and
shortcuts (batch `web-app-manifest-wd-2026-05`).

These top-level members accept a sibling language map:

| Fallback member | Language map |
| --- | --- |
| `name` | `name_localized` |
| `short_name` | `short_name_localized` |
| `icons` | `icons_localized` |

Each shortcut can similarly pair `name`, `short_name`, `description`, and
`icons` with `name_localized`, `short_name_localized`,
`description_localized`, and `icons_localized`.

The unsuffixed member remains the fallback. A localized text entry is either a
string or an object with:

- required `value`;
- optional `lang`, defaulting to the language-map key;
- optional `dir`, defaulting to the manifest-wide `dir`.

A localized image entry is an array of image resources. User agents should
select the best available language match.

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
  },
  "shortcuts": [{
    "name": "New",
    "name_localized": { "fr": "Nouveau" },
    "url": "/new"
  }]
}
```

## Dark-theme colors and sRGB conversion

`color_scheme_dark` can override only `theme_color` and `background_color`
when the operating system uses a dark theme. User preferences, including
accessibility settings, can affect whether the dark values apply.

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

The normal and dark color values are retained only if the user agent can
convert the CSS color to sRGB without external data. It can convert `lab()` and
`color(display-p3 ...)`; it ignores a color based on a custom profile that
requires `@color-profile`.

## Installability and installed-application semantics

At the specification level, every website is an installable web application.
Whether and how installation is offered remains at the user agent's
discretion. An installed application is more than a bookmark because its
manifest members, or their defaults, are applied to its top-level traversable.

Do not use the specification definition as evidence that a particular browser
will expose installation UI.

## Manifest update handling

A manifest is fetched and processed on every page load. User agents should
apply non-security-sensitive updates immediately, but identity-surface changes
need special handling.

Require express permission before applying changes to:

- `name` or `name_localized`;
- `short_name` or `short_name_localized`;
- `icons` or `icons_localized`.

A changed image `src` counts as an update. An icon that is not significantly
visually different may be treated as non-security-sensitive. A locale change
may automatically choose a different localized representation, but that
change should be presented the next time the application opens.

## Storefront metadata

The top-level `categories`, `description`, `iarc_rating_id`, and `screenshots`
members now belong to the Manifest Application Information companion
specification, rather than the core Web Application Manifest draft.
