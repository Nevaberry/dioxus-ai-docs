# Schema Features (6.2+)

## ULID Support (6.2)

Auto-generated ULID values for `String` fields:

```prisma
model User {
  id String @id @default(ulid())
}
```

ULIDs are lexicographically sortable, globally unique identifiers — an alternative to UUID or CUID.

## SQLite `Json` and `enum` Fields (6.2)

SQLite now supports `Json` and `enum` fields in the Prisma schema:

```prisma
datasource db {
  provider = "sqlite"
  url      = "file:./dev.db"
}

model User {
  id   Int    @id @default(autoincrement())
  role Role
  data Json
}

enum Role {
  Customer
  Admin
}
```

## Mapped Enums with `@map` (7.0)

Enum members can use `@map` to set database-level values. Use `@@map` on the enum itself to set the table name:

```prisma
enum PaymentProvider {
  MixplatSMS    @map("mixplat/sms")
  InternalToken @map("internal/token")
  Offline       @map("offline")
  @@map("payment_provider")
}
```

**Important**: In TypeScript, enum members use their Prisma-side names (NOT the `@map()` values). The 7.0.0 behavior that used mapped values was reverted in 7.3.0 back to v6 behavior:

```ts
// Use the Prisma-side name
PaymentProvider.MixplatSMS // === "MixplatSMS" (not "mixplat/sms")
```

## `compilerBuild` Option (7.3)

Choose between query compiler builds optimized for speed or bundle size:

```prisma
generator client {
  provider      = "prisma-client"
  output        = "../src/generated/prisma"
  compilerBuild = "fast"  // "fast" (default) | "small"
}
```
