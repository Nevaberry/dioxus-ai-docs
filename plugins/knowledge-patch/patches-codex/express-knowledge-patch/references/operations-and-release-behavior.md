# Operations and Release Behavior

## Listener failures

`app.listen()` reports server error events through its callback in
5.0-migration behavior instead of throwing them as Express 4 did. Distinguish
the error callback from successful listening:

```js
const server = app.listen(8080, '0.0.0.0', (error) => {
  if (error) throw error
  console.log(server.address())
})
```

Exercise a bind failure, such as a port conflict, in startup tests.

## Router debug namespaces

Router traces moved out of `express:*`. In Express 5.1 and later, their
namespaces are `router`, `router:layer`, and `router:route`
(5.0-migration). Enable both families to retain the detail formerly available
through the Express 4 wildcard:

```sh
DEBUG=express:*,router,router:* node index.js
```

## Default npm install and lifecycle phases

Express 5.1.0 moved v5 to npm's `latest` tag. An unversioned install therefore
selects v5, while v4 entered maintenance:

```sh
npm install express
npm install "express@4" # explicitly remain on v4
```

The lifecycle policy is:

- A major remains `CURRENT` and off `latest` for at least three months.
- It remains `ACTIVE` and on `latest` for at least twelve months.
- It then receives only security and high-priority fixes during
  `MAINTENANCE`.

Pin the desired major when a deployment must not follow a change to the
default npm tag.

## Extended query-parser reversion

Express 5.2.1 fully reverts the breaking extended-query-parser change that
shipped in 5.2.0 (5.2.x). CVE-2024-51999 was rejected, and there is no
vulnerability associated with that behavior.

Upgrade deployments pinned to 5.2.0 instead of relying on its short-lived
parser behavior. Verify the application's parser configuration and query
semantics after the upgrade.
