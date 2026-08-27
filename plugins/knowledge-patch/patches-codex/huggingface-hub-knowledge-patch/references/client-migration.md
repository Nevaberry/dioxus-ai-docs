# Client migration and packaging

## Python and dependency compatibility

The `huggingface-hub-v1-client` transition initially required Python 3.9 or
newer, but later 1.x releases may raise that floor. Read `Requires-Python` from
the installed release's package metadata rather than treating Python 3.9 as a
guarantee for the entire 1.x line.

Optional and CLI dependency groups changed with v1. Packaging should select
the extra that the installed release actually supports, or declare the needed
direct dependency. Do not preserve an old extra name solely because it worked
before the migration.

Deprecated TensorFlow and Keras utilities were removed from the core client.
Framework integrations should own serialization and model-card callbacks and
call Hub primitives for remote operations.

## HTTPX migration

The client replaced both `requests` and `aiohttp` with HTTPX.

- Transport failures are based on `httpx.HTTPError`.
- Hub response failures use the `HfHubHttpError` hierarchy.
- `configure_http_backend` gives way to `set_client_factory` and
  `set_async_client_factory`.
- Proxies, TLS configuration, timeouts, transports, and mocks belong on the
  global or custom HTTPX client, not legacy per-call `proxies=` arguments.

Update exception handlers, retry predicates, test doubles, and instrumentation
together. A compatibility layer that only replaces imports can still miss
changed exception ancestry and client lifetime.

## Removed client abstractions

`Repository`, `HfFolder`, and `InferenceApi` were removed.

- Use `HfApi` commit-oriented HTTP operations or supported Git/Xet tooling for
  repository work.
- Use `login`, `logout`, `auth_switch`, and `get_token` for authentication.
- Use `InferenceClient` or `AsyncInferenceClient` for inference.

Moving from `Repository` to commit operations changes conflict handling,
atomicity, and local-worktree behavior. Re-evaluate those properties rather
than treating `HfApi` as a drop-in local Git wrapper.

## CLI migration

The `huggingface-cli` executable was replaced by `hf`. Update shell scripts,
container health checks, documentation, and command allowlists to current
families such as:

```console
hf auth --help
hf download --help
hf upload --help
hf cache --help
```

## Authentication and download arguments

The `use_auth_token` alias was removed. Direct callers and downstream wrappers
must expose and pass `token`.

Downloads no longer accept:

- `resume_download`: supported cache behavior handles resumption where
  applicable.
- `force_filename`: use the returned path and current destination controls.
- `local_dir_use_symlinks`: use current `local_dir` materialization behavior.

The central cache, `local_dir`, returned paths, and `force_download` cover the
remaining supported decisions; do not recreate removed filename or symlink
semantics in a wrapper without an application-specific need.

```python
from huggingface_hub import HfApi, snapshot_download

api = HfApi()
info = api.model_info("org/model", token=token)
path = snapshot_download("org/model")
```

## Upload return values

Upload methods return current commit-oriented information or URLs rather than
the old file-CDN abstraction. Follow the exact v1 return type for the method in
use. Do not rely on an older result's truthiness, concatenate it with strings,
or infer local Git-wrapper semantics from it.

## Xet-first large-file migration

Xet is integrated automatically through `hf_xet` as the supported large-file
path. The
`hf_transfer` integration was removed, and `HF_HUB_ENABLE_HF_TRANSFER` no
longer activates it. Enable `HF_XET_HIGH_PERFORMANCE` only when its documented
resource tradeoff is acceptable for the host.
