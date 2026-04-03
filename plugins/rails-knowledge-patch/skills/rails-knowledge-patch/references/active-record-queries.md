# Active Record Queries & Schema

## params.expect replaces require/permit (8.0)

```ruby
# New preferred way (safer, more explicit)
params.expect(post: [:title, :body])
# replaces: params.require(:post).permit(:title, :body)
```

## SQLite virtual tables (8.0)

```ruby
create_virtual_table :posts_search, :fts5, ["content", "title"]
```

## Custom batch columns (8.0)

```ruby
Product.in_batches(cursor: [:shop_id, :id]) do |relation|
  # batches using composite cursor
end
```

## Pluck with hash for joined tables (8.0)

```ruby
Post.joins(:comments).pluck(:id, comments: :id)
```

## db:migrate on fresh database (8.0)

Running `db:migrate` on a fresh database now loads the schema first, then runs only pending migrations. Use `db:migrate:reset` for the old behavior of running all migrations from scratch.

## UPDATE with JOIN for PostgreSQL and SQLite3 (8.1)

```ruby
Comment.joins(:post).update_all("title = posts.title")
```

Previously only supported by MySQL. Now works for PostgreSQL and SQLite3 (without LIMIT/ORDER/GROUP BY).

## #first/#last without order deprecated (8.1)

Using order-dependent finders without explicit `order` is deprecated. Configure:

```ruby
# config/application.rb (Rails 8.1 default)
config.active_record.raise_on_missing_required_finder_order_columns = true
```

Raises `ActiveRecord::MissingRequiredOrderError` if no `order`, `implicit_order_column`, `query_constraints`, or `primary_key` to fall back on.

## Schema columns sorted alphabetically (8.1)

Columns in `schema.rb` are now sorted alphabetically instead of by creation order. Reduces merge conflicts.

## skip_transactional_tests_for_database (8.1)

Per-database transactional test control:

```ruby
class MostlyTransactionalTest < ActiveSupport::TestCase
  self.use_transactional_tests = true
  skip_transactional_tests_for_database :shared
end
```

## New exception classes (8.1)

- `ActiveRecord::CheckViolation` — check constraint violations
- `ActiveRecord::ExclusionViolation` — PostgreSQL exclusion constraint violations

## Other query-related changes (8.1)

- `affected_rows` added to `ActiveRecord::Result`
- `rename_schema` method for PostgreSQL
- `reset_counters` accepts array of IDs: `Aircraft.reset_counters([1, 2, 3], :wheels_count)`
