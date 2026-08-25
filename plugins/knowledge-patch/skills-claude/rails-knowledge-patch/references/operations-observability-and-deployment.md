# Operations, Observability, and Deployment

## Local development

### Development containers

Since `7.2`, Rails can generate a `.devcontainer` setup for a new or existing
application. It contains a Dockerfile, Compose file, and `devcontainer.json`.
Defaults include the chosen database, Redis, Headless Chrome, and local Active
Storage with preview support.

```console
rails new myapp --devcontainer
rails devcontainer
```

### Server backtraces

Setting `BACKTRACE` disables backtrace cleaning during ordinary server runs,
not only during tests.

## Runtime defaults

### Puma threads

Generated Puma configuration defaults to three threads rather than five.
Upgraded deployments that relied on the generated value therefore have less
per-process concurrency. Recalculate Puma process counts, queue concurrency,
and database pool capacity together.

### Docker memory allocation

Generated Rails Dockerfiles install and use jemalloc to reduce allocator
fragmentation in threaded processes.

## Structured observability

### Event reporting

The `8.1-guide` adds `Rails.event` for structured notifications. Events can
include payload fields, shared context, and tags:

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

Registered subscribers implement `emit(event)`. The event is a hash, and the
subscriber controls its serialization and output destination.

## Local CI

Applications can declare a local workflow in `config/ci.rb` and run it with
`bin/ci`. The DSL executes named command steps and can branch on `success?` to
report success or failure.

```ruby
CI.run do
  step "Setup", "bin/setup --skip-server"
  step "Style", "bin/rubocop"
  step "Tests", "bin/rails test"
end
```

An optional `gh signoff` step can make a successful local run a merge
prerequisite.

## Credentials

`rails credentials:fetch` reads a dot-delimited key from encrypted Rails
credentials. This lets deployment scripts create secret files without a
separate secret store:

```sh
KAMAL_REGISTRY_PASSWORD=$(rails credentials:fetch kamal.registry_password)
```

## Kamal deployment defaults

### Local registry

Kamal 2.8 uses a local registry by default for basic deployments, so getting
started no longer requires a remote registry. Large deployments can still
configure a remote registry.

### SSL behavior

Rails 8.1.1 no longer assumes or forces SSL in production for generated Kamal
deployments. The generated deployment can boot before TLS is available; enable
the relevant SSL settings once TLS has been provisioned.

## Migrating to Kamal 2

The `deployment-with-kamal` migration is an operational sequence, not only a
Gemfile upgrade.

### Prerequisites

For an in-place Kamal 1 migration, first install Kamal 1.9.x and complete a
successful deployment. That version also supplies the downgrade path.

Kamal 2 then changes several deployment surfaces:

- Traefik is replaced by `kamal-proxy`;
- containers move to a `kamal` Docker network;
- configuration needs incompatible updates; and
- deployment secrets move from `.env` to `.kamal/secrets`.

Validate the converted configuration for every destination before upgrading:

```console
$ gem install kamal --version 1.9.0
$ kamal deploy
$ gem install kamal
$ kamal config
$ kamal config -d staging
```

### Application port

Kamal 2 changes the proxy's default application port from 3000 to 80. If the
application does not listen on port 80, set `app_port` explicitly or update the
image's `EXPOSE` port.

### Upgrade and rolling migration

`kamal upgrade` migrates the proxy, network, application, and accessories
separately for each destination. On a multi-server deployment, `--rolling`
migrates host by host and `-h` selects particular hosts. Pre- and post-proxy
reboot hooks can coordinate an upstream load balancer.

```console
$ kamal upgrade -d staging
$ kamal upgrade --rolling -d staging
```

The command may be rerun for hosts already migrated in the requested
direction.

### Rollback

To roll back, uninstall Kamal 2, activate Kamal 1.9, and run `kamal downgrade`
with the same destination and host-targeting options. The downgrade command is
also safe to rerun for hosts already moved in that direction.

```console
$ kamal downgrade -d staging
```
