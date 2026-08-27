# Requests and Validation

## Understand request defaults

Requests are same-origin-only by default. `DELETE` values use URL parameters;
to restrict URL parameters to `GET` and restore the earlier behavior, set:

```js
htmx.config.methodsThatUseUrlParams = ["get"];
```

Only disable the same-origin guard when cross-origin access is required:

```js
htmx.config.selfRequestsOnly = false;
```

## Report native form validation

htmx blocks invalid form requests but, for compatibility, does not show the
browser's validation UI or focus the first invalid input by default. Enable
that behavior with:

```js
htmx.config.reportValidityOfForms = true;
```

Use `hx-validate="true"` when a non-form request trigger should also run
validation.

## Allowlist cross-origin destinations

After enabling cross-origin requests, handle `htmx:validateUrl` as an explicit
allowlist. The event exposes `detail.url` and `detail.sameHost`; cancel it to
deny a destination:

```js
document.body.addEventListener("htmx:validateUrl", (event) => {
  if (!event.detail.sameHost &&
      event.detail.url.hostname !== "api.example.com") {
    event.preventDefault();
  }
});
```

CORS must permit the htmx request headers and expose the htmx response headers
the client needs to read.

## Keep CSRF tokens fresh during boosted navigation

An inherited `hx-headers` value can send a CSRF token with every request, but
`hx-boost` does not replace the `<html>` or `<body>` elements. Put a rotating
token on an element that boosted navigation actually replaces. When the
server framework provides hidden CSRF form inputs, prefer those inputs.
