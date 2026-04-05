# Query API Additions (6.2+)

## `updateManyAndReturn` (6.2)

Like `createManyAndReturn`, updates many records and returns the actual rows (not just a count). Supported on PostgreSQL, CockroachDB, and SQLite only.

```ts
const users = await prisma.user.updateManyAndReturn({
  where: { email: { contains: 'prisma.io' } },
  data: { role: 'ADMIN' },
})
```

## `limit` on `updateMany()` and `deleteMany()` (6.3)

Previously `limit` was only available on find queries. Now you can limit batch mutation operations:

```ts
await prisma.user.deleteMany({
  where: { inactive: true },
  limit: 100,
})

await prisma.user.updateMany({
  where: { role: 'GUEST' },
  data: { active: false },
  limit: 50,
})
```
