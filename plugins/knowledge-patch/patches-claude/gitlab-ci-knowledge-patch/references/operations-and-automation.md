# Operations, Observability, and Automation

## Inspect project CI/CD analytics

Since 18.0, a redesigned project CI/CD analytics view is available in limited
availability on GitLab Dedicated. It exposes pipeline performance trends and
reliability metrics in the project UI. Confirm that the feature is enabled for the
Dedicated instance before building an operational process around it.

## Inspect CI/CD Catalog component usage

Since 19.0, Ultimate customers on GitLab.com, GitLab Self-Managed, and GitLab
Dedicated can open a catalog resource's usage details to see:

- Projects that consume each component.
- The component version selected by each project.
- Whether that selected version is current.

Consumers on outdated versions appear first, making the view useful for prioritizing
component upgrades.

## Export GitLab Runner telemetry with OTLP

GitLab Runner 19.0 adds instrumentation feature negotiation, an OTLP export client,
and its first trace span, `job_execution`. Configure a compatible OTLP collector and
verify negotiation and export before using the span as an operational signal.

## Use Duo CLI locally or in CI/CD

Since 19.2, Duo CLI is generally available through `glab` or as a standalone tool.
It supports interactive chat and headless CI/CD execution and can use GitLab project,
pipeline, and agent context. Its working features include shared sessions, selection
among available AI models, tool approvals, MCP connections, slash commands, skills,
and `AGENTS.md` instructions. GitLab Self-Managed and Dedicated administrators can
disable the capability.

## Define reusable custom flows

Since 19.2, generally available custom flows are reusable YAML workflows managed
from a project or the AI Catalog. A flow can provide:

- Multiple collaborating agents.
- Human approval or feedback checkpoints.
- Public or private visibility.
- Validated configuration.
- Service-account and composite-identity execution.
- Triggers from mentions, assignments, pipeline events, and merge-request lifecycle
  events.

Choose explicit identities and approval checkpoints for actions that mutate a
repository or deployment.

## Start foundational flows from Agentic Chat

Since 19.2, Agentic Chat can hand a request to the Developer, Code Review, or Fix
CI/CD Pipeline foundational flow. The user approves the handoff in chat and can
follow the resulting work in that conversation or under **AI** > **Sessions**.

## Use the CI Expert Agent

Since 19.2, the generally available CI Expert Agent can create, debug, and optimize
pipelines using repository context. When Orbit and its beta Knowledge Graph are
enabled, it can also use graph-based code intelligence for more contextual
recommendations. Treat the graph-enhanced path as dependent on both optional
features being enabled.

## Get targeted fixes from the Fix CI/CD Pipeline Flow

Since 19.2, the Fix CI/CD Pipeline Flow classifies a failure before taking action.
When the relevant files are already in a merge-request diff, it returns fixes as
code suggestions on that merge request. It also:

- Follows child-pipeline failures across the complete hierarchy.
- Reads project-specific behavior from `AGENTS.md`.
- Collapses its reasoning in merge-request comments by default.

Review suggestions and the traversed child-pipeline context before applying a fix.
