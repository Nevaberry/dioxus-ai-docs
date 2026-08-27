# Repository Writes and Authentication

## Safe repository mutations

### Use optimistic concurrency for contested writes

Repository mutations that accept `parent_commit` can compare it with the
current branch head. Supply the commit you read when an overwrite or lost
update would be unsafe. If another writer moved the branch, the mutation fails
instead of silently applying to an unexpected base.

Handle that failure as a concurrency event: refresh state, reconcile the
change, and retry only after deciding how the new branch contents affect the
intended mutation.

## Safe authenticated downloads

### Do not forward tokens across storage redirects

Repository `resolve` requests may redirect from the Hub to content-addressed
storage. A raw HTTP client must follow the redirect without forwarding its
bearer token to an unrelated origin.

Prefer `hf_hub_download` or another supported client flow, which handles the
redirect safely. If a raw client is required, apply an origin-aware
authorization policy rather than copying headers unconditionally.

## Token selection

### Understand credential precedence

`HF_TOKEN` takes precedence over a token stored on disk. APIs that accept
`token=` distinguish these values:

- A token string uses that explicit credential.
- `True` requests the locally resolved token.
- `False` suppresses authentication even when a token is available.

```python
api.model_info("open/model", token=False)
api.model_info("org/private-model", token=True)
```

Set `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` when otherwise-anonymous reads must not
receive the available token implicitly. This is distinct from passing an
explicit token for private or authorized operations.

## Token storage and retirement

### Move auth state with `HF_TOKEN_PATH`

`HF_TOKEN_PATH` overrides the stored-token file beneath `HF_HOME`. Changing
`HF_HUB_CACHE` or `HF_XET_CACHE` alone does not relocate authentication state,
because content caches and credentials have separate paths.

### Separate logout from remote revocation

`logout()` and `hf auth logout` remove saved local credentials. They do not
revoke the token at the Hub.

When a token is compromised, retired, or no longer meant to work from any
machine, also revoke it in Hub settings. Conversely, remember that logout does
not erase private repository bytes already downloaded into local caches.
