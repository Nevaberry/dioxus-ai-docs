---
name: angular-knowledge-patch
description: "Angular v19-v21 features: linkedSignal, resource/httpResource, signal forms, route-level SSR render modes, incremental hydration, zoneless change detection, Vitest migration, and Angular Aria components."
version: "21.0.0"
license: MIT
metadata:
  author: Nevaberry
  tags:
    - angular
    - signals
    - ssr
    - forms
    - zoneless
---

# Angular Knowledge Patch (v19–v21)

**Baseline**: Angular through v18.x (signals basics, new control flow, standalone components, zoneless experimental, SSR hydration basics, esbuild builder).

This patch covers features from Angular v19 through v21 (2024-11 to 2025-11).

## Index

| Topic | File | Key APIs |
|-------|------|----------|
| Signals & Reactivity | [references/signals-and-reactivity.md](references/signals-and-reactivity.md) | `linkedSignal`, `resource`, `httpResource` |
| Signal Forms | [references/signal-forms.md](references/signal-forms.md) | `form()`, `FormField`, validators |
| SSR & Hydration | [references/ssr-and-hydration.md](references/ssr-and-hydration.md) | `RenderMode`, `ServerRoute`, incremental hydration |
| Zoneless & Testing | [references/zoneless-and-testing.md](references/zoneless-and-testing.md) | `provideZonelessChangeDetection`, Vitest |
| Components & Templates | [references/components-and-templates.md](references/components-and-templates.md) | Angular Aria, regex in templates, `@defer` viewport |

---

## Quick Reference

### Signal APIs at a glance

| API | Status | Import | Purpose |
|-----|--------|--------|---------|
| `linkedSignal` | Stable (v20) | `@angular/core` | Writable signal that resets when source changes |
| `resource` | Experimental | `@angular/core` | Signal-based async data loading |
| `httpResource` | Experimental | `@angular/common/http` | Signal-based HTTP fetching (reads only) |
| `form()` | Experimental (v21+) | `@angular/forms/signals` | Signal-based forms with schema validation |

### linkedSignal — short form

```typescript
const selected = linkedSignal(() => options()[0]);
selected.set(options()[2]); // writable
// Resets to options()[0] when options() changes
```

### resource — basic pattern

```typescript
import { resource, Signal } from '@angular/core';

const userId: Signal<string> = getUserId();
const userResource = resource({
  params: () => ({ id: userId() }),
  loader: ({ params, abortSignal }) =>
    fetch(`/users/${params.id}`, { signal: abortSignal }),
});
// userResource.value(), .isLoading(), .error(), .hasValue()
// IMPORTANT: .value() throws in error state — guard with .hasValue()
```

### httpResource — basic pattern

```typescript
import { httpResource } from '@angular/common/http';

// Reactive URL — re-fetches when userId() changes
const user = httpResource<User>(() => `/api/user/${userId()}`);
// user.value(), .isLoading(), .error(), .hasValue(), .headers()
// Only for reads — use HttpClient directly for mutations
```

### Zoneless Angular (stable v20.2, default v21)

```typescript
bootstrapApplication(AppComponent, {
  providers: [
    provideZonelessChangeDetection(),
    provideBrowserGlobalErrorListeners(),
  ],
});
// Remove zone.js polyfill from angular.json
```

### Vitest (default in v21)

```bash
# Migrate existing Jasmine tests
ng g @schematics/angular:refactor-jasmine-vitest
```

### Route-level render mode

```typescript
import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRouteConfig: ServerRoute[] = [
  { path: '/login', mode: RenderMode.Server },
  { path: '/dashboard', mode: RenderMode.Client },
  {
    path: '/product/:id',
    mode: RenderMode.Prerender,
    async getPrerenderPaths() {
      return (await inject(ProductService).getIds()).map((id) => ({ id }));
    },
  },
  { path: '/**', mode: RenderMode.Prerender },
];
```

### Incremental hydration

```typescript
provideClientHydration(withIncrementalHydration())

// Template
@defer (hydrate on viewport) {
  <shopping-cart/>
}
```

### Signal Forms — minimal example

```typescript
import { form, FormField, required, email, submit } from '@angular/forms/signals';

loginModel = signal({ email: '', password: '' });
loginForm = form(this.loginModel, (schema) => {
  required(schema.email, { message: 'Email is required' });
  email(schema.email, { message: 'Invalid email' });
  required(schema.password, { message: 'Password is required' });
});
```

Template: `<input [formField]="loginForm.email" />`, access state via `loginForm.email()` → `.value()`, `.touched()`, `.valid()`, `.errors()`, `.dirty()`, `.pending()`.

### linkedSignal — long form (preserve selection across source changes)

```typescript
const selected = linkedSignal<ShippingMethod[], ShippingMethod>({
  source: shippingOptions,
  computation: (newOptions, previous) =>
    newOptions.find(o => o.id === previous?.value.id) ?? newOptions[0],
});
```

### httpResource — advanced request + Zod validation

```typescript
const user = httpResource(() => ({
  url: `/api/user/${userId()}`,
  method: 'GET',
  headers: { 'X-Special': 'true' },
  params: { fast: 'yes' },
}));

// Response type variants
httpResource.text(() => url);
httpResource.blob(() => url);

// Zod validation
const res = httpResource(() => `/api/people/${id()}`, {
  parse: starWarsPersonSchema.parse,
});
```

### Angular Aria (developer preview, v21)

Headless accessible components: `npm i @angular/aria`. Patterns: Accordion, Combobox, Grid, Listbox, Menu, Tabs, Toolbar, Tree. Unstyled — you provide all CSS.
