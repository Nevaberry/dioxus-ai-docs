# Signals & Reactivity (v19–v21)

## linkedSignal (stable in v20)

Writable signal that automatically resets when a source signal changes. Two forms:

### Short form — recomputes when any read signal changes

```typescript
const selected = linkedSignal(() => options()[0]);
selected.set(options()[2]); // writable like signal()
// When options() changes, selected resets to options()[0]
```

### Long form — access previous value to preserve selection

```typescript
const selected = linkedSignal<ShippingMethod[], ShippingMethod>({
  source: shippingOptions,
  computation: (newOptions, previous) =>
    newOptions.find((o) => o.id === previous?.value.id) ?? newOptions[0],
});
```

---

## resource (experimental)

Signal-based async data loading. Replaces manual subscribe/unsubscribe patterns.

```typescript
import { resource, Signal } from '@angular/core';

const userId: Signal<string> = getUserId();
const userResource = resource({
  params: () => ({ id: userId() }),
  loader: ({ params, abortSignal }) =>
    fetch(`/users/${params.id}`, { signal: abortSignal }),
});

// Read state
userResource.value(); // the loaded data
userResource.hasValue(); // boolean
userResource.isLoading(); // boolean
userResource.error(); // error or undefined
// IMPORTANT: reading .value() in error state throws — guard with .hasValue()
```

Streaming form uses `stream` instead of `params`/`loader` — returns `Promise<Signal<ResourceStreamItem<T>>>`.

---

## httpResource (experimental)

Signal-based HTTP fetching built on `HttpClient`. Requires `provideHttpClient()`.

### Simple — reactive URL string

```typescript
import { httpResource } from '@angular/common/http';

const user = httpResource<User>(() => `/api/user/${userId()}`);
```

### Advanced — full request object

```typescript
const user = httpResource(() => ({
  url: `/api/user/${userId()}`,
  method: 'GET',
  headers: { 'X-Special': 'true' },
  params: { fast: 'yes' },
}));
```

### Response types

```typescript
httpResource.text(() => url);
httpResource.blob(() => url);
httpResource.arrayBuffer(() => url);
```

### Zod validation

```typescript
const res = httpResource(() => `/api/people/${id()}`, {
  parse: starWarsPersonSchema.parse,
});
```

### Template usage

`user.value()`, `user.isLoading()`, `user.error()`, `user.hasValue()`, `user.headers()`.

Only use `httpResource` for reads — use `HttpClient` directly for mutations (POST/PUT/DELETE).
