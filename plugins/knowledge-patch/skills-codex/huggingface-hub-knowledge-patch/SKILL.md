---
name: huggingface-hub-knowledge-patch
description: Hugging Face Hub
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Hugging Face Hub

Use this skill when maintaining Python clients, repository operations, cache
and transfer workflows, routed inference, Inference Endpoints, or Spaces on
Hugging Face Hub. Check the installed package metadata and live service state
before applying compatibility advice because package and service behavior can
change independently.

## Reference index

| Reference | Topics |
| --- | --- |
| [Client migration and packaging](references/client-migration.md) | Python compatibility, HTTPX, removed APIs, CLI migration, downloads, uploads, Xet, framework integrations |
| [Repository operations and authentication](references/repositories-auth.md) | Optimistic concurrency, redirect-safe downloads, token resolution, storage, logout and revocation, server-side copies |
| [Storage, cache, and transfers](references/storage-transfers.md) | Immutable cache paths, `local_dir`, cache cleanup, resumable large uploads, futures, Xet and LFS |
| [Inference, endpoints, and Spaces](references/inference-spaces.md) | Provider routing, credentials, endpoint lifecycle and hardware, engine images, parallelism, Space metadata, persistence, secrets, OAuth |

## Start with installed reality

Before changing code, inspect the installed release and its requirements:

```console
python -c "import importlib.metadata as m; print(m.version('huggingface-hub')); print(m.metadata('huggingface-hub').get_all('Requires-Python'))"
hf --help
```

- Do not assume every 1.x release supports Python 3.9 merely because 1.0 did.
- Select extras and direct dependencies from the installed release's package
  metadata; optional and CLI dependency groups changed with v1.
- Treat the current API signatures and return annotations as authoritative
  when migrating wrappers.

## Migrate v1 client code first

### Replace the HTTP stack

The client uses HTTPX instead of `requests` and `aiohttp`.

- Catch `httpx.HTTPError` for transport failures.
- Catch the appropriate `HfHubHttpError` subtype for Hub responses.
- Replace `configure_http_backend` with `set_client_factory` or
  `set_async_client_factory`.
- Configure proxies, TLS, timeouts, transports, and mocks on the global or
  custom HTTPX client; do not pass legacy per-call `proxies=` arguments.

Do not preserve exception branches that depend on the old client libraries.
Audit retry predicates, mocks, and observability hooks along with imports.

### Replace removed abstractions

| Removed | Use instead |
| --- | --- |
| `Repository` | `HfApi` commit operations or supported Git/Xet tooling |
| `HfFolder` | `login`, `logout`, `auth_switch`, and `get_token` |
| `InferenceApi` | `InferenceClient` or `AsyncInferenceClient` |
| `huggingface-cli` | `hf` |

Moving from `Repository` to HTTP commit operations changes conflicts,
atomicity, and local-worktree behavior. Redesign the workflow instead of
performing a name-only substitution.

Common CLI families are now:

```console
hf auth --help
hf download --help
hf upload --help
hf cache --help
```

### Replace removed arguments

- Use `token=` rather than `use_auth_token=` in direct calls and wrappers.
- Remove `resume_download`; supported cache behavior resumes where applicable.
- Remove `force_filename`; use returned paths and current destination controls.
- Remove `local_dir_use_symlinks`; use the current `local_dir` behavior.
- Keep `force_download` only when a fresh transfer is actually required.

```python
from huggingface_hub import HfApi, snapshot_download

api = HfApi()
info = api.model_info("org/model", token=token)
path = snapshot_download("org/model")
```

### Treat upload results as commit-oriented

Upload methods return current commit information or URLs, not the removed
file-CDN abstraction. Follow the exact installed return type; do not use old
truthiness assumptions, concatenate it as a string, or infer local Git-wrapper
semantics.

## Make authentication explicit

For APIs accepting `token=`:

| Value | Behavior |
| --- | --- |
| credential string | Use that credential |
| `True` | Resolve the locally available token |
| `False` | Suppress authentication |

`HF_TOKEN` overrides a credential stored on disk. Set
`HF_HUB_DISABLE_IMPLICIT_TOKEN=1` when otherwise-anonymous reads must not send
an available token.

```python
api.model_info("open/model", token=False)
api.model_info("org/private-model", token=True)
```

Use `HF_TOKEN_PATH` to relocate the stored-token file under `HF_HOME`.
Changing `HF_HUB_CACHE` or `HF_XET_CACHE` alone does not relocate credentials.
Logout removes local saved credentials but does not revoke the remote token;
revoke compromised or retired tokens in Hub settings too.

For raw `resolve` downloads, follow redirects without forwarding a bearer
token to an unrelated origin. Prefer `hf_hub_download`, which handles this
safely.

## Protect repository writes

Supply `parent_commit` on a repository mutation when the known branch head is
an important precondition. If the branch moved, the operation fails instead
of applying on an unexpected base.

For large releases, distinguish resumability from atomicity:

- `upload_large_folder` can reuse persisted progress on rerun.
- It can create multiple commits and is not one transaction.
- Keep the source folder stable while the operation runs.
- Publish all-or-nothing releases through a staging branch or repository,
  validate them, and then promote them.

## Handle cache paths as immutable

Central-cache paths may link multiple revision snapshots to shared blobs.
Never edit a returned central-cache path in place; copy it to a working
directory first.

Use `local_dir` when files need to be materialized for local work. Exclude its
`.cache/huggingface` resume metadata from publication and expect less
cross-project deduplication than with the central cache.

Clean cache content through supported commands:

```console
hf cache ls
hf cache rm
hf cache prune
```

The Xet chunk cache is separate from snapshot and repository-ref state.
Logging out does not delete previously downloaded private bytes.

## Use Xet-aware transfer behavior

Xet through `hf_xet` is the supported large-file path. The removed
`hf_transfer` integration is not re-enabled by `HF_HUB_ENABLE_HF_TRANSFER`.
Use `HF_XET_HIGH_PERFORMANCE` only after accepting its documented resource
tradeoff.

A generic Git clone of a Xet-backed repository may leave pointers or metadata
without large-file bytes. Verify filter and pointer state, or download through
a Hub API. Legacy Git LFS clients can use the compatibility bridge, but LFS
and Xet do not have identical storage or performance behavior.

## Choose an inference route deliberately

`InferenceClient(..., provider="auto")` selects an available routed provider;
it is not a dedicated deployment. Select a named provider when processor,
region, isolation, scaling, billing, or optional chat behavior matters, or
target a deployed endpoint URL.

```python
from huggingface_hub import InferenceClient

client = InferenceClient("org/model", provider="auto", token=token)
```

Use a Hugging Face token with the required permissions and billing association
for Hub-routed inference. Use a partner provider's key only for its documented
direct route, never an arbitrary model repository URL.

## Operate dedicated endpoints by state

Creation and updates are asynchronous. Poll remote state, handle terminal
failure, and only then direct traffic to the endpoint.

- `scale_to_zero` retains configuration and permits a later cold start.
- `pause` requires an explicit resume.
- Endpoint exposure is configured independently of source-repository privacy.

Discover deployable hardware and its price, quota, and availability before
constructing a deployment:

```console
hf endpoints hardware --vendor aws --region eu-west-1
```

For vLLM or SGLang on multi-accelerator instances, explicitly set tensor or
data parallelism. Those engines default to one accelerator, and the API
rejects a multi-accelerator mismatch.

Managed engine payloads may be keyed by engine name. Pass supported
engine-specific tuning and container fields, and do not read the removed
`huggingface_hub.constants.INFERENCE_ENDPOINT_IMAGE_KEYS` constant.

## Design Spaces for their runtime semantics

- Treat the ordinary filesystem as ephemeral across restarts and rebuilds.
- Put durable state on provisioned persistent storage at its documented mount
  or in an external service.
- A sleeping Space wakes on access; a paused Space needs an explicit restart
  or resume.
- A restart does not guarantee preservation of ephemeral files.
- `suggested_hardware` and `suggested_storage` recommend configuration to
  users; they do not allocate resources.
- `preload_from_hub` can stage narrowly selected, revision-pinned files, but it
  does not replace dependency declarations.
- Space variables are visible to users with settings access. Secrets become
  write-only in the settings UI or API after creation; both are normally
  injected as environment variables.
- README `hf_oauth` config prepares user-login OAuth settings and scopes. It
  does not authorize the Space server process to private repositories.

Consult the indexed references before implementing a migration or operational
workflow; they retain the edge cases and exact compatibility boundaries.
