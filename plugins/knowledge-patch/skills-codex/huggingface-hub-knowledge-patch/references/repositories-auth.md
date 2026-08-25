# Repository operations and authentication

## Optimistic concurrency for writes

Repository mutations that accept `parent_commit` can use it as the expected
branch head. Supply the known commit when an overwrite or lost update would be
unsafe. If another writer moved the branch, the mutation fails instead of
silently applying to an unexpected base.

This is an optimistic-concurrency precondition, not a repository lock. Decide
whether the caller should re-read, merge, retry, or stop after a mismatch.

## Redirect-safe file downloads

Repository `resolve` requests can redirect to content-addressed storage. A raw
HTTP client must follow the redirect without forwarding the bearer token to an
unrelated origin. Prefer `hf_hub_download` or another supported client flow,
which handles this safely.

Do not implement redirect support by unconditionally copying authorization
headers across origins.

## Explicit token resolution

`HF_TOKEN` takes precedence over a token stored on disk. For APIs accepting
`token=`:

| Value | Resolution |
| --- | --- |
| string | Use that credential directly |
| `True` | Request the locally resolved token |
| `False` | Suppress authentication |

Set `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` when a locally available token must stay
off otherwise-anonymous reads.

```python
from huggingface_hub import HfApi

api = HfApi()
public = api.model_info("open/model", token=False)
private = api.model_info("org/private-model", token=True)
```

## Token storage and revocation

`HF_TOKEN_PATH` overrides the stored-token file beneath `HF_HOME`. Changing
`HF_HUB_CACHE` or `HF_XET_CACHE` alone does not move authentication state.

`logout()` and `hf auth logout` remove saved local credentials. They do not
revoke the remote token. When a credential is compromised or retired, remove
the local copy and revoke the token in Hub settings.

Logout also does not erase previously downloaded private content. Treat cache
cleanup as a separate data-retention operation.

## Server-side copies in commits

Supported clients accept `CommitOperationCopy` alongside add and delete
operations in `create_commit`. Eligible content is copied server-side without
re-uploading, while the operation still produces a repository commit.

Validate that the source, destination, revision, and repository context are
supported before relying on the optimization.
