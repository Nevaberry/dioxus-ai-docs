# Markdown and MDX

## Processor selection

Astro's Markdown pipeline is selected with `markdown.processor` (`6.4.0`). The unified-based processor remains available from `@astrojs/markdown-remark`:

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

Unified-specific `remarkPlugins`, `rehypePlugins`, `remarkRehype`, `gfm`, and `smartypants` now belong inside `unified()`. Their former top-level forms, such as `markdown.remarkPlugins`, are deprecated and scheduled for removal in Astro 8.

### Sätteri

`@astrojs/markdown-satteri` provides the Rust-based Sätteri processor and feature flags such as directives (`6.4.0`):

```js
import { satteri } from '@astrojs/markdown-satteri';

export default defineConfig({
  markdown: {
    processor: satteri({ features: { directive: true } }),
  },
});
```

Sätteri does not execute remark or rehype plugins. Stay on `unified()` when those plugins are required, or port them to Sätteri MDAST or HAST plugins.

Astro 7 selects Sätteri for both Markdown and MDX by default, with GFM built in and enabled (`7.0.0`). Plugin-dependent projects must explicitly retain `unified()` rather than relying on the old default.

## Frontmatter and data formats

Markdown and MDX accept TOML frontmatter between `+++` delimiters without extra configuration (`5.2.0`):

```md
+++
date = 2025-01-30
title = 'TOML frontmatter'
[params]
author = 'Houston'
+++

# Page title
```

This is separate from `glob()` loader support for standalone `.toml` data files, which became native in `5.12.0`.

## Syntax highlighting

`markdown.syntaxHighlight.excludeLangs` skips selected fenced-code languages while leaving Shiki enabled for the rest (`5.5.0`). This is useful when another plugin, such as Mermaid, must receive its own blocks unchanged.

```js
export default defineConfig({
  markdown: {
    syntaxHighlight: {
      type: 'shiki',
      excludeLangs: ['mermaid'],
    },
    rehypePlugins: [rehypeMermaid],
  },
});
```

When using the newer processor configuration, place the relevant unified options inside `unified()`.

## Heading IDs

`experimental.headingIdCompat` generates IDs compatible with common GitHub- and npm-style processors, especially for headings whose special characters produce trailing dashes under Astro's default algorithm (`5.5.0`).

```js
export default defineConfig({
  experimental: { headingIdCompat: true },
});
```

## SmartyPants

`markdown.smartypants` can be an options object rather than only a boolean (`6.1.0`). It exposes individual punctuation transforms and locale-specific opening and closing quotes:

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

For the unified processor, keep this option inside `unified()` under the processor-based configuration.

## Images and loader-rendered Markdown

- Standard Markdown syntax for a remote image uses Astro's image service by default; use an HTML `<img>` for a one-image opt-out, while files in `public/` remain unprocessed (`5.4.0`).
- Responsive-image configuration also applies to Markdown and MDX images.
- Custom content loaders can call `renderMarkdown(content)` and store its `{ html, metadata }` result as `rendered` to use project Markdown settings and the normal `render(entry)` flow (`5.9.0`).
