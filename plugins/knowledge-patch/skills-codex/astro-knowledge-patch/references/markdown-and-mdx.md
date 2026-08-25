# Markdown and MDX

## TOML frontmatter

Since 5.2.0, Markdown and MDX accept TOML frontmatter without configuration. Delimit it with `+++`; it works for file exports and content collections.

```md
+++
title = 'TOML in Astro'
[params]
author = 'Houston'
+++
```

## Markdown images

Since 5.4.0, remote images in standard Markdown syntax pass through Astro's image service automatically. Use HTML `<img>` for a one-image opt-out; images in `public/` remain unprocessed. The then-experimental responsive-image flag also applied responsive properties and styles to Markdown and MDX images. Responsive image configuration later became stable under `image`.

## Highlighting and heading IDs

Since 5.5.0, `markdown.syntaxHighlight.excludeLangs` skips Shiki for selected fenced-code languages while leaving highlighting enabled elsewhere, allowing processors such as Mermaid to handle those blocks.

The same batch introduced `experimental.headingIdCompat`, which generates heading IDs compatible with common GitHub/npm processors rather than Astro's older handling of trailing dashes from special characters.

## SmartyPants

Since 6.1.0, `markdown.smartypants` can be an options object with individual punctuation transformations and locale-specific opening/closing quote characters:

```js
markdown: {
  smartypants: {
    dashes: 'oldschool',
    openingQuotes: { double: '«', single: '‹' },
    closingQuotes: { double: '»', single: '›' },
    ellipses: 'unspaced',
  },
}
```

When configuring `unified()` through `markdown.processor`, place this option inside the processor rather than at top level.

## Pluggable processors

Astro 6.4.0 adds `markdown.processor`. `unified()` keeps the traditional pipeline, but its options now belong inside the processor. Top-level `remarkPlugins`, `rehypePlugins`, `remarkRehype`, `gfm`, and `smartypants` are deprecated for removal in Astro 8.

```js
import { unified } from '@astrojs/markdown-remark';

export default {
  markdown: {
    processor: unified({ remarkPlugins: [remarkToc] }),
  },
};
```

The `@astrojs/markdown-satteri` package supplies a Rust processor with native flags such as directives. It does not execute remark or rehype plugins; retain unified or port those plugins to Sätteri MDAST/HAST plugins.

```js
import { satteri } from '@astrojs/markdown-satteri';

export default {
  markdown: {
    processor: satteri({ features: { directive: true } }),
  },
};
```

In 7.0.0, Sätteri becomes the default for both Markdown and MDX, with GFM built in and enabled. Projects using remark or rehype plugins must select unified explicitly.
