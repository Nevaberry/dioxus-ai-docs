# Rails 8.0 Architecture Changes

## Solid Trifecta — No Redis Required

Rails 8.0 ships three database-backed replacements for Redis:

### Solid Queue (Job Backend)

Default Active Job backend. Uses `FOR UPDATE SKIP LOCKED` (PostgreSQL 9.5+, MySQL 8.0+, SQLite).

```ruby
# config/application.rb — already default in new Rails 8.0 apps
config.active_job.queue_adapter = :solid_queue
```

```yaml
# config/solid_queue.yml
production:
  dispatchers:
    - polling_interval: 1
      batch_size: 500
  workers:
    - queues: "*"
      threads: 5
      processes: 2
```

Key features:
- Concurrency controls (`limits_concurrency key:, to:, group:, duration:`)
- Recurring jobs (`config/recurring.yml`)
- Mission Dashboard UI (via `solid_queue` engine mount)
- Puma plugin: `plugin :solid_queue` in `config/puma.rb`

### Solid Cache (Fragment Cache)

Replaces Redis/Memcached for HTML fragment caching. Stores in database.

```ruby
# config/environments/production.rb — already default
config.cache_store = :solid_cache_store
```

### Solid Cable (WebSocket Pub/Sub)

Replaces Redis for Action Cable. Messages stored in database, retained 1 day by default.

```yaml
# config/cable.yml
production:
  adapter: solid_cable
  silence_polling: true
  message_retention: 1.day
```

## Kamal 2 Deployment

New apps include `config/deploy.yml` and `.kamal/` directory. Kamal 2 replaces Traefik with `kamal-proxy`.

```bash
kamal setup     # provision fresh server + deploy
kamal deploy    # subsequent deploys
kamal console   # remote Rails console
kamal app logs  # tail production logs
```

Key config (`config/deploy.yml`):
```yaml
service: myapp
image: myorg/myapp
servers:
  web:
    hosts: ["192.168.1.1"]
proxy:
  ssl: true
  host: myapp.com
```

### Thruster

HTTP/2 proxy included in Dockerfile, sits in front of Puma:
- X-Sendfile acceleration
- Asset caching and compression
- Gzip/Brotli compression

## Authentication Generator

```bash
rails generate authentication
```

Generates:
- `User` and `Session` models
- `Authentication` concern (included in `ApplicationController`)
- Login/logout views and controllers
- Password reset flow with `PasswordsMailer`
- `Current.user` / `Current.session` accessors

Limitations: No signup flow, no MFA, no OAuth — intended as a starting point.

### allow_browser Guard

```ruby
class ApplicationController < ActionController::Base
  allow_browser versions: :modern  # Chrome/Edge 120+, Firefox 121+, Safari 17.2+
end
```

Returns 406 for older browsers. Use `allow_browser versions: :all` to skip.

## Propshaft (Asset Pipeline)

Replaces Sprockets. Key differences:
- No transpilation (use `jsbundling-rails` or `importmap-rails`)
- Digest stamping only (fingerprinted filenames)
- Much simpler — no asset compilation step

```ruby
# Gemfile — default in new Rails 8.0 apps
gem "propshaft"
```

Asset helpers work the same (`image_tag`, `stylesheet_link_tag`, `javascript_include_tag`).

## Turbo 8 — Morphing Page Refreshes

Turbo 8 uses [Idiomorph](https://github.com/bigskysoftware/idiomorph) for DOM morphing instead of full page replacement.

```erb
<%# app/views/layouts/application.html.erb %>
<%= turbo_refreshes_with method: :morph, scroll: :preserve %>
```

### Broadcasts

```ruby
class Post < ApplicationRecord
  broadcasts_refreshes  # broadcasts morphing refreshes to subscribers
end
```

```erb
<%# In view %>
<%= turbo_stream_from @post %>
```

This replaces the need for granular `turbo_stream` broadcast templates — the server re-renders the full page and Turbo morphs only the differences.
