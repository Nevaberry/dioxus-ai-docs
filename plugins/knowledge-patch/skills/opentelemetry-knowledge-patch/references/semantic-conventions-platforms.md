# Semantic Conventions: Platforms, Runtimes, and Entities

## Process identity and metrics

Executable details form a separate `process.executable` entity.
`process.pid` and `process.creation.time` are Required identity attributes;
descriptive process attributes are Optional.

Use:

- `process.unix.file_descriptor.count` on Unix-like systems.
- `process.windows.handle.count` on Windows.

These replace `process.open_file_descriptor.count`. Process attributes,
process metrics, and the process entity are Release Candidate.

## Service and deployment identity

Service modeling separates namespace, service, and instance entities.

- `service.peer.name` and `service.peer.namespace` replace `peer.service`.
- `service.instance.id` is stable.
- `deployment.environment.name` is stable.
- Well-known deployment environment values are `Production`, `Staging`,
  `Test`, and `Development`.
- Alpha `service.criticality` values are `critical`, `high`, `medium`, and
  `low`.

## System metrics

Current metric and attribute names include:

- `system.network.packet.dropped`.
- `system.network.packet.count`.
- `system.network.connection.count`.
- `system.memory.linux.shared`.
- The general `*.memory.linux` word ordering.
- `system.cpu.*` for CPU metrics.
- `process.state`.
- `system.paging.fault.type`.
- `process.context_switch.type`.

`cpu.logical_number` is Opt-In.

## V8 JavaScript heap metrics

Heap-space metrics use `v8js.memory.heap.space.*`.

- The old meaning of `v8js.memory.heap.limit` moved to
  `v8js.memory.heap.space.size`.
- `v8js.memory.heap.limit` is now an UpDownCounter for the absolute V8 heap
  limit.

## Kubernetes

### Metric-name migration

Node allocatable metric names include:

- `k8s.node.cpu.allocatable`.
- `k8s.node.memory.allocatable`.
- `k8s.node.pod.allocatable`.

Plural UpDownCounter names are normalized to singular forms, such as
`k8s.job.pod.active`. Container limit and request metrics use
UpDownCounters. CPU limit/request utilization metrics are excluded from code
generation.

### Persistent storage and in-place resize

New `k8s.persistentvolume` and `k8s.persistentvolumeclaim` entities have
phase and storage capacity/request metrics.

`k8s.container.ephemeral_storage.usage` distinguishes `rootfs` from `logs`
through `k8s.container.ephemeral_storage.fs_type`.

Container CPU and memory limit/request telemetry distinguishes desired values
from current values during in-place resize.

### Services, workloads, and pods

The `k8s.service` entity includes endpoint and load-balancer-ingress counts.
Additional Kubernetes telemetry covers:

- Node system containers and filesystems.
- Pod volumes.
- Pod and container memory and status.
- Restarts and readiness.
- Node conditions.
- Quotas and HPA targets.

Pod entities add `k8s.pod.ip`, `k8s.pod.hostname`, and `k8s.pod.start_time`.

### Maturity

Selected Kubernetes and container-registry resource attributes are stable.
`k8s.pod.cpu.time`, `k8s.node.cpu.time`, and `container.cpu.time` are Release
Candidate.

## Application telemetry

Application conventions add:

- `app.build_id`.
- `app.screen.name`.
- A jank event.
- A minimal end-user application crash definition.

## Cloud platforms

### Azure

Use:

- `azure.service.request.id`.
- `azure.resource_provider.namespace`.
- Dotted `cloud.platform` values.
- `azure.resource_group.name`.

On Azure, `cloud.account.id` is the subscription ID.

### Google Cloud and other providers

GCE labels are resource attributes. Conventions also add GCE Instance Group
Manager attributes and `gcp.apphub_destination.*`.

Cloud enumerations include GCP Agent Engine, Hetzner, Linode/Akamai, and
Vultr.

## Language and runtime conventions

### .NET and ASP.NET Core

.NET adds network spans for DNS, TLS, and sockets, plus optional HTTP
connection relationships. ASP.NET Core adds Identity,
authentication/authorization, and memory-pool metrics.

### Go, JVM, and Kotlin

- Go adds Opt-In CPU time, garbage-collection pause and cycle metrics, and
  detailed-state attributes.
- The JVM adds `jvm.file_descriptor.limit`.
- `kotlin` is a valid `telemetry.sdk.language` value.

## SDK self-observability metrics

- `otel.sdk.span.started` replaces `otel.sdk.span.ended` and can distinguish
  the parent span's origin.
- `otel.span.sampling_result` on `otel.sdk.span.live` permits only
  `RECORD_ONLY` and `RECORD_AND_SAMPLE`.
- Exporter retry metrics count one operation across all attempts, including
  the final attempt and backoff.
- Processor metrics reserve `already_shutdown` as an `error.type`.

## Event and exporter metadata

- Non-OTLP paths can carry `otel.event.name` and `otel.scope.schema_url`.
- Zipkin and Prometheus exporters have specified `component.type` values.
- The `otel.scope` entity has been removed.
- Events may use complex attributes in place of body fields.
- The event body may contain a display message.

## Convention maturity and directional meaning

CI/CD spans, metrics, logs, attributes, and entities are Release Candidate.
VCS conventions and feature-flag conventions are also Release Candidate.

These attribute conventions are Release Candidate:

- `cpu.mode`.
- `disk.io.direction`.
- `network.io.direction`.
- `system.paging.fault.type`.

`network.io.direction` describes traffic at the observed interface boundary,
not logical application-flow direction.

## Mainframe, filesystem, and network filesystems

- Mainframe and z/OS conventions use `os.type=zos`, replacing `z_os`.
- NFS metrics use the `nfs.*` namespace with `rpc.onc.*` and `rpc.nfs.*`
  attributes.
- OpenShift adds cluster-quota metrics.
- Filesystem lock counts are supported.

## Profile conversion metadata

Pprof attributes support lossless profile conversion, including:

- `pprof.profile.comment`.
- `pprof.scope.default_sample_type`.
- `pprof.scope.sample_type_order`.

LuaJIT is a recognized frame type.
