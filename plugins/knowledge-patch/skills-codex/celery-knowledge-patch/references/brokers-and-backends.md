# Brokers and Result Backends

## Redis recovery

Kombu 5.5 improves recovery from long-standing Redis broker disconnections
(`5.5.0`). The Redis result backend also implements
`exception_safe_to_retry`, allowing its retry machinery to recognize
transient Redis failures that are safe to retry.

Keep retry policy bounded and observable. The classification supports
recovery from temporary outages; it does not imply that every backend error
is retryable.

## Redis credential providers and client names

Use `redis_backend_credential_provider` to obtain Redis backend credentials
from a provider instead of embedding a static password (`5.6-guide`). This
supports provider-backed schemes such as AWS ElastiCache IAM authentication.

Set `redis_client_name` to label Celery result-backend connections in Redis
monitoring:

```python
redis_client_name = "celery-results"
```

## Delayed-delivery log redaction

The delayed-delivery mechanism sanitizes passwords in broker URLs in all log
output (`5.6-guide`). Continue to treat broker URLs as secrets and avoid
copying them into application messages, custom logging, or exception text;
the built-in redaction does not sanitize unrelated logging paths.

## Google Cloud Pub/Sub broker

Install the broker transport with the `gcpubsub` extra (`5.5-guide`):

```console
pip install "celery[gcpubsub]"
```

Configure the broker with a project URL:

```python
broker_url = "gcpubsub://projects/project-id"
```

## Database backend table creation

The database result backend's `create_tables_at_setup` setting defaults to
`True` (`5.5-guide`). Backend initialization therefore creates result tables
eagerly.

Set it to `False` to retain lazy creation until tables are first needed, or
when migrations or another schema-management system owns table creation:

```python
create_tables_at_setup = False
```

Ensure the schema exists before result writes when eager creation is disabled.

## Remote local-DynamoDB endpoints

The DynamoDB result backend can connect to a local DynamoDB-compatible service
running on a host other than `localhost` (`5.5.0`):

```python
result_backend = "dynamodb://@dynamodb:8000"
```

This form is useful when the service is addressed by a container or network
hostname.

## Azure Blob managed credentials

The Azure Block Blob result backend supports managed credentials (`5.5.0`).
Deployed workers can therefore authenticate through their managed identity or
credential environment without embedding static storage keys. Verify the
identity's storage permissions and credential discovery in the worker runtime.

