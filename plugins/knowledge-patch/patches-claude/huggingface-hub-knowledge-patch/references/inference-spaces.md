# Inference, Endpoints, and Spaces

## Routed inference

### Do not confuse provider routing with a dedicated deployment

`InferenceClient(..., provider="auto")` selects an available provider for a
supported model and task under current routing rules. Model-page serverless
availability and a dedicated Inference Endpoint are separate capabilities.

The shared client API does not promise that routes have the same processor,
region, isolation, scaling, billing, or optional chat features. Select a named
provider when those constraints matter, or explicitly use the URL of a
deployed endpoint.

```python
from huggingface_hub import InferenceClient

client = InferenceClient("org/model", provider="auto", token=token)
```

### Match credentials to the route

Hub-routed inference can use a Hugging Face token carrying the required
inference permissions and billing association. A direct partner-provider
route uses that provider's key according to the route documentation. Never
send a partner credential to an arbitrary model repository URL.

### Use newly supported DeepInfra tasks

The DeepInfra provider supports text-to-speech and feature-extraction through
the Hub inference provider integration (since `1.28.0`).

## Dedicated Inference Endpoint lifecycle

### Poll create and update operations

Creating or updating an Inference Endpoint is asynchronous. Poll the returned
remote state, handle terminal failure, and send traffic only after the state
indicates readiness.

`scale_to_zero` keeps the endpoint configuration and allows a later request to
cold-start serving. `pause` requires an explicit resume. Configure endpoint
exposure independently from whether the source model repository is private.

### Discover deployable hardware combinations

`hf endpoints hardware` lists mutually valid vendor, region, accelerator,
instance-type, and instance-size combinations (since `1.28.0`). Results
include hourly price, namespace quota, and availability. The default view
shows hardware the namespace can deploy immediately, and filters narrow it.

```console
hf endpoints hardware --vendor aws --region eu-west-1
```

The SDK returns the flattened hardware data as `InferenceEndpointHardware`
objects from `list_inference_endpoints_hardware()`.

## Endpoint engine images and parallelism

### Pass managed-engine image payloads

Inference Endpoint `custom_image` payloads can be keyed by an engine such as
`vLLM`, `sGLang`, `tgi`, `tei`, `llamacpp`, or `hfServe` (since `1.28.0`). Put
engine-specific tuning next to the container fields in that payload.

A dictionary without a top-level `url` is forwarded unchanged. This permits
new API-managed engines without requiring a client upgrade.
`update_inference_endpoint` accepts the same payload shapes as endpoint
creation.

Stop reading the undocumented
`huggingface_hub.constants.INFERENCE_ENDPOINT_IMAGE_KEYS`; that constant is
removed.

### Configure multi-accelerator parallelism

The `hf endpoints deploy` and `hf endpoints update` commands accept `--engine`,
`--tensor-parallel-size`, and `--data-parallel-size` (since `1.28.0`). The
update command also accepts `--custom-image`, `--health-route`, and `--port`.

Set parallelism explicitly for vLLM or SGLang on a multi-accelerator instance.
Those engines default to one accelerator, and the API rejects the resulting
mismatch.

```console
hf endpoints deploy ENDPOINT_NAME --repo ORG/MODEL \
  --framework custom --accelerator gpu --instance-size x8 \
  --instance-type INSTANCE_TYPE --region REGION --vendor VENDOR \
  --engine vllm --custom-image IMAGE \
  --tensor-parallel-size 8

hf endpoints update ENDPOINT_NAME \
  --tensor-parallel-size 4 --data-parallel-size 2
```

## Space configuration

### Separate recommendations from allocated resources

README `suggested_hardware` and `suggested_storage` fields recommend choices
to users duplicating or configuring a Space. They do not allocate runtime
hardware or persistent storage; configure those separately in runtime
settings.

`preload_from_hub` can stage narrowly selected, revision-pinned Hub files at
build or startup. It does not replace dependency declarations. Custom HTTP
headers are restricted to the documented allowlist.

### Put durable state outside the ordinary filesystem

A Space's ordinary filesystem is ephemeral across restarts and rebuilds.
Store durable state on separately provisioned persistent storage at its
documented mount, or in an external service.

A sleeping Space wakes on access. A paused Space requires explicit restart or
resume, and restarting does not guarantee preservation of ephemeral files.

### Keep runtime secrets and OAuth authority distinct

Space variables are visible to users with settings access. Secrets become
write-only through the settings UI or API after creation. Both are normally
injected into the runtime as environment variables.

README `hf_oauth` configuration can provision OAuth callback and client
settings plus requested scopes for user login. It does not automatically give
the Space's server process access to private repositories; configure that
server-side authority separately.
