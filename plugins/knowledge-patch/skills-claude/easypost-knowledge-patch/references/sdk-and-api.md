# SDK and API compatibility

## Node.js SDK migration

The Node.js SDK uses `fetch` rather than `superagent` and no longer supports
Node 16.

Rename integration hooks as follows:

| Previous name | Current name |
| --- | --- |
| `superagentMiddleware` | `httpMiddleware` |
| `fetchClient` | `httpClient` |

API resources are returned as plain JSON-compatible objects rather than
model-class instances.

## Generic requests

The C#, Java, Node.js, PHP, and Ruby SDKs expose a generic request interface for
calling arbitrary API endpoints, including endpoints that do not yet have
typed resource wrappers.

## Response timestamps

Supported API endpoints standardize timestamps as ISO 8601.

## Index endpoint rate limits

Index endpoints have request-per-second rate limiting. Integrations that
enumerate resources must tolerate throttling rather than assume unrestricted
pagination.
