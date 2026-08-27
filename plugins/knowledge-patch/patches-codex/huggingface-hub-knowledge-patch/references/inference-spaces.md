# Inference, endpoints, and Spaces

## Routed providers are not dedicated deployments

`InferenceClient(..., provider="auto")` selects an available provider for a
supported model and task under current Hub routing rules. Model-page
serverless availability and a dedicated Inference Endpoint are separate
capabilities.

The common client surface does not guarantee the same processor, region,
isolation, scaling, billing, or optional chat features across routes. Choose a
named provider when those constraints matter, or explicitly target a deployed
endpoint URL.

```python
from huggingface_hub import InferenceClient

client = InferenceClient("org/model", provider="auto", token=token)
```

## Route-specific inference credentials

Hub-routed inference can use a Hugging Face token carrying the required
inference permissions and billing association. A direct partner-provider route
uses that provider's key as documented for the route. Never send a partner
credential to an arbitrary model repository URL.

## Dedicated endpoint lifecycle

Creating or updating an Inference Endpoint is asynchronous. Poll the returned
remote state, handle terminal failure, and direct traffic only after the state
is ready.

- `scale_to_zero` retains configuration and permits a later request to
  cold-start serving.
- `pause` requires an explicit resume.
- Endpoint exposure is configured independently of whether the source model
  repository is private.

## Discover deployable endpoint hardware

Since `1.28.0`, `hf endpoints hardware` lists mutually valid vendor, region,
accelerator, instance-type, and instance-size combinations. Results include
hourly price, namespace quota, and availability. By default the command shows
hardware the namespace can deploy immediately, and filters can narrow it.

```console
hf endpoints hardware --vendor aws --region eu-west-1
```

The SDK exposes the flattened results as `InferenceEndpointHardware` objects
through `list_inference_endpoints_hardware()`.

## Managed engine image payloads

Inference Endpoint `custom_image` payloads can be keyed by an engine name such
as `vLLM`, `sGLang`, `tgi`, `tei`, `llamacpp`, or `hfServe`, with
engine-specific tuning alongside container fields. A dictionary without a
top-level `url` is forwarded unchanged, allowing newly supported API engines
without a client upgrade. `update_inference_endpoint` accepts the same payload
shapes as endpoint creation.

The undocumented
`huggingface_hub.constants.INFERENCE_ENDPOINT_IMAGE_KEYS` constant was removed;
stop reading it directly.

## Multi-accelerator endpoint parallelism

`hf endpoints deploy` and `hf endpoints update` accept `--engine`,
`--tensor-parallel-size`, and `--data-parallel-size`. The update command also
accepts `--custom-image`, `--health-route`, and `--port`.

Set parallelism explicitly when vLLM or SGLang receives a multi-accelerator
instance. These engines default to one accelerator, and the API rejects the
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

## DeepInfra task support

The DeepInfra inference provider supports text-to-speech and
feature-extraction requests through the Hub provider integration.

## Space metadata controls

README fields `suggested_hardware` and `suggested_storage` recommend choices
to users duplicating or configuring a Space. Actual hardware and persistent
storage are allocated separately through runtime settings.

`preload_from_hub` can stage narrowly selected, revision-pinned Hub files
during build or startup. It does not replace dependency declarations. Custom
HTTP headers are limited to the documented allowlist.

## Space persistence and stopped states

A Space's ordinary filesystem is ephemeral across restarts and rebuilds.
Durable state belongs on separately provisioned persistent storage at its
documented mount or in an external service.

A sleeping Space wakes on access. A paused Space requires an explicit restart
or resume, and restarting does not guarantee preservation of ephemeral files.

## Space secrets and OAuth authorities

Space variables are visible to users with settings access. Secrets become
write-only through the settings UI or API after creation. Both are normally
injected into the runtime as environment variables.

README `hf_oauth` configuration can provision OAuth callback and client
settings plus requested scopes for user login. It does not automatically
authorize the Space's server process to access private repositories.
