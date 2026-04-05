---
name: gcp-knowledge-patch
description: "GCP changes since training cutoff — Gen AI SDK replaces Vertex AI SDK, Gemini 2.5/3.x models, Cloud Run worker pools, Artifact Registry migration, ADK. Load before working with GCP."
license: MIT
metadata:
  author: Nevaberry
  version: "latest"
---

# Google Cloud Platform Knowledge Patch

Claude's baseline knowledge covers GCP through ~2024. This skill provides changes from 2025 onwards: the Gen AI SDK replacing Vertex AI, new Gemini models, Cloud Run improvements, Container Registry shutdown, and the Agent Development Kit.

## Reference Index

- `references/gen-ai-sdk.md` — Google Gen AI SDK (replaces Vertex AI SDK): installation, client setup, migration patterns, API changes
- `references/gemini-models.md` — Current Gemini model lineup, image generation, embeddings
- `references/cloud-run.md` — Worker pools, Compose deployment, IAP without load balancer
- `references/artifact-registry.md` — Container Registry shutdown, migration to Artifact Registry
- `references/agent-development-kit.md` — ADK framework for multi-agent AI systems

## Quick Reference

### Gen AI SDK — Migration Summary

The `vertexai.generative_models` module is **deprecated** (removal after June 24, 2026). Use the Google Gen AI SDK.

| Language | Old package | New package |
|----------|------------|-------------|
| Python | `google-cloud-aiplatform` | `pip install google-genai` |
| Node.js | `@google-cloud/vertexai` | `npm install @google/genai` |
| Go | `cloud.google.com/go/vertexai/genai` | `go get google.golang.org/genai` |
| Java | `com.google.cloud:google-cloud-vertexai` | `com.google.genai:google-genai` |

```python
from google import genai
from google.genai.types import HttpOptions

client = genai.Client(http_options=HttpOptions(api_version="v1"))
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello",
)
print(response.text)
```

**Vertex AI env vars:**
```bash
export GOOGLE_CLOUD_PROJECT=my-project
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_VERTEXAI=True
```

**Node.js:**
```javascript
import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({
  vertexai: true,
  project: process.env.GOOGLE_CLOUD_PROJECT,
  location: process.env.GOOGLE_CLOUD_LOCATION,
});
const response = await ai.models.generateContent({
  model: 'gemini-2.5-flash',
  contents: 'Hello',
});
console.log(response.text);
```

**Go:**
```go
client, _ := genai.NewClient(ctx, genai.ClientConfig{
    HTTPOptions: genai.HTTPOptions{APIVersion: "v1"},
})
resp, _ := client.Models.GenerateContent(ctx,
    "gemini-2.5-flash",
    genai.Text("Hello"),
    nil,
)
fmt.Println(resp.Text())
```

**Vertex AI Express Mode** — use API key instead of ADC:
```python
client = genai.Client(vertexai=True, api_key="YOUR_API_KEY")
```

**Key API pattern changes:**
- Config via typed objects: `config=types.GenerateContentConfig(system_instruction=..., temperature=0.3)`
- Function calling — pass Python functions directly: `config=types.GenerateContentConfig(tools=[my_function])`
- Embeddings: `client.models.embed_content(model="gemini-embedding-001", contents="text", config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"))`
- Caching: `client.caches.create(model=..., config=CreateCachedContentConfig(contents=..., ttl="86400s"))`
- Chat: `chat = client.chats.create(model="gemini-2.5-flash", config=...)`

See `references/gen-ai-sdk.md` for full before/after migration examples.

### Gemini Models (March 2026)

| Model | ID | Status |
|-------|----|--------|
| Gemini 2.0 Flash | `gemini-2.0-flash` | GA (retires June 2026) |
| Gemini 2.5 Pro | `gemini-2.5-pro` | GA |
| Gemini 2.5 Flash | `gemini-2.5-flash` | GA |
| Gemini 2.5 Flash-Lite | `gemini-2.5-flash-lite` | GA |
| Gemini 3 Flash | `gemini-3-flash` | Preview |
| Gemini 3.1 Pro | `gemini-3.1-pro` | Preview |
| Gemini 3.1 Flash-Lite | `gemini-3.1-flash-lite-preview` | Preview |

- **Image generation**: Use `gemini-2.5-flash-image` or `gemini-3.1-flash-image` (preview). Imagen endpoints deprecated.
- **Embeddings**: Use `gemini-embedding-001` (replaces `text-embedding-005` series).

See `references/gemini-models.md` for details.

### Container Registry → Artifact Registry

Container Registry **shut down March 18, 2025**. All images must use Artifact Registry.

- Domain: `pkg.dev` (e.g., `us-docker.pkg.dev/my-project/my-repo/image:tag`)
- `gcr.io` URLs now redirect to Artifact Registry if you set up gcr.io repositories
- Commands: `gcloud artifacts repositories create` / `gcloud artifacts docker images list` (not `gcloud container images`)

### Cloud Run

**Worker pools** — new resource type for non-request workloads (background processing, queue consumers). Unlike services, worker pools don't listen for HTTP requests:

```bash
gcloud run worker-pools deploy my-worker \
  --image=us-docker.pkg.dev/my-project/repo/worker:latest \
  --region=us-central1
```

Supports GPU, VPC Direct, Cloud Storage volume mounts.

**Compose deployment (GA):**
```bash
gcloud run deploy --compose=docker-compose.yaml
```

**IAP without load balancer (GA):** Configure Identity-Aware Proxy directly on Cloud Run services.

See `references/cloud-run.md` for details.

### Agent Development Kit (ADK)

```bash
pip install google-adk     # Python
npm install @google/adk    # TypeScript
```

Cloud Run auto-detects ADK entrypoints for Python source deployments.

See `references/agent-development-kit.md` for details.
