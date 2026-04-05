# Realtime

## Realtime Authorization (Private Channels)

Broadcast and Presence access is now controlled via RLS policies on the `realtime.messages` table. Channels must be created with `private: true`. Uses `realtime.topic()` helper in policies. Authorization is validated at connection/join time.

```sql
-- Allow authenticated users to receive broadcasts on specific topics
CREATE POLICY "users can read room broadcasts" ON "realtime"."messages" FOR
SELECT
  TO authenticated USING (
    EXISTS (
      SELECT
        1
      FROM
        public.rooms_users
      WHERE
        room_topic = (
          SELECT
            realtime.topic ()
        )
        AND user_id = auth.uid ()
    )
  );

-- Control who can send broadcasts (INSERT policy)
CREATE POLICY "users can broadcast to their rooms" ON "realtime"."messages" FOR INSERT TO authenticated
WITH
  CHECK (
    EXISTS (
      SELECT
        1
      FROM
        public.rooms_users
      WHERE
        room_topic = (
          SELECT
            realtime.topic ()
        )
        AND user_id = auth.uid ()
    )
  );
```

The `extension` column on `realtime.messages` distinguishes message types: `'broadcast'` for Broadcast, `'presence'` for Presence. Client-side setup:

```javascript
await supabase.realtime.setAuth(); // Required — sends current JWT to Realtime
const channel = supabase
  .channel('room:123', { config: { private: true } })
  .on('broadcast', { event: 'message' }, (payload) => console.log(payload))
  .subscribe();
```

Disable "Allow public access" in Realtime Settings to enforce private channels project-wide.

## Broadcast from Database

Trigger Realtime broadcasts directly from Postgres using two built-in functions. This is now the **recommended approach** for subscribing to database changes (over Postgres Changes), as it scales better and supports authorization.

```sql
-- Simple message broadcast (flexible format)
SELECT realtime.send(
  '{"score": 42}'::jsonb,  -- payload
  'score_update',           -- event name
  'game:123',               -- topic
  FALSE                     -- private (TRUE requires authorization)
);

-- Broadcast record changes (structured format for triggers)
CREATE OR REPLACE FUNCTION public.orders_broadcast()
RETURNS trigger
SECURITY DEFINER SET search_path = ''
AS $$
BEGIN
  PERFORM realtime.broadcast_changes(
    'orders:' || coalesce(NEW.id, OLD.id)::text,  -- topic
    TG_OP,              -- event (INSERT/UPDATE/DELETE)
    TG_OP,              -- operation
    TG_TABLE_NAME,      -- table
    TG_TABLE_SCHEMA,    -- schema
    NEW,                -- new record
    OLD                 -- old record
  );
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER orders_realtime
AFTER INSERT OR UPDATE OR DELETE ON public.orders
FOR EACH ROW EXECUTE FUNCTION orders_broadcast();
```

Messages are stored in the partitioned `realtime.messages` table (auto-cleaned after 3 days). Client listens via broadcast events on private channels:

```javascript
await supabase.realtime.setAuth();
const changes = supabase
  .channel('orders:456', { config: { private: true } })
  .on('broadcast', { event: 'INSERT' }, (payload) => console.log(payload))
  .on('broadcast', { event: 'UPDATE' }, (payload) => console.log(payload))
  .on('broadcast', { event: 'DELETE' }, (payload) => console.log(payload))
  .subscribe();
```

## Broadcast Replay

Private channels can replay previously sent database broadcasts on join. Only messages sent via Broadcast from Database are replayable.

```javascript
const channel = supabase.channel('chat:main', {
  config: {
    private: true,
    broadcast: {
      replay: {
        since: Date.now() - 60_000, // epoch ms — last 60 seconds
        limit: 25, // max messages (up to 25)
      },
    },
  },
});

channel
  .on('broadcast', { event: 'message' }, (payload) => {
    if (payload?.meta?.replayed) {
      console.log('Historical:', payload);
    } else {
      console.log('Live:', payload);
    }
  })
  .subscribe();
```

Requires supabase-js >= 2.74.0. Replayed messages include `meta.replayed: true` and `meta.id`.

## Realtime Limits

| | Free | Pro | Pro (no cap) | Team | Enterprise |
|---|---|---|---|---|---|
| Concurrent connections | 200 | 500 | 10,000 | 10,000 | 10,000+ |
| Messages/sec | 100 | 500 | 2,500 | 2,500 | 2,500+ |
| Channel joins/sec | 100 | 500 | 2,500 | 2,500 | 2,500+ |
| Channels/connection | 100 | 100 | 100 | 100 | 100+ |
| Broadcast payload | 256 KB | 3 MB | 3 MB | 3 MB | 3+ MB |
| Postgres change payload | 1 MB | 1 MB | 1 MB | 1 MB | 1+ MB |

When Postgres change payload limit is exceeded, `new`/`old` payloads only include fields <= 64 bytes.
