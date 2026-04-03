# Cloud Run

## Worker Pools

New resource type for **non-request workloads** (background processing, queue consumers). Unlike services, worker pools don't listen for HTTP requests.

```bash
gcloud run worker-pools deploy my-worker \
  --image=us-docker.pkg.dev/my-project/repo/worker:latest \
  --region=us-central1
```

Supports GPU, VPC Direct, Cloud Storage volume mounts.

## Compose Deployment (GA)

Deploy services using a Docker Compose file:

```bash
gcloud run deploy --compose=docker-compose.yaml
```

## IAP Without Load Balancer (GA)

Configure Identity-Aware Proxy directly on Cloud Run services without needing a load balancer.
