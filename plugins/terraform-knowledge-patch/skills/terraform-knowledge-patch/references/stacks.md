# Stacks

## Stacks CLI (1.13)

`terraform stacks` command added. Stacks are an HCP Terraform feature for multi-environment deployments from a single config.

Two file types:
- `*.tfcomponent.hcl` — defines `component` blocks referencing modules
- `*.tfdeploy.hcl` — defines `deployment` blocks (one per environment/region)

```hcl
# network.tfcomponent.hcl
component "network" {
  source  = "hashicorp/network/aws"
  version = "1.0.0"
  inputs = {
    cidr = var.cidr
  }
}
```

```hcl
# prod.tfdeploy.hcl
deployment "us-east" {
  inputs = {
    cidr = "10.0.0.0/16"
  }
}
deployment "eu-west" {
  inputs = {
    cidr = "10.1.0.0/16"
  }
}
```

Limits: max 20 deployments, 100 components, 10,000 resources per stack. Requires HCP Terraform.
