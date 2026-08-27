---
name: huggingface-hub-knowledge-patch
description: Hugging Face Hub
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Hugging Face Hub Knowledge Patch

Use this skill for work involving `huggingface_hub`, Hub repositories,
authentication, downloads, uploads, caches, Xet or Git LFS, routed inference,
Inference Endpoints, or Spaces.

Start from the installed package metadata and signatures. Confirm repository
state and asynchronous remote state when behavior depends on either one.

## Reference index

| Reference | Topics |
| --- | --- |
| [Client migration](references/client-migration.md) | Python support, HTTPX, removed APIs and CLI, arguments, return values, Xet, packaging |
| [Repository writes and authentication](references/repositories-auth.md) | Optimistic concurrency, redirect safety, token resolution, storage, logout and revocation |
| [Files, caches, and uploads](references/files-cache-uploads.md) | Cache immutability, `local_dir`, cleanup, large-folder and deferred uploads, copies, LFS bridge |
| [Inference and Spaces](references/inference-spaces.md) | Routed providers, credentials, endpoint lifecycle and hardware, engine images, parallelism, Space configuration |

## Breaking client changes

### Check Python compatibility per installed release

The initial v1 client requires Python 3.9 or newer, but do not treat that as
the floor for every later 1.x release. Read the installed release's package
metadata before choosing a runtime or publishing package constraints.

### Configure HTTPX, not requests or aiohttp

The client uses HTTPX for synchronous and asynchronous traffic. Treat
transport failures as `httpx.HTTPError`-based and Hub response failures as
members of the `HfHubHttpError` hierarchy.

Replace `configure_http_backend` with `set_client_factory` or
`set_async_client_factory`. Put proxy, TLS, timeout, transport, and mock
configuration on the global or custom HTTPX client; do not pass per-call
`proxies=`.

### Replace removed abstractions

Do not import or recommend `Repository`, `HfFolder`, or `InferenceApi`.

- Use `HfApi` or supported Git/Xet tools for repository work.
- Use `login`, `logout`, `auth_switch`, and `get_token` for authentication.
- Use `InferenceClient` or `AsyncInferenceClient` for inference.

Moving from a local `Repository` worktree to commit-oriented HTTP calls changes
conflict handling, atomicity, and local-worktree behavior. Review those
semantics instead of mechanically replacing the class name.

### Use the `hf` command

Replace `huggingface-cli` automation with `hf`, including `hf auth`,
`hf download`, `hf upload`, and `hf cache` commands.

### Remove obsolete call arguments

Replace `use_auth_token` with `token`, including in downstream wrappers.

Downloads no longer accept `resume_download`, `force_filename`, or
`local_dir_use_symlinks`. Use supported cache resumption, returned paths,
`force_download`, the central cache, and current `local_dir` behavior.

```python
api.model_info("org/model", token=token)
snapshot_download("org/model")
```

### Inspect upload return types

Upload methods return commit-oriented information or URLs rather than the old
file-CDN abstraction. Follow the exact current return type; do not depend on an
old result's truthiness, string concatenation, or local Git-wrapper semantics.

### Use Xet for large files

Xet is integrated through `hf_xet`. The `hf_transfer` integration is removed,
and `HF_HUB_ENABLE_HF_TRANSFER` no longer enables it. Set
`HF_XET_HIGH_PERFORMANCE` only after accepting its documented resource cost.

### Keep framework integration outside the core client

Removed TensorFlow/Keras helpers should be replaced by framework-owned
serialization and model-card callbacks that call Hub primitives. For
packaging, select the actual supported extra or direct dependency of the
installed release because optional and CLI dependency groups changed.

## Repository and authentication safety

### Guard writes with the expected branch head

For mutations accepting `parent_commit`, pass the known branch head when a
lost update or overwrite would be unsafe. If the branch moved, the request
fails rather than applying on an unexpected base.

### Handle storage redirects without leaking credentials

Repository `resolve` requests may redirect to content-addressed storage. A raw
HTTP client must follow the redirect without forwarding the bearer token to an
unrelated origin. Prefer `hf_hub_download` or another supported client flow,
which handles this safely.

### Choose token behavior explicitly

`HF_TOKEN` overrides the token stored on disk. For APIs with `token=`:

- A string selects that credential.
- `True` requests the locally resolved token.
- `False` suppresses authentication.

Use `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` to keep an available token off reads
that should remain anonymous.

```python
api.model_info("open/model", token=False)
api.model_info("org/private-model", token=True)
```

`HF_TOKEN_PATH` overrides the stored-token file normally kept under `HF_HOME`.
`HF_HUB_CACHE` and `HF_XET_CACHE` do not move authentication state.

`logout()` and `hf auth logout` delete saved local credentials but do not
revoke the remote token. Revoke compromised or retired tokens in Hub settings
as well.

## File, cache, and upload safety

### Never edit the central cache in place

Central-cache `snapshots/{commit}` trees link to shared content under `blobs`
where links are supported. Editing a returned cache path may corrupt shared
content or affect multiple snapshots. Copy files to a working directory first.

`local_dir` materializes selected files and writes resume metadata under
`.cache/huggingface`. Exclude that metadata from publication and expect less
cross-project deduplication than the central cache provides.

### Clean caches through supported commands

Use `hf cache ls`, `hf cache rm`, and `hf cache prune`; do not delete cache
internals during active work. Hub snapshots and the Xet chunk cache are
separate layers. Logging out does not erase downloaded private data.

### Treat large-folder upload as resumable, not atomic

`upload_large_folder` records hashing, pre-upload, and commit progress in the
source folder's `.cache/huggingface`. Preserve that directory, rerun with the
same folder and repository, and do not modify files during the upload.

The operation may create multiple commits. For all-or-nothing publication,
upload to a staging branch or repository, validate it, and then promote it.

### Keep deferred work alive and observe failures

`run_as_future=True` returns futures and preserves per-client queue order, but
the work is process-local. Keep the process alive and retrieve every future's
failure. Stop scheduled commit helpers and verify their last commit before the
job exits.

### Prefer server-side copies when eligible

Pass `CommitOperationCopy` with add and delete operations to `create_commit`
for supported server-side copies. The copy still creates a repository commit
and is limited by supported source, destination, revision, and repository
contexts.

### Verify large-file materialization

Legacy Git LFS clients can use the compatibility bridge for Xet-backed
repositories, but Xet and LFS differ in storage and performance. A successful
generic clone may leave pointers rather than large-file bytes. Inspect filter
and pointer state or use a Hub download API.

## Inference and endpoint operations

### Distinguish routing from deployment

`InferenceClient(..., provider="auto")` selects an available routed provider
for a supported model and task. It does not create or identify a dedicated
Inference Endpoint, and the common surface does not guarantee a processor,
region, isolation, scaling, billing model, or optional chat feature.

Choose a named provider when those constraints matter, or target a deployed
endpoint URL explicitly.

```python
from huggingface_hub import InferenceClient

client = InferenceClient("org/model", provider="auto", token=token)
```

Hub-routed inference can use a Hugging Face token with the required inference
permissions and billing association. Direct partner routes use that provider's
documented key. Never send a partner key to an arbitrary model repository URL.

### Poll endpoint changes

Endpoint create and update operations are asynchronous. Poll remote state,
handle terminal failure, and only then send traffic. `scale_to_zero` retains
configuration and allows a later request to cold-start serving; `pause`
requires an explicit resume. Configure endpoint exposure separately from the
source model repository's visibility.

### Match engines to multi-accelerator hardware

When vLLM or SGLang uses a multi-accelerator instance, set tensor or data
parallelism explicitly. Those engines default to one accelerator, and the API
rejects a mismatch. Use the current endpoint hardware discovery command or SDK
before deployment, and see the inference reference for managed-engine payloads
and exact CLI options.

## Space operations

README `suggested_hardware` and `suggested_storage` are recommendations, not
allocations. Configure actual hardware and persistent storage in runtime
settings. Use revision-pinned `preload_from_hub` selections for narrow staging,
not as a replacement for dependency declarations, and stay within the custom
header allowlist.

The ordinary Space filesystem is ephemeral. Put durable state on provisioned
persistent storage at its documented mount or in an external service. A
sleeping Space wakes on access; a paused Space requires restart or resume, and
restarting does not preserve ephemeral files.

Variables are visible to users with settings access. Secrets become write-only
through the settings UI or API after creation; both normally enter the runtime
as environment variables. README `hf_oauth` settings configure user-login
OAuth, but do not automatically authorize the server process to private
repositories.

## Working checklist

1. Inspect the installed package metadata and callable signatures.
2. Replace removed client APIs, arguments, CLI commands, and transport hooks.
3. Make token selection and anonymous access intentional.
4. Protect repository writes with `parent_commit` where races matter.
5. Treat shared cache paths as immutable and clean both cache layers safely.
6. Design large uploads around multiple commits and process-local background work.
7. Distinguish routed inference, dedicated endpoints, and Space runtimes.
8. Poll endpoint state and verify accelerator, engine, and parallelism choices.
9. Put Space durability and authority in explicitly provisioned mechanisms.
