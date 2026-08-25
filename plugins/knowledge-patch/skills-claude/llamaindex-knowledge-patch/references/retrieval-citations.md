# Retrieval and citations

## Preserve explicit zero and omitted conjunctions

In `0.14.24`, MMR embedding search honors an explicit `mmr_threshold=0`.
`MetadataFilters(condition=None)` now defaults to AND. Remove truthiness
workarounds for zero thresholds and avoid supplying a redundant conjunction
merely to obtain AND behavior.

## Use asynchronous reranking directly

`LLMRerank` implements an asynchronous reranking path. Async query pipelines
no longer need to force the postprocessor through synchronous execution.

## Treat citations as independent fragments

`CitationQueryEngine` gives each derived citation node an independent ID and
offsets. Consumers should use those identities and spans to distinguish and
locate citation fragments rather than assuming that every fragment shares its
source node's identity.
