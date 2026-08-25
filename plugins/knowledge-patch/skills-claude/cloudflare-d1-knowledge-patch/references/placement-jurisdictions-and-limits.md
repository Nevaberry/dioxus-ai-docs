# Placement, Jurisdictions, and Limits

## Default primary placement

By default, D1 places a database’s primary near the location from which the
creation request was made. If most writes originate elsewhere, supply a
creation-time location hint.

D1 chooses the nearest possible location by latency; a hint is not an exact
placement guarantee.

```sh
wrangler d1 create new-database --location=weur
```

Supported hints are:

- `wnam`
- `enam`
- `weur`
- `eeur`
- `apac`
- `oc`

The `sam`, `afr`, and `me` hints are unsupported, and D1 databases do not run in
those regions.

## Jurisdiction constraints

A jurisdiction guarantees where a database runs and stores its data. Choose it
only during database creation; it cannot be added or changed later.

Supported values are `eu` and `fedramp`:

```sh
npx wrangler@latest d1 create db-with-jurisdiction --jurisdiction=eu
```

When both a jurisdiction and a location hint are supplied, the jurisdiction
takes precedence and the location hint is ignored.

The constraint controls where the database runs and persists data. It does not
restrict where Workers may access the database. When read replication is
enabled, replicas remain within the database’s jurisdiction.

Coverage attribution: `2025`.

## Account storage limit

The D1 storage maximum per account on the Workers paid plan is 1 TB, increased
from 250 GB.
