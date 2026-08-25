# Terraform Stacks and HCP Terraform

## Stack composition and deployments (`terraform-stacks-and-hcp`)

Stacks compose modules in `*.tfcomponent.hcl` and repeat that composition with different inputs through `*.tfdeploy.hcl`. Components in one Stack share a lifecycle, while each deployment has isolated state and independently approves or defers a new Stack version.

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

Terraform 1.13 exposes operations from the installed Stacks plugin under `terraform stacks`; discover plugin-specific subcommands with `terraform stacks -help` (`terraform-1.13.0`). Terraform 1.15 validates Stack input variables (`terraform-1.15.0`).

## Deployment groups and approval

Generally available deployment groups replace public-beta orchestration rules. HCP Terraform creates a group for deployments without an explicit assignment. Default groups are available on current plans; custom groups and auto-approval checks require Premium.

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

## Deferred and linked deployments

When unknown values prevent downstream planning, Stacks can return a partial plan and defer the remaining objects. This supports staged infrastructure such as creating a cluster before planning Kubernetes resources. An unapplied deployment does not block planning in other deployments.

Linked Stacks connect separately managed Stacks, pass data across the boundary, and trigger downstream updates after upstream change. One Stack can link to at most 20 upstream Stacks and expose values to at most 25 downstream Stacks.

## Availability and limits

Production Stacks with backward-compatible APIs are available on current resources-under-management plans, but not legacy HCP Terraform team plans. Limits are:

- 20 deployments per Stack.
- One deployment per deployment group.
- 100 components per Stack.
- 10,000 resources per Stack.

## Private execution and VCS

Stack deployments can run on self-hosted agents behind private networks or firewalls; agent pools can be scoped to particular Stacks. VCS integration supports GitHub, GitLab, Azure DevOps Services, and Bitbucket. IP allowlists can restrict access to trusted HCP Terraform addresses.

HCP Terraform Premium and Terraform Enterprise can run module tests on self-hosted agents, allowing test access to private services and policy-controlled environments.

## Registry behavior

Private registries can publish reusable, versioned Stack component configurations. Component outputs can feed other component inputs, but the artifact contains only component configuration, never deployment-specific configuration.

HCP Terraform and Terraform Enterprise private registries can publish a module from a selected directory within a VCS repository. Publishers can choose the module name and target provider instead of following the earlier one-module-per-repository naming requirement.

Terraform 1.14.2 adds component-registry source resolution for Stacks (`terraform-1.14.0`). In Stacks, `path.module` and `path.root` return documented relative paths starting in 1.14.3; use 1.14.5 or later when `terraform stacks validate` must resolve relative module paths.

## Workspace migration and compatibility

Terraform 1.9.5 cloud blocks can address HCP workspaces by HCP resource ID (`terraform-1.9.0`).

Terraform Migrate 2.0 has a public-beta workflow that extracts workspace configuration, generates Stack configuration, transfers state into a deployment, and creates and initializes the Stack. Use dry runs to validate output without changing the source workspace.

## HCP-integrated tooling

The Terraform MCP server can authenticate to HCP Terraform or Terraform Enterprise, use private- and public-registry context for module recommendations, and create, run, or update account workspaces.

The Cloudability Governance run task adds cost estimates, recommendations, quota violations, and financial guardrails to HCP run details regardless of whether runs originate in the UI, CLI, or VCS.

## Encryption and compliance

The generally available Hold Your Own Key feature lets an organization own the keys protecting sensitive Terraform artifacts; state and plan artifacts are encrypted before upload to HCP Terraform.

A registry Sentinel policy set provides prewritten AWS controls for NIST SP 800-53 Revision 5.

Terraform 1.15.9 mitigates a Unicode-normalization issue that could upload `.terraformignore`-excluded files during HCP Terraform or Terraform Enterprise runs. Upgrade when ignore rules protect files that must stay local (`terraform-1.15.9`).

## Usage reporting

HCP Terraform's Usage view reports `Billable Stacks resources` separately. `Billable managed resources` is the combined total across Stacks and workspaces.
