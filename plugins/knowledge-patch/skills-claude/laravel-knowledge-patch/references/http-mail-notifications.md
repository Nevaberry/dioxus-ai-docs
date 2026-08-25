# HTTP Client, Mail, Notifications, and Broadcasting

## Broadcasting installs without lifecycle scripts (2026-04)

The `install:broadcasting` command now invokes Yarn with `--ignore-scripts`, so package `postinstall` scripts are not executed during installation.

## Cloudflare email delivery (2026-04)

Laravel's mail system adds support for Cloudflare Email Service.

## Conditional CORS bypasses (2026-01)

`HandleCors::skipWhen()` accepts a callback for exempting selected requests from CORS handling.

## Configurable mail transport retry periods (2025-04)

Round-robin and failover mail transports now allow their retry period to be configured, so applications can control when a temporarily failed transport becomes eligible again.

## Custom Markdown extensions in mail (2026-03-laravel-12)

Laravel's Markdown mail renderer now loads custom Markdown extensions, allowing mail rendering to use application-specific Markdown behavior.

## Custom server-sent events (2025-03)

`response()->eventStream()` now supports custom event names and start messages, allowing a stream to identify event types and send an initial message.

## Database notification read timestamps (12.0.0)

The database notification channel now supports setting the read timestamp through `readAt()`.

## Delayed mail dispatch (2026-02)

`Mailable::later()` now applies its delay to the underlying `SendQueuedMailable` job.

## Encoded HTML strings in Markdown mail (2025-05)

`Illuminate\Support\EncodedHtmlString` represents text that should be HTML-encoded when rendered while leaving existing `HtmlString` values untouched; Markdown mail rendering can toggle this encoding behavior.

## Fluent asynchronous HTTP requests (2025-12)

`PendingRequest` HTTP methods may now return promises, and pools use `FluentPromise` for cleaner chaining. `Pool` and `Batch` also expose `newRequest()` for constructing requests within those coordinators.

## HTTP client lifecycle hooks (2025-12)

`PendingRequest` adds `withRequestContext()`, and the HTTP client can run callbacks after building a response, providing explicit request-context and post-construction extension points.

## HTTP query helpers (2026-07)

The HTTP client provides `Http::query()`, while HTTP tests provide `query()` and `queryJson()` helpers for working with request query data.

## HTTP response JSON flags (2026-01)

HTTP client responses accept JSON decoding flags through `Response::json()`, including flags such as `JSON_BIGINT_AS_STRING` for preserving large integer values.

```php
$data = Http::get($url)->json(flags: JSON_BIGINT_AS_STRING);
```

## HTTP response override signatures (13.0-upgrade)

Custom HTTP client response classes must keep overrides compatible with the newly declared callback parameters.

```php
public function throw($callback = null);
public function throwIf($condition, $callback = null);
```

## Inline attachments through Resend (2025-08)

The Resend mail transport now supports inline attachments, allowing mail rendered with embedded or content-ID assets to retain them when sent through Resend.

## Line-break rejection in email addresses (2026-05)

Email addresses containing line breaks are now rejected instead of reaching mail handling.

## Macroable notifications (2026-01)

`Notification` is now macroable, enabling application-specific extensions through the standard `macro()` API.

## Normalized HTTP connection exceptions (2025-06)

SSL certificate and connection failures from the HTTP client no longer leak as Guzzle exceptions; they are exposed through Laravel's HTTP client exception abstraction.

## Notification failure events (2025-04)

A failed notification send now dispatches `NotificationFailed`, allowing failure listeners to observe errors that occur while a channel sends a notification.

## Notification sending lifecycle (2026-02)

`sendNow()` preserves mutations a notification makes inside `via()`, and notifications may define `afterSending()` logic to run after delivery.

## Optional mail configuration names (2026-07)

Mail configuration options no longer require a `name` value.

## Password reset mail subject (13.0-upgrade)

The default password reset subject is now `Reset your password` instead of `Reset Password Notification`; update exact mail assertions and translation overrides.

## Per-request HTTP exception truncation (2025-06)

An individual pending HTTP request can set its `RequestException` message truncation limit instead of relying only on the shared default.

```php
Http::truncateExceptionsAt(240)->get($url)->throw();
```

## PSR-compatible HTTP client (2026-06)

Laravel 13's HTTP client can be used directly as a PSR client, allowing integrations that require the PSR client contract to accept Laravel's client.

## Raw Resend attachments (2025-06)

The Resend mail transport can send raw, non-encoded attachment content, so callers do not have to pre-encode attachments for that transport.

## Recording non-faked HTTP requests (2025-03)

The HTTP client can record real requests without faking their responses, so tests and diagnostics can inspect traffic while it is still sent normally.

```php
Http::record();
Http::get('https://example.test');
$recorded = Http::recorded();
```

## Redis cluster broadcasting (2025-08)

Laravel's Redis broadcaster now supports clustered Redis connections, so a cluster-backed application no longer needs a separate non-clustered connection solely for broadcasting.

## Retrying HTTP middleware exceptions (2025-04)

HTTP client requests configured with `retry()` now retry when client middleware throws an exception instead of limiting retries to response and connection failures.

## SES tenant support (2026-07)

The SES v2 mail transport supports SES tenants.

## Single failover notifications (2026-01)

`CacheFailedOver` and `QueueFailedOver` now fire only for the first failure in a failover attempt, so listeners are not invoked once for every failed backend.

## Stream bodies in HTTP fakes (2026-07)

HTTP fake responses accept stream bodies, allowing tests to model streamed response content.

## Transport exceptions on notification failures (2025-07)

`NotificationFailed` events now receive the originating `TransportException`, allowing failure listeners to inspect the underlying mail transport error.
