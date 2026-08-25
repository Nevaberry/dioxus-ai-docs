# Networking, edge, APIs, and DNS

Use this reference for networking, edge, apis, and dns compatibility details. Entries are grouped by task and service, with their source batch shown inline.

## VPCs, endpoints, and network connectivity

### ACM interface endpoints

**Batch:** `2025-12`

EC2 constructs provide interface VPC endpoint services for ACM and ACM Private CA.

### AgentCore interface endpoints

**Batch:** `2025-10`

`InterfaceVpcEndpointAwsService` includes `BEDROCK_AGENTCORE` and `BEDROCK_AGENTCORE_GATEWAY`.

### BYOIP IPv6 for VpcV2

**Batch:** `2025-01`

`VpcV2` can use bring-your-own-IP IPv6 addressing.

### Cloud WAN core-network routes

**Batch:** `2025-11`

EC2 constructs support routes for Cloud WAN core networks.

### Cross-region VPC endpoints

**Batch:** `2025-08`

`AWS::EC2::VPCEndpoint` exposes the `ServiceRegion` property.

### Existing Cloud Map namespaces

**Batch:** `2026-08`

ECS cluster constructs can use existing Cloud Map namespaces.

### MediaConnect L2 constructs

**Batch:** `2026-07`

MediaConnect now has L2 construct support.

### Prefix lists as connection peers

**Batch:** `2025-06`

An EC2 `PrefixList` now implements `IPeer`, so it can be passed directly to connection and security-group rule APIs.

## Amazon CloudFront

### CloudFront certificate diagnostics

**Batch:** `2026-08`

CloudFront warns when `minimumProtocolVersion` is set without a certificate.

### CloudFront Functions JavaScript 2.0 default

**Batch:** `2026-03`

Under its feature flag, CloudFront Functions now default to the JavaScript 2.0 runtime.

### CloudFront gRPC

**Batch:** `2025-02`

CloudFront distributions can be configured for gRPC traffic.

### CloudFront host-header-only origin policy

**Batch:** `2026-07`

CloudFront exposes the `Managed-HostHeaderOnly` managed origin request policy.

### CloudFront HTTP-origin controls

**Batch:** `2025-09`

HTTP origins can select an IP-address type and configure a response-completion timeout.

### CloudFront origin-group selection

**Batch:** `2025-02`

L2 CloudFront distributions and origin groups support origin-group selection criteria.

### CloudFront VPC origins

**Batch:** `2025-02`

CloudFront distributions can use origins hosted inside a VPC.

### Feature-flagged HTTPS redirect distribution

**Batch:** `2025-12`

Under its feature flag, Route 53 patterns' `HttpsRedirect` uses CloudFront `Distribution` as its default distribution implementation.

### Lambda Function URL origin addressing

**Batch:** `2025-10`

CloudFront Lambda Function URL origins accept an `ipAddressType`.

### Versioned CloudFront origin reads

**Batch:** `2025-02`

CloudFront origins support a versioned-read access level.

## Amazon API Gateway

### Additional API Gateway configuration

**Batch:** `2025-11`

`SpecRestApi` accepts `binaryMediaTypes`, and API Gateway v2 `WebSocketStage` accepts `accessLogSettings`.

### API Gateway additional-items typing

**Batch:** `2025-06`

API Gateway `JsonSchema.additionalItems` accepts the JSON Schema-compatible `boolean | JsonSchema` type.

### API Gateway response streaming

**Batch:** `2025-11`

API Gateway constructs support response streaming with a configurable response transfer mode.

### API Gateway REST base properties

**Batch:** `2025-03`

`endpointConfiguration` is now defined on `RestApiBaseProps`.

### API Gateway TLS 1.3 domain policies

**Batch:** `2026-03`

API Gateway domain names support TLS 1.3 security policies.

### API Gateway v2 SQS integrations

**Batch:** `2025-02`

API Gateway v2 integration constructs support SQS.

### API Gateway v2 stage variables

**Batch:** `2025-07`

HTTP and WebSocket API stages support stage variables.

### Consolidated Lambda integration permissions

**Batch:** `2025-11`

REST and HTTP API Lambda integrations can opt to consolidate their Lambda permissions.

### Dual-stack API Gateway v2 APIs

**Batch:** `2025-04`

API Gateway v2 constructs support dual-stack HTTP and WebSocket APIs.

### Dual-stack API Gateway v2 domains

**Batch:** `2025-05`

API Gateway v2 domain names support dual-stack addressing.

### Dual-stack REST APIs

**Batch:** `2025-05`

API Gateway REST API constructs support dual-stack addressing.

### EventBridge PutEvents HTTP API integration

**Batch:** `2026-01`

API Gateway v2 integrations can invoke EventBridge `PutEvents`.

### HTTP API stage access logging

**Batch:** `2025-04`

API Gateway v2 `HttpStage` supports access logging.

### HTTP APIs as EventBridge targets

**Batch:** `2025-04`

EventBridge target constructs support API Gateway v2 `HttpApi`.

### Lambda-authorizer roles

**Batch:** `2026-04`

API Gateway v2 Lambda authorizers support an explicitly configured role.

### Private API resource policies

**Batch:** `2025-02`

API Gateway constructs support resource-policy configuration for private APIs.

### SpecRestApi deployment mode

**Batch:** `2025-04`

`SpecRestApi` accepts a `mode` property.

### Step Functions REST API JSONata paths

**Batch:** `2026-08`

`CallApiGatewayRestApiEndpoint` supports JSONata expressions for `api_path`.

### WebSocket API usage plans and API keys

**Batch:** `2025-08`

API Gateway v2 L2 constructs now support usage plans and API keys for `WebSocketApi`.

### WebSocket schema-validation opt-out

**Batch:** `2025-09`

WebSocket APIs accept `disableSchemaValidation` to bypass schema validation.

## Elastic Load Balancing

### Application Load Balancer JWT verification

**Batch:** `2026-04`

Elastic Load Balancing v2 constructs support JWT verification for Application Load Balancers.

### Feature-flagged NLB security groups

**Batch:** `2025-11`

Under its feature flag, Elastic Load Balancing v2 creates Network Load Balancer security-group settings by default.

### Load-balancer mTLS CA-name advertisement

**Batch:** `2025-02`

Elastic Load Balancing v2 supports `AdvertiseTrustStoreCaNames` for mutual TLS.

### Minimum load-balancer capacity

**Batch:** `2025-02`

Elastic Load Balancing v2 constructs support minimum Load Balancer Capacity Unit reservations.

### Multi-value headers for Lambda target groups

**Batch:** `2025-05`

Elastic Load Balancing v2 Lambda target groups support multi-value headers.

### Network Load Balancer subnet mappings

**Batch:** `2025-04`

Elastic Load Balancing v2 constructs support subnet mappings for Network Load Balancers.

### Target-group health attributes

**Batch:** `2025-09`

Elastic Load Balancing v2 target groups support health attributes.

## Route 53 and DNS

### Alias-record TTL diagnostics

**Batch:** `2025-06`

Route 53 `RecordSet` warns when a TTL is supplied together with an alias target.

### ARecord delete-existing deprecation

**Batch:** `2025-08`

The delete-existing field on `ARecord` is deprecated.

### Gateway endpoint addressing

**Batch:** `2026-08`

`GatewayVpcEndpoint` accepts `ipAddressType` and `dnsRecordIpType`.

### Restricted Route 53 delegation

**Batch:** `2025-11`

Route 53 `grantDelegation` can restrict the delegated zone names.

### Route 53 accelerated recovery

**Batch:** `2026-04`

Public hosted-zone constructs support accelerated recovery.

### Route 53 failover records

**Batch:** `2025-12`

Route 53 record-set constructs support failover routing policies.

### SVCB and HTTPS DNS records

**Batch:** `2025-09`

Route 53 provides resource-record classes for SVCB and HTTPS records.

### Token-safe Elastic Beanstalk aliases

**Batch:** `2025-05`

Elastic Beanstalk Route 53 targets accept `hostedZoneId` for tokenized endpoints, defaulting it from the stack region or `endpointUrl`.

## Cross-service networking

### Client VPN automatic reconnect

**Batch:** `2025-10`

EC2 Client VPN endpoint constructs support automatic VPN-session reconnect.

### EKS load-balancer controller versions

**Batch:** `2026-06`

`AlbControllerVersion` supports versions 2.8.3 through 3.2.2.

### MediaPackage v2 region and name handling

**Batch:** `2026-04`

MediaPackage v2 resources expose a region attribute and apply additional naming validation.

### Stronger IPeer method types

**Batch:** `2026-05`

EC2 `IPeer` methods now return specific interfaces instead of `any`, giving callers stricter API contracts.
