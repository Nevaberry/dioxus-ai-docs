# Terraform Stacks

GA in HCP Terraform, September 2025.

## Overview

Terraform Stacks provide a component-based architecture for deploying infrastructure across multiple environments. Instead of duplicating module calls or using workspaces, you define components once and deploy them with different inputs.

## File Types

Stacks introduce two new file types:

### Component Config (`.tfcomponent.hcl`)

Defines the infrastructure components and their dependencies:

```hcl
component "networking" {
  source = "./modules/networking"
  inputs = {
    region = var.region
    cidr   = var.cidr
  }
}

component "cluster" {
  source = "./modules/k8s"
  inputs = {
    vpc_id = component.networking.vpc_id
  }
}
```

Components reference each other via `component.<name>.<output>`, creating an implicit dependency graph.

### Deployment Config (`.tfdeploy.hcl`)

Defines the environments/deployments with their specific inputs:

```hcl
deployment "us-east" {
  inputs = {
    region = "us-east-1"
    cidr   = "10.0.0.0/16"
  }
}

deployment "eu-west" {
  inputs = {
    region = "eu-west-1"
    cidr   = "10.1.0.0/16"
  }
}
```

## CLI

Stacks are managed via `terraform stacks` subcommands.

## Limits

- Maximum 20 deployments per stack
- Maximum 100 components per stack
- Maximum 10,000 resources per stack

## Requirements

- **Requires HCP Terraform** — Stacks are not available in open-source Terraform or OpenTofu
- Uses the HCP Terraform orchestration layer for deployment coordination
