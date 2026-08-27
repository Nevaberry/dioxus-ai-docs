# Operations and Observability

## OpenTelemetry replaces OpenTracing

Since 3.21.0, custom deployments must move from the old OpenTracing integration
to an OpenTelemetry-capable collector. Saleor can emit metrics and OTLP traces
with W3C Trace Context. A public telemetry stream omits codebase-oriented
details such as individual SQL queries.

## Deployment environment contracts change

Since 3.21.0, GCP private storage uses `GS_MEDIA_PRIVATE_BUCKET_NAME` instead
of `GS_MEDIA_BUCKET_NAME`. Environment parsing accepts numeric and lowercase
boolean values, S3 deployments can set `AWS_S3_URL_PROTOCOL`, and the token
generator class is configurable. Django Debug Toolbar and
`ENABLE_DEBUG_TOOLBAR` are no longer supported.

## JWKS keys declare the signing algorithm

Since 3.21.0, keys returned by `/.well-known/jwks.json` include the JWK `alg`
member, allowing consumers to identify the intended signing algorithm from the
key.

## Staff deletion always removes the user

Since 3.23.0, `staffDelete` always deletes the staff user, including when the
account has orders. It no longer merely clears `is_staff` for such accounts.
Callers that relied on order history to preserve the user must add their own
safeguard.

## Legacy deployment and management hooks are removed

Since 3.23.0, `JWT_EXPIRE` can no longer disable JWT expiration, and
`manage.py createsuperuser` no longer supports custom `User` database models.
Deployment configuration and account-provisioning automation must remove those
assumptions.

## GraphQL field usage is measurable

Since 3.23.0, the `saleor.graphql.field.usage` OpenTelemetry metric counts
resolver calls for deprecated fields and for custom fields declared with
`monitor_usage=True`. Operators can use it to measure clients before removing
or migrating fields.

## Bulk delete mutations cap IDs

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

Every bulk delete mutation accepts at most 100 IDs by default and returns an
`INVALID` error above the limit. Deployments can change the cap with
`BULK_DELETE_LIMIT`.

```env
BULK_DELETE_LIMIT=250
```
