# Artifact Registry (Container Registry Shutdown)

Container Registry was **shut down March 18, 2025**. All images must use Artifact Registry.

## Key Changes

- Domain: `pkg.dev` (e.g., `us-docker.pkg.dev/my-project/my-repo/image:tag`)
- `gcr.io` URLs now redirect to Artifact Registry if you set up gcr.io repositories
- Commands: `gcloud artifacts repositories create` / `gcloud artifacts docker images list` (not `gcloud container images`)
