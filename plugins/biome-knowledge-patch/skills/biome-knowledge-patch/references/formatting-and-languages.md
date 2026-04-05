# Formatting & Language Support (v2.0–v2.4)

## Assists

New category between formatter and linter. Actions without diagnostics. Import organizing moved here from linter.

```json
{
  "assist": {
    "actions": {
      "source": {
        "organizeImports": "on",
        "useSortedKeys": {
          "level": "on",
          "options": {
            "groupByNesting": true
          }
        },
        "useSortedAttributes": "on",
        "noDuplicateClasses": "on"
      }
    }
  }
}
```

Import organizer revamp features: cross-chunk sorting, import merging from same module, custom ordering, export organizing, import attribute sorting.

## HTML Formatter (v2.0)

Experimental, disabled by default.

```json
{ "html": { "formatter": { "enabled": true } } }
```

Supported options: `attributePosition`, `bracketSameLine`, `whitespaceSensitivity`.

## Vue/Svelte/Astro Full Support (v2.3)

```json
{
  "html": {
    "experimentalFullSupportEnabled": true,
    "formatter": { "enabled": true, "indentScriptAndStyle": false }
  }
}
```

Capabilities:
- Formats/lints JS/TS in `script` blocks
- Formats/lints CSS in `style` blocks
- Formats/lints HTML templates
- CSS parser handles framework-specific pseudo-classes: `:deep`, `:slotted`, `v-bind()`, `:global`

## Tailwind v4 CSS (v2.3)

```json
{ "css": { "parser": { "tailwindDirectives": true } } }
```

Parses `@utility`, `@theme`, and other Tailwind v4 directives without errors.

## Embedded Snippets (v2.4)

Format and lint CSS-in-JS (styled-components, Emotion) and GraphQL in template literals:

```json
{ "javascript": { "experimentalEmbeddedSnippetsEnabled": true } }
```
