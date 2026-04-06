---
name: rails-knowledge-patch
description: "Rails 8.0–8.1 changes — Solid Queue/Cache/Cable (no Redis), Kamal 2 deployment, Propshaft, authentication generator, Turbo 8 morphing, params.expect, job continuations, structured events. Load before working with Rails."
license: MIT
version: "8.1.3"
metadata:
  author: Nevaberry
---

# Ruby on Rails Knowledge Patch

Covers Rails 8.0–8.1 changes. Training cutoff: Rails 7.1, Ruby 3.3.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Rails 8.0 architecture | [references/rails-8-architecture.md](references/rails-8-architecture.md) | Solid Queue/Cache/Cable, Kamal 2, Propshaft, auth generator, Turbo morphing |
| Active Record queries & schema | [references/active-record-queries.md](references/active-record-queries.md) | params.expect, pluck hash, UPDATE with JOIN, first/last deprecation, schema sorting |
| Active Record columns & serialization | [references/active-record-columns.md](references/active-record-columns.md) | only_columns, update_column touch, serialized comparable, JSON coder, PG 18 virtual columns |
| Database configuration | [references/database-config.md](references/database-config.md) | Connection pool options, transaction isolation, SQLite extensions, invisible indexes |
| Active Job continuations | [references/active-job-continuations.md](references/active-job-continuations.md) | Resumable multi-step jobs with cursor tracking |
| Tooling & framework | [references/tooling.md](references/tooling.md) | Local CI, credentials:fetch, structured events, markdown rendering, deprecated associations |
| Deprecations & removals | [references/deprecations.md](references/deprecations.md) | sidekiq adapter, ActiveSupport::Configurable, mb_chars, Active Storage Azure |

## Rails 8.0 — No Redis, No Sprockets, No Traefik

Rails 8.0 removes external dependencies:

- **Solid Queue** replaces Sidekiq/Resque as default Active Job backend (database-backed, `FOR UPDATE SKIP LOCKED`)
- **Solid Cache** replaces Redis/Memcached for fragment caching
- **Solid Cable** replaces Redis for Action Cable pub/sub
- **Propshaft** replaces Sprockets (digest stamping only, no transpilation)
- **Kamal 2** replaces Capistrano/manual deployment (with `kamal-proxy` instead of Traefik)
- **Authentication generator** (`rails generate authentication`) — session-based, password-resettable
- **Turbo 8 morphing** — `turbo_refreshes_with method: :morph, scroll: :preserve` for DOM morphing
- **allow_browser** guard — `allow_browser versions: :modern` returns 406 for old browsers
- **Thruster** — HTTP/2 proxy in Dockerfile for asset caching/compression

See `references/rails-8-architecture.md` for full details, configuration, and code examples.

## Quick Reference

### params.expect replaces require/permit (8.0)

```ruby
# New preferred way (safer, more explicit)
params.expect(post: [:title, :body])
# replaces: params.require(:post).permit(:title, :body)
```

### SQLite virtual tables (8.0)

```ruby
create_virtual_table :posts_search, :fts5, ["content", "title"]
```

### Custom batch columns (8.0)

```ruby
Product.in_batches(cursor: [:shop_id, :id]) do |relation|
  # batches using composite cursor
end
```

### Pluck with hash for joined tables (8.0)

```ruby
Post.joins(:comments).pluck(:id, comments: :id)
```

### db:migrate on fresh database (8.0)

`db:migrate` on a fresh database now loads the schema first, then runs only pending migrations. Use `db:migrate:reset` for the old behavior.

### Active Job Continuations (8.1)

Long-running jobs broken into resumable steps via `ActiveJob::Continuable`:

```ruby
class ProcessImportJob < ApplicationJob
  include ActiveJob::Continuable

  def perform(import_id)
    step :validate do
      # runs once
    end

    step :process do |step|
      Record.find_each(start: step.cursor) do |record|
        record.process
        step.advance! from: record.id
      end
    end

    step :finalize  # calls private method
  end
end
```

### Structured Event Reporting (8.1)

```ruby
Rails.event.notify("user.signup", user_id: 123, email: "user@example.com")
Rails.event.tagged("graphql") { Rails.event.notify("query.executed", duration: 42) }
Rails.event.set_context(request_id: "abc123", shop_id: 456)
```

### Connection pool configuration (8.1)

```yaml
production:
  adapter: postgresql
  max_connections: 10 # renamed from pool (old name still works)
  min_connections: 2
  keepalive: 300
  max_age: 600
```

### Transaction isolation (8.1)

```ruby
ActiveRecord.with_transaction_isolation_level(:read_committed) do
  Tag.create!  # uses read_committed isolation
end
# Also: connection.current_transaction.isolation
```

### Deprecated associations (8.1)

```ruby
has_many :posts, deprecated: true                       # warn mode (default)
has_many :posts, deprecated: { mode: :raise }           # or :notify
has_many :posts, deprecated: { mode: :warn, backtrace: true }
```

Reports all usage: `author.posts`, `author.preload(:posts)`, nested attributes, etc.

### only_columns — inverse of ignored_columns (8.1)

```ruby
class User < ApplicationRecord
  self.only_columns = %w[id name email]
end
```

### UPDATE with JOIN — PostgreSQL & SQLite3 (8.1)

```ruby
Comment.joins(:post).update_all("title = posts.title")
```

Previously MySQL-only. Now works for PostgreSQL and SQLite3 (without LIMIT/ORDER/GROUP BY).

### Local CI (8.1)

```ruby
# config/ci.rb — run with bin/ci
CI.run do
  step "Setup", "bin/setup --skip-server"
  step "Style: Ruby", "bin/rubocop"
  step "Tests: Rails", "bin/rails test"

  if success?
    step "Signoff", "gh signoff"
  else
    failure "CI failed.", "Fix the issues and try again."
  end
end
```

### credentials:fetch command (8.1)

```bash
rails credentials:fetch kamal.registry_password
# Useful in .kamal/secrets:
# KAMAL_REGISTRY_PASSWORD=$(rails credentials:fetch kamal.registry_password)
```

### update_column with touch (8.1)

```ruby
user.update_column(:nice, true, touch: true)        # also updates updated_at
user.update_columns(last_ip: request.remote_ip, touch: true)
```

### Serialized comparable attributes (8.1)

```ruby
serialize :config, type: Hash, coder: JSON, comparable: true  # avoids false dirty tracking
```

### SQLite extensions in database.yml (8.1)

```yaml
development:
  adapter: sqlite3
  extensions:
    - SQLean::UUID # module responding to .to_path
    - .sqlpkg/nalgeon/crypto/crypto.so # filesystem path
```

### PG 18 virtual generated columns (8.1)

```ruby
create_table :users do |t|
  t.string :name
  t.virtual :lower_name, type: :string, as: "LOWER(name)"          # virtual on PG 18+
  t.virtual :name_length, type: :integer, as: "LENGTH(name)", stored: true
end
```

### first/last without order deprecated (8.1)

```ruby
# config/application.rb (Rails 8.1 default)
config.active_record.raise_on_missing_required_finder_order_columns = true
```

Raises `ActiveRecord::MissingRequiredOrderError` if no `order`, `implicit_order_column`, `query_constraints`, or `primary_key`.

### New exception classes (8.1)

- `ActiveRecord::CheckViolation` — check constraint violations
- `ActiveRecord::ExclusionViolation` — PostgreSQL exclusion constraint violations

### Key changes summary

| Feature | Version | Area |
|---------|---------|------|
| Solid Queue/Cache/Cable defaults | 8.0 | Infrastructure |
| Kamal 2 deployment | 8.0 | Deployment |
| Propshaft asset pipeline | 8.0 | Assets |
| Authentication generator | 8.0 | Security |
| Turbo 8 morphing | 8.0 | Hotwire |
| `allow_browser` guard | 8.0 | Security |
| `params.expect` | 8.0 | Controllers |
| SQLite virtual tables | 8.0 | Active Record |
| Custom batch cursors | 8.0 | Active Record |
| Pluck with hash | 8.0 | Active Record |
| `db:migrate` loads schema first | 8.0 | Migrations |
| Job continuations | 8.1 | Active Job |
| Structured events | 8.1 | Framework |
| Local CI (`bin/ci`) | 8.1 | Tooling |
| Markdown rendering | 8.1 | Action View |
| `credentials:fetch` | 8.1 | Tooling |
| Deprecated associations | 8.1 | Active Record |
| `only_columns` | 8.1 | Active Record |
| `update_column` touch | 8.1 | Active Record |
| Connection pool config | 8.1 | Database |
| Transaction isolation | 8.1 | Active Record |
| Serialized comparable | 8.1 | Active Record |
| JSON coder options | 8.1 | Active Record |
| SQLite extensions in YAML | 8.1 | Database |
| Invisible indexes | 8.1 | MySQL/MariaDB |
| first/last without order deprecated | 8.1 | Active Record |
| UPDATE with JOIN (PG/SQLite) | 8.1 | Active Record |
| PG 18 virtual generated columns | 8.1 | PostgreSQL |
| Schema columns sorted | 8.1 | Migrations |
| New exception classes | 8.1 | Active Record |
