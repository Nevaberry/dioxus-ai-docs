# API Migrations and Type Contracts

## `NoInfer` now comes from TypeScript

Query core removed its custom `NoInfer<T>` re-export in batch `5.101.4`. The supported
replacement is TypeScript's built-in `NoInfer<T>`, which requires TypeScript 5.4 or
newer.

```ts
// Remove:
import type { NoInfer } from '@tanstack/query-core'

// Use the global utility directly:
type LockedInput<T> = NoInfer<T>
```

This is both an import migration and a compiler-version constraint. Do not create a
new dependency on the removed query-core type when updating shared helpers.

## Query and mutation callback contexts

The callback contracts expanded in batch `5.66-5.90`:

- `QueryFunctionContext` exposes its `QueryClient` as `client`.
- A mutation function receives a context argument after its variables.
- Mutation lifecycle callbacks receive a context argument.
- `onSuccess` types its `onMutateResult` argument as defined rather than possibly
  absent.

```tsx
useMutation({
  mutationFn: (variables, context) => save(variables, context),
  onSuccess: (data, variables, onMutateResult, context) => {},
})
```

Wrapper APIs must forward the new context arguments and preserve the defined
`onMutateResult` type. Avoid restating callbacks with an older, shorter signature.

## `QueryFilters` accepts realistic key shapes

In batch `5.101.4`, `QueryFilters` typing was corrected to accept partial query keys,
preserve `readonly`, and support query-key unions whose tuples have different
lengths.

For example, a registered union may contain both a short collection key and a longer
detail key. Filtering with a valid prefix should not require erasing the union or
casting away `readonly`. If a helper still fails such inputs, inspect the helper's
generic constraints before blaming the core filter type.

## Persister inference stays narrow

Persister typing in batch `5.101.4` has two deliberate directions of inference:

- infer `TQueryFnData` from the persister;
- prevent the persister from widening `TQueryKey`.

This preserves narrowed registered query keys. It also keeps results from wrappers
that use `DataTag` branding assignable. Generic wrappers should propagate the
persister's data type without broadening a registered key to an unconstrained
`QueryKey`.

## React prefetch options reject `skipToken`

React prefetch-query option types reject `skipToken` as a query function (batch
`5.66-5.90`). `skipToken` is not a mechanism for omitting a prefetch. Put the
condition around the prefetch call and provide a valid query function whenever the
call is made.

## Streamed-query option migration

The experimental streamed-query contract changed in batch `5.66-5.90`:

| Old contract | Current contract |
| --- | --- |
| `queryFn` option | `streamFn` option |
| `maxChunks` option | Removed |
| Custom `reducer` without a seed | Custom `reducer` requires `initialValue` |

The helper also supports `refetchMode: 'replace'`.

```tsx
queryFn: experimental_streamedQuery({
  streamFn: async function* () {
    yield 'ready'
  },
  initialValue: [] as string[],
  reducer: (all, chunk) => [...all, chunk],
  refetchMode: 'replace',
})
```

Do not retain `maxChunks` in a wrapper's public options, and do not alias `queryFn`
back to the old meaning. Requiring `initialValue` makes a custom reducer's empty-stream
result defined.

## Runtime-check migration

The direct `isServer` export is deprecated as a consumer-facing runtime check. Batch
`5.101-environment-manager` introduces `environmentManager.isServer()` as the
effective query-core and React-adapter check. See
`runtime-and-observers.md` for global overrides and restoring default detection.
