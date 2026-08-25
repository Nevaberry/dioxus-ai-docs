# Worker Versioning

## Check the component floor

The current Worker Versioning model requires these minimum SDK versions:

| SDK | Minimum |
| --- | --- |
| Go | 1.35.0 |
| Python | 1.11 |
| Java | 1.29 |
| TypeScript | 1.12 |
| .NET | 1.7.0 |
| Ruby | 0.5.0 |

Self-hosted installations also require Temporal CLI 1.4.1, Server 1.29.1, and
UI 2.38.0 or newer.

## Model deployments and routing

A Worker Deployment Version is the pair of deployment name and Build ID. It
can contain Workers polling multiple Task Queues. A Task Queue joins a version
when a Worker in that version polls it.

Each deployment has one Current Version and optionally one Ramping Version.
New Pinned or Auto-Upgrade Workflows start only on one of those two versions.

- Rolling deployments are incompatible with Worker Versioning.
- Blue-green deployments provide controlled routing but should use
  Auto-Upgrade instead of pinning.
- Rainbow deployments retain more than two versions, allowing pinned
  executions to drain on their original builds.

## Choose Pinned or Auto-Upgrade

Pinned fits Workflows that finish before their build should be retired.
Auto-Upgrade plus replay-safe patching fits executions that span builds.
Long-lived Workflows that Continue-as-New can remain Pinned for each run and
upgrade at a Continue-as-New boundary.

Versioned Workers must opt in with a deployment name, Build ID, and optional
default behavior. Without a default, each Workflow Type must declare its own
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

During migration, defaulting to Auto-Upgrade most closely preserves legacy
routing until every Workflow Type is annotated. Child Workflows of an
Auto-Upgrade parent or predecessor default to Auto-Upgrade, not Unspecified.

During a ramp, unavailable or undersized Current or Ramping Workers can block
their assigned share of Tasks. The other version does not consume that share
automatically.

Serverless Worker versions must use qualified, versioned function ARNs in
production. An unqualified ARN can point a supposedly pinned Workflow at
changed code.

Set behavior per Workflow Type when it should not inherit the Worker default:

```python
@workflow.defn(versioning_behavior=VersioningBehavior.PINNED)
class OrderWorkflow:
    ...
```

## Activate and ramp only polling versions

Use deployment routing commands only after Workers for the corresponding
version are polling. `describe` shows registered versions. Current and Ramping
assignments control production traffic.

```bash
temporal worker deployment set-current-version \
  --deployment-name "$DEPLOYMENT" --build-id "$BUILD_ID"
temporal worker deployment set-ramping-version \
  --deployment-name "$DEPLOYMENT" --build-id "$BUILD_ID" --percentage=5
```

Inspect an execution's behavior, assigned version, and override with:

```bash
temporal workflow describe -w "$WORKFLOW_ID"
```

## Move and convert existing executions carefully

Move one pinned execution with `temporal workflow update-options`. Set
`--versioning-override-behavior pinned` together with
`--versioning-override-deployment-name` and
`--versioning-override-build-id`. Add `--query` to select a batch by
`TemporalWorkerDeploymentVersion`.

Moving changes routing; it does not guarantee that the target code can replay
the existing history. Patch the target code when necessary. For an incompatible
rollback, use `reset with-workflow-update-options` so reset and move occur
atomically.

Convert mistakenly long-lived pinned executions by setting
`--versioning-override-behavior auto_upgrade`, optionally with a Workflow Type
and deployment-version query. They resume on their Target Version. Patch that
target when it differs from the build that produced the history.

## Upgrade Pinned runs at Continue-as-New

The experimental SDK-level Continue-as-New upgrade option allows a pinned run
to detect a changed Target Version and start its next run there without
patching the completed run.

```python
if workflow.info().is_target_worker_deployment_version_changed():
    workflow.continue_as_new(
        next_input,
        initial_versioning_behavior=ContinueAsNewVersioningBehavior.AUTO_UPGRADE,
    )
```

The changed-target flag refreshes only after a Workflow Task completes.
Sleeping Workflows do not wake because the target changed; Signal them or
check after a normal Workflow Task. The old definition's emitted inputs must
remain compatible with the new definition's first Workflow Task.

## Drain and retire versions

Versions progress from Inactive to Active, then Draining while open pinned
Workflows remain, and finally Drained. An Inactive version that was never
Current or Ramping does not enter drainage.

`temporal worker deployment describe-version` exposes periodically refreshed
drainage status. Stop that version's Workers after drainage completes. Closed
pinned Workflow Queries can still require compatible Workers, so account for
that access before shutdown.

## Send tests to an unreleased build

Synthetic tests can bypass normal production routing and start directly on an
unreleased build by setting a pinned version override:

```python
versioning_override = PinnedVersioningOverride(
    WorkerDeploymentVersion("orders", "candidate-build")
)
```

## Manage the deployment-version cap

Worker Deployments persist, but their versions are capped. The hosted service
currently allows 100 versions per deployment.

When a new version reaches the cap, the Server deletes the oldest Drained
version that had no pollers during the previous five minutes. If none
qualifies, the new Worker's poll fails. Stop polling with an obsolete drained
version, or increase the self-hosted limit.

Polling later with the same deployment name and Build ID recreates a deleted
version.
