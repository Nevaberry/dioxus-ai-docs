# Gemini Model Lineup (as of March 2026)

| Model | ID | Status |
|-------|----|--------|
| Gemini 2.0 Flash | `gemini-2.0-flash` | GA (retires June 2026) |
| Gemini 2.5 Pro | `gemini-2.5-pro` | GA |
| Gemini 2.5 Flash | `gemini-2.5-flash` | GA |
| Gemini 2.5 Flash-Lite | `gemini-2.5-flash-lite` | GA |
| Gemini 3 Flash | `gemini-3-flash` | Preview |
| Gemini 3.1 Pro | `gemini-3.1-pro` | Preview |
| Gemini 3.1 Flash-Lite | `gemini-3.1-flash-lite-preview` | Preview |

## Image Generation

Imagen endpoints are deprecated. Use Gemini models with image generation:

- `gemini-2.5-flash-image` — GA
- `gemini-3.1-flash-image` — Preview

## Embeddings

Use `gemini-embedding-001` (replaces the `text-embedding-005` series).

```python
client.models.embed_content(
    model="gemini-embedding-001",
    contents="text to embed",
    config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
)
```
