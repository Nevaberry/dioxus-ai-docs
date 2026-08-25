# Workers and Deployments

## SDK support

Temporal officially supports SDKs for Go, Java, Python, TypeScript, .NET, Ruby,
PHP, and Rust. Swift, Haskell, Clojure, and Scala SDKs are third-party projects
and are not officially supported.

## Worker topology

A Worker Entity polls exactly one Task Queue and contains a Workflow Worker, an
Activity Worker, or both. A Worker Process can host multiple Worker Entities,
so one process can poll multiple Task Queues.

All user Workflow and Activity code executes in externally operated Worker
Processes. It never runs on the Temporal Service.

## Useful Worker identities

SDKs default Worker Identity to:

```text
${process.pid}@${os.hostname()}
```

The value appears in Event History and Task Queue poller lists. In containers,
the default is often PID `1` plus a random or ephemeral hostname, which is
difficult to correlate with logs. Set a concise, unique identity tied to the
execution context or log stream, such as an ECS Task ID plus environment and
region.

## Version prerequisites

The current Worker Versioning model requires these minimums:

| Component | Minimum version |
| --- | --- |
| Go SDK | 1.35.0 |
| Python SDK | 1.11 |
| Java SDK | 1.29 |
| TypeScript SDK | 1.12 |
| .NET SDK | 1.7.0 |
| Ruby SDK | 0.5.0 |
| CLI for self-hosted installations | 1.4.1 |
| Server for self-hosted installations | 1.29.1 |
| UI for self-hosted installations | 2.38.0 |

Check all independently; a sufficiently new SDK does not compensate for an old
self-hosted Server, CLI, or UI.

## Deployment Versions and Task Queues

A Worker Deployment Version is identified by deployment name plus Build ID.
The same version can contain Workers polling several Task Queues. A Task Queue
joins that version when a Worker from the version polls it.

Each Worker Deployment has:

- exactly one Current Version; and
- optionally one Ramping Version.

New Pinned or Auto-Upgrade Workflows start only on one of those two versions.
Do not assign a version until its Workers are polling.

## Deployment shapes

Rolling deployments are incompatible with Worker Versioning. Blue-green
deployments provide controlled routing, but should use Auto-Upgrade rather than
pinning. Rainbow deployments retain more than two versions, allowing pinned
executions to drain on their original builds.

## Pinned versus Auto-Upgrade

Use Pinned when Workflows will finish before the build should be retired. A
long-running Workflow that Continue-as-New can stay Pinned within each run and
upgrade at a Continue-as-New boundary.

Use Auto-Upgrade with replay-safe patching for Workflows that span builds.
During migration, a default of Auto-Upgrade most closely preserves legacy
routing until all Workflow Types are explicitly annotated.

Child Workflows of an Auto-Upgrade parent or predecessor default to
Auto-Upgrade, not Unspecified. During a ramp, a missing or undersized Current
or Ramping Worker pool can block its share of Tasks rather than allow the other
version to consume them.

## Worker opt-in

Versioned Workers opt in with deployment name, Build ID, and an optional
default behavior. If there is no default, each Workflow Type must declare its
behavior.

```python
Worker(
    client,
    task_queue="orders",
    workflows=workflows,
    activities=activities,
    deployment_config=WorkerDeploymentConfig(
        version=WorkerDeploymentVersion("orders", build_id),
        use_worker_versioning=True,
        default_versioning_behavior=VersioningBehavior.UNSPECIFIED,
    ),
)
```

Serverless Worker versions must use qualified, versioned function ARNs in
production. Otherwise a pinned execution can invoke code that changed behind
an unqualified target.

## Workflow-Type declarations

Versioning behavior can be declared per Workflow Type instead of inherited
from the Worker. Python uses the Workflow definition decorator:

```python
@workflow.defn(versioning_behavior=VersioningBehavior.PINNED)
class OrderWorkflow:
    ...
```

## Activate and ramp builds

Wait for the corresponding versioned Workers to poll before changing routing.
Describe the deployment to confirm registered versions, then set Current and,
if desired, Ramping:

```bash
temporal worker deployment set-current-version \
  --deployment-name "$DEPLOYMENT" --build-id "$BUILD_ID"

temporal worker deployment set-ramping-version \
  --deployment-name "$DEPLOYMENT" --build-id "$BUILD_ID" --percentage=5
```

Inspect an execution's behavior, assigned version, and override:

```bash
temporal workflow describe -w "$WORKFLOW_ID"
```

## Move pinned executions

Move one pinned execution with `temporal workflow update-options`, supplying
all three override values:

```bash
temporal workflow update-options \
  --workflow-id "$WORKFLOW_ID" \
  --versioning-override-behavior pinned \
  --versioning-override-deployment-name "$DEPLOYMENT" \
  --versioning-override-build-id "$BUILD_ID"
```

Add `--query` to move a batch selected by
`TemporalWorkerDeploymentVersion`. Moving routing does not make the target code
replay-compatible; patch it when needed.

For an incompatible rollback, use `reset with-workflow-update-options` so the
reset and version move are atomic.

## Convert mistakenly pinned long-lived executions

Set `--versioning-override-behavior auto_upgrade`, optionally selecting a batch
by Workflow Type and deployment-version query. Converted executions resume on
their Target Version. Patch that target when it differs from the build that
produced their histories.

## Upgrade at Continue-as-New

The experimental SDK-level Continue-as-New upgrade option lets a pinned run
detect a Target Version change and start its next run on that version without
patching the completed run.

```python
if workflow.info().is_target_worker_deployment_version_changed():
    workflow.continue_as_new(
        next_input,
        initial_versioning_behavior=ContinueAsNewVersioningBehavior.AUTO_UPGRADE,
    )
```

The flag refreshes only after a Workflow Task completes. A sleeping Workflow
does not wake solely because the target changed; Signal it or check after a
normal Workflow Task. Inputs emitted by the old definition must be compatible
with the first Workflow Task of the new definition.

## Drainage and retirement

Versions move through:

```text
Inactive -> Active -> Draining -> Drained
```

Draining means open pinned Workflows remain. An Inactive version that was never
Current or Ramping does not enter drainage.
`temporal worker deployment describe-version` reports periodically refreshed
drainage status. Workers can stop after the version reaches Drained, but closed
pinned Workflow Queries still require compatible Workers.

## Target an unreleased build

Synthetic tests can start directly on a candidate build by using a pinned
version override:

```python
versioning_override = PinnedVersioningOverride(
    WorkerDeploymentVersion("orders", "candidate-build")
)
```

This tests the candidate without assigning it Current or Ramping production
traffic.

## Deployment Version collection

Worker Deployments persist, but their versions are capped. The hosted service
currently permits 100 versions per deployment.

When the next version registers, the Server deletes the oldest Drained version
that had no pollers during the previous five minutes. If no version qualifies,
the new Worker's poll fails until an old drained version stops polling or the
self-hosted limit is raised. Polling later with the same deployment name and
Build ID recreates a deleted version.
