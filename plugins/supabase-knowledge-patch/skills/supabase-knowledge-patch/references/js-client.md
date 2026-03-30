# JS Client (supabase-js v2.74–v2.101)

## Node.js 20+ Required (v2.79.0+)

Starting with v2.79.0, all Supabase JS libraries require Node.js 20+. The `@supabase/node-fetch` polyfill was removed — native fetch is now required. If you must stay on Node.js 18, pin to `@supabase/supabase-js@2.78.0`.

## New PostgREST Filters

**`notin(column, values)`** — inverse of `in()`, excludes rows matching any value:

```typescript
const { data } = await supabase
  .from('countries')
  .select()
  .notin('id', [1, 2, 3]);
```

**`isdistinct(column, value)`** — SQL `IS DISTINCT FROM`, treats NULL as a comparable value (unlike `neq` which returns NULL for NULL comparisons):

```typescript
const { data } = await supabase
  .from('users')
  .select()
  .isdistinct('deleted_at', null); // returns rows where deleted_at IS DISTINCT FROM NULL (i.e., not null)
```

## Auth Throw Mode (v2.79.0+)

Auth methods can now throw errors instead of returning `{ data, error }`. Configure at client creation:

```typescript
const supabase = createClient(url, key, {
  auth: { throwOnError: true },
});

// Now throws instead of returning error
try {
  const { data } = await supabase.auth.signInWithPassword({ email, password });
} catch (err) {
  console.error(err.message);
}
```

## Auth `skipAutoInitialize` (v2.97.0+)

Prevents the auth client from automatically restoring the session on creation. Useful for SSR or service-side usage where you don't want the constructor to trigger async session recovery:

```typescript
const supabase = createClient(url, key, {
  auth: { skipAutoInitialize: true },
});

// Manually initialize when ready
await supabase.auth.initialize();
```

## Auth `detectSessionInUrl` Custom Predicate (v2.88.0+)

`detectSessionInUrl` now accepts a function (not just boolean) for custom session detection logic:

```typescript
const supabase = createClient(url, key, {
  auth: {
    detectSessionInUrl: (url) =>
      url.searchParams.has('code') && url.pathname === '/auth/callback',
  },
});
```

## Auth `currentPassword` for User Updates (v2.98.0+)

`updateUser()` now accepts `currentPassword` to require password verification before changes:

```typescript
await supabase.auth.updateUser({
  password: 'new-password',
  data: { currentPassword: 'old-password' },
})
```

## Functions Configurable Timeout (v2.81.0+)

Edge Function invocations now support a timeout option. Abort and timeout errors are normalized as `FunctionsFetchError`:

```typescript
const { data, error } = await supabase.functions.invoke('slow-function', {
  body: { input: 'data' },
  signal: AbortSignal.timeout(30000), // 30 second timeout
})
```

## CORS Headers Export (v2.95.0+)

Canonical CORS headers for Edge Functions available as a named export:

```typescript
import { corsHeaders } from '@supabase/supabase-js/cors'

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  return new Response(
    JSON.stringify({ data: 'Hello' }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
})
```

Includes all headers sent by Supabase client libraries and allows all standard HTTP methods.

## `DatabaseWithoutInternals` Utility Type (v2.89.0+)

New exported type that strips Supabase internal schemas from your Database type, useful when passing database types to utilities that shouldn't see internal tables:

```typescript
import { DatabaseWithoutInternals } from '@supabase/supabase-js'
import { Database } from './database.types'

type PublicDB = DatabaseWithoutInternals<Database>
```

## PostgREST URL Length Validation (v2.94.0+)

Queries that would produce URLs exceeding the server's max length are now detected. The client automatically validates URL length and provides timeout protection for long-running filter chains.
