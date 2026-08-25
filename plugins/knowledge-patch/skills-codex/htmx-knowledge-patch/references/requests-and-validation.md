# Requests and Validation

Use this reference when working with browser validation, cross-origin requests,
CORS, or CSRF tokens during boosted navigation.

## Native validation

### Report invalid forms to the user

htmx blocks invalid form requests. For compatibility, it does not show the
browser's native validation UI or focus the first invalid control by default.
Enable both behaviors with:

```js
htmx.config.reportValidityOfForms = true;
```

### Validate non-form triggers

Use `hx-validate="true"` when a non-form request trigger should participate in
validation as well.

## Cross-origin request allowlisting

Requests are same-origin-only by default. If the application deliberately sets
`htmx.config.selfRequestsOnly = false`, validate each destination explicitly.

The `htmx:validateUrl` event provides:

- `event.detail.url`, the destination URL.
- `event.detail.sameHost`, whether that URL uses the same host.

Cancel the event to deny a destination:

```js
document.body.addEventListener("htmx:validateUrl", (event) => {
  if (!event.detail.sameHost && event.detail.url.hostname !== "api.example.com") {
    event.preventDefault();
  }
});
```

Keep the allowlist narrow and explicit rather than treating all cross-origin
URLs as trusted.

## CORS requirements

URL validation is only the client-side decision. The cross-origin server must
also:

- Allow the htmx request headers that the application sends.
- Expose the htmx response headers that client-side code must read.

Configure both sides when enabling cross-origin requests.

## CSRF tokens with boosted navigation

An inherited `hx-headers` value can send a CSRF token with every request, but
boosted navigation does not update the `<html>` or `<body>` elements. A token
stored only on either element can therefore become stale as server responses
rotate it.

Place a rotating token on an element that boosted navigation actually replaces.
When the framework supplies hidden CSRF form inputs, prefer those inputs so the
token travels with the form content being refreshed.

## Related migration defaults

`DELETE` values use URL parameters and request destinations are restricted to
the same origin by default. See
[Migration and configuration](migration-and-configuration.md#changed-request-and-scrolling-defaults)
before restoring earlier request behavior.
