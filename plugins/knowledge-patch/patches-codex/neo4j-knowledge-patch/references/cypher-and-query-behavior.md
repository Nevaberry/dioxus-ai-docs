# Cypher and Query Behavior

Use this reference when selecting a language version, adopting Cypher 25
syntax, or updating tests and consumers for corrected runtime behavior.

## Language selection and defaults

The `2025.06` line provides frozen, compatibility-focused Cypher 5 alongside
evolving Cypher 25. Existing and new databases initially defaulted to Cypher 5.
Choose Cypher 25 per database at creation or alteration, set
`db.query.default_language` for new and initial databases, or override one
query:

```cypher
CYPHER 25 RETURN 1 AS value
```

Starting in 2026.02, distributed `neo4j.conf` explicitly sets
`db.query.default_language=CYPHER_25`. New deployments that use the packaged
file therefore default newly created databases to Cypher 25, while retained
configuration can preserve earlier behavior.

## Query composition

### Conditional and sequential queries

Cypher 25 adds `WHEN`/`ELSE` for conditional query composition and `NEXT` for
linear composition. GQL-style curly braces are accepted around top-level
queries and around arguments to composite queries such as `UNION`, `UNION ALL`,
and conditional queries.

### Standalone `FILTER` and `LET`

Use `FILTER` for mid-query filtering and `LET` to add projected variables. A
`WITH` boundary is no longer required between writing and reading clauses.

```cypher
MATCH (p:Person)
LET name = p.name
FILTER name IS NOT NULL
RETURN name
```

### Explicit duplicate retention and reordered unions

`RETURN ALL` and `WITH ALL` explicitly retain duplicates. `UNION` and
`UNION ALL` branches whose return items use different ordering are supported
and are no longer deprecated.

### Composable commands

Cypher 25 can combine several commands in one query and mix them with other
statements. The composable commands are:

```text
SHOW INDEXES
SHOW CONSTRAINTS
SHOW CURRENT GRAPH TYPE
SHOW FUNCTIONS
SHOW PROCEDURES
SHOW SETTINGS
SHOW TRANSACTIONS
SHOW DATABASES
TERMINATE TRANSACTIONS
```

## GQL-compatible syntax

### Label predicates

Cypher 25 accepts GQL `IS LABELED` and `IS NOT LABELED` as equivalents of
Cypher `IS` and `IS NOT` label predicates (since `2026.04.0`).

```cypher
MATCH (n)
WHERE n IS LABELED Person
RETURN n
```

### `FOR` statement

Cypher 25 supports GQL `FOR` to extract rows from a list; it is equivalent to
`UNWIND`.

```cypher
FOR item IN [1, 2, 3]
RETURN item
```

### Identifier and parameter characters

Cypher 25 treats U+0085 NEXT LINE as whitespace, not as an identifier
character, and rejects previously deprecated identifier characters. Parameters
may begin with more characters from GQL's extended identifier character set.

## Path semantics

### Match modes

Trail semantics remains the default and can be requested as
`MATCH DIFFERENT RELATIONSHIPS`. `REPEATABLE ELEMENTS` uses walk semantics and
allows a relationship to repeat in a matched path.

```cypher
MATCH REPEATABLE ELEMENTS p = (a)-[*]->(b)
RETURN p
```

### `ACYCLIC` with restrictive selectors

Cypher 25 permits `ACYCLIC`, which prevents repeated nodes in a path, with
`ANY`, `SHORTEST`, `SHORTEST k`, `ALL SHORTEST`, and `SHORTEST k GROUPS`.

### Parameterized path patterns

Parameters are permitted in `SHORTEST` and `ANY` path patterns.

## Expressions and functions

### Limited replacement

Cypher 25 adds an optional limit argument to `replace()`:

```cypher
RETURN replace('banana', 'a', 'o', 2)
```

### Native string functions

Cypher 25 adds `string.indexOf`, `string.join`, and `string.regexReplace`. The
corresponding `apoc.text.*` functions are deprecated (since `2026.05.0`).

### Copying entity properties

A node or relationship can no longer appear directly on the right side of a
Cypher 25 `SET` properties clause. Convert the entity explicitly:

```cypher
SET target = properties(source)
```

### Subquery-expression aggregation

Inside Cypher 25 `COLLECT`, `COUNT`, and `EXISTS` subquery expressions,
imported variables are constants rather than aggregation grouping keys. An
aggregation can therefore produce a result even when no rows match. Cypher 5
retains the previous grouping behavior.

### Empty-input standard deviation

`stDev()` returns `null`, rather than `0`, for empty input.

## Graph references

Cypher 25 requires a composite constituent to be one symbolic reference such
as `compdb.constituent`, not separately quoted parts such as
`` `compdb`.`constituent` ``. Resolution infers whether the prefix names a
composite.

Function arguments that contain more dots use the complete string reference:

```cypher
USE graph.byName("composite.with.dot.constituent")
```

Ambiguous database, alias, and constituent names are rejected in Cypher 5 and
Cypher 25. A local constituent cannot be a user's home database and must be
accessed through its composite.

## Administration result contracts

In Cypher 25, `SHOW TRANSACTIONS` returns `startTime` and
`currentQueryStartTime` as `ZONED DATETIME`, not `STRING`. Several transaction
columns now use `null` for unavailable values.

Administration commands with `WAIT` report cluster state as notifications
rather than result rows. Revoking a privilege that cannot exist raises an
error.

`db.schema.nodeTypeProperties()` and `db.schema.relTypeProperties()` return
Cypher type names, not Java type names, in `propertyTypes`. Update parsers and
expected vocabularies.

`EXPLAIN` and `PROFILE` consistently report the underlying point-release
version in query plans. Tools comparing plan text must accept the more detailed
value.

## Parallel and pipelined runtimes

### Parallel Repeat-over-VarExpand heuristic

The parallel runtime disables its Repeat-over-VarExpand planning heuristic by
default because variable-length patterns with input cardinality one could use
excessive memory. Restore it for one query only when needed:

```cypher
CYPHER parallelRepeatHeuristic=enabled
MATCH (a:A {prop: 123}) ((n)-[r:R]->(m))+ (b)
RETURN a, b
```

The accepted values are `enabled` and `disabled`.

### Corrected result behavior

- In the pipelined runtime, `COUNT(DISTINCT)` no longer overcounts when a plan
  lacks a leveraged order.
- An ordered `OR EXISTS` subquery no longer silently loses a result row (since
  `2026.06.0`). A corrected query can return rows an earlier runtime omitted.
- Undirected scans over multiple relationship types no longer omit sibling
  relationships. Affected scans had undercounted by roughly half.

## Concurrent transaction batching

`CALL { … } IN CONCURRENT TRANSACTIONS` supports `DISJOINT BY`. It schedules
disjoint parallel write work before transactions start, avoiding lock
contention and deadlocks in cases such as merges under unique constraints and
relationship creation.

## Graph types

`GRAPH TYPE` is generally available for production schema definition,
enforcement, and validation. `SHOW CURRENT GRAPH TYPE AS GRAPH` returns lists
of virtual nodes and relationships instead of a string representation:

```cypher
SHOW CURRENT GRAPH TYPE AS GRAPH
```

## Vector `SEARCH`

Cypher 25 vector searches support `IN` within the filter predicate:

```cypher
MATCH (movie:Movie)
SEARCH movie IN (
  VECTOR INDEX moviePlots
  FOR $queryVector
  WHERE movie.genre IN ['Horror', 'SciFi']
  LIMIT $topK
)
RETURN movie.title AS title, movie.rating AS rating
```

`db.index.vector.queryNodes()` and
`db.index.vector.queryRelationships()` are deprecated in Cypher 25; prefer
`SEARCH`. `db.index.vector.createNodeIndex()` is removed in favor of
`CREATE VECTOR INDEX`, and `db.create.setVectorProperty()` is removed in favor
of `db.create.setNodeVectorProperty()`.
