# Cypher Language and Query Runtime

## Language selection

### Choose between Cypher 5 and Cypher 25 (2025.06)

Cypher 5 is frozen for compatibility, while Cypher 25 evolves with new
language behavior. Existing and new databases initially default to Cypher 5.
Choose Cypher 25 per database at creation or alteration, set
`db.query.default_language` for new and initial databases, or override one
query:

```cypher
CYPHER 25 RETURN 1 AS value
```

Starting in 2026.02, packaged `neo4j.conf` explicitly sets the default to
`CYPHER_25`. Inspect the effective database and configuration values rather
than assuming either default.

## Query composition

### Compose conditional and sequential queries (2025.06)

Cypher 25 adds `WHEN`/`ELSE` branches for conditional composition and `NEXT`
for linear composition. It accepts GQL-style curly braces around top-level
queries and around composite-query arguments such as `UNION`, `UNION ALL`,
and conditional queries.

### Filter and project without artificial boundaries (2025.06)

Use standalone `FILTER` for mid-query filtering and `LET` to add projected
variables. A `WITH` boundary is no longer required between writing and reading
clauses:

```cypher
MATCH (p:Person)
LET name = p.name
FILTER name IS NOT NULL
RETURN name
```

### Compose administration commands (2026.05.0)

Cypher 25 can combine these commands with one another and with other Cypher
statements:

- `SHOW INDEXES`
- `SHOW CONSTRAINTS`
- `SHOW CURRENT GRAPH TYPE`
- `SHOW FUNCTIONS`
- `SHOW PROCEDURES`
- `SHOW SETTINGS`
- `SHOW TRANSACTIONS`
- `SHOW DATABASES`
- `TERMINATE TRANSACTIONS`

## Paths and match modes

### Select walk or trail semantics (2025.06)

`REPEATABLE ELEMENTS` enables walk semantics, allowing a relationship to
repeat in a matched path:

```cypher
MATCH REPEATABLE ELEMENTS p = (a)-[*]->(b)
RETURN p
```

Trail semantics remains the default. Request it explicitly with
`MATCH DIFFERENT RELATIONSHIPS`.

### Combine `ACYCLIC` with restrictive selectors (2026.05.0)

Cypher 25 permits `ACYCLIC`, which prevents repeated nodes within a path, with
`ANY`, `SHORTEST`, `SHORTEST k`, `ALL SHORTEST`, and `SHORTEST k GROUPS`.

### Parameterize path patterns (2025.06)

Parameters are accepted in `SHORTEST` and `ANY` path patterns.

## Projection, unions, and properties

### State duplicate retention explicitly (2025.06)

`RETURN ALL` and `WITH ALL` explicitly retain duplicates. `UNION` and
`UNION ALL` branches whose return items appear in different orders are
supported and are no longer deprecated.

### Copy properties through a map (2025.06)

Cypher 25 does not allow a node or relationship directly on the right side of
a `SET` properties clause. Convert the entity explicitly:

```cypher
SET target = properties(source)
```

## GQL-aligned syntax

### Use label predicates (2026.04.0)

Cypher 25 supports `IS LABELED` and `IS NOT LABELED` as GQL equivalents of the
existing `IS` and `IS NOT` label predicates:

```cypher
MATCH (n)
WHERE n IS LABELED Person
RETURN n
```

### Expand lists with `FOR` (2026.04.0)

Cypher 25 supports the GQL `FOR` statement as the equivalent of `UNWIND`:

```cypher
FOR item IN [1, 2, 3]
RETURN item
```

### Validate identifier and parameter characters (2025.06)

Cypher 25 treats U+0085 NEXT LINE as whitespace rather than allowing it inside
identifiers. It rejects identifier characters that were previously
deprecated. Parameters may start with additional characters from GQL's
extended identifier-character set.

## Functions and aggregation

### Use native string functions (2026.05.0)

Cypher 25 provides `string.indexOf`, `string.join`, and
`string.regexReplace`. The matching `apoc.text.*` functions are deprecated.

The `replace()` function also accepts an optional limit argument (2025.06):

```cypher
RETURN replace('banana', 'a', 'o', 2)
```

### Account for empty-input standard deviation (2026.05.0)

`stDev()` now returns `null`, not `0`, for empty input.

### Understand imported subquery-expression variables (2025.06)

Inside Cypher 25 `COLLECT`, `COUNT`, and `EXISTS` subquery expressions,
imported variables are constants rather than aggregation grouping keys. An
aggregation can therefore produce a result when no rows match. Cypher 5 keeps
the former grouping behavior for compatibility.

## Graph references

### Use a unified composite constituent name (2025.06)

Cypher 25 requires a composite constituent reference to be one symbolic name,
such as `compdb.constituent`, rather than separate escaped parts such as
`` `compdb`.`constituent` ``. Resolution consistently infers whether the
prefix identifies a composite.

Function arguments with additional dots use the complete string reference:

```cypher
USE graph.byName("composite.with.dot.constituent")
```

Ambiguous database, alias, and constituent names are rejected in both Cypher
versions. A local constituent cannot be a user's home database and must be
accessed through its composite.

## Administrative Cypher result changes

### Inspect property uniqueness constraints (2025.06)

Cypher 25 accepts `SHOW [NODE|RELATIONSHIP] PROPERTY UNIQUENESS CONSTRAINTS`,
with `PROPERTY` optional. Result type names are
`NODE_PROPERTY_UNIQUENESS` and `RELATIONSHIP_PROPERTY_UNIQUENESS`.

The `indexProvider` option has been removed from index and constraint creation
commands.

### Consume transaction and `WAIT` results correctly (2025.06)

`SHOW TRANSACTIONS` returns `startTime` and `currentQueryStartTime` as
`ZONED DATETIME` rather than `STRING`; several unavailable transaction values
are `null`. Administration commands with `WAIT` report cluster state through
notifications instead of result rows. Revoking a privilege that cannot exist
raises an error.

## Runtime controls and corrected results

### Enable the parallel repeat heuristic only per measured query (2026.05.0)

The parallel runtime disables Repeat-over-VarExpand planning by default. The
heuristic could consume excessive memory for variable-length patterns with an
input cardinality of one. Re-enable it per query when justified:

```cypher
CYPHER parallelRepeatHeuristic=enabled
MATCH (a:A {prop: 123}) ((n)-[r:R]->(m))+ (b)
RETURN a, b
```

The only accepted values are `enabled` and `disabled`.

### Remove workarounds for corrected pipelined results

- As of 2026.05.0, the pipelined runtime no longer overcounts
  `COUNT(DISTINCT)` in plans without a leveraged order.
- As of 2026.06.0, an ordered `OR EXISTS` subquery no longer silently drops a
  result row. Corrected queries may return rows omitted by affected releases.
- As of 2026.06.0, undirected scans across multiple relationship types no
  longer omit sibling relationships. Affected scans had undercounted output by
  roughly half.

Retest expected counts and snapshots when upgrading; the corrected result set
can legitimately differ from the buggy output.

## Concurrent transaction batches

### Declare disjoint work (2026.06.0)

`CALL { … } IN CONCURRENT TRANSACTIONS` supports `DISJOINT BY`. Neo4j
schedules disjoint parallel writes before starting transactions, avoiding
lock contention and deadlocks in workloads such as unique-constraint merges
and relationship creation.
