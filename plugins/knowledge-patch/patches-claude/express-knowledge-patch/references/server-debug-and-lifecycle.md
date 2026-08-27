# Server Startup, Debugging, and Lifecycle

## Listen callback errors

`app.listen()` passes server error events to its callback instead of throwing
them. The callback must distinguish failure from successful listening:

```js
const server = app.listen(8080, '0.0.0.0', (error) => {
  if (error) throw error
  console.log(server.address())
})
```

This startup change is part of batch `5.0-migration`.

## Router debug namespaces

Router traces moved out of `express:*`. In Express 5.1 and newer, use the
`router`, `router:layer`, and `router:route` namespaces. Enable both namespace
families to retain the detail previously obtained from the Express wildcard:

```sh
DEBUG=express:*,router,router:* node index.js
```

## Default npm install

Express 5.1.0 moved the v5 line to npm's `latest` tag. An unversioned install
therefore selects v5:

```sh
npm install express
```

Pin v4 explicitly when intentionally remaining on that major:

```sh
npm install "express@4"
```

## Lifecycle phases

Under the lifecycle policy introduced with `5.1.0`:

1. A major stays `CURRENT` and remains off npm's `latest` tag for at least
   three months.
2. It stays `ACTIVE` and on `latest` for at least twelve months.
3. It then enters `MAINTENANCE`, receiving only security and high-priority
   fixes.

At the same transition, v4 entered maintenance.
