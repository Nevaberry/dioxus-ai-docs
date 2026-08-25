# Client Migration and Compatibility

## Runtime and transport compatibility

### Check each installed release's Python requirement

The initial v1 client requires Python 3.9 or newer. Later 1.x releases may
raise that minimum, so use the installed release's package metadata rather
than assuming Python 3.9 works across the entire release family.

### Migrate transport configuration to HTTPX

The v1 client migration (`huggingface-hub-v1-client`) replaces both `requests`
and `aiohttp` with HTTPX. Transport failures are `httpx.HTTPError`-based, while
Hub response failures use the `HfHubHttpError` hierarchy. Audit exception
handlers so transport and Hub response failures are caught at the intended
level.

Replace `configure_http_backend` with `set_client_factory` and
`set_async_client_factory`. Configure proxies, TLS, timeouts, transports, and
mocks on a global or custom HTTPX client instead of using per-call `proxies=`.

## Removed abstractions and commands

### Replace repository, authentication, and inference classes

`Repository`, `HfFolder`, and `InferenceApi` are removed.

- Use `HfApi` or supported Git/Xet tooling for repository work.
- Use `login`, `logout`, `auth_switch`, and `get_token` for authentication.
- Use `InferenceClient` or `AsyncInferenceClient` for inference.

Commit-oriented HTTP operations are not a drop-in semantic replacement for a
local `Repository` worktree: conflict handling, atomicity, and local-worktree
behavior differ. Design the workflow around commits and remote branch state.

### Replace `huggingface-cli` with `hf`

Current automation uses the `hf` command, including `hf auth`, `hf download`,
`hf upload`, and `hf cache`. Update shell scripts and documentation that still
invoke `huggingface-cli`.

## Authentication and download calls

### Rename the authentication argument

The `use_auth_token` alias is removed. Pass `token` in direct calls and update
downstream wrappers that expose the old alias.

```python
api.model_info("org/model", token=token)
snapshot_download("org/model")
```

### Remove obsolete download controls

Downloads no longer accept `resume_download`, `force_filename`, or
`local_dir_use_symlinks`.

- Let supported cache behavior resume transfers where applicable.
- Use returned paths rather than forcing the old filename behavior.
- Use `force_download` when a fresh download is required.
- Choose between the central cache and current `local_dir` materialization.

## Upload and large-file migration

### Follow exact upload return types

Upload methods return commit-oriented information or URLs instead of the old
file-CDN abstraction. Check the exact v1 signature and return type. Do not
assume an older result's truthiness, append strings to it, or treat it like a
local Git wrapper result.

### Use the Xet integration

Xet is the supported v1 path for large-file transfers and is integrated
automatically through `hf_xet`. The `hf_transfer` integration is removed;
`HF_HUB_ENABLE_HF_TRANSFER` no longer activates it.

`HF_XET_HIGH_PERFORMANCE` is the replacement performance control, but enable
it only when its documented resource tradeoff is acceptable for the host.

## Framework and packaging integration

Deprecated TensorFlow/Keras utilities are removed from the core client.
Framework integrations should own serialization and model-card callbacks,
then call Hub primitives for remote operations.

Optional and CLI dependency groups changed with v1. Package against the
actual supported extra or direct dependency of the installed release rather
than assuming an earlier extra name still installs the required components.
