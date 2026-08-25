# Terraform Stacks and HCP Terraform

## Components and deployments

Stacks compose modules in `*.tfcomponent.hcl` and repeat the composition with
different inputs in `*.tfdeploy.hcl`. Components in one Stack share a
lifecycle; each deployment has isolated state and can approve or defer a Stack
version independently (`terraform-stacks-and-hcp`).

```hcl
# stack.tfcomponent.hcl
component "cluster" {
  source    = "./eks"
  inputs    = { aws_region = var.aws_region }
  providers = { aws = provider.aws.this }
}

# deployments.tfdeploy.hcl
deployment "west" {
  inputs = { aws_region = "us-west-1" }
}
```

Terraform 1.13 exposes installed Stacks-plugin operations through
`terraform stacks`; discover the actual subcommands with
`terraform stacks -help` (`terraform-1.13.0`). Terraform 1.15 adds Stacks
input-variable validation (`terraform-1.15.0`).

## Deployment groups and approval

Generally available deployment groups replace public-beta orchestration rules.
HCP Terraform creates a group for deployments without a manual assignment.
Default groups are available on current plans; custom groups and auto-approval
checks require Premium (`terraform-stacks-and-hcp`).

```hcl
deployment "canary" {
  deployment_group = deployment_group.canary
}

deployment_group "canary" {
  auto_approve_checks = [deployment_auto_approve.no_deletes]
}

deployment_auto_approve "no_deletes" {
  check {
    condition = context.plan.changes.remove == 0
    reason    = "Plan removes ${context.plan.changes.remove} resources."
  }
}
```

## Partial plans and links

When unknown values prevent downstream planning, Stacks can return a partial
plan and defer the remaining changes. This supports staged work such as
creating a cluster before planning its dependents. An unapplied deployment
does not prevent planning elsewhere in the Stack (`terraform-stacks-and-hcp`).

Linked Stacks declare dependencies, pass data across boundaries, and trigger
downstream updates. A Stack may link to at most 20 upstream Stacks and expose
values to at most 25 downstream Stacks (`terraform-stacks-and-hcp`).

## Availability and limits

Production Stacks with backward-compatible APIs are available on current
resources-under-management plans, not legacy HCP Terraform team plans. Limits
are (`terraform-stacks-and-hcp`):

- 20 deployments per Stack.
- One deployment per deployment group.
- 100 components per Stack.
- 10,000 resources per Stack.

Terraform 1.14.2 adds component-registry source resolution. In Stacks,
`path.module` and `path.root` return documented relative paths starting in
1.14.3; use 1.14.5 or later when `terraform stacks validate` resolves relative
module paths (`terraform-1.14.0`).

## Private execution and source control

Stack deployments can run on self-hosted agents behind private networks and
firewalls, and agent pools can be scoped to individual Stacks. VCS connectivity
supports GitHub, GitLab, Azure DevOps Services, and Bitbucket, with IP
allowlists for trusted HCP Terraform addresses
(`terraform-stacks-and-hcp`).

HCP Terraform Premium and Terraform Enterprise can run module tests on
self-hosted agents, giving tests the same access to private services and policy
controls as plan and apply (`terraform-stacks-and-hcp`).

## Registry publishing

Private registries can publish reusable, versioned Stack component
configuration whose outputs feed other component inputs. The artifact contains
component configuration only, not deployment configuration
(`terraform-stacks-and-hcp`).

HCP Terraform and Terraform Enterprise can publish a module from a selected
directory in a VCS repository, and publishing can choose its module name and
target provider. One-module-per-repository naming is no longer required
(`terraform-stacks-and-hcp`).

## Workspace migration

Terraform Migrate 2.0 provides a public-beta workflow that extracts workspace
configuration, generates Stack configuration, transfers state into a
deployment, and creates and initializes the Stack. Use dry runs to validate
the generated result without changing the source workspace
(`terraform-stacks-and-hcp`).

Terraform can address `cloud` workspaces by HCP resource ID starting in 1.9.5
(`terraform-1.9.0`).

## Governance and integrations

- The Terraform MCP server can authenticate to HCP Terraform or Terraform
  Enterprise, use public and private registry context for recommendations, and
  create, run, or update account workspaces from an automation client
  (`terraform-stacks-and-hcp`).
- The Cloudability Governance run task adds cost estimates, recommendations,
  quota violations, and financial guardrails to run details regardless of
  whether a run starts in the UI, CLI, or VCS
  (`terraform-stacks-and-hcp`).
- A registry Sentinel policy set supplies pre-written AWS controls for NIST SP
  800-53 Revision 5 (`terraform-stacks-and-hcp`).

## Artifact encryption and usage reporting

Hold Your Own Key lets an organization control keys that encrypt sensitive
state and plan artifacts before upload to HCP Terraform
(`terraform-stacks-and-hcp`).

The HCP Terraform Usage view reports `Billable Stacks resources` separately.
`Billable managed resources` is the combined total across Stacks and
workspaces (`terraform-stacks-and-hcp`).
