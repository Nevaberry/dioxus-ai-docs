# Core DDS Semantics

Source batch: `dds-1.4-core`.

## Reader-cache state and lifecycle

Choose the data-access operation according to ownership of the cached sample:

- `read` returns matching samples, leaves them in the reader cache, and marks
  them as read;
- `take` returns matching samples and removes them from the cache.

State-based selection combines three independent dimensions:

| Dimension | Values |
| --- | --- |
| Sample state | `READ`, `NOT_READ` |
| View state | `NEW`, `NOT_NEW` |
| Instance state | `ALIVE`, `NOT_ALIVE_DISPOSED`, `NOT_ALIVE_NO_WRITERS` |

These masks can be combined; do not collapse sample, view, and instance state
into a single lifecycle flag.

Always inspect `SampleInfo.valid_data` before reading a value. Disposal and
no-writers transitions can deliver metadata about an instance without a new
valid value. Code that ignores `valid_data` can mistake a lifecycle
notification for an ordinary data sample.

## Status handling and listeners

DDS status structures are counters and state indicators, not event queues.
They commonly contain:

- a cumulative count; and
- a change since the relevant status was last accessed.

Accessing a status can reset its change count or status flag. Taking data or
running a listener can likewise reset the corresponding condition. Therefore,
do not infer that each occurrence remains queued until application code handles
one notification.

Listener callbacks normally run on threads controlled by the implementation.
Keep callbacks bounded:

1. capture only the state needed to identify the work;
2. hand the work to application-owned execution;
3. return without blocking;
4. avoid acquiring application locks that could participate in lock inversion.

When counts appear to skip or a status condition stops triggering, identify
every access path—including listeners and data-taking paths—that may have
cleared the change or flag.

## Requested-versus-offered QoS

Reader and writer QoS is matched directionally. A writer offer satisfies a
reader request only if every compatibility-checked policy is compatible.

Key directions include:

| Policy | Required relationship |
| --- | --- |
| Reliability | A reliable reader requires a reliable writer |
| Durability | Writer durability must be at least the requested durability |
| Deadline | Offered deadline period must be no greater than the requested period |

Endpoint discovery and QoS matching are separate. An incompatible reader and
writer can discover each other while reporting requested- or
offered-incompatible-QoS status. When data is silent, check discovery,
addressing, identity, and QoS matching separately.

## Topic QoS and endpoint mutation

Topic QoS can be copied as a template when a data reader or data writer is
created. That copy does not form a live link: changing the topic QoS later does
not continuously update existing endpoints.

QoS mutability is policy-specific. Before changing an enabled entity:

1. identify the exact endpoint policy;
2. check whether that policy is mutable after enablement;
3. apply the change only when supported;
4. recreate the entity when an immutable policy must change.

Avoid troubleshooting under the assumption that a successful topic-QoS update
retrofitted all readers and writers created from it.

## Durability, history, and resource limits

`TRANSIENT_LOCAL` retains historical data in the originating writer. Once that
writer is gone, its retained history is no longer available from that source.
It is not a substitute for an external durability service.

`TRANSIENT` and `PERSISTENT` depend on durability-service support. That support
and its operational requirements are not uniform across implementations, so
verify the deployed product rather than assuming those modes create a portable
persistent store.

`KEEP_ALL` does not mean unbounded storage. Resource limits still cap retained
samples and instances. With reliable delivery, exhausted limits or a slow
reader can cause a writer to block or prevent it from serving all expected
history. Diagnose history and reliability together with configured limits.

## Presentation and coherent changes

The `PRESENTATION` policy controls multiple independent aspects:

- access scope: `INSTANCE`, `TOPIC`, or `GROUP`;
- whether coherent access is requested;
- whether ordered access is requested.

Coherent-change brackets can make a compatible set of writes visible together
to a compatible subscriber. They do not create database transactions: there is
no database-style isolation and no rollback.

Treat the chosen scope as a real compatibility and support requirement.
`GROUP` scope can depend on implementation support, and publisher/subscriber
configuration must agree with the intended access pattern.

## Partition matching

`PARTITION` belongs to publishers and subscribers rather than directly to
individual writers and readers. The default partition sequence contains one
empty string.

A publication and subscription match when their partition string sequences
intersect under DDS expression rules. Do not treat both sides as regular
expressions and assume their theoretical languages will be intersected. For
portable behavior, make at least one side of an intended match a literal.

Partitions are mutable after enablement. Changing a publisher or subscriber
partition can dynamically add or remove endpoint matches.

Partitions are also announced through discovery. They are a matching and
organization mechanism, not a confidentiality or authorization boundary.
