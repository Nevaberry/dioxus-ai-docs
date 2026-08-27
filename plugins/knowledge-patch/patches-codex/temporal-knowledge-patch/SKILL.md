---
name: temporal-knowledge-patch
description: Temporal
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Temporal Knowledge Patch

Use this skill when designing, reviewing, debugging, deploying, or operating
Temporal Workflows, Activities, Workers, Worker Deployments, CLI automation, or
Temporal Cloud connectivity.

## How to apply this skill

1. Identify whether the change touches deterministic Workflow code, Activity
   side effects, Worker routing, deployment state, CLI configuration, or Cloud
   access.
2. For Workflow edits, classify the change before implementation. Replay-safe
   changes can ship directly; Command-producing changes need Worker Versioning
   or patching.
3. For Worker rollouts, choose Pinned or Auto-Upgrade from execution lifetime
   and replay requirements, then verify the new code against representative
   histories.
4. For CLI and Cloud work, inspect the target address, Namespace, profile,
   authentication, TLS server name, and replacement semantics before changing
   state.
5. Prefer project manifests, deployed Server and CLI versions, code, tests, and
   observed behavior when they differ from this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [workflows-activities-and-replay.md](references/workflows-activities-and-replay.md) | Replay compatibility, Command-producing edits, Activity retries and Heartbeats, replay-safe SDK APIs, pre-deployment replay |
| [workers-and-deployments.md](references/workers-and-deployments.md) | SDK support, Worker topology and identity, Worker Versioning requirements, routing, overrides, drainage, and version collection |
| [cli-and-self-hosted-operations.md](references/cli-and-self-hosted-operations.md) | Cloud routing, Schedules, remote Clusters, replicated Namespaces, Nexus Endpoints, configuration, TLS, and output |
| [cloud-security-connectivity-and-migration.md](references/cloud-security-connectivity-and-migration.md) | API keys, Namespace authentication, private connectivity, rule replacement, DNS/SNI, control plane, and migration |

## Breaking-change triage

Workflow compatibility is about emitted Commands and recorded events, not only
source-level API compatibility.

### Usually replay-compatible

- Change Activity or Child Workflow inputs, return values, or execution
  timeouts without changing their types or IDs.
- Change external Signal inputs.
- Change a Timer duration, except between `0` and nonzero in Java, Python, and
  Go, or between `-1` (infinite) and another value in .NET.
- Call Workflow APIs that do not emit Commands.
- Add a Signal Handler only if no Signal of that type has already been
  received in histories that will replay.

### Version or patch these changes

- Add, remove, or reorder scheduling or cancellation of Timers, Activities, or
  Child Workflows.
- Add, remove, or reorder external Signals or Nexus operations.
- Change termination, patch/version, Search Attribute, Memo, Side Effect, or
  Mutable Side Effect calls.
- Change an Activity Type, Child Workflow Type, or their IDs.

Use the current Worker Versioning model as the primary rollout mechanism.
Patching remains useful by itself or with Worker Versioning. Do not build new
rollouts around the pre-2025 experimental Worker Versioning method; it was
scheduled for removal from Temporal Server in March 2026.

## Never branch business logic on replay state

Replay-state guards are observability tools. In Python,
`workflow.unsafe.is_replaying()`, and in TypeScript,
`workflowInfo().unsafe.isReplaying`, may suppress custom metrics or
notifications. Branching Workflow business logic on these values violates
determinism.

For behavior matching built-in logging and tracing, use Python
`workflow.unsafe.is_replaying_history_events()` or TypeScript
`workflowInfo().unsafe.isReplayingHistoryEvents`. Both are false for read-only
Queries and Update validators.

## Activity correctness under retries

Activity completion is observed exactly once, but Activity code is not executed
exactly once. A Worker can perform an external side effect, crash before
reporting completion, and execute the code again under the Retry Policy.

- Make side effects idempotent.
- For an external key stable across attempts, combine Workflow Run ID with
  Activity ID.
- Configure at least one Activity timeout, normally Start-to-Close.
- Operations lasting more than a few minutes should Heartbeat or poll.
- A retry restarts from initial state unless Heartbeats established recoverable
  progress.
- A running Activity must permit Heartbeating for cancellation to be delivered.

## Choose a Worker routing behavior

### Pinned

Use Pinned when a Workflow should finish before its build is retired. A
long-lived Workflow that Continue-as-New can remain Pinned during each run and
upgrade at the run boundary.

### Auto-Upgrade

Use Auto-Upgrade with replay-safe patching for executions spanning builds.
During migration, making Auto-Upgrade the Worker default most closely preserves
legacy routing until every Workflow Type has an explicit annotation.

Child Workflows of an Auto-Upgrade parent or predecessor default to Auto-Upgrade
rather than Unspecified. If Current or Ramping Workers are missing or
undersized, their traffic share can block instead of spilling to the other
version.

### Deployment shapes

- Rolling deployments are incompatible with Worker Versioning.
- Blue-green deployments can use controlled routing, but should use
  Auto-Upgrade instead of pinning.
- Rainbow deployments keep more than two versions so pinned executions can
  drain on their original builds.

## Worker Versioning readiness

The current model requires at least:

| Component | Minimum |
| --- | --- |
| Go SDK | 1.35.0 |
| Python SDK | 1.11 |
| Java SDK | 1.29 |
| TypeScript SDK | 1.12 |
| .NET SDK | 1.7.0 |
| Ruby SDK | 0.5.0 |
| Self-hosted CLI | 1.4.1 |
| Self-hosted Server | 1.29.1 |
| Self-hosted UI | 2.38.0 |

A versioned Worker opts in with deployment name, Build ID, and optionally a
default behavior. Without a default, every Workflow Type must declare its
behavior. In serverless environments, point versions at qualified, versioned
function ARNs; an unqualified target can change beneath a pinned execution.

## Safe rollout sequence

1. Start the candidate Worker in verification mode without polling the
   production Task Queue.
2. Query representative recent executions, convert the result iterator with
   `map_histories()`, and run `Replayer.replay_workflows()`.
3. Fail the deployment on any replay error.
4. Start versioned Workers and wait until they poll their Task Queues.
5. Set the deployment's Current Version.
6. Optionally set a Ramping Version and a small percentage.
7. Inspect execution behavior, assigned version, and overrides with
   `temporal workflow describe`.
8. Retire a version only after drainage status reaches Drained and required
   closed-Workflow Query support is accounted for.

Do not place encrypted Payload histories into a replay environment that cannot
decrypt them. Scrub PII or keep those histories out of pre-deployment and CI
replay paths.

## Routing invariants

A Worker Deployment Version is deployment name plus Build ID. One version may
contain Workers polling several Task Queues, and a Task Queue joins when one of
those Workers polls it. Each deployment has one Current Version and optionally
one Ramping Version. New Pinned and Auto-Upgrade Workflows start only on one of
those two versions.

Move pinned executions only after establishing replay compatibility with the
target code. An incompatible rollback needs
`reset with-workflow-update-options` so reset and reassignment are atomic.
Changing a mistakenly long-lived execution to Auto-Upgrade resumes it on its
Target Version; patch that target if it differs from the history-producing
build.

## SDK determinism quick reference

### Python

- Decorate `__init__` with `@workflow.init` when handlers need initialized
  input state. Its parameters and annotations must match `@workflow.run`.
- Use `workflow.logger`, `workflow.random()`, `workflow.uuid4()`, and
  `workflow.now()` inside Workflows.
- Avoid standard logging, randomness, UUID, and wall-clock APIs in Workflow
  code.

### TypeScript

- Workflow bundles may import packages only when they do not reference Node.js
  or DOM APIs.
- Put provably unused forbidden modules in `BundleOptions.ignoreModules`.
- Import Activity types into Workflow code, never Activity implementations.
- `WeakRef`, `FinalizationRegistry`, and `crypto.randomUUID()` are unavailable.
- Sandboxed `Math.random()`, `Date`, and `setTimeout()` are deterministic.
  UUID libraries backed by `Math.random()` are safe.
- `Date.now()` and `new Date()` return the last Workflow Task completion time,
  which advances only after an `await`.

## CLI safety checks

- `temporal cloud login` authenticates the CLI but does not implicitly route
  service commands. Set the Cloud gRPC address and fully qualified Namespace.
- Use the Cloud extension's `temporal cloud namespace` commands for Cloud
  Namespace administration, not `temporal operator namespace`.
- Distinguish TOML `--config-file`/`--profile` from YAML
  `--env-file`/`--env`.
- `--api-key` or any TLS option enables TLS automatically. Use `--tls=false`
  only for an intentional plaintext override.
- Remember that archival state and URI are separate for History and
  Visibility, and an enabled archival URI is immutable.
- Nexus Endpoint updates patch only the supplied fields.

## Cloud connectivity safety checks

Connectivity Rules select allowed paths, not individual connections. No rules
means public traffic and configured private paths are accepted; attaching any
rule immediately rejects every unmatched path. The Web UI is outside this
enforcement.

Rule attachments are complete-set replacements. Stage a public rule alongside
private rules before removing public access. `--remove-all` returns the
Namespace to public access. Because rules cannot be edited, replace and
reattach them when requirements change.

Private connectivity does not configure client DNS. Set private DNS or use the
private endpoint address and the correct TLS server name for the authentication
mode and active region. A wrong SNI value can reset TLS even when port 7233 is
reachable.

## Final review checklist

- Workflow changes are classified against recorded Commands.
- Replay-state APIs affect observability only.
- Activity side effects have stable idempotency keys and Heartbeats where
  needed.
- Candidate code replays representative, decryptable, privacy-safe histories.
- Current and Ramping assignments happen after Workers begin polling.
- Overrides and rollbacks include replay compatibility and atomic reset needs.
- CLI address, Namespace, configuration selector, TLS, and output mode are
  explicit.
- Cloud rule replacement, DNS, SNI, RBAC, and API-key limits are checked before
  access changes.
