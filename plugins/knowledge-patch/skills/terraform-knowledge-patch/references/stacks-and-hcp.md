# Terraform Stacks and HCP Terraform

Stack configuration and orchestration, service limits, execution, migration, registry workflows, governance, and billing visibility.

## Stack configuration and orchestration

### Deployment groups and conditional auto-approval

*Current service behavior — batch `terraform-stacks-and-hcp`.*

Deployment groups replace the beta orchestration-rules model and attach shared approval policy to deployments; unassigned deployments receive an automatically created default group. Custom groups and auto-approve checks require HCP Terraform Premium, while default groups are available on all current plans.

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

### Linked Stacks

*Current service behavior — batch `terraform-stacks-and-hcp`.*

Linked Stacks express dependencies between separately managed foundational and application Stacks, pass data across their boundary, and trigger downstream updates when an upstream change is detected. A Stack can link to at most 20 upstream Stacks and expose values to at most 25 downstream Stacks.

### Partial plans through deferred changes

*Current service behavior — batch `terraform-stacks-and-hcp`.*

Stacks can produce a partial plan instead of failing when downstream objects depend on values that remain unknown, then defer the unplannable changes to a later operation. This supports layered workloads such as creating a Kubernetes cluster before planning resources that require its endpoint, and an unapplied deployment does not prevent later Stack versions from being planned for it.

### Registry sources for Stacks components

*Terraform 1.14.0 — batch `terraform-1.14.0`.*

Starting in 1.14.2, Terraform Stacks can resolve component sources through a component registry.

### Repeated deployments have isolated state

*Current service behavior — batch `terraform-stacks-and-hcp`.*

Define Stack instances with `deployment` blocks in a separate `*.tfdeploy.hcl` configuration layer. Deployments reuse the same components with different inputs, but each has an isolated state and can independently approve or defer a plan produced by a new Stack version.

```hcl
deployment "west-coast" {
  inputs = {
    aws_region     = "us-west-1"
    instance_count = 2
  }
}

deployment "east-coast" {
  inputs = {
    aws_region     = "us-east-1"
    instance_count = 1
  }
}
```

### Stack component configuration

*Current service behavior — batch `terraform-stacks-and-hcp`.*

Stacks add a configuration layer over existing Terraform modules and replace the traditional root-module organization with components that share a lifecycle. Define each component in a `*.tfcomponent.hcl` file with its module source, inputs, and explicit provider mappings.

```hcl
component "cluster" {
  source = "./eks"
  inputs = {
    aws_region    = var.aws_region
    instance_type = "t2.medium"
  }
  providers = {
    aws = provider.aws.this
  }
}
```

### Stack operations through the CLI

*Terraform 1.13.0 — batch `terraform-1.13.0`.*

The new `terraform stacks` command exposes operations supplied by the installed Stacks plugin. Its subcommands vary with the plugin implementation, so use `terraform stacks -help` to discover the available surface.

### Stacks GA compatibility and service limits

*Current service behavior — batch `terraform-stacks-and-hcp`.*

Public-beta Stack configurations require updates for the GA format; GA provides backward-compatible APIs for production and is available on current resources-under-management plans, but not legacy HCP Terraform team plans. A Stack is limited to 20 deployments, one deployment per deployment group, 100 components, and 10,000 resources.

## Execution, integration, and migration

### Expanded VCS connections for Stacks

*Current service behavior — batch `terraform-stacks-and-hcp`.*

Stacks can connect to GitHub, GitLab, Azure DevOps Services, and Bitbucket. VCS connections also honor IP allowlists, allowing access to be restricted to trusted HCP Terraform addresses.

### HCP-authenticated Terraform MCP server

*Current service behavior — batch `terraform-stacks-and-hcp`.*

The Terraform MCP server can authenticate to an HCP Terraform or Terraform Enterprise account. An AI client can then use private- and public-registry context for module recommendations and create, run, or update account workspaces without switching to a separate interface.

### Module tests on self-hosted agents

*Current service behavior — batch `terraform-stacks-and-hcp`.*

HCP Terraform Premium and Terraform Enterprise can execute Terraform module tests on self-hosted agents. Tests can therefore access the same private services and policy-controlled environment used for plan and apply rather than requiring a separate hosted test environment.

### Monorepo-aware private module publishing

*Current service behavior — batch `terraform-stacks-and-hcp`.*

The HCP Terraform and Terraform Enterprise private registries can publish a module by selecting both a VCS repository and a module directory within it. Publishing can also choose the module name and target provider instead of deriving them from the former one-module-per-repository naming convention.

### Self-hosted execution for Stacks

*Current service behavior — batch `terraform-stacks-and-hcp`.*

HCP Terraform can run Stack deployments through self-hosted agents behind private networks or firewalls, and an agent pool can be scoped to particular Stacks. This brings Stack plan and apply execution under the same private execution model as workspaces.

### Workspace-to-Stack migration

*Current service behavior — batch `terraform-stacks-and-hcp`.*

Terraform Migrate 2.0 adds a public-beta, CLI-driven workspace-to-Stack workflow that extracts workspace configuration, generates Stack configuration, transfers state into a deployment, and creates and initializes the Stack. It supports dry runs so the generated result can be validated without changing the source workspace.

## Governance, security, and usage

### Cloudability governance run task

*Current service behavior — batch `terraform-stacks-and-hcp`.*

The Cloudability Governance run task adds cost estimates, recommendations, quota violations, and financial guardrails to HCP Terraform run details. The same feedback appears whether a run begins in the UI, CLI, or through VCS.

### Hold Your Own Key artifact encryption

*Current service behavior — batch `terraform-stacks-and-hcp`.*

HCP Terraform's generally available Hold Your Own Key feature lets an organization own the encryption keys used for sensitive Terraform artifacts. State and plan artifacts are encrypted before upload to HCP Terraform, so plaintext secrets are not sent to the service.

### Pre-written AWS NIST policies

*Current service behavior — batch `terraform-stacks-and-hcp`.*

A pre-written Sentinel policy set is available for enforcing NIST SP 800-53 Revision 5 controls on AWS Terraform configurations. It can be adopted as a versioned registry policy set instead of implementing the control library from scratch.

### Stack resource-usage visibility

*Current service behavior — batch `terraform-stacks-and-hcp`.*

The HCP Terraform Usage view reports `Billable Stacks resources` separately and also reports `Billable managed resources`, which combines Stack and workspace resources. Operators can therefore reconcile Stack adoption with resources-under-management billing.

