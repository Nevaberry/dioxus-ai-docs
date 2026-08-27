# Core Toolkit and Validation

Topic-organized compatibility guidance for AWS CDK.

## CLI, Bootstrap, and Import

### Bootstrap trust removal (`2025-01`)

`cdk bootstrap` accepts `--untrust`, providing a direct way to retract bootstrap trust.

### Public CLI plugin contract (`2025-01`)

A public CLI-plugin contract now defines the supported boundary between the CLI and plugins, and imports of internal CLI libraries are disallowed. Credential plugins may return `null` for expiration and may initially return empty credentials.

### Simplified resource import (`2025-01`)

The CLI supports CloudFormation simplified resource import, reducing the setup required for bringing existing resources under stack management.

### Toolkit version environment contract (`2025-03`)

The cloud-assembly API now declares `CDK_TOOLKIT_VERSION` as a supported environment variable.

## Construct Composition and Lifecycle

### CDK Mixins (`2026-03`)

CDK introduces Mixins as an extension mechanism, graduates `@aws-cdk/cfn-property-mixins` to stable, and provides helpers for converting between Aspects and Mixins. `PropertyMergeStrategy` can merge arbitrary CloudFormation property objects, and S3 and ECS service mixins now ship in `aws-cdk-lib`.

### Deferred values with source traces (`2026-04`)

Core provides a `Box` API for deferred values that preserves accurate stack traces.

### Property injection across L2 constructs (`2025-05`)

Property injectors can target all L2 constructors.

### Property merge strategies (`2026-05`)

`PropertyMergeStrategy` now supports array merge strategies, and the built-in strategies are compatible with deferred `Box` values.

### Scoped removal policies (`2025-03`)

Core exposes `RemovalPolicies.of(scope)` as the scope-oriented entry point for applying removal policies.

### Suppressible informational annotations (`2025-07`)

Core annotations provide `addInfoV2` for informational messages that consumers can suppress.

## Feature Flags and Context

### Additional context cache keys (`2025-06`)

CDK context values can include an additional cache key, allowing otherwise identical lookups to occupy distinct cache entries.

### Feature flags in cloud assemblies (`2025-07`)

Cloud assemblies report feature-flag configuration and feature-flag information for downstream consumers.

## General Guidance

### Gitignore negation in subdirectories (`2025-09`)

Negated gitignore patterns inside subdirectories now re-include matching files.

## Synthesis and Assemblies

### Cross-region stack outputs (`2026-05`)

Core adds `Fn::GetStackOutput` for cross-region references. Cross-region references also avoid the earlier “exports cannot be updated” failure.

### Git source metadata in templates (`2026-07`)

Synthesized CloudFormation templates can now carry Git source metadata.

### Nested-stack indentation suppression (`2026-02`)

Nested stacks can suppress indentation in their synthesized templates.

### Weak cross-stack references (`2026-05`)

Core supports weak cross-stack references both within the same environment and across environments.

### Weak-reference guidance and list attributes (`2026-06`)

Core now recommends weak references when reference strength has not been chosen. Weak cross-stack references also work with list-valued attributes instead of failing.

## Validation and Errors

### App validation plugins (`2026-04`)

`Validations` is now the entry point for adding validation plugins to CDK apps and supports `addWarning`, `addError`, and `acknowledge`. Policy-validation interfaces have also graduated from `policyValidationBeta1` to `policyValidation`.

### Boolean context validation (`2026-06`)

Core validation correctly handles the string `"false"` when a boolean context value is expected.

### CloudFormation include with AWS::NoValue (`2025-09`)

CloudFormation include accepts `AWS::NoValue` for non-string properties without a type-validation error.

### Comprehensive built-in template validation (`2026-07`)

Core now validates templates against a comprehensive default rule set. Set `CDK_VALIDATION=false` to disable built-in template validation for a CDK invocation.

```sh
CDK_VALIDATION=false cdk synth
```

### Error codes (`2026-03`)

CDK errors and error annotations now carry error codes, allowing callers to classify failures without parsing messages.

### External construct-error traces (`2026-06`)

`ConstructError` can carry external traces, and available external stack traces are appended to cloud-assembly metadata for better source diagnostics.

### Self-contained validation reports (`2026-07`)

Validation reports are now self-contained, and Cloud Assembly relative-path handling has been corrected.

### Typed validation and error contracts (`2025-01, 2025-04, 2025-06`)

**2025-01:** Construct validation in API Gateway v2 and its authorizers, ELBv2, Lambda, RDS, Route 53, S3, SNS, SQS, SSM, and Synthetics now throws `ValidationError` instead of untyped errors. The CLI also emits typed errors, allowing callers to distinguish error classes without parsing messages.

**2025-04:** Kinesis, Cognito Identity Pools, FSx, and SES now throw typed validation errors instead of untyped errors.

**2025-06:** Custom Resources, IAM, Region Info, Secrets Manager, Service Catalog, and additional core paths now throw typed validation errors; Region Info also exports its error types from `region-info/lib/fact`.

### Validation report controls (`2026-05`)

Validation reports are now always written to the cloud assembly and include construct annotations. The `failSynthOnValidationErrors` context key can suppress validation-error console output and the exit code, and plugin violations can also be suppressed.

### Validation report schema (`2026-06`)

`validation-report.json` uses a new schema and includes suppressed violations, so report consumers must account for violations that did not fail synthesis.

### Validation-plugin context and outputs (`2026-06`)

`IPolicyValidationContext` now exposes `scope`, and validation plugins can create files in the cloud assembly.

### WebSocket schema-validation opt-out (`2025-09`)

WebSocket APIs accept `disableSchemaValidation` to bypass schema validation.
