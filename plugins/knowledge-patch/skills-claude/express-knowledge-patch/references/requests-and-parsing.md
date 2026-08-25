# Requests and Parsing

## URL-encoded bodies and request body presence

`express.urlencoded()` defaults `extended` to `false`. Set the option
explicitly if the application depends on another mode.

Without body-parsing middleware, `req.body` is `undefined`. Do not rely on an
empty object being present:

```js
app.post('/items', (req, res) => {
  if (req.body === undefined) return res.sendStatus(400)
  res.json(req.body)
})
```

## Query parser and request properties

The default query parser is `"simple"`. `req.query` is exposed through a
getter, so code must not assign a replacement value to it.

`req.host` retains the request's port number. Account for the port when code
compares or persists the host value.

These defaults and property changes are part of the `5.0-migration` batch.

## Extended-query-parser rollback

Express 5.2.1 fully reverted the breaking extended-query-parser change that
first shipped in 5.2.0. CVE-2024-51999 was rejected, and there is no
vulnerability associated with that parser behavior.

Upgrade deployments pinned to 5.2.0 instead of depending on its short-lived
parser behavior. This correction is covered by batch `5.2.x`.

## Brotli request encoding

Express supports Brotli encoding for requests from clients that support it.
