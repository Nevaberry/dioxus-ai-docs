# Compatibility and Upgrade Decisions

## Runtime and dependency floors

For the `5.5-guide` line, supported runtimes are CPython 3.8 through 3.13 and
PyPy 3.10 or newer. Minimum integration versions are:

- Kombu 5.5;
- redis-py 4.5.2;
- Billiard 4.2.1; and
- Django 2.2.28.

SQLAlchemy 1.4 and 2.0 are both supported. Django users can pass
`--skip-checks` to bypass Django core checks when starting Celery commands:

```console
celery -A proj worker --skip-checks
```

This line replaces the `pycurl` dependency with `urllib3`; account for that
when constructing constrained environments or container images.

For the `5.6-guide` line, supported runtimes are CPython 3.9 through 3.13 and
PyPy 3.11. The minimum Kombu version is 5.6 and the minimum Billiard version is
4.2.4. In particular, CPython 3.8 and PyPy 3.10 are no longer in the supported
matrix.

## SQS transport dependency reversal

The SQS transport returns to `pycurl` in the `5.6-guide` line, reversing the
earlier move to `urllib3`. For an SQS deployment, restore `pycurl` and any
system packages it needs in the build and runtime environment. Do not infer
the SQS dependency from the preceding release line.

## Support policy

Celery 4.x is unsupported. Celery 5.x is not an LTS line and is supported only
until Celery 6.x. Treat migration planning and security-maintenance decisions
accordingly rather than assuming a long-term 5.x support window.

## Upgrade checklist

1. Verify the Python implementation and version in every worker image.
2. Inspect direct and transitive pins for Kombu, Billiard, and redis-py.
3. Check the Django floor and decide whether core checks should run.
4. Check the SQLAlchemy major version when using the database result backend.
5. If SQS is configured, verify the transport's required HTTP dependency for
   the target line.
6. Rebuild and smoke-test the image rather than reusing an environment whose
   native dependencies came from a prior release line.

