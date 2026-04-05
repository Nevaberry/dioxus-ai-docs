# Tooling & Framework

## Structured Event Reporting (8.1)

New `Rails.event` API for structured events:

```ruby
Rails.event.notify("user.signup", user_id: 123, email: "user@example.com")

Rails.event.tagged("graphql") do
  Rails.event.notify("query.executed", duration: 42)
end

Rails.event.set_context(request_id: "abc123", shop_id: 456)
```

Subscribers implement `#emit(event)` receiving a hash with `:name`, `:payload`, `:source_location`, `:tags`, `:context`.

## Local CI (8.1)

New `config/ci.rb` DSL run by `bin/ci`:

```ruby
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

## Markdown rendering (8.1)

```ruby
class PagesController < ApplicationController
  def show
    @page = Page.find(params[:id])
    respond_to do |format|
      format.html
      format.md { render markdown: @page }  # calls @page.to_markdown
    end
  end
end
```

## credentials:fetch command (8.1)

```bash
rails credentials:fetch kamal.registry_password
# Useful in .kamal/secrets:
# KAMAL_REGISTRY_PASSWORD=$(rails credentials:fetch kamal.registry_password)
```

## Deprecated associations (8.1)

```ruby
class Author < ApplicationRecord
  has_many :posts, deprecated: true              # default: :warn mode
  has_many :posts, deprecated: { mode: :raise }  # or :notify
  has_many :posts, deprecated: { mode: :warn, backtrace: true }
end
```

Reports all usage: `author.posts`, `author.preload(:posts)`, nested attributes, etc.
