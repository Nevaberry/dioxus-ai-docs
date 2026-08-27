# Files, Caches, and Upload Workflows

## Downloaded files and cache paths

### Treat central-cache results as immutable

The central cache stores content under `blobs` and presents revision trees
under `snapshots/{commit}` through links where supported. Editing a path
returned from a snapshot may therefore mutate shared blob content or damage
multiple snapshots. Copy the file into a working directory before modifying
it.

### Account for `local_dir` metadata

Using `local_dir` materializes selected files in that directory and records
resume metadata below `.cache/huggingface`. Exclude this metadata from
publication or source-control payloads.

`local_dir` also provides less cross-project deduplication than the central
cache, so choose it for a materialized working tree rather than assuming it
has identical storage characteristics.

## Cache cleanup

### Use cache commands instead of deleting internals

Use `hf cache ls`, `hf cache rm`, and `hf cache prune` to inspect and remove
Hub cache content. Avoid manually deleting internals while clients may be
using them.

The Hub snapshot cache and Xet chunk cache are distinct layers:

- Removing snapshots does not necessarily remove Xet chunks.
- Clearing chunks does not update repository references.
- Logging out does not delete private bytes already present on disk.

Select and clean each layer deliberately according to the storage and privacy
goal.

## Large and asynchronous uploads

### Resume `upload_large_folder` from its metadata

`upload_large_folder` stores hashing, pre-upload, and commit progress in the
source folder's `.cache/huggingface`. A rerun against the same source folder
and repository can reuse completed work.

Keep that metadata until the upload finishes, and do not modify source files
during the run. Changing the folder or repository breaks the assumptions
behind safe progress reuse.

### Do not treat a large-folder upload as one transaction

The operation can create multiple commits. A failure may therefore leave a
valid partial history rather than rolling back the whole upload.

For an all-or-nothing release, upload to a staging branch or separate
repository, validate the complete result, and then promote it.

### Observe process-local deferred work

Calls with `run_as_future=True` return futures and preserve queue order within
the client. They are background operations in the current process, not
durable remote jobs.

Keep the process alive, wait for each future, and retrieve its failure.
Scheduled commit helpers also need an explicit stop and verification of their
last commit before the process exits.

## Commit composition

### Copy eligible files server-side

`create_commit` accepts `CommitOperationCopy` alongside add and delete
operations. An eligible copy occurs server-side without re-uploading the
content and still produces a repository commit.

The operation remains subject to the supported source, destination, revision,
and repository contexts. Validate those contexts rather than assuming an
arbitrary cross-repository or cross-revision copy is available.

## Xet and Git LFS interoperability

### Verify that a clone materialized large bytes

Xet-backed repositories retain a compatibility bridge for legacy Git LFS
clients. The bridge supports interoperability, but Xet and LFS do not have
identical storage or performance behavior.

A generic Git clone can succeed while leaving repository metadata or pointer
files instead of the large-file bytes. Inspect Git filters and pointer state,
or use a Hub download API when materialization must be guaranteed.
