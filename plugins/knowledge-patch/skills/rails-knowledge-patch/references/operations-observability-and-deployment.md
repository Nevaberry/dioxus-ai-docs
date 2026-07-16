# Operations, Observability, and Deployment

Topic details draw from batches `7.2`, `8.0`, `8.1-guide`, `8.1`, and `deployment-with-kamal`.

## Contents

- [Development and runtime defaults](#development-and-runtime-defaults)
- [Structured events](#structured-events)
- [Local CI and credential access](#local-ci-and-credential-access)
- [Kamal deployment defaults](#kamal-deployment-defaults)
- [Migrating from Kamal 1](#migrating-from-kamal-1)
- [Upgrade and rollback commands](#upgrade-and-rollback-commands)

## Development and runtime defaults

### Development containers

Generate a `.devcontainer` setup for a new or existing application (`7.2`):

```console
rails new myapp --devcontainer
rails devcontainer
```

The generated setup includes a Dockerfile, Compose file, and `devcontainer.json`. Defaults account for the selected database, Redis, Headless Chrome, and local Active Storage with preview support.

### Puma, allocation, and backtraces

Generated Puma configuration uses three threads instead of five (`7.2`). Recalculate per-process concurrency and database pool capacity when an existing deployment relied on the generated default.

Generated Rails Dockerfiles install and use jemalloc to reduce allocator fragmentation in threaded processes (`7.2`).

Setting the `BACKTRACE` environment variable disables backtrace cleaning during normal server runs, not only tests (`7.2`).

### Regular-expression timeout

Rails sets Ruby's global `Regexp.timeout` to one second by default (`8.0`). Audit intentionally expensive expressions before overriding it; an application that depends on longer execution may otherwise start timing out after upgrade.

## Structured events

`Rails.event` emits structured notifications with payloads, tags, and shared context (`8.1-guide`):

```ruby
Rails.event.set_context(request_id: "abc123", shop_id: 456)
Rails.event.tagged("graphql") do
  Rails.event.notify(
    "user.signup",
    user_id: 123,
    email: "user@example.com"
  )
end
```

Each registered subscriber implements `emit(event)`, receives the event as a hash, and decides serialization and emission behavior.

Active Record reports `active_record.strict_loading_violation` and `active_record.sql` through this structured reporter (`8.1`). See the Active Record reference for SQL notification retry and affected-row metadata.

## Local CI and credential access

### Local CI workflow

Declare a local workflow in `config/ci.rb` and run it with `bin/ci` (`8.1-guide`):

```ruby
CI.run do
  step "Setup", "bin/setup --skip-server"
  step "Style", "bin/rubocop"
  step "Tests", "bin/rails test"
end
```

The DSL runs named command steps. Branch on `success?` when the workflow needs explicit success or failure reporting. An optional `gh signoff` step can make a successful local run a merge prerequisite.

### Fetching encrypted credentials

`rails credentials:fetch` prints a dot-delimited value from encrypted Rails credentials (`8.1-guide`). It can populate deployment secret files without a separate secret store:

```sh
KAMAL_REGISTRY_PASSWORD=$(rails credentials:fetch kamal.registry_password)
```

## Kamal deployment defaults

### Registry behavior

Kamal 2.8 uses a local registry by default for basic deployments (`8.1-guide`), so a remote registry is no longer required to get started. Large-scale deployments can still use a remote registry.

### Application port

Kamal 2 changes the proxy's default application port from 3000 to 80 (`deployment-with-kamal`). If the container does not listen on 80, set `app_port` explicitly or change the image's `EXPOSE` port.

### SSL generation default

Rails `8.1.1` no longer assumes or forces SSL in production for generated Kamal deployments (`8.1`). This lets the generated deployment boot before TLS is configured. Enable the production SSL settings once TLS is available.

## Migrating from Kamal 1

For an in-place migration, first install Kamal 1.9.x and complete a successful deploy (`deployment-with-kamal`). That release establishes the supported downgrade path.

```console
gem install kamal --version 1.9.0
kamal deploy
gem install kamal
```

Kamal 2 makes several incompatible infrastructure and configuration changes:

- Replaces Traefik with `kamal-proxy`.
- Moves containers onto a Docker network named `kamal`.
- Requires corresponding incompatible configuration changes.
- Moves deployment secrets from `.env` to `.kamal/secrets`.

Validate converted configuration for every destination before upgrading:

```console
kamal config
kamal config -d staging
```

## Upgrade and rollback commands

`kamal upgrade` migrates the proxy, network, application, and accessories separately for each destination (`deployment-with-kamal`):

```console
kamal upgrade -d staging
kamal upgrade --rolling -d staging
```

On a multi-server destination, `--rolling` proceeds one host at a time. Use `-h` to target selected hosts. Pre- and post-proxy-reboot hooks can coordinate traffic with an upstream load balancer.

Upgrade is rerunnable for hosts already migrated in the requested direction.

To roll back:

1. Uninstall Kamal 2.
2. Activate Kamal 1.9.
3. Run `kamal downgrade` with the same destination, rolling, or host targeting options as needed.

```console
kamal downgrade -d staging
```

Downgrade is also rerunnable for hosts already moved in the requested direction.
