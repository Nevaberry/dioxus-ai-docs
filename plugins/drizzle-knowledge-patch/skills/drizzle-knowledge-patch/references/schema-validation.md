# Schema Validation

## Validator packages consolidated into `drizzle-orm`

*Since 1.0.0-beta.15 (2025-02-05)*

Separate validator packages (`drizzle-zod`, `drizzle-valibot`, `drizzle-typebox`, `drizzle-arktype`) are now available as subpath imports from `drizzle-orm`. Old packages still work but new imports are recommended.

```ts
// Old (still works)
import { createInsertSchema } from 'drizzle-zod';

// New
import { createInsertSchema } from 'drizzle-orm/zod';
import { createInsertSchema } from 'drizzle-orm/valibot';
import { createInsertSchema } from 'drizzle-orm/typebox';       // using 'typebox'
import { createInsertSchema } from 'drizzle-orm/typebox-legacy'; // using '@sinclair/typebox'
import { createInsertSchema } from 'drizzle-orm/arktype';
import { createInsertSchema } from 'drizzle-orm/effect-schema';  // NEW: Effect integration
```

### Supported libraries

| Library | Import path |
|---|---|
| Zod | `drizzle-orm/zod` |
| Valibot | `drizzle-orm/valibot` |
| TypeBox | `drizzle-orm/typebox` |
| TypeBox (legacy `@sinclair/typebox`) | `drizzle-orm/typebox-legacy` |
| ArkType | `drizzle-orm/arktype` |
| Effect Schema | `drizzle-orm/effect-schema` |
