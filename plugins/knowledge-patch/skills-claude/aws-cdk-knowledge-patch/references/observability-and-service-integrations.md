# Observability and Service Integrations

Topic-organized compatibility guidance for AWS CDK.

## Amazon SES

### SES configuration-set email validation (`2026-05`)

SES configuration sets support automatic email validation.

### SES custom-tracking HTTPS policy (`2025-05`)

SES constructs support an HTTPS policy for custom tracking domains.

## AppConfig

### AppConfig configuration-profile deletion protection (`2025-05`)

AppConfig configuration profiles now participate in deletion-protection checks.

### AppConfig deployment-tick extensions (`2025-01`)

AppConfig L2 extensions support the `atDeploymentTick` action point.

### AppConfig environment deletion protection (`2025-01`)

AppConfig environments can opt into deletion protection.

## CloudWatch Logs

### CloudWatch Logs deletion protection (`2026-01`)

CloudWatch Logs constructs support deletion-protection configuration.

### CloudWatch Logs field indexes (`2025-03`)

The Log Group L2 construct accepts `fieldIndexPolicies`.

### CloudWatch Logs transformers (`2025-07`)

CloudWatch Logs constructs support log transformers.

### Cross-account CloudWatch widgets (`2025-07`)

CloudWatch log-query and metric widgets accept an account ID for cross-account visibility.

### Infrequent Access logs in ADC regions (`2025-07`)

The CloudWatch Logs Infrequent Access log class is supported in ADC regions.

### Metric filters on transformed logs (`2025-10`)

CloudWatch Logs metric filters can opt to run against transformed logs.

### Metric-filter dimensions (`2025-06, 2025-07`)

Metrics exposed from CloudWatch Logs metric filters do not retain the filter's dimension map. The short-lived retention behavior introduced in 2025-06 was reverted in 2025-07.

### Multiple stats commands in log queries (`2025-07`)

CloudWatch Logs query strings can contain multiple `stats` commands.

### Regex JSON metric filters (`2025-02`)

CloudWatch Logs JSON metric filters support regular-expression patterns.

## CloudWatch Synthetics

### New Synthetics Python runtimes (`2025-05`)

The Synthetics runtime catalog includes Python canary runtimes 5.0 and 5.1.

### New Synthetics runtimes (`2025-01`)

The Synthetics runtime catalog now includes Node Playwright 1.0 and Python Selenium 4.1.

### New Synthetics runtimes (`2026-01`)

The Synthetics runtime catalog adds `syn-nodejs-3.0`, Playwright 4.0 and 5.0, and Puppeteer 12.0 and 13.0.

### New Synthetics runtimes (`2026-05`)

The Synthetics runtime catalog includes Playwright 5.1 and 6.0.

### Root-level Synthetics scripts (`2025-10`)

Synthetics canary assets may place script files at the archive root when using Puppeteer runtime version 11 or later.

### Safe canary updates (`2025-06`)

Synthetics constructs support safe canary updates.

### Synthetics browser selection (`2025-09`)

Canary constructs expose the browser type.

### Synthetics canary groups (`2026-04`)

Synthetics constructs support canary groups.

### Synthetics Node.js 3.1 (`2026-03`)

The Synthetics canary runtime catalog includes Node.js 3.1.

### Synthetics Playwright 2.0 (`2025-06`)

The Synthetics runtime catalog includes Playwright 2.0.

### Synthetics run retries (`2025-07`)

Synthetics canaries accept `maxRetries` to configure automatic retries of canary runs.

### Synthetics tag replication (`2025-07`)

Synthetics constructs support tag replication.

## Metrics, Alarms, and Dashboards

### CloudWatch alarm rules (`2026-08`)

Composite alarm rules support `AT_LEAST` expressions, and CloudWatch alarms support mute rules.

### CloudWatch anomaly-detection alarms (`2025-05`)

CloudWatch constructs support anomaly-detection alarms.

### CloudWatch metric identity and visibility (`2025-07`)

CloudWatch `Metric` exposes `id` and `visible` properties.

### CloudWatch pie-chart labels (`2025-09`)

CloudWatch pie charts can display labels.

### CloudWatch quoted metric-math strings (`2026-06`)

CloudWatch metric-math validation no longer treats quoted strings as unknown identifiers.

### Dashboard query languages (`2025-07`)

CloudWatch dashboard constructs expose the `queryLanguage` property.

### PromQL alarms (`2026-05`)

CloudWatch provides a PromQL Alarm L2 construct.

### Search expressions in graph widgets (`2025-07`)

CloudWatch dashboard graph widgets support search expressions.

## Other Integrations

### Amplify build compute types (`2025-10`)

Amplify constructs support configuring the build compute type.

### EMR instance-fleet priority allocation (`2026-05`)

EMR instance fleets support priority allocation.

### Expanded EMR create-cluster options (`2025-09`)

`EmrCreateClusterOptions` accepts `ebsRootVolumeIops`, `ebsRootVolumeThroughput`, and `managedScalingPolicy`.

### Fluentd asynchronous connections (`2025-04`)

`FluentdLogDriver` uses `async`, replacing the deprecated `asyncConnect` property.

### MediaConnect L2 constructs (`2026-07`)

MediaConnect now has L2 construct support.

### MediaPackage v2 region and name handling (`2026-04`)

MediaPackage v2 resources expose a region attribute and apply additional naming validation.

### Region Info additions (`2025-07`)

Region Info supports the `eusc-de` and `ap-southeast-6` regions.

### SageMaker serverless inference (`2025-11`)

SageMaker constructs support serverless inference endpoints.

### Typed Glue partition projection (`2026-02`)

Glue constructs support typed partition-projection configuration.
