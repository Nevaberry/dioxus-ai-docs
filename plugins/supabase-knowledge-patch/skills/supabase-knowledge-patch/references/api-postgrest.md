# API & PostgREST

## New API Key Model (Publishable & Secret Keys)

Supabase is replacing JWT-based `anon` and `service_role` keys with new non-JWT key types:

| Type | Format | Replaces |
|------|--------|----------|
| Publishable key | `sb_publishable_...` | `anon` JWT |
| Secret key | `sb_secret_...` | `service_role` JWT |

Both old and new keys work simultaneously during transition — zero-downtime migration. Key differences:

- **Not JWTs** — the API Gateway validates the `apikey` header and mints a short-lived JWT internally before forwarding to PostgREST.
- **Secret keys are browser-blocked** — requests with a browser `User-Agent` always return 401.
- **Independent rotation** — rotate/delete individual secret keys without affecting other keys or users. No JWT secret rotation needed.
- **Edge Functions limitation** — Edge Functions only support JWT verification via legacy `anon`/`service_role` keys. With publishable/secret keys, use `--no-verify-jwt` and implement your own auth logic inside the function (e.g., `supabase.auth.getClaims(token)`).

```typescript
// Client-side: use publishable key (replaces anon key)
const supabase = createClient(SUPABASE_URL, 'sb_publishable_...')

// Server-side: use secret key (replaces service_role key)
const supabase = createClient(SUPABASE_URL, 'sb_secret_...', {
  auth: { persistSession: false },
})
```

Publishable/secret keys are platform-only (not available in CLI or self-hosting). Self-hosted projects still use `anon`/`service_role` JWT keys.

## `overrideTypes<>()` for Query Results

New method on supabase-js (v2.48.0+) to override TypeScript types of query results:

```typescript
// Partial override (merges with inferred types)
const { data } = await supabase
  .from('countries')
  .select()
  .overrideTypes<Array<{ id: string }>>();

// Full replacement (ignores inferred types)
const { data } = await supabase
  .from('countries')
  .select()
  .overrideTypes<Array<{ id: string }>, { merge: false }>();

// Works with .single() and .maybeSingle()
const { data } = await supabase
  .from('countries')
  .select()
  .single()
  .overrideTypes<{ id: string }>();
```

## Enhanced JSON Field Type Inference

Starting from supabase-js v2.48.0, custom types for JSON fields get type inference with `->` and `->>` operators in select strings:

```typescript
// Define custom JSON type via MergeDeep on generated types
type CustomJsonType = { foo: string; bar: { baz: number } };

// Query with JSON selectors — types auto-inferred
const { data } = await supabase
  .from('your_table')
  .select('data->bar->baz, data->foo');
// data type: Array<{ baz: number; foo: string }>
```

`->` returns the JSON type, `->>` returns `string`. Works with nested paths.

## Python Type Generation

CLI now supports Python type generation (v2.66.0+) producing Pydantic BaseModel classes:

```bash
npx supabase gen types --lang=python --project-id "$PROJECT_REF" --schema public >database_types.py
# or for local dev:
npx supabase gen types --lang=python --local >database_types.py
```

Generates `PublicTableName` (select), `PublicTableNameInsert`, and `PublicTableNameUpdate` classes:

```python
from .database_types import PublicMovies, PublicMoviesInsert
from supabase import create_client

client = create_client(url, key)
movies = client.table("movies")

selected = [PublicMovies(m) for m in movies.select("*").execute().data]
inserted = [
    PublicMovies(m)
    for m in movies.insert(PublicMoviesInsert(name="foo", data="bar")).execute().data
]
```
