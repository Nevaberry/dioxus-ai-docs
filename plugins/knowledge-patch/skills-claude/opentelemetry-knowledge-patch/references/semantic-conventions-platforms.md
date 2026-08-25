# Semantic Conventions: Platforms, Runtimes, and Entities

## Process, service, and deployment

### Process identity and descriptor metrics (`semantic-conventions`)

Executable details form a separate `process.executable` entity. `process.pid`
and `process.creation.time` are Required identity attributes; descriptive
process attributes are Optional. Use `process.unix.file_descriptor.count` and
`process.windows.handle.count` instead of
`process.open_file_descriptor.count`. Process attributes, metrics, and the
entity are Release Candidate.

### Service and deployment identity (`semantic-conventions`)

Model namespace, service, and instance as separate entities. Replace
`peer.service` with `service.peer.name` and, where applicable,
`service.peer.namespace`. `service.instance.id` is stable.
`deployment.environment.name` is stable and defines `Production`, `Staging`,
`Test`, and `Development`. Alpha `service.criticality` accepts `critical`,
`high`, `medium`, and `low`.

### Process and system limits (`2026-08-stable`)

The Release Candidate process namespace adds `process.disk.operations`,
`process.memory.utilization`, and `process.signals_pending`. System conventions
add `system.process.limit`.

## System and runtime metrics

### System and Linux names (`semantic-conventions`)

Use `system.network.packet.dropped`, `system.network.packet.count`,
`system.network.connection.count`, `system.memory.linux.shared`, and the
general `*.memory.linux` ordering. CPU metrics remain under `system.cpu.*`.
Other migrations include `process.state`, `system.paging.fault.type`, and
`process.context_switch.type`; `cpu.logical_number` is Opt-In.

### V8 heap metrics (`semantic-conventions`)

Heap-space metrics use `v8js.memory.heap.space.*`. The old
`v8js.memory.heap.limit` meaning moved to `v8js.memory.heap.space.size`;
`v8js.memory.heap.limit` is now an UpDownCounter for the absolute V8 heap
limit.

### Language and runtime coverage (`semantic-conventions`)

.NET has network spans for DNS, TLS, and sockets plus optional HTTP connection
relationships. ASP.NET Core has Identity, authentication/authorization, and
memory-pool metrics. Go has Opt-In CPU time, GC pause/cycle metrics, and
detailed-state attributes. The JVM adds `jvm.file_descriptor.limit`, and
`kotlin` is a valid `telemetry.sdk.language` value.

## Kubernetes and containers

### Metric-name and instrument migration (`semantic-conventions`)

Node allocatable metrics use names such as `k8s.node.cpu.allocatable`,
`k8s.node.memory.allocatable`, and `k8s.node.pod.allocatable`. Plural
UpDownCounter names become singular, for example `k8s.job.pod.active`.
Container limit/request metrics use UpDownCounters; CPU limit/request
utilization metrics are excluded from code generation.

### Storage and in-place resize telemetry (`semantic-conventions`)

`k8s.persistentvolume` and `k8s.persistentvolumeclaim` entities have phase and
storage capacity/request metrics. `k8s.container.ephemeral_storage.usage`
distinguishes `rootfs` from `logs` with
`k8s.container.ephemeral_storage.fs_type`. Container CPU and memory
limit/request telemetry distinguishes desired and current values for in-place
resize.

### Service and workload telemetry (`semantic-conventions`)

The `k8s.service` entity has endpoint and load-balancer-ingress counts.
Additional telemetry covers node system containers, filesystems, pod volumes,
pod/container memory and status, restarts, readiness, node conditions, quotas,
and HPA targets. Pod entities add `k8s.pod.ip`, `k8s.pod.hostname`, and
`k8s.pod.start_time`.

### Convention maturity (`semantic-conventions`)

Selected Kubernetes and container-registry resource attributes are stable.
`k8s.pod.cpu.time`, `k8s.node.cpu.time`, and `container.cpu.time` are Release
Candidate.

### Paging faults, memory, CPU, and filesystems (`2026-08-stable`)

Use `k8s.pod.paging.faults`, `k8s.node.paging.faults`, and
`container.paging.faults`, without the former `.memory` segment. The related
container, pod, and node `memory.usage` instruments are UpDownCounters;
selected container and Kubernetes memory metrics are Release Candidate.
Measure CPU usage in cores as
`(cpuTimeEnd - cpuTimeStart) / elapsedSeconds`. Node filesystem telemetry adds
`k8s.node.filesystem.inode.count` and `k8s.node.filesystem.inode.free`.

## Application and cloud

### Application telemetry (`semantic-conventions`)

Application conventions add `app.build_id`, `app.screen.name`, a jank event,
and a minimal end-user application crash definition.

### Cloud platform attributes (`semantic-conventions`)

Azure names use `azure.service.request.id`,
`azure.resource_provider.namespace`, dotted `cloud.platform` values, and
`azure.resource_group.name`; on Azure, `cloud.account.id` is the subscription
ID. Treat GCE labels as resource attributes. GCE Instance Group Manager and
`gcp.apphub_destination.*` attributes are available. Cloud enumerations cover
GCP Agent Engine, Hetzner, Linode/Akamai, and Vultr.

### Scaleway and host identity (`2026-08-stable`)

Scaleway Cloud is represented in `cloud.provider`, with
`cloud.platform=scaleway_cloud_compute`. Invoke commands used to collect
`host.id` by full path.

## SDK, event, and exporter metadata

### SDK self-observability metrics (`semantic-conventions`)

`otel.sdk.span.started` replaces `otel.sdk.span.ended` and can distinguish the
parent-span origin. On `otel.sdk.span.live`, `otel.span.sampling_result`
permits only `RECORD_ONLY` and `RECORD_AND_SAMPLE`. Exporter retry metrics
count one operation through its final attempt and backoff. Processor metrics
reserve `already_shutdown` as an `error.type`.

### Event and exporter metadata (`semantic-conventions`)

Non-OTLP paths can carry `otel.event.name` and `otel.scope.schema_url`.
Zipkin and Prometheus exporters have specified `component.type` values, and
the `otel.scope` entity has been removed. Events may use complex attributes
instead of body fields; the event body may contain a display message.

## Convention maturity and additional platforms

### Maturity promotions (`semantic-conventions`)

CI/CD spans, metrics, logs, attributes, entities, and VCS conventions are
Release Candidate. So are `cpu.mode`, `disk.io.direction`,
`network.io.direction`, and `system.paging.fault.type`.
`network.io.direction` describes traffic at the observed interface boundary,
not logical flow direction. Feature-flag conventions are Release Candidate.

### Network interface maturity (`2026-08-stable`)

`network.interface.name` is Release Candidate.

### Mainframe, filesystem, and NFS coverage (`semantic-conventions`)

Conventions cover mainframes and z/OS; use `os.type=zos` instead of `z_os`.
NFS has `nfs.*` metrics with `rpc.onc.*` and `rpc.nfs.*` attributes. OpenShift
has cluster-quota metrics, and filesystem lock counts are supported.

### Profile conversion metadata (`semantic-conventions`)

Pprof attributes including `pprof.profile.comment`,
`pprof.scope.default_sample_type`, and `pprof.scope.sample_type_order` support
lossless profile conversion. LuaJIT is a recognized frame type.
