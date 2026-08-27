---
name: temporal-knowledge-patch
description: Temporal
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Temporal Knowledge Patch

Use this skill when designing, reviewing, upgrading, deploying, or operating
Temporal Workflows, Workers, CLI automation, or Temporal Cloud infrastructure.
It focuses on replay safety, Activity recovery, SDK sandbox behavior, current
Worker Versioning, production CLI usage, and Cloud connectivity.

## Reference index

| Reference | Topics |
| --- | --- |
| [workflow-safety.md](references/workflow-safety.md) | Replay-compatible edits, command-producing changes, Activity retries, heartbeats, replay gates |
| [workers-and-sdks.md](references/workers-and-sdks.md) | Official SDKs, Worker topology and identity, Python replay APIs, TypeScript sandbox behavior |
| [worker-versioning.md](references/worker-versioning.md) | Deployment versions, routing behaviors, ramps, overrides, Continue-as-New, drainage, garbage collection |
| [cli-operations.md](references/cli-operations.md) | Cloud routing, schedules, remote Clusters, replication, archival, Nexus, profiles, TLS, output |
| [cloud.md](references/cloud.md) | API keys, Namespace authentication, Connectivity Rules, private DNS and SNI, control plane, migration |

## Start with replay safety

Workflow code is replayed against recorded Event History. Treat a code edit as
safe only when it preserves the sequence of Commands for every existing
history.

Usually replay-compatible:

- Change Activity or Child Workflow inputs, return values, or execution
  timeouts without changing their types or IDs.
- Change an external Signal's inputs.
- Change a Timer duration, except between zero and nonzero in Java, Python, or
  Go, or between `-1` (infinite) and another value in .NET.
- Call Workflow APIs that do not emit Commands.
- Add a Signal Handler only if that Signal Type has never already been
  received by affected histories.

Require Worker Versioning, patching, or both:

- Add, remove, or reorder scheduling or cancellation of Timers, Activities,
  Child Workflows, external Signals, or Nexus operations.
- Change termination, patch/version, Search Attribute, Memo, Side Effect, or
  Mutable Side Effect calls.
- Rename Activity or Child Workflow types or IDs.

Prefer current Worker Versioning for new deployments. The older experimental
method is being removed from the Server and should not shape new rollout
designs.

## Treat Activities as at-least-once code

Temporal records a successful Activity completion once, but Activity code can
run or partially run more than once. A Worker can crash after an external side
effect and before reporting completion.

- Make external effects idempotent.
- Derive a stable per-Activity key from Workflow Run ID plus Activity ID.
- Configure at least one Activity timeout, usually Start-to-Close.
- Heartbeat operations that last more than a few minutes.
- Persist resumable progress in heartbeat details.
- Remember that cancellation of a running Activity depends on heartbeating.

Without heartbeat progress, a retry begins from the Activity's initial state.

## Use deterministic Workflow APIs

### Python

Inside Workflow code, use:

- `workflow.logger` for replay-aware logging.
- `workflow.random()` for deterministic randomness.
- `workflow.uuid4()` for deterministic UUIDs.
- `workflow.now()` for the last Workflow Task time.

Do not use standard wall-clock, random, UUID, or ordinary logging behavior as a
substitute.

Use `@workflow.init` on `__init__` when message handlers need input-derived
state before `run` starts. Constructor parameters and annotations must match
the `@workflow.run` method, which still receives the same inputs.

Replay flags are observability tools, not business-logic inputs. Never branch
Workflow behavior on `workflow.unsafe.is_replaying()`. When reproducing the
built-in logging and tracing semantics, use
`workflow.unsafe.is_replaying_history_events()`; it is false for read-only
Queries and Update validators.

### TypeScript

Workflow code runs in a deterministic Webpack sandbox:

- Import packages only if they do not reference Node.js or DOM APIs.
- Put a provably runtime-unused forbidden module in
  `BundleOptions.ignoreModules` only when necessary.
- Import Activity types, never Activity implementations, into Workflow code.
- Do not use `WeakRef`, `FinalizationRegistry`, or `crypto.randomUUID()`.

The sandbox replaces `Math.random()`, `Date`, and `setTimeout()` with
deterministic implementations. UUID libraries backed by `Math.random()` are
safe. `Date.now()` and `new Date()` expose the last Workflow Task completion
time and advance only after an `await`.

TypeScript's `workflowInfo().unsafe.isReplaying` has the same
observability-only constraint as Python's replay flag. Use
`workflowInfo().unsafe.isReplayingHistoryEvents` for built-in logging/tracing
semantics.

## Gate deployments with replay

Before allowing new Worker code to poll its production Task Queue:

1. Run a single instance in verification mode.
2. Query representative recent executions.
3. Convert the result iterator with `map_histories()`.
4. Pass the histories to `Replayer.replay_workflows()`.
5. Fail the deployment on any replay error.
6. Start the remaining Worker instances only after a clean replay.

Do not move encrypted Payload histories into a test environment that lacks
their decryptor. Scrub histories containing PII or keep them outside CI and
pre-deployment replay paths.

## Choose a Worker Versioning behavior

Use Pinned when a Workflow should finish before its build is retired. Use
Auto-Upgrade plus replay-safe patches when executions span builds. A
long-running Workflow can stay Pinned for one run and upgrade at a
Continue-as-New boundary.

Versioned Workers opt in with a deployment name, Build ID, and optional default
behavior. If there is no default, every Workflow Type must declare its
behavior. During migration, Auto-Upgrade best preserves legacy routing until
all types have explicit annotations.

Key routing constraints:

- A deployment has one Current Version and at most one Ramping Version.
- New Pinned and Auto-Upgrade Workflows begin on one of those versions.
- Set routing only after Workers for the target version are polling.
- An unavailable or undersized Current or Ramping pool can strand its traffic
  share; the other version does not automatically absorb it.
- Rolling deployments are incompatible with Worker Versioning.
- Blue-green rollouts should use Auto-Upgrade rather than pinning.
- Rainbow deployments retain older versions while pinned executions drain.
- Serverless Workers must use qualified, versioned function ARNs.

Moving a pinned execution does not make its history compatible with the target
code. Patch the target when necessary. Use an atomic
`reset with-workflow-update-options` for an incompatible rollback.

## Operate versions through drainage

Versions move from Inactive to Active, then Draining while open pinned
Workflows remain, and finally Drained. A version that was never Current or
Ramping stays Inactive rather than entering drainage.

Stop Workers only after `describe-version` reports drainage complete, while
accounting for closed pinned Workflow Queries that still need compatible
Workers.

The hosted service caps versions per deployment. When the cap is reached, the
next registration deletes the oldest Drained version with no pollers in the
previous five minutes. If none qualifies, registration fails. Stop pollers for
an obsolete drained version, or raise the self-hosted limit. Reusing a deleted
deployment name and Build ID recreates that version.

## Use CLI configuration deliberately

The Temporal CLI has two separate configuration systems:

- `--config-file` reads TOML and `--profile` chooses a profile.
- `--env-file` reads YAML and `--env` chooses an environment.

Use `--disable-config-file` or `--disable-config-env` to suppress their
respective implicit inputs. Supplying `--api-key` or any TLS option enables
TLS; use `--tls=false` only for an intentional plaintext override.

For scripts, select `--output text|json|jsonl|none` and
`--time-format relative|iso|raw`. With JSON output,
`--no-json-shorthand-payloads` keeps raw Payload objects.

Cloud login does not redirect ordinary service commands. Pass the Cloud gRPC
address and fully qualified Namespace, and use `temporal cloud namespace` for
Cloud Namespace administration.

## Apply Cloud network controls safely

API-key authentication must be enabled for a Namespace during setup. Keys
inherit the linked user's or Service Account's RBAC.

Connectivity Rules constrain accepted paths, not live connections:

- With no attached rules, public traffic and configured private paths work.
- Attaching any rule rejects every unmatched path immediately.
- Rule objects are immutable; replace them rather than updating them.
- Namespace attachments are full-set replacement, not a patch.
- `--remove-all` returns the Namespace to public access.
- The Web UI is outside Connectivity Rule enforcement.

Stage public and private rules together before removing public access. Enabling
Stable IPs later requires recreating and reattaching the public rule.

Private connectivity does not alter client DNS. Configure private DNS or use
the endpoint DNS name/IP and override TLS server name. SNI depends on
single-region versus multi-region routing and on mTLS versus API-key
authentication; the wrong SNI can reset TLS even when port 7233 is reachable.

Read the topic references before changing production routing, Namespace
replication, archival, Nexus endpoints, Worker assignment, or private
connectivity.
