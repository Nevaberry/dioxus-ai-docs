# JS Client

## Monorepo Restructure (supabase-js v2.74.0+)

All Supabase JS libraries have been consolidated into a single monorepo at `github.com/supabase/supabase-js`. The old separate repos (`auth-js`, `postgrest-js`, `realtime-js`, `storage-js`, `functions-js`) are archived.

New structure:

```
github.com/supabase/supabase-js/
├── packages/core/
│   ├── supabase-js/       # Main SDK
│   ├── auth-js/
│   ├── postgrest-js/
│   ├── realtime-js/
│   ├── storage-js/
│   └── functions-js/
├── nx.json                # Nx workspace config
└── package.json           # Root workspace
```

**For package users**: Nothing changed — same `npm install @supabase/supabase-js`, same APIs, same imports. All packages now share a single version number for guaranteed compatibility (no more version matrix issues).

**For contributors**: Use Nx commands instead of per-repo npm scripts:

```bash
npx nx build auth-js          # Build a specific library
npx nx test postgrest-js      # Test a specific library
npx nx affected --target=test # Test only what changed
npx nx graph                  # Visualize dependency graph
```

## Node.js 18 Support Dropped (v2.79.0+)

All Supabase JS libraries require **Node.js 20+** as of v2.79.0. The `@supabase/node-fetch` polyfill was removed — native `fetch()` is now required. If you get `fetch is not defined`, upgrade Node. Last version supporting Node 18: `@supabase/supabase-js@2.78.0`.

## Enhanced JSON Type Inference (v2.48.0+)

Define custom types for JSON/JSONB columns and get type-safe inference when using `->` and `->>` operators in `.select()` strings.

```typescript
import { MergeDeep } from 'type-fest';
import { Database as DatabaseGenerated } from './database.types';

type Metadata = {
  foo: string;
  bar: { baz: number };
  status: 'active' | 'inactive';
};

type Database = MergeDeep<
  DatabaseGenerated,
  {
    public: {
      Tables: {
        items: { Row: { data: Metadata | null } };
      };
    };
  }
>;

// Type-safe JSON path queries
const { data } = await supabase
  .from('items')
  .select('data->bar->baz, data->status, data->>foo');
// Inferred: { baz: number; status: 'active' | 'inactive'; foo: string }[]
// -> returns JSON type, ->> returns string
```

## `overrideTypes<>()` for Response Type Control

Override the inferred return type of any query:

```typescript
// Partial override (merges with inferred type)
const { data } = await supabase.from('countries').select()
  .overrideTypes<Array<{ id: string }>>()

// Full replacement (discards inferred type)
const { data } = await supabase.from('countries').select()
  .overrideTypes<Array<{ id: string }>, { merge: false }>()

// Works with .single() / .maybeSingle()
const { data } = await supabase.from('countries').select().single()
  .overrideTypes<{ id: string }>()
```

## New PostgREST Filter Methods (v2.84.0+)

New filter operators added to the query builder:

```typescript
// IS DISTINCT FROM — null-safe inequality (v2.84.0)
const { data } = await supabase.from('items')
  .select().isDistinct('status', 'active')

// Regex pattern matching (v2.84.0)
const { data } = await supabase.from('items')
  .select().match('name', '~', '^A.*z$')       // POSIX regex
  .match('name', '~*', '^a.*z$')               // case-insensitive regex

// NOT IN shorthand (v2.88.0)
const { data } = await supabase.from('items')
  .select().notin('status', ['archived', 'deleted'])
```

## Throw-on-Error Mode for Auth (v2.79.0)

Auth methods can now throw errors instead of returning `{ data, error }`:

```typescript
const supabase = createClient(url, key, {
  auth: { throwOnError: true }
})

try {
  // Throws on failure instead of returning { error }
  const { data } = await supabase.auth.signInWithPassword({
    email: 'user@example.com',
    password: 'password',
  })
} catch (err) {
  console.error(err) // AuthError instance
}
```

## `DatabaseWithoutInternals` Utility Type (v2.89.0)

New exported type that strips Supabase-internal schemas from the Database type, useful when building libraries or utilities that should only operate on user schemas:

```typescript
import { DatabaseWithoutInternals } from '@supabase/supabase-js'
import { Database } from './database.types'

type UserDB = DatabaseWithoutInternals<Database>
// Excludes auth, storage, realtime, etc. schemas
```

## Embedded/Computed Function Type Inference (v2.75.0)

PostgREST computed fields (SQL functions that take a table row as input) are now type-inferred in `.select()`:

```typescript
// Given: CREATE FUNCTION full_name(profiles) RETURNS text ...
const { data } = await supabase
  .from('profiles')
  .select('id, full_name')  // full_name is inferred as string
```

## Functions Client: Configurable Timeout (v2.81.0)

Edge Function invocations now support a configurable timeout. Abort and timeout errors are normalized to `FunctionsFetchError`:

```typescript
const { data, error } = await supabase.functions.invoke('my-function', {
  body: { input: 'data' },
  signal: AbortSignal.timeout(10_000), // 10 second timeout
})
// error instanceof FunctionsFetchError for both abort and timeout
```

## PostgREST URL Length Validation (v2.94.0)

The PostgREST client now validates URL length and provides timeout protection. Queries that would generate URLs exceeding browser/server limits are caught early with a descriptive error, rather than failing silently or with cryptic HTTP errors.

## Canonical CORS Headers Export (v2.95.3)

Convenience export for Edge Functions CORS setup:

```typescript
import { corsHeaders } from '@supabase/supabase-js'

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }
  // ... handler logic
  return new Response(JSON.stringify(data), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  })
})
```

## Auth: `skipAutoInitialize` Option (v2.97.0)

Prevent the auth client from automatically initializing (fetching session, setting up listeners) on construction:

```typescript
const supabase = createClient(url, key, {
  auth: { skipAutoInitialize: true }
})

// Manually initialize when ready
await supabase.auth.initialize()
```

Useful for SSR environments or when you need to set up auth state before the client starts managing sessions.

## Auth: Custom `detectSessionInUrl` Predicate (v2.88.0)

Replace the boolean `detectSessionInUrl` option with a custom predicate function for fine-grained control over when the auth client processes URL tokens:

```typescript
const supabase = createClient(url, key, {
  auth: {
    detectSessionInUrl: (url) => {
      // Only process auth callbacks on specific paths
      return url.pathname.startsWith('/auth/callback')
    },
  },
})
```
