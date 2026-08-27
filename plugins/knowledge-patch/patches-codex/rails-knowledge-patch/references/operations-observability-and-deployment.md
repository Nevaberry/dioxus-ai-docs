# Operations, Observability, and Deployment

## Development containers

Rails 7.2 (`7.2`) can generate `.devcontainer` for both new and existing applications. The generated setup contains a Dockerfile, Compose file, and `devcontainer.json`; defaults include the selected database, Redis, Headless Chrome, and local Active Storage with previews.

```console
rails new myapp --devcontainer
rails devcontainer
```

## Puma concurrency default

Generated Puma configuration uses three threads instead of five (`7.2`). An upgrade that adopts the new generated default reduces per-process concurrency. Recalculate Puma process/thread capacity together with database-pool and queue-worker needs.

## Generated container runtime

Generated Dockerfiles install and use jemalloc to reduce allocator fragmentation in threaded processes (`7.2`). Setting the `BACKTRACE` environment variable disables backtrace cleaning during normal server runs, not only during tests.

## Structured event reporting

Rails exposes structured event reporting through `Rails.event` (`8.1-guide`). Add shared payload fields with `set_context`, add nested tags with `tagged`, and publish event-specific fields with `notify`:

```ruby
Rails.event.set_context(request_id: "abc123", shop_id: 456)
Rails.event.tagged("graphql") do
  Rails.event.notify("user.signup", user_id: 123, email: "user@example.com")
end
```

Registered subscribers implement `emit(event)`. The event is a hash, and the subscriber owns serialization and output.

Active Record additionally reports `active_record.strict_loading_violation` and `active_record.sql`; see the Active Record reference for notification payload changes.

## Local CI workflows

Applications can declare a local CI workflow in `config/ci.rb` and execute it with `bin/ci` (`8.1-guide`). The DSL runs named command steps and can branch on `success?` to report success or failure.

```ruby
CI.run do
  step "Setup", "bin/setup --skip-server"
  step "Style", "bin/rubocop"
  step "Tests", "bin/rails test"
end
```

An optional `gh signoff` step can make a passing local run a merge prerequisite.

## Fetching encrypted credentials

`rails credentials:fetch` reads a dot-delimited key from encrypted Rails credentials (`8.1-guide`). This lets deployment tooling populate secret files without a separate secret store:

```sh
KAMAL_REGISTRY_PASSWORD=$(rails credentials:fetch kamal.registry_password)
```

## Registry-free basic Kamal deployments

Kamal 2.8 uses a local registry by default for basic deployments (`8.1-guide`), so getting started does not require a remote registry. Large-scale deployments may still configure one.

## Production SSL defaults

Rails 8.1.1 no longer assumes or forces SSL in production for generated Kamal deployments (`8.1`). This lets the generated setup boot before TLS exists. Enable the SSL settings after TLS is available.

## Kamal 2 in-place migration

Before an in-place migration from Kamal 1, install Kamal 1.9.x and complete a successful deploy. That version supplies the downgrade path.

```console
$ gem install kamal --version 1.9.0
$ kamal deploy
$ gem install kamal
$ kamal config
$ kamal config -d staging
```

Kamal 2 makes several coupled changes:

- `kamal-proxy` replaces Traefik.
- Containers move onto the `kamal` Docker network.
- Configuration requires incompatible updates.
- Deployment secrets move from `.env` to `.kamal/secrets`.

Validate the converted configuration with `kamal config` for every destination before upgrading.

## Application port

Kamal 2 changes the proxy's default application port from 3000 to 80. If the application does not listen on port 80, set `app_port` explicitly or update the image's `EXPOSE` port.

## Upgrade, rolling migration, and rollback

`kamal upgrade` migrates the proxy, network, application, and accessories separately for each destination. On multiple servers, `--rolling` works host by host, `-h` targets selected hosts, and pre/post proxy-reboot hooks can coordinate an upstream load balancer.

```console
$ kamal upgrade -d staging
$ kamal upgrade --rolling -d staging
```

To roll back, uninstall Kamal 2, activate Kamal 1.9, and run `kamal downgrade` with the same destination and host-targeting options:

```console
$ kamal downgrade -d staging
```

Upgrade and downgrade commands can be rerun on hosts already migrated in the requested direction.
