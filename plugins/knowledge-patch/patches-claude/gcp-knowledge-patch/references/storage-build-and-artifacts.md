# Storage, Build, and Artifacts

Use this reference for Cloud Storage event transfers, Artifact Registry and public-image delivery, direct source artifacts, builders, and continuous deployment.

Availability labels and version gates are part of each item. Keep Preview behavior gated, and apply the latest lifecycle entry when an item has several dated updates.

## Artifact and image delivery

### Artifact Registry repositories for Cloud Run functions

*2025-02*

In Preview, a Cloud Run function deployment can specify the Artifact Registry image repository in which its container is stored.

### Public GitHub Container Registry images on Cloud Run

*2026-07-2*

Cloud Run can import public container images from GitHub Container Registry at GA.

## Source builds and continuous deployment

### Developer Connect continuous deployment

*2025-12*

In Preview, the Cloud Run console can use Developer Connect to configure continuous deployments from GitHub, GitLab, and Bitbucket repositories.

### Direct Cloud Run source artifacts

*2025-11*

Preview deployments can send source artifacts directly to Cloud Run and bypass Cloud Build.

### GPU source-build machine default

*2025-08*

In Preview, GPU-enabled Cloud Run services and functions deployed from source with `gcloud beta run` default their Cloud Build step to the `e2-highcpu-8` machine type.

## Cloud Storage transfers

### Event-driven Cloud Storage transfers

*2025-05*

GA event-driven transfers from Cloud Storage to BigQuery can start automatically when objects are added or modified in a bucket.
