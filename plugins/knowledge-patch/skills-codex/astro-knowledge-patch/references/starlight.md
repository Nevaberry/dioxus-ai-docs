# Starlight

## Composable generated sidebars

In starlight-0.39, `autogenerate` becomes a sidebar item. Move it inside a labeled group's `items`; the array may mix a generated directory with page IDs and custom links:

```js
starlight({
  sidebar: [{
    label: 'Features',
    items: [
      'features-overview',
      { autogenerate: { directory: 'features' } },
      { label: 'Support', link: 'https://support.example.com' },
    ],
  }],
});
```

## Internationalized links

In starlight-0.39, multilingual sites emit `x-default` alternate links pointing to the page in the default locale, providing a search fallback when no language-specific match applies.

## CJK spacing

In starlight-0.39, Starlight uses CSS `text-autospace` to insert spacing automatically between Chinese or Japanese text and non-CJK characters.
