# Manifest and Launch Behavior

Use this reference when authoring a web app manifest, reviewing installation
semantics, handling post-install identity changes, or predicting desktop link
launch behavior.

## Installed-PWA link capture

In `chrome-139-pwa-navigation`, Chrome 139 changed desktop navigation for
installed PWAs on Windows, macOS, and Linux.

A link is generally capturable when its navigation:

- creates a new frame; and
- does not open an auxiliary browsing context.

For a capturable link, Chrome checks whether the target is inside an installed
PWA's manifest scope and whether the user permits capture. If both checks
pass, the link opens in the installed PWA through the Launch Handling
Algorithm. It opens in a browser tab when no PWA controls the target or the
user opted out. ChromeOS support was still pending.

The result is therefore conditional on navigation shape, manifest scope,
installation state, user preference, and platform. In-scope links are captured
by default on the supported desktop platforms, but capture is not universal.

## Localized manifest data

The `web-app-manifest-wd-2026-05` draft adds language-map siblings for
manifest identity fields and shortcut metadata.

### Supported pairs

At the manifest top level:

| Fallback member | Language map |
| --- | --- |
| `name` | `name_localized` |
| `short_name` | `short_name_localized` |
| `icons` | `icons_localized` |

Inside each shortcut:

| Fallback member | Language map |
| --- | --- |
| `name` | `name_localized` |
| `short_name` | `short_name_localized` |
| `description` | `description_localized` |
| `icons` | `icons_localized` |

The unsuffixed member remains the fallback when no language-map entry is a
better match.

### Text entry shape

A localized text entry may be either:

- a string; or
- an object with `value` and optional `lang` and `dir` overrides.

For an object entry, `lang` defaults to the language-map key and `dir`
defaults to the manifest-wide `dir`. The user agent should select the best
language match.

Localized image entries are arrays of image resources rather than text-entry
objects.

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

## Dark-theme colors

`color_scheme_dark` can override only `theme_color` and `background_color`
when the operating system is using a dark theme. User preferences, including
accessibility settings, may affect whether the override is applied.

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

For the normal and dark values alike, the user agent retains a color only when
it can convert that CSS color to sRGB without external data. `lab()` and
`color(display-p3 ...)` are convertible. A color that requires a custom
profile supplied through `@color-profile` is ignored.

## Installability and installed-application semantics

At the specification level, every website is an installable web application.
The user agent still decides whether and how to offer installation.

An installed web application is not merely a bookmark: its manifest members,
or the defaults for those members, are applied to the application's top-level
traversable.

## Updating identity surfaces

A user agent fetches and processes the manifest on every page load.
Non-security-sensitive changes should be applied immediately.

Updates to these identity surfaces require a different path:

- `name` and `name_localized`
- `short_name` and `short_name_localized`
- `icons` and `icons_localized`

The user agent should present such changes and obtain express permission
before applying them. A changed image `src` counts as an update. If an icon is
not significantly visually different, the user agent may treat the update as
non-security-sensitive.

A locale change may automatically select a localized identity
representation. The selected change should be presented the next time the
application opens.

## Storefront metadata ownership

The top-level members `categories`, `description`, `iarc_rating_id`, and
`screenshots` are defined in the separate Manifest Application Information
specification. They are no longer defined by the core Web Application
Manifest draft.
