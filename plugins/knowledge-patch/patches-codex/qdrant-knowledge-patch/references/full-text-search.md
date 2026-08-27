# Full-Text Search

Use this reference when creating text payload indexes or building text and
keyword filter conditions. Index-time capabilities must be enabled before the
corresponding query forms can work.

## Tokenization and normalization

### Multilingual tokenizer (since 1.15.0)

The built-in `multilingual` tokenizer handles languages without whitespace word
boundaries, including Japanese and Chinese. It avoids a custom build or
external word-segmentation preprocessing for these languages.

```http
PUT /collections/{collection_name}/index
{
  "field_name": "description",
  "field_index_params": {
    "type": "text",
    "tokenizer": "multilingual"
  }
}
```

Select tokenization per indexed field. Validate mixed-language content and the
actual query vocabulary rather than assuming one tokenizer is optimal for
every language.

### Configurable stop words (since 1.15.0)

A full-text index can remove configured stop words during analysis. Use the
index option instead of requiring every client to strip the same words.

```http
PUT /collections/{collection_name}/index
{
  "field_name": "title",
  "field_index_params": {
    "type": "text",
    "stopwords": "english"
  }
}
```

Stop-word removal can discard meaningful domain terms. Test recall with the
chosen language configuration before adopting it broadly.

### Snowball stemming (since 1.15.0)

Configure a language-specific Snowball stemmer to normalize grammatical
variants to common roots. This can increase matches between related word forms.

```http
PUT /collections/{collection_name}/index
{
  "field_name": "body",
  "field_index_params": {
    "type": "text",
    "stemmer": {
      "type": "snowball",
      "language": "english"
    }
  }
}
```

Stemming changes token equivalence, so evaluate precision as well as recall.

### ASCII folding (since 1.16.0)

Set `ascii_folding` to `true` at full-text index creation to normalize
diacritics in indexed text and search input. It allows a query such as `cafe`
to match `café`.

```json
{
  "type": "text",
  "ascii_folding": true
}
```

Folding is index configuration, not merely a client query transformation.
Recreate or configure the relevant index before relying on folded matching.

## Query forms

### Exact phrase matching (since 1.15.0)

Set `phrase_matching: true` when creating the full-text index. Qdrant builds an
additional data structure for word-order matching. Query with `match.phrase` to
require the words in the supplied order.

```http
PUT /collections/{collection_name}/index
{
  "field_name": "headline",
  "field_index_params": {
    "type": "text",
    "phrase_matching": true
  }
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

Do not treat phrase matching as an implicit capability of every text index; it
must be provisioned ahead of the query.

### Match any analyzed term (since 1.16.0)

`text_any` tokenizes a multi-term query and matches a text field containing at
least one resulting term. It replaces a client-generated `should` condition for
each token with one match condition.

```json
{
  "match": {
    "text_any": "apple banana cherry"
  }
}
```

The index analyzer determines the terms, so keep tokenizer, stop words,
stemming, and folding in mind when predicting matches.

### Keyword prefix matching (since 1.19.0)

Keyword filters accept `"match": {"prefix": "..."}`. Prefix support must be
enabled on the keyword index before the condition can be used. Enable it only
for fields that require prefix access, then test both matching and resource
cost.

## Index design workflow

1. Classify the field as analyzed text or exact keyword data.
2. Select multilingual tokenization when whitespace segmentation is
   insufficient.
3. Decide whether stop words, language stemming, and ASCII folding reflect the
   product's expected equivalence rules.
4. Enable phrase structures or keyword prefix support at index creation when
   queries require them.
5. Build tests containing diacritics, grammatical variants, stop words,
   no-whitespace languages, exact phrases, and prefixes.
6. Recreate or migrate an index when a newly required capability is absent.

## Common mistakes

- Stripping stop words differently in each client instead of configuring one
  index policy.
- Using a whitespace tokenizer for Japanese or Chinese and compensating with
  ad hoc preprocessing.
- Sending `match.phrase` to an index created without `phrase_matching`.
- Assuming `text_any` bypasses the configured analyzer.
- Enabling ASCII folding at query time only.
- Sending keyword prefix conditions before enabling prefix support on the
  index.
