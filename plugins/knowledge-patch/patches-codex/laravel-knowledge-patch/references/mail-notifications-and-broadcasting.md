# Mail, Notifications, and Broadcasting

Mail transports, mailables, notification lifecycle, and broadcasting integrations.

## Broadcasting installs without lifecycle scripts (2026-04)

The `install:broadcasting` command now invokes Yarn with `--ignore-scripts`, so package `postinstall` scripts are not executed during installation.

## Cloudflare email delivery (2026-04)

Laravel's mail system adds support for Cloudflare Email Service.

## Configurable mail transport retry periods (2025-04)

Round-robin and failover mail transports now allow their retry period to be configured, so applications can control when a temporarily failed transport becomes eligible again.

## Custom Markdown extensions in mail (2026-03-laravel-12)

Laravel's Markdown mail renderer now loads custom Markdown extensions, allowing mail rendering to use application-specific Markdown behavior.

## Custom queued-notification jobs (2025-06)

Queued notification dispatch can override the default `SendQueuedNotifications` job class when job-level behavior needs customization.

## Database notification read timestamps (12.0.0)

The database notification channel now supports setting the read timestamp through `readAt()`.

## Delayed mail dispatch (2026-02)

`Mailable::later()` now applies its delay to the underlying `SendQueuedMailable` job.

## Encoded HTML strings in Markdown mail (2025-05)

`Illuminate\Support\EncodedHtmlString` represents text that should be HTML-encoded when rendered while leaving existing `HtmlString` values untouched; Markdown mail rendering can toggle this encoding behavior.

## Inline attachments through Resend (2025-08)

The Resend mail transport now supports inline attachments, allowing mail rendered with embedded or content-ID assets to retain them when sent through Resend.

## Macroable notifications (2026-01)

`Notification` is now macroable, enabling application-specific extensions through the standard `macro()` API.

## Missing models in queued notifications (13.0-upgrade)

Queued notifications now honor the notification class's `#[DeleteWhenMissingModels]` attribute and `$deleteWhenMissingModels` property, deleting the job instead of failing when a serialized model is missing.

## Notification failure events (2025-04)

A failed notification send now dispatches `NotificationFailed`, allowing failure listeners to observe errors that occur while a channel sends a notification.

## Notification sending lifecycle (2026-02)

`sendNow()` preserves mutations a notification makes inside `via()`, and notifications may define `afterSending()` logic to run after delivery.

## Optional mail configuration names (2026-07)

Mail configuration options no longer require a `name` value.

## Raw Resend attachments (2025-06)

The Resend mail transport can send raw, non-encoded attachment content, so callers do not have to pre-encode attachments for that transport.

## Redis cluster broadcasting (2025-08)

Laravel's Redis broadcaster now supports clustered Redis connections, so a cluster-backed application no longer needs a separate non-clustered connection solely for broadcasting.

## Scheduled output email default (12.0.0)

Scheduled command `emailOutput()` now sends mail only when output exists by default.

## SES tenant support (2026-07)

The SES v2 mail transport supports SES tenants.

## Transport exceptions on notification failures (2025-07)

`NotificationFailed` events now receive the originating `TransportException`, allowing failure listeners to inspect the underlying mail transport error.
