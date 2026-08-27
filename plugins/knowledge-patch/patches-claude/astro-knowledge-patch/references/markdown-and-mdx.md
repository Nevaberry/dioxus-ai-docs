# Markdown and MDX

## TOML frontmatter (5.2.0)

Markdown and MDX accept TOML frontmatter without configuration. Delimit it
with `+++`; it works for file exports and content collections.

```md
+++
date = 2025-01-30
title = 'Use TOML frontmatter in Astro!'
[params]
author = 'Houston'
+++

# Support for TOML frontmatter is here!
```

The built-in `glob()` loader also parses standalone TOML data files natively
from 5.12.0.

## Remote and responsive Markdown images (5.4.0)

Remote images written with standard Markdown syntax pass through Astro's
image service by default in Markdown and MDX. Use an HTML `<img>` to bypass
optimization for one remote image. Images under `public/` remain unprocessed.

```md
![Houston](https://images.unsplash.com/photo-1530089711124-9ca31fb9e863)
```

In Astro 5.4, `experimental.responsiveImages` also makes Markdown and MDX
images responsive by generating properties and styles. Astro 5.10 promotes
responsive image configuration to stable `image.responsiveStyles` and
`image.layout`.

## Excluding languages from highlighting (5.5.0)

`markdown.syntaxHighlight.excludeLangs` leaves selected fenced-code languages
unhighlighted while preserving Shiki elsewhere. This allows processors such
as Mermaid to handle their own blocks.

```js
import rehypeMermaid from 'rehype-mermaid';

export default defineConfig({
  markdown: {
    syntaxHighlight: { type: 'shiki', excludeLangs: ['mermaid'] },
    rehypePlugins: [rehypeMermaid],
  },
});
```

When using Astro 7, keep such rehype configuration inside an explicitly
selected `unified()` processor.

## Processor-compatible heading IDs (5.5.0)

`experimental.headingIdCompat` generates IDs compatible with common GitHub
and npm processors, rather than Astro's earlier behavior around trailing
dashes produced from special characters.

```js
export default defineConfig({
  experimental: { headingIdCompat: true },
});
```

## Rendering Markdown in loaders (5.9.0)

Custom content loaders receive `renderMarkdown(content)`. It applies project
Markdown configuration and plugins and returns `{ html, metadata }`; place the
result in an entry's `rendered` field to enable `render(entry)` and
`<Content />` for remote Markdown.

## Structured SmartyPants options (6.1.0)

`markdown.smartypants` accepts an object as well as a boolean. The object can
select punctuation transformations and locale-specific quote characters.

```js
export default defineConfig({
  markdown: {
    smartypants: {
      dashes: 'oldschool',
      openingQuotes: { double: '«', single: '‹' },
      closingQuotes: { double: '»', single: '›' },
      ellipses: 'unspaced',
    },
  },
});
```

## Pluggable processors (6.4.0)

`markdown.processor` can replace the unified-based pipeline. To keep unified,
import it from `@astrojs/markdown-remark` and move processor options into its
argument:

```js
import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import remarkToc from 'remark-toc';

export default defineConfig({
  markdown: {
    processor: unified({ remarkPlugins: [remarkToc] }),
  },
});
```

The top-level `markdown.remarkPlugins`, `rehypePlugins`, `remarkRehype`, `gfm`,
and `smartypants` forms are deprecated and scheduled for removal in Astro 8.

## Sätteri processor (6.4.0)

`@astrojs/markdown-satteri` supplies a Rust-based Markdown and MDX processor
with native feature flags such as directives:

```js
import { defineConfig } from 'astro/config';
import { satteri } from '@astrojs/markdown-satteri';

export default defineConfig({
  markdown: {
    processor: satteri({ features: { directive: true } }),
  },
});
```

Sätteri does not run remark or rehype plugins. Projects depending on those
plugins must remain on `unified()` or port them to Sätteri MDAST or HAST
plugins.

## Astro 7 default processor (7.0.0)

Sätteri becomes the default for Markdown and MDX, with GFM built in and
enabled. Existing projects that rely on remark or rehype plugins must select
`unified()` explicitly; relying on the old implicit default silently drops
those plugins.
