# Starlight

## Sidebar generation

In Starlight 0.39, `autogenerate` is a sidebar item rather than a property of a labeled group (`starlight-0.39`). Move it under `items`, where it can be mixed with page IDs and custom links:

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

## Internationalization and typography

- Multilingual sites emit an `x-default` alternate link for the version of each page in the default locale, giving search engines an explicit fallback.
- Starlight applies CSS `text-autospace` to add spacing automatically between Chinese or Japanese text and non-CJK characters.
