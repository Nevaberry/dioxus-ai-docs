# Relational Query Builder v2

The relational query builder was completely redesigned in v1. The old `relations()` helper is replaced by `defineRelations()`, and `drizzle({ schema })` becomes `drizzle({ relations })`.

## Defining Relations with `defineRelations`

```ts
import { defineRelations } from 'drizzle-orm';
import * as schema from './schema';

export const relations = defineRelations(schema, (r) => ({
  users: {
    posts: r.many.posts(),
    profile: r.one.profiles({
      from: r.users.id,
      to: r.profiles.userId,
    }),
  },
  posts: {
    author: r.one.users({
      from: r.posts.authorId,
      to: r.users.id,
    }),
    comments: r.many.comments(),
  },
}));
```

### Many-to-Many Through a Junction Table

```ts
groups: r.many.groups({
  from: r.users.id.through(r.usersToGroups.userId),
  to: r.groups.id.through(r.usersToGroups.groupId),
}),
```

## Initializing with Relations

```ts
import { relations } from './relations';
import { drizzle } from 'drizzle-orm/node-postgres';

const db = drizzle({ relations });
```

## Object-Based `where` Syntax

Replaces the old callback-with-operators pattern. Filters are plain objects.

### Simple Equality

```ts
db.query.users.findMany({ where: { id: 1 } });
```

### Operators as Object Keys

```ts
db.query.users.findMany({ where: { age: { gt: 18 } } });
```

### OR, AND, NOT, RAW

```ts
db.query.users.findMany({
  where: {
    OR: [{ age: { gt: 18 } }, { name: { like: 'A%' } }],
    NOT: { id: { in: [1, 2, 3] } },
  },
});
```

### Filter by Relations

Find users who have posts matching a condition:

```ts
db.query.users.findMany({
  where: { posts: { content: { like: 'M%' } } },
});
```

### Available Column Operators

`eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `notIn`, `like`, `ilike`, `notLike`, `notIlike`, `isNull`, `isNotNull`, `arrayOverlaps`, `arrayContained`, `arrayContains`.

## Object-Based `orderBy`

```ts
db.query.posts.findMany({
  orderBy: { id: 'asc' },
  with: {
    comments: { orderBy: { id: 'desc' } },
  },
});
```

## `offset` in Nested `with` Queries

New in v1 — nested relations now support `offset` alongside `limit`:

```ts
db.query.posts.findMany({
  with: {
    comments: { limit: 3, offset: 5 },
  },
});
```
