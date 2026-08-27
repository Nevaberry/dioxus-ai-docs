# Upgrading and breaking changes

Use this reference to identify runtime, dependency, configuration, and API migrations before debugging application behavior.

## Output and rendering modes

Since 5.0.0, the former `hybrid` mode is part of the default static output. Add an adapter and set `export const prerender = false` only on routes that need runtime rendering; leave other routes prerendered.

Queued rendering began behind `experimental.queuedRendering.enabled` in 6.0.0. It is stable, automatic, and no longer configured experimentally in 7.0.0. Route caching likewise began under `experimental.cache` in 6.0.0, then moved to top-level `cache` and `routeRules` in 7.0.0.

## Runtime and dependency requirements

Astro 5.0.0 moved to Vite 6 and exposed Vite's Environment API to integrations without normally requiring application changes.

Astro 5.8.0 supports Node.js 18 only at 18.20.8; otherwise it requires Node.js 20.3.0 or 22.0.0 and later. Node.js 19 and 21 are unsupported. Prefer pinning Node.js 22 because Astro 6 removes Node.js 18 support.

Astro 6.0.0 requires Node.js 22 or later and upgrades to Vite 7, Shiki 4, and Zod 4. Update pinned Vite dependencies and import Zod from `astro/zod`, not `astro:content`.

Astro 6.1.0 warns when a project installs top-level Vite 8. Keep an Astro 6 override such as `{ "overrides": { "vite": "^7" } }`; `astro add cloudflare` adds it automatically. The Astro 7 alpha described in 6.2.0 moves to Vite 8, may break integrations that depend on Vite internals, and makes the Rust compiler the only compiler, so remove `experimental.rustCompiler` when testing it.

## Configuration promotion and replacement

- Configuration imports were introduced behind `experimental.serializeConfig` in 5.2.0 and became stable as `astro:config/client` and `astro:config/server` in 5.7.0. Remove the flag.
- Sessions used `experimental.session` with top-level driver settings in 5.3.0, then became stable in 5.7.0. Remove the flag but keep `session` driver configuration.
- Responsive layouts began behind `experimental.responsiveImages` in 5.0.0, expanded to Markdown and MDX in 5.4.0, and became stable under `image.responsiveStyles` and `image.layout` in 5.10.0.
- CSP began under `experimental.csp` in 5.9.0 and moved to stable `security.csp` in 6.0.0.
- Fonts began under `experimental.fonts` in 5.7.0 and moved to top-level `fonts` in 6.0-guides.
- SVG optimization began as `experimental.svgo` in 5.16.0 and was replaced by pluggable `experimental.svgOptimizer` in 6.2.0.
- Structured logging began under `experimental.logger` with `--experimentalJson` in 6.2.0; in 7.0.0 use top-level `logger` and `--json`.

## Markdown processor migration

Astro 6.4.0 added pluggable `markdown.processor` configuration. The old top-level `remarkPlugins`, `rehypePlugins`, `remarkRehype`, `gfm`, and `smartypants` options are deprecated for removal in Astro 8; move them into `unified({ ... })`.

Astro 7.0.0 makes Sätteri the Markdown and MDX default with GFM enabled. Sätteri does not run remark or rehype plugins, so projects that need them must select `unified()` explicitly or port them to Sätteri MDAST/HAST plugins.

## SVG component migration

SVG imports first appeared behind `experimental.svg` in 5.0.0 and became stable in 5.7.0. Since 5.6.0, components no longer accept `title`, `size`, or `mode`, are always inline, and receive no default `role`. Use `aria-label`, explicit `width` and `height`, and an explicit accessibility role when needed.

## Environment behavior migration

The 5.12.0 `experimental.rawEnvValues` option stopped coercing raw `import.meta.env` strings but did not affect `astro:env`. In 5.13.0, `experimental.staticImportMetaEnv` superseded it by also inlining private values in Vite-compatible fashion. Remove `rawEnvValues` when enabling the newer behavior.

## Cookie API migration

Since 6.3.0, call the instance method `cookies.consume()`; the deprecated `AstroCookies.consume(cookies)` remains only for adapter compatibility. After the cookie v2 update in 7.0.1-7.2.4, URL-safe cookie values are no longer percent-encoded, while already encoded values still round-trip unchanged.
