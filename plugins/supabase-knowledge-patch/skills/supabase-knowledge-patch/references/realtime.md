# Realtime

## Realtime Authorization (Private Channels)

Control Broadcast and Presence access with RLS policies on `realtime.messages`. Replaces the old public-by-default model.

Two steps: (1) create RLS policies on `realtime.messages`, (2) use `private: true` in client config.

```sql
-- Allow authenticated users to receive broadcasts for rooms they belong to
CREATE POLICY "members can receive broadcast" ON "realtime"."messages" FOR
SELECT
  TO authenticated USING (
    realtime.messages.extension = 'broadcast'
    AND EXISTS (
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

-- Allow members to send broadcasts
CREATE POLICY "members can send broadcast" ON "realtime"."messages" FOR INSERT TO authenticated
WITH
  CHECK (
    realtime.messages.extension = 'broadcast'
    AND EXISTS (
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

Key details:
- `realtime.topic()` — returns the channel topic being joined
- `realtime.messages.extension` — `'broadcast'` or `'presence'`, use in policies to scope by feature
- JWT claims accessible via `current_setting('request.jwt.claims')::json`
- Permissions checked at join time (not per-message)
- Disable "Allow public access" in Realtime Settings to enforce private channels

Client usage:

```js
await supabase.realtime.setAuth() // Required for authorization
const channel = supabase.channel('room:123', {
  config: { private: true },
})
```

## Broadcast from Database

Trigger broadcast messages server-side using `realtime.send()` and `realtime.broadcast_changes()`. Messages go through the WAL via the `realtime.messages` table (partitioned daily, 3-day retention).

```sql
-- Send arbitrary JSON to a topic
SELECT realtime.send(
  '{"msg": "hello"}'::jsonb,  -- payload
  'new-message',               -- event name
  'room:123',                  -- topic
  FALSE                        -- private (TRUE requires RLS)
);
```

For broadcasting row changes, use a trigger with `realtime.broadcast_changes()`:

```sql
CREATE OR REPLACE FUNCTION public.notify_changes()
RETURNS trigger
SECURITY DEFINER SET search_path = ''
AS $$
BEGIN
  PERFORM realtime.broadcast_changes(
    'topic:' || NEW.id::text,  -- topic
    TG_OP,                     -- event
    TG_OP,                     -- operation
    TG_TABLE_NAME,             -- table
    TG_TABLE_SCHEMA,           -- schema
    NEW,                       -- new record
    OLD                        -- old record
  );
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER broadcast_changes_trigger
AFTER INSERT OR UPDATE OR DELETE ON public.my_table
FOR EACH ROW EXECUTE FUNCTION public.notify_changes();
```

Client listens on broadcast events (not postgres_changes):

```js
await supabase.realtime.setAuth()
const channel = supabase
  .channel('topic:42', { config: { private: true } })
  .on('broadcast', { event: 'INSERT' }, (payload) => console.log(payload))
  .on('broadcast', { event: 'UPDATE' }, (payload) => console.log(payload))
  .subscribe()
```

Advantage over Postgres Changes: uses broadcast infrastructure (faster, no per-client replication slot overhead), and works with Realtime Authorization.

## Broadcast Replay (Alpha)

Replay historical broadcast messages on private channels. Only works with messages sent via Broadcast from Database.

```js
const channel = supabase.channel('room:main', {
  config: {
    private: true,
    broadcast: {
      replay: {
        since: 1697472000000, // Unix timestamp in milliseconds
        limit: 10,            // Max 25 messages
      },
    },
  },
})

channel.on('broadcast', { event: 'position' }, (payload) => {
  if (payload?.meta?.replayed) {
    console.log('Historical message:', payload)
  } else {
    console.log('Live message:', payload)
  }
}).subscribe()
```

Requires `supabase-js` v2.74.0+. Replayed messages include `meta.replayed: true` flag.
