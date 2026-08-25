# Semantic Conventions: Platforms, Runtimes, and Entities

## Process, service, and deployment identity

### Process

- Executable details form a separate `process.executable` entity.
- `process.pid` and `process.creation.time` are Required identity attributes;
  descriptive process attributes are Optional.
- `process.unix.file_descriptor.count` and
  `process.windows.handle.count` replace
  `process.open_file_descriptor.count`.
- Process attributes, metrics, and the entity are Release Candidate.
- The Release Candidate process namespace adds `process.disk.operations`,
  `process.memory.utilization`, and `process.signals_pending`.

### Service and deployment

- Service modeling separates namespace, service, and instance entities.
- `service.peer.name` and `service.peer.namespace` replace `peer.service`.
- `service.instance.id` is stable.
- `deployment.environment.name` is stable; known values are `Production`,
  `Staging`, `Test`, and `Development`.
- Alpha `service.criticality` accepts `critical`, `high`, `medium`, or `low`.

## System and runtime metrics

### System and Linux names

Use current names and ordering:

- `system.network.packet.dropped`
- `system.network.packet.count`
- `system.network.connection.count`
- `system.memory.linux.shared`, following the general `*.memory.linux`
  ordering
- `process.state`
- `system.paging.fault.type`
- `process.context_switch.type`

CPU metrics remain under `system.cpu.*`; `cpu.logical_number` is Opt-In.
System conventions also add `system.process.limit`.

### V8

Heap-space metrics use `v8js.memory.heap.space.*`. The old meaning of
`v8js.memory.heap.limit` moved to `v8js.memory.heap.space.size`;
`v8js.memory.heap.limit` is now an UpDownCounter for the absolute V8 heap
limit.

## Kubernetes and containers

### Metric-name and instrument migrations

- Node allocatable names include `k8s.node.cpu.allocatable`,
  `k8s.node.memory.allocatable`, and `k8s.node.pod.allocatable`.
- Plural UpDownCounter names are singular, for example
  `k8s.job.pod.active`.
- Container limit/request metrics use UpDownCounters. CPU limit/request
  utilization metrics are excluded from code generation.
- Paging-fault metrics are `k8s.pod.paging.faults`,
  `k8s.node.paging.faults`, and `container.paging.faults`, without the old
  `.memory` segment (batch `2026-08-stable`).
- Corresponding container, pod, and node `memory.usage` instruments are
  UpDownCounters; selected container and Kubernetes memory metrics are
  Release Candidate.
- CPU usage is measured in cores as
  `(cpuTimeEnd - cpuTimeStart) / elapsedSeconds`.
- Node filesystem metrics add `k8s.node.filesystem.inode.count` and
  `k8s.node.filesystem.inode.free`.

### Storage and in-place resize

New `k8s.persistentvolume` and `k8s.persistentvolumeclaim` entities have phase
and storage capacity/request metrics. Use
`k8s.container.ephemeral_storage.usage` and distinguish `rootfs` from `logs`
with `k8s.container.ephemeral_storage.fs_type`. Container CPU and memory
limit/request telemetry distinguishes desired and current values during
in-place resize.

### Services, workloads, and maturity

- `k8s.service` adds endpoint and load-balancer-ingress counts.
- Additional telemetry covers node system containers and filesystems, pod
  volumes, pod/container memory and status, restarts, readiness, node
  conditions, quotas, and HPA targets.
- Pod entities add `k8s.pod.ip`, `k8s.pod.hostname`, and
  `k8s.pod.start_time`.
- Selected Kubernetes and container-registry resource attributes are stable.
- `k8s.pod.cpu.time`, `k8s.node.cpu.time`, and `container.cpu.time` are
  Release Candidate.

## Application and cloud

### Application

Application conventions add `app.build_id`, `app.screen.name`, a jank event,
and a minimal end-user application crash definition.

### Cloud

- Azure uses `azure.service.request.id`,
  `azure.resource_provider.namespace`, dotted `cloud.platform` values, and
  `azure.resource_group.name`. On Azure, `cloud.account.id` is the
  subscription ID.
- GCE labels are Resource attributes.
- GCE Instance Group Manager and `gcp.apphub_destination.*` attributes are
  defined.
- Cloud enums cover GCP Agent Engine, Hetzner, Linode/Akamai, and Vultr.
- Scaleway uses `cloud.provider` plus
  `cloud.platform=scaleway_cloud_compute`.
- Invoke commands used to collect `host.id` by full path.

## Language and framework runtimes

- .NET defines network spans for DNS, TLS, and sockets, plus optional HTTP
  connection relationships.
- ASP.NET Core adds Identity, authentication/authorization, and memory-pool
  metrics.
- Go adds Opt-In CPU time, GC pause/cycle metrics, and detailed-state
  attributes.
- The JVM adds `jvm.file_descriptor.limit`.
- `kotlin` is a valid `telemetry.sdk.language` value.

## SDK and component self-observability

- `otel.sdk.span.started` replaces `otel.sdk.span.ended` and can distinguish
  parent-span origin.
- `otel.span.sampling_result` on `otel.sdk.span.live` permits only
  `RECORD_ONLY` and `RECORD_AND_SAMPLE`.
- Exporter retry metrics count one operation across all attempts and backoff
  through the final result.
- Processor metrics reserve `already_shutdown` as an `error.type`.
- `otel.sdk.processor.span.processed` and
  `otel.sdk.processor.log.processed` count items when a processor passes them
  to an exporter—not at queue acceptance or export completion. Export outcome
  does not change the count.

## Event and exporter metadata

- Non-OTLP paths can carry `otel.event.name` and `otel.scope.schema_url`.
- Zipkin and Prometheus exporters have specified `component.type` values.
- The `otel.scope` entity has been removed.
- Events may use complex attributes instead of body fields; the body may hold
  a display message.

## Stability and domain expansion

- CI/CD spans, metrics, logs, attributes, and entities and the VCS conventions
  are Release Candidate.
- `cpu.mode`, `disk.io.direction`, `network.io.direction`, and
  `system.paging.fault.type` are Release Candidate.
- `network.io.direction` describes traffic at the observed interface boundary,
  not logical flow direction.
- Feature-flag conventions are Release Candidate.
- `network.interface.name` is Release Candidate.
- Mainframe and z/OS conventions use `os.type=zos`, replacing `z_os`.
- NFS metrics use `nfs.*` with `rpc.onc.*` and `rpc.nfs.*` attributes.
- OpenShift adds cluster-quota metrics, and filesystem conventions include
  lock counts.

## Profile conversion metadata

Pprof attributes support lossless profile conversion, including
`pprof.profile.comment`, `pprof.scope.default_sample_type`, and
`pprof.scope.sample_type_order`. LuaJIT is a recognized frame type.
