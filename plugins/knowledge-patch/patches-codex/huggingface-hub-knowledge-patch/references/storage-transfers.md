# Storage, cache, and transfer operations

## Central-cache paths are immutable inputs

The central cache stores content under `blobs` and exposes revision trees under
`snapshots/{commit}` through links where supported. Editing a returned path can
corrupt shared content or affect multiple snapshots. Copy cached content into
a working directory before modifying it.

`local_dir` instead materializes selected files in the requested directory and
writes resume metadata beneath `.cache/huggingface`. Exclude that metadata from
publication. This mode generally provides less cross-project deduplication
than the central cache.

## Clean cache layers deliberately

Use supported commands to inspect and remove Hub cache content rather than
deleting internal directories during active work:

```console
hf cache ls
hf cache rm
hf cache prune
```

The Xet chunk cache is separate from Hub snapshots and repository refs.
Removing snapshots does not necessarily remove chunks, and clearing chunks
does not update repository refs. Logging out does not remove downloaded
private bytes, so credential lifecycle and data-retention cleanup must be
handled separately.

## Resumable large-folder uploads

`upload_large_folder` persists hashing, pre-upload, and commit progress in the
source folder's `.cache/huggingface`. Rerunning against the same folder and
repository can reuse completed work.

- Keep the metadata available until the upload is finished.
- Do not modify source files during the run.
- Do not treat resumability as transactional atomicity.

The operation may create multiple commits. For an all-or-nothing release,
upload to a staging branch or repository, validate it, and promote it only
after validation succeeds.

## Process-local deferred uploads

Calls with `run_as_future=True` return futures and preserve each client's queue
order. They are background tasks in the current process, not durable remote
jobs.

Keep the process alive until work finishes and retrieve every future's result
so failures are observed. Stop scheduled commit helpers before process exit
and verify their final commit.

## Xet and legacy Git LFS

Xet-backed repositories retain a compatibility bridge for legacy Git LFS
clients, but Xet and LFS do not have identical storage or performance
behavior.

A successful generic Git clone may contain repository metadata or pointers
without materializing the large-file bytes. Verify filter and pointer state,
or use a Hub download API when the work requires actual content.
