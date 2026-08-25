# Full-Text Search

## Multilingual tokenization

The `multilingual` tokenizer handles languages without whitespace word
boundaries, including Japanese and Chinese, without custom builds or external
preprocessing (since 1.15.0):

```http
PUT /collections/{collection_name}/index
{
  "field_name": "description",
  "field_index_params": {"type": "text", "tokenizer": "multilingual"}
}
```

## Configurable stop words

A full-text index can remove configured stop words automatically rather than
requiring callers to strip them from each query (since 1.15.0):

```http
PUT /collections/{collection_name}/index
{
  "field_name": "title",
  "field_index_params": {"type": "text", "stopwords": "english"}
}
```

## Snowball stemming

A language-specific Snowball stemmer normalizes grammatical variants to common
roots, increasing matches between related word forms (since 1.15.0):

```http
PUT /collections/{collection_name}/index
{
  "field_name": "body",
  "field_index_params": {
    "type": "text",
    "stemmer": {"type": "snowball", "language": "english"}
  }
}
```

## Exact phrase matching

Enable `phrase_matching` when creating the full-text index; it builds an
additional data structure and cannot be supplied only at query time (since
1.15.0). Then use `match.phrase` to require the words in order:

```http
PUT /collections/{collection_name}/index
{
  "field_name": "headline",
  "field_index_params": {"type": "text", "phrase_matching": true}
}

POST /collections/{collection_name}/points/query
{
  "query": [0.01, 0.45, 0.67, 0.12],
  "filter": {
    "must": {
      "key": "headline",
      "match": {"phrase": "machine time"}
    }
  },
  "limit": 10
}
```

## Match-any full-text queries

`text_any` tokenizes a multi-term query and matches a text field containing at
least one term (since 1.16.0). It replaces client-built `should` filters with a
single condition:

```json
{
  "match": {
    "text_any": "apple banana cherry"
  }
}
```

## ASCII folding

Set `ascii_folding` to `true` when creating a full-text payload index to
normalize diacritics in both indexed text and search terms (since 1.16.0). For
example, `cafe` can then match `café`.

```json
{
  "type": "text",
  "ascii_folding": true
}
```
