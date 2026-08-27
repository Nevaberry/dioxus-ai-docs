# Duo Agents and Flows

## Use Duo CLI from the terminal or CI/CD

Since 19.2, GitLab Duo CLI is generally available through `glab` or as a
standalone tool. Use interactive chat locally or headless mode in CI/CD. It can
use GitLab project, pipeline, and agent context and supports shared sessions,
model selection, tool approvals, MCP connections, slash commands, skills, and
`AGENTS.md`.

GitLab Self-Managed and GitLab Dedicated administrators can turn the CLI off.

## Define reusable custom flows

Since 19.2, custom flows are generally available as reusable YAML workflows.
Manage them from a project or the AI Catalog. They support:

- Multiple agents.
- Human approval or feedback checkpoints.
- Public or private visibility.
- Validated configuration.
- Service-account and composite-identity execution.
- Triggers from mentions, assignments, pipeline events, and merge request
  lifecycle events.

## Start foundational flows from Agentic Chat

Since 19.2, Agentic Chat can hand a request to the Developer, Code Review, or
Fix CI/CD Pipeline foundational flow. The user approves the handoff in chat
and can follow the run either there or under **AI** > **Sessions**.

## Automatically remediate vulnerable dependencies

Since 19.2, dependency scanning auto-remediation is available in beta on
GitLab.com, GitLab Self-Managed, and GitLab Dedicated. When enabled, it watches
projects and opens merge requests that update vulnerable dependencies to safe
patch or minor versions by default.

The credit-consuming Agentic Breaking Change Resolution option also permits
major upgrades. It can analyze a failed update pipeline, the dependency
changelog, and code usage; commit compatibility fixes to the same merge
request; and rerun the pipeline until it passes.

## Use the CI Expert Agent in production workflows

Since 19.2, the CI Expert Agent is generally available for creating,
debugging, and optimizing pipelines from repository context. When Orbit and
its beta Knowledge Graph are enabled, the agent can also use graph-based code
intelligence for more contextual recommendations.

## Get targeted fixes from the Fix CI/CD Pipeline Flow

Since 19.2, the Fix CI/CD Pipeline Flow classifies failures before taking
action. If the relevant files already appear in a merge request diff, it
returns fixes as code suggestions on that merge request.

The flow follows child-pipeline failures across the complete hierarchy,
accepts project-specific behavior from `AGENTS.md`, and collapses its reasoning
in merge request comments by default.
