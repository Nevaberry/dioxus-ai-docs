# Upgrading and breaking changes

## Astro 5 application model (5.0.0)

The former `hybrid` output mode is folded into the default `static` mode. Add
an adapter and export `prerender = false` only from routes that need runtime
rendering; all other routes remain prerendered.

Astro 5 is based on Vite 6. The Vite Environment API is available to
integration authors, but ordinary projects normally need no Vite-specific
code changes.

## Astro 5 Node.js floor (5.8.0)

Astro 5.8 supports Node.js 18 only at 18.20.8 and otherwise requires Node.js
20.3.0 or 22.0.0 and later. Node.js 19 and 21 are unsupported. Prefer pinning
Node.js 22 because Node.js 18 support is transitional:

```text
22
```

## Astro 6 runtime and dependency floor (6.0.0)

Astro 6 requires Node.js 22 or later and aligns its toolchain with Vite 7,
Shiki 4, and Zod 4. Upgrade a pinned Vite dependency to v7 or later and import
schema helpers from `astro/zod`, not `astro:content`:

```ts
import { z } from 'astro/zod';
```

Astro 6.1 still targets Vite 7 and warns during dev startup if a project has
top-level Vite 8. The Cloudflare add command installs this compatibility guard
automatically (6.1.0):

```json
{
  "overrides": { "vite": "^7" }
}
```

## Astro 7 compiler and toolchain (6.2.0)

The Astro 7 alpha moved to Vite 8, which can break plugins and integrations
that rely on Vite internals. It also made the Rust compiler the default and
only compiler. Remove `experimental.rustCompiler` when testing that toolchain.

Astro 6 projects can try the compiler first by installing
`@astrojs/compiler-rs` and enabling the flag:

```js
export default defineConfig({
  experimental: { rustCompiler: true },
});
```

## Stable and relocated configuration in Astro 7 (7.0.0)

- Sätteri replaces unified as the default Markdown and MDX processor. GFM is
  built in and enabled. Explicitly configure `unified()` to retain remark and
  rehype plugins.
- Queued rendering is stable, automatic, and no longer needs
  `experimental.queuedRendering`.
- Response caching moves from `experimental.cache` to top-level `cache`, and
  cache policies live in top-level `routeRules`.
- Structured logging moves from `experimental.logger` to `logger`; use
  `--json` instead of `--experimentalJson`.
- A standard advanced-routing handler becomes active only at `src/fetch.ts`.

## Feature promotion timeline

Use the stable form supported by the installed Astro version:

| Earlier form | Stable or replacement form |
|---|---|
| `experimental.session: true` (5.3.0) | Sessions need no flag from 5.7.0; keep driver options under `session` |
| `experimental.svg: true` (5.0.0) | SVG default imports are stable components from 5.7.0 |
| `experimental.serializeConfig` (5.2.0) | Config virtual modules need no flag from 5.7.0 |
| `experimental.responsiveImages` (5.0.0) | Use stable `image.responsiveStyles` and `image.layout` from 5.10.0 |
| `experimental.csp` (5.9.0) | Use stable `security.csp` from 6.0.0 |
| `experimental.fonts` (5.7.0) | Use top-level `fonts` from 6.0-guides |
| `experimental.svgo` (5.16.0) | Use pluggable `experimental.svgOptimizer` from 6.2.0 |
| `experimental.rawEnvValues` (5.12.0) | `experimental.staticImportMetaEnv` supersedes it in 5.13.0 |

## SVG component migration (5.6.0)

Imported SVG components no longer accept `title`, `size`, or `mode`. Use
`aria-label`, explicit `width` and `height`, and remove component and config
`mode` because imported SVGs are always inline. Astro supplies no default
`role`, so add one when semantics require it:

```astro
<Logo aria-label="My company logo" role="img" width={64} height={64} />
```

## Markdown processor migration (6.4.0)

`markdown.processor` replaces the fixed unified pipeline. Options for
`remarkPlugins`, `rehypePlugins`, `remarkRehype`, `gfm`, and `smartypants`
belong inside `unified({ ... })`; their top-level Markdown forms are deprecated
and scheduled for removal in Astro 8. Sätteri cannot execute remark or rehype
plugins.

## Cookie consumption migration (6.3.0)

Use `cookies.consume()` to mark an instance consumed and retrieve its
`Set-Cookie` values. The deprecated static `AstroCookies.consume(cookies)`
remains only for adapter compatibility. Calls to `set()` after consumption
warn because headers have already been sent.

## Cookie serialization compatibility (7.0.1-7.2.4)

After the move to `cookie` v2, values composed only of URL-safe characters are
no longer percent-encoded in `Set-Cookie` headers. Values already encoded still
round-trip unchanged; avoid tests that require unnecessary percent encoding.
