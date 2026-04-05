# Active Record Columns & Serialization

## ActiveRecord::Base.only_columns (8.1)

Inverse of `ignored_columns` — list columns to consider rather than ones to ignore:

```ruby
class User < ApplicationRecord
  self.only_columns = %w[id name email]
end
```

## update_column/update_columns touch option (8.1)

```ruby
user.update_column(:nice, true, touch: true)        # also updates updated_at
user.update_columns(last_ip: request.remote_ip, touch: true)
```

## Serialized comparable attributes (8.1)

Compare deserialized values instead of serialized strings (avoids false dirty tracking):

```ruby
serialize :config, type: Hash, coder: JSON, comparable: true
```

## ActiveRecord::Coder::JSON instantiation (8.1)

Pass options to JSON coder:

```ruby
serialize :config, coder: ActiveRecord::Coder::JSON.new(symbolize_names: true)
```

## PostgreSQL 18 virtual generated columns (8.1)

Virtual (not persisted) generated columns are now default on PG 18+ (use `stored: true` for stored):

```ruby
create_table :users do |t|
  t.string :name
  t.virtual :lower_name, type: :string, as: "LOWER(name)"          # virtual on PG 18+
  t.virtual :name_length, type: :integer, as: "LENGTH(name)", stored: true  # stored
end
```
