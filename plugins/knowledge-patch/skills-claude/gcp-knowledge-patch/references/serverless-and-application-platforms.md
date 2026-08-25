# Serverless and Application Platforms

Use this reference for Cloud Run services, jobs, functions, worker pools, deployments, runtimes, networking, GPUs, scaling, probes, and service health.

Availability labels and version gates are part of each item. Keep Preview behavior gated, and apply the latest lifecycle entry when an item has several dated updates.

## Deployment, IAM, and integrations

### Cloud Run deployment IAM

*2025-01*

Creating or updating a Cloud Run resource now requires the acting user or service account to have explicit access to every referenced container image; for Artifact Registry, grant the deploying principal `roles/artifactregistry.reader` on the image project or repository. For source deployments, grant the Preview `roles/run.builder` role to the Compute Engine default service account that builds the service or function.

### Cloud Run integrations removal

*2025-02*

Cloud Run integrations are discontinued in the console and CLI, although already-deployed services that use them continue to work. Configure each connected Google Cloud product through its individual product experience instead.

### Compose deployments to Cloud Run

**2025-11:** In Preview, a Compose file can deploy services to Cloud Run.

**2026-03:** Deploying Cloud Run services from a Compose file is GA.

### Conditional Cloud Run invocation

*2025-06*

Cloud Run invocation IAM Conditions can use the request host and request path when defining access to a service.

## Runtimes, source builds, and buildpacks

### Cloud Run .NET 10

*2026-01*

The .NET 10 runtime is available on Cloud Run in Preview.

### Cloud Run `pyproject.toml` support

*2026-01*

Cloud Run and Cloud Run functions source deployments can manage dependencies with `pyproject.toml` at GA across all supported Python versions.

### Cloud Run Go and Node.js runtimes

*2025-07*

Go 1.24 is GA. Go 1.25 using its release candidates and Node.js 24 are available in Preview.

### Cloud Run Go runtime lifecycle

*2026-07-2*

Starting with Go runtime 1.26, Cloud Run runtime support dates align more closely with the Go community release cycle.

### Cloud Run Java 25

**2025-10:** The Java 25 runtime is available for Cloud Run in Preview.

**2025-12:** The Java 25 runtime is GA on Cloud Run.

### Cloud Run Node.js 24 GA

*2025-11*

The Node.js 24 runtime is GA on Cloud Run.

### Cloud Run OS-only runtime

*2025-12*

The Preview `osonly24` runtime supports deploying Go applications from source and binaries such as Dart and Go.

### Cloud Run PHP and Ruby runtimes

*2025-06*

Cloud Run support for the PHP 8.4 and Ruby 3.4 runtimes is GA.

### Cloud Run Python 3.13

*2025-04*

The Python 3.13 runtime is available for Cloud Run in Preview.

### Cloud Run Python 3.14 package installer

*2025-11*

The Preview Python 3.14 runtime defaults the Python buildpack to `uv` for dependencies in `requirements.txt`; this also applies to later Python versions. Set the following environment variable to retain `pip`:

```sh
GOOGLE_PYTHON_PACKAGE_MANAGER=pip
```

### Cloud Run Python framework entrypoints

*2025-08*

The Python buildpack supports source deployments for frameworks including FastAPI, Gradio, and Streamlit. With Python 3.13 or later, it derives the default entrypoint from the web-server or framework configuration in `requirements.txt`.

### Cloud Run Python runtime and source builds

*2025-12*

The Python 3.14 runtime is GA, and `pyproject.toml` dependency management is GA for Python 3.13 and later while remaining in Preview for Python 3.12 and earlier. In Preview, the Python buildpack can also detect a default entrypoint for Agent Development Kit applications.

### Cloud Run Ruby 4.0 and Go 1.26 runtimes

*2026-03*

The Ruby 4.0 and Go 1.26 runtimes are GA on Cloud Run.

### Cloud Run runtime and builder updates

*2026-02*

PHP 8.5, `osonly24`, .NET 10, and Ubuntu 24 LTS source deployments with `gcr.io/buildpacks/builder:google-24` are GA. Go 1.26 is available in Preview.

### Cloud Run runtime updates

*2025-05*

Ruby 3.4 and PHP 8.4 runtimes are available in Preview, while the previously Preview Python 3.13 runtime is GA.

### Java Cloud Run function execution IDs

*2025-05*

For Java Cloud Run functions using Functions Framework 1.4.0 or later, `java.util.logging.Logger` can add a unique execution ID to log output.

### Ubuntu 24 Cloud Run source builder

*2025-11*

Preview source deployments can use the Ubuntu 24 LTS builder `gcr.io/buildpacks/builder:google-24`.

## Networking, ingress, egress, and regions

### Cloud Run console region default

*2025-05*

The console region selector for a new Cloud Run service or job now defaults to `europe-west1`.

### Cloud Run GPU region

*2025-06*

Cloud Run GPUs are available in `us-east4`.

### Direct VPC egress for Cloud Run jobs

*2025-04*

Direct VPC egress support for Cloud Run jobs is GA.

### Direct VPC ingress for Cloud Run worker pools

*2026-02*

A Cloud Run worker pool can use Direct VPC ingress so every worker instance receives a private address on the selected network and subnet. Workers can retrieve their private IP addresses from the metadata server for internal VPC communication.

### External IPv6 from Cloud Run

*2025-11*

GA dual-stack subnets let Cloud Run resources use Direct VPC egress for IPv4 and internal IPv6 traffic while sending external IPv6 traffic to the public internet.

### Internal IPv6 from Cloud Run

*2025-01*

In Preview, Cloud Run services and jobs can use dual-stack subnets with Direct VPC egress to send both IPv4 and internal IPv6 traffic into a VPC network.

### Multi-region Cloud Run service health

*2025-11*

Preview Cloud Run service health provides automated failover and failback for internal traffic to highly available multi-region services.

### Multi-region Cloud Run services

*2025-09*

A multi-region Cloud Run service can be deployed and configured at GA with one `gcloud` command or from YAML or Terraform.

### VPC Flow Logs for Cloud Run

*2025-10*

In Preview, VPC Flow Logs can observe Cloud Run traffic that uses Direct VPC egress.

## Jobs, worker pools, and execution models

### Cloud Run job sidecars

*2025-04*

Running multiple containers as sidecars in a Cloud Run job is GA.

### Cloud Run sandboxes

*2026-07*

Preview Cloud Run sandboxes provide isolated service environments for executing untrusted code, including code generated by agents.

### Cloud Run worker pools

*2025-06*

Preview Cloud Run worker pools are specifically designed for non-request workloads.

### GPUs in Cloud Run jobs

*2025-06*

Cloud Run jobs can use GPUs in Preview.

### GPUs in Cloud Run worker pools

*2025-09*

Preview Cloud Run worker pools can be configured with GPUs.

### Seven-day Cloud Run job tasks

*2025-11*

Cloud Run job tasks can have a timeout of up to 168 hours at GA.

### Sidecars in Cloud Run jobs

*2025-01*

Cloud Run jobs can run multiple containers as sidecars in Preview.

## GPUs, storage, and compute

### Cloud Run ephemeral disk

*2026-04*

Preview ephemeral disk can be mounted by a Cloud Run service, job, or worker pool and persists only for the lifetime of that instance.

### Cloud Run GPU zonal redundancy

*2025-03*

In Preview, new GPU-backed services default to zonal redundancy, but a service can explicitly use GPUs with or without zonal redundancy and request quota for either configuration.

### Cloud Run GPUs

*2025-04*

GPU support for Cloud Run services is GA.

### Cloud Run L4 GPU driver

*2026-07-2*

NVIDIA L4 GPUs on Cloud Run services, jobs, and worker pools can use driver version `580.x.x`.

### Cloud Run memory metric semantics

*2025-05*

For most services on the second-generation execution environment, Cloud Monitoring memory-usage metrics no longer include operating-system page-cache memory and therefore report lower utilization.

### Cloud Run volume-mount options

*2025-09*

At GA, Cloud Storage volume mounts for Cloud Run services, jobs, and worker pools accept mount options.

### RTX PRO 6000 GPUs on Cloud Run

*2026-02*

In Preview, Cloud Run services, jobs, and worker pools can use NVIDIA RTX PRO 6000 Blackwell GPUs.

## Scaling, health, and observability

### Cloud Run readiness probes

*2025-11*

Cloud Run services support HTTP and gRPC readiness probes in Preview.

### Cloud Run scaling targets

*2026-04*

Preview scaling controls let a Cloud Run workload specify custom CPU or concurrency targets.

### Cloud Run service health and readiness probes reach GA

*2026-06*

GA Cloud Run service health provides automated failover and failback for internal and external traffic to highly available multi-region services, and Cloud Run services now have GA HTTP and gRPC readiness probes.

### External Cloud Run service health

*2026-02*

Preview Cloud Run service health can automate failover and failback of external traffic for a highly available multi-region service.

### Manual scaling for Cloud Run services

*2025-02*

Preview manual scaling lets a Cloud Run service use manual scaling in place of the built-in autoscaler.

### Service-level Cloud Run maximum instances

*2025-06*

In Preview, maximum-instance configuration can be applied at the Cloud Run service level.

## Services, functions, and platform behavior

### Cloud KMS Autokey for Cloud Run

*2025-04*

Cloud KMS with Autokey is GA for Cloud Run.

### Cloud Run `.env` files

*2025-08*

In Preview, services, jobs, and worker pools can set multiple environment variables from a `.env` file.

```dotenv
LOG_LEVEL=info
API_URL=https://api.example.com
```

### Cloud Run flexible CUD coverage

*2025-07*

Compute flexible committed use discounts now cover Cloud Billing account spend across Cloud Run services with request-based billing and Cloud Run functions. The improved spend-based CUD experience applies automatically to new users and users without an active spend-based CUD.

### Cloud Run function label propagation

*2025-05*

Labels set through `gcloud functions` or the Cloud Functions v2 API propagate to Cloud Run when the function is deployed there.

### Cloud Run functions and automatic base-image updates

*2025-02*

Deploying functions in Cloud Run and configuring automatic base-image updates for source-deployed services and functions are GA. Both CLI workflows require Google Cloud SDK 511.0.0 or later.

### Cloud Run remote MCP server

*2026-02*

The Preview Cloud Run remote MCP server lets agents and AI applications deploy workloads with Cloud Run.

### Direct Identity-Aware Proxy for Cloud Run

*2026-03*

Configuring IAP directly on a Cloud Run service, without a load balancer, is GA.

### Disabling the Cloud Run `run.app` URL

*2025-07*

At GA, a service can disable its built-in `run.app` URL so traffic can enter only through explicitly configured ingress paths.

### Gemini Cloud Assist in Cloud Run

*2025-04*

Preview Gemini Cloud Assist can design, optimize, and troubleshoot Cloud Run applications from its chat panel.

### Identity-Aware Proxy for Cloud Run

*2025-04*

In Preview, IAP can secure a Cloud Run service across all ingress paths.
