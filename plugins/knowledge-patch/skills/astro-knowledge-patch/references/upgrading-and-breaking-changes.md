# Upgrading and breaking changes

Use this reference when moving an existing project forward. It records both current migrations and older transitions that can still appear in maintained code.

## Runtime and toolchain

- Astro 7 uses the Sätteri Markdown and MDX processor by default and enables queued rendering by default (`7.0.0`). Projects that need remark or rehype plugins must select the unified processor explicitly.
- Astro 6 requires Node.js 22 or later and moved to Vite 7, Shiki 4, and Zod 4 (`6.0.0`). Update pinned Vite dependencies and import schema helpers from `astro/zod`, not `astro:content`.
- Astro 6.1 still targets Vite 7 and warns when a project installs top-level Vite 8. `astro add cloudflare` adds `"overrides": { "vite": "^7" }` to avoid known crashes (`6.1.0`).
- The Astro 7 alpha moved to Vite 8 and made `@astrojs/compiler-rs` the default and only compiler, so integrations that use Vite internals required testing and `experimental.rustCompiler` had to be removed (`6.2.0`).
- Astro 5.8 accepted Node.js 18 only at 18.20.8 and otherwise required 20.3.0 or 22.0.0 or later; Node.js 19 and 21 were unsupported (`5.8.0`). Pinning the recommended Node.js 22 in `.nvmrc` avoided the temporary Node.js 18 edge case.
- Astro 5 itself shipped with Vite 6 (`5.0.0`). Its Environment API became available to integration authors, while ordinary project upgrades were not expected to require code changes.

## Rendering and output migrations

- There is no separate `hybrid` output mode in Astro 5. Use the default `static` output, install an adapter, and export `prerender = false` only from routes that need runtime rendering (`5.0.0`).
- Queued rendering began behind `experimental.queuedRendering.enabled` in Astro 6 (`6.0.0`) and is automatic in Astro 7 (`7.0.0`).
- Route caching began under `experimental.cache` (`6.0.0`). In Astro 7, move `cache` and `routeRules` to the top level; `cache.invalidate()` can purge by tag or path (`7.0.0`).
- Advanced routing first exposed composable `astro/fetch` and `astro/hono` handlers (`6.3.0`). Astro 7 activates a custom pipeline when the standard fetch handler is placed at `src/fetch.ts` (`7.0.0`).

## Configuration promotions and replacements

| Old form | Current or replacement form |
|---|---|
| `experimental.session` plus top-level session settings (`5.3.0`) | Sessions are stable; remove the flag and keep `session` configuration (`5.7.0`). |
| `experimental.svg` (`5.0.0`) | Local SVG default imports are components without a flag (`5.7.0`). |
| `experimental.serializeConfig` (`5.2.0`) | `astro:config/client` and `astro:config/server` are stable (`5.7.0`). |
| `experimental.responsiveImages` and `image.experimentalDefaultStyles` (`5.9.0`) | Configure `image.responsiveStyles` and `image.layout` directly (`5.10.0`). |
| `experimental.csp` (`5.9.0`) | Use `security.csp` (`6.0.0`). |
| `experimental.fonts` (`5.7.0`) | Use top-level `fonts` (`6.0-guides`). |
| `experimental.svgo` (`5.16.0`) | Use pluggable `experimental.svgOptimizer`, commonly with `svgoOptimizer()` (`6.2.0`). |
| `experimental.rawEnvValues` (`5.12.0`) | `experimental.staticImportMetaEnv` superseded it (`5.13.0`). |
| `experimental.logger` and `--experimentalJson` (`6.2.0`) | Use top-level `logger` and `--json` (`7.0.0`). |
| top-level Markdown plugin and syntax options | Put them inside `markdown.processor: unified(...)`; the old forms are deprecated for removal in Astro 8 (`6.4.0`). |

## SVG compatibility

The experimental SVG component API removed `title`, `size`, and `mode` in `5.6.0`. Use `aria-label` instead of `title`, explicit `width` and `height` instead of `size`, remove both component and configuration `mode`, and add an explicit accessibility `role` where appropriate. These rules still apply after SVG components became stable in `5.7.0`.

Astro 6.3 stopped rasterizing SVG image sources by default because SVG can contain active content. Set `image.dangerouslyProcessSVG: true` only for trusted inputs; importing SVG as a component is unaffected (`6.3.0`).

## Markdown migration

Astro 6.4 introduced `markdown.processor` and moved unified-specific `remarkPlugins`, `rehypePlugins`, `remarkRehype`, `gfm`, and `smartypants` options into `unified()` (`6.4.0`). Astro 7 selects Sätteri for Markdown and MDX and enables GFM by default (`7.0.0`). Sätteri cannot run remark or rehype plugins, so plugin-dependent projects must configure `unified()` explicitly or port plugins to Sätteri MDAST or HAST plugins.

## Cookie API compatibility

Use the instance method `cookies.consume()` to consume response cookies and obtain their `Set-Cookie` values. The static `AstroCookies.consume(cookies)` form is deprecated but remains for adapter compatibility (`6.3.0`).
