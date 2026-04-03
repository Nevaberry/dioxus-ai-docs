# Terraform Actions

Introduced in Terraform 1.14 (preview).

## Overview

Terraform Actions are day 2 operations defined by providers. They codify operational tasks alongside infrastructure definitions, bridging the gap between provisioning and ongoing operations.

## What Actions Enable

Actions can be triggered:
- **Before/after resource CRUD** — automatically as part of plan/apply
- **Ad hoc via CLI** — on-demand operational tasks

## Use Cases

- Lambda function invocations after deployment
- Cache invalidations after CDN config changes
- Ansible playbook execution after VM provisioning
- Database migrations after schema resource updates
- Certificate rotation on demand

## Key Points

- Actions are **provider-defined** — the provider declares what actions are available for each resource type
- This is a **preview feature** in TF 1.14 — the API may change
- Actions bring "day 2 operations" into the Terraform lifecycle instead of requiring external scripts or CI/CD steps
