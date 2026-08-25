# Core data access and QoS

Use this reference when implementing reader loops, interpreting statuses,
matching endpoints, or choosing durability, presentation, and partition
policies. These rules follow the DDS core behavior identified by
`dds-1.4-core`.

## Read and take from the reader cache

`read` returns matching samples while leaving them in the reader cache and
marks returned samples as read. `take` returns matching samples and removes
them from the cache.

Selection is the intersection of three independent state dimensions:

| Dimension | States |
| --- | --- |
| Sample | `READ`, `NOT_READ` |
| View | `NEW`, `NOT_NEW` |
| Instance | `ALIVE`, `NOT_ALIVE_DISPOSED`, `NOT_ALIVE_NO_WRITERS` |

Always branch on `SampleInfo.valid_data` before using the value. DDS may deliver
an invalid-data sample that reports an instance lifecycle transition without a
new application value. Process its metadata, but do not treat its value payload
as fresh data.

## Interpret status conditions

DDS status structures combine cumulative counts with changes since the
relevant status was last accessed. Status conditions are therefore stateful
indicators, not event queues.

Accessing a status may reset its change counter or status flag. Taking data or
executing a listener may also clear the relevant condition. Code must not
expect one retained notification for every occurrence, and multiple
occurrences may be represented by one observed status change.

Listener callbacks normally execute on threads controlled by the DDS
implementation. Avoid blocking, lengthy work, and application locks in a
listener. Capture the minimum state and hand the work to an application-owned
queue or executor to avoid delaying middleware progress or creating lock
cycles.

## Apply requested/offered QoS

QoS compatibility is directional: a writer's offered policy must satisfy the
reader's requested policy for every compatibility-checked policy.

- A reader requesting reliable delivery requires a reliable writer.
- The writer's durability level must be at least the reader's requested level.
- The writer's offered deadline period must be no greater than the reader's
  requested period.

An incompatible writer and reader can still discover each other. Use
requested-incompatible-QoS and offered-incompatible-QoS status to distinguish
endpoint discovery from QoS matching when discovered participants or endpoints
produce no data.

## Use topic QoS as a creation template

Copying topic QoS while creating a reader or writer initializes that endpoint;
it does not establish a continuous link. A later topic-QoS update does not
propagate to already-created endpoints.

QoS mutability is defined per policy. If an immutable policy must change after
the entity is enabled, delete and recreate the affected entity with the new
QoS.

## Bound durability and history with actual resources

`TRANSIENT_LOCAL` retains historical samples in the originating writer. Once
that writer is gone, its retained history is no longer available.

`TRANSIENT` and `PERSISTENT` depend on durability-service support, which is not
uniform across implementations. Confirm product support and deployment
requirements before relying on either level.

`KEEP_ALL` does not mean unlimited storage. Resource-limit policies still cap
retained samples and instances. Under reliable delivery, reaching those bounds
can block a writer or leave it unable to serve a slow reader. Configure history
and resource limits together and test the chosen behavior under backpressure.

## Scope coherent presentation correctly

`PRESENTATION` defines an access scope of `INSTANCE`, `TOPIC`, or `GROUP` and
separately requests coherent access or ordered access.

Coherent-change brackets can cause a compatible subscriber to observe a set of
writes together. They do not provide database isolation and cannot roll back
writes. `GROUP` scope may also depend on implementation support, so verify the
deployed product before making it an architectural requirement.

## Match partitions portably

Partition QoS belongs to publishers and subscribers rather than to topics. The
default partition sequence contains the single empty string.

A publisher and subscriber match when their partition string sequences
intersect according to DDS expression rules. Two wildcard expressions are not
generally treated as regular expressions whose languages are intersected. For
portable behavior, arrange for at least one side of a match to use a literal
partition string.

Partition QoS is mutable after enablement. Changing it may establish new
endpoint matches or remove existing ones. Partition names remain visible in
discovery metadata, so use security facilities—not partitions—to enforce an
authorization boundary.
