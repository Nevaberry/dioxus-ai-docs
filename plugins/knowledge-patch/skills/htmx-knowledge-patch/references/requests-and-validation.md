# Requests and Validation

## Request-method and origin defaults

`DELETE` request values are sent as URL parameters, while requests are
restricted to the same origin by default. Restore the earlier method behavior
or allow cross-origin requests only when an application explicitly depends on
it:

```js
htmx.config.methodsThatUseUrlParams = ["get"];
htmx.config.selfRequestsOnly = false;
```

Changing `methodsThatUseUrlParams` to only `get` moves `DELETE` values away
from the URL. Disabling `selfRequestsOnly` must be paired with destination
validation and correct CORS policy.

## Cross-origin requests

After cross-origin requests are enabled, `htmx:validateUrl` exposes the parsed
destination as `event.detail.url` and indicates same-host destinations through
`event.detail.sameHost`. Cancel the event to deny a destination:

```js
document.body.addEventListener("htmx:validateUrl", (event) => {
  if (!event.detail.sameHost &&
      event.detail.url.hostname !== "api.example.com") {
    event.preventDefault();
  }
});
```

Browser CORS checks still apply. The remote origin must allow the htmx request
headers the application sends and expose any htmx response headers the client
needs to read.

## Native form validation

htmx blocks a form request when native constraint validation fails. For
compatibility, it does not display the browser's validation UI or focus the
first invalid control by default. Enable both behaviors with:

```js
htmx.config.reportValidityOfForms = true;
```

Use `hx-validate="true"` when a non-form element initiating a request should
also invoke validation.

## CSRF tokens and boosted navigation

An inherited `hx-headers` value can attach a CSRF token to every request, but
boosted navigation does not replace the `<html>` or `<body>` element. A token
stored only on either element can become stale when the server rotates it.

Put a rotating token on an element that the boosted navigation actually
replaces. Framework-provided hidden form inputs are another safe choice when
the framework refreshes and validates them as part of normal responses.
