# Kubernetes, OpenShift, and Snapshots

## Store Kubernetes snapshots in Google Cloud

Since 1.21.0, the Enterprise snapshot-agent sidecar for Consul on Kubernetes can send snapshots to Google Cloud Storage. Local storage, Amazon S3, and Azure Blob Storage remain available targets.

## Authenticate Azure snapshots without static credentials

Since 1.22.0, the Enterprise snapshot agent can authenticate to Azure Blob Storage with Azure Managed Service Identity. Prefer this route when the workload identity and storage authorization are available, avoiding static storage credentials in snapshot configuration.

## Enforce Pod Security Admission by namespace

Since 1.21.0, Consul can be deployed and configured under Kubernetes Pod Security Admission controls applied per namespace. Pod Security Admission replaces PodSecurityPolicy for minimum pod-security enforcement.

Test all Consul components against the intended namespace policy before switching the policy to enforcement.

## Select a supported OpenShift platform

Consul 1.21.0 supports OpenShift Container Platform 4.16, 4.17, and 4.18.

IPv6 behavior introduced later is not supported on OpenShift. Do not infer IPv6 support from VM or Kubernetes compatibility alone.

## Scale Enterprise API Gateways

Since 2.0.0, Enterprise API Gateways on Kubernetes can scale beyond the former eight-replica limit. Horizontal Pod Autoscaling can be enabled through annotations on the Gateway resource.

Size the autoscaler and gateway limits together so replica growth does not overwhelm upstream services.

## Migrate OpenShift gateway resources

Since 2.0.0, newer Kubernetes resource types in the `consul.hashicorp.com` API group support OpenShift 4.19 and later. Earlier Kubernetes Gateway API `v1alpha` resources are incompatible with those OpenShift releases.

Inventory existing gateway resources and migrate them to the new types during an OpenShift upgrade. Coordinate controller compatibility, resource conversion, and traffic cutover rather than treating the platform upgrade as an in-place API change.
