# Breaking Changes (Astro 6.0)

## Node.js Requirement

Astro 6.0 requires **Node 22+**. Node 18 and 20 are no longer supported.

## Removed APIs

| Removed | Replacement |
|---|---|
| `Astro.glob()` | Use `import.meta.glob()` or content collections |
| `emitESMImage()` | Use `astro:assets` image pipeline |
| `<ViewTransitions />` | Use `<ClientRouter />` |
| Legacy content collections | Use loader-based content collections (`defineCollection` with `loader`) |

## Zod 4

Astro 6.0 ships with **Zod 4**. Zod 3 is no longer supported. Update any custom schemas using Zod 3-specific APIs. Import from `astro/zod` as before.

## i18n

`i18n.redirectToDefaultLocale` default behavior changed — review your i18n config if relying on the previous default.

## Upgraded Dependencies

| Dependency | Version | Notes |
|---|---|---|
| Vite | 7 | Update any pinned Vite versions before upgrading |
| Shiki | 4 | Powers `<Code />` component and Markdown code blocks |
