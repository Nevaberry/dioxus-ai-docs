# Nuxt 4 Migration

## Compatibility Mode (3.12)

Opt into Nuxt 4 breaking changes incrementally via a config flag:

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  future: {
    compatibilityVersion: 4,
  },
})
```

### What it enables

Setting `compatibilityVersion: 4` activates v4 behavior changes while still running on Nuxt 3.12+:

- **Shallow reactive asyncData payloads** — `useAsyncData` and `useFetch` return shallow reactive refs instead of deep reactive refs, reducing unnecessary reactivity overhead
- Other v4 defaults as they are added in subsequent 3.x releases

### Migration strategy

1. Set `future.compatibilityVersion: 4` in `nuxt.config.ts`
2. Fix any issues that arise from the behavior changes
3. When Nuxt 4 releases, the upgrade path is already handled
