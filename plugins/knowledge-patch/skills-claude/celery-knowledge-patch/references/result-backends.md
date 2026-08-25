# Result Backends

## Database table creation

The database result backend option `create_tables_at_setup` defaults to
`True`. Backend initialization therefore creates the required tables eagerly.

Set it to `False` to keep lazy table creation until the tables are first
needed:

```python
create_tables_at_setup = False
```

This is useful when migrations or another schema-management system owns table
creation.

## Redis retry classification

The Redis result backend classifies transient failures with
`exception_safe_to_retry`. Its retry machinery can therefore recover from
temporary Redis outages.

## Redis credential providers

`redis_backend_credential_provider` enables provider-based authentication for
the Redis result backend, including AWS ElastiCache IAM authentication. Use a
provider instead of embedding static credentials.

Set `redis_client_name` to label Celery backend connections in Redis
monitoring.

## Remote local-DynamoDB services

The DynamoDB result backend accepts a local DynamoDB endpoint on a host other
than `localhost`:

```python
result_backend = "dynamodb://@dynamodb:8000"
```

This form addresses the service by its remote host and port.

## Azure Blob Storage managed credentials

The Azure Block Blob result backend supports managed credentials. Deployed
workers can authenticate without embedding static storage keys.
