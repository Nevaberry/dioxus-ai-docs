# Google Gen AI SDK Migration

## Replace legacy packages

Use the GA packages and centralized clients:

| Language | Replace | With |
| --- | --- | --- |
| Python | `google-generativeai` | `google-genai` |
| JavaScript | `@google/generative-ai` | `@google/genai` |
| Go | `github.com/google/generative-ai-go` | `google.golang.org/genai` |

Model objects and separate file or cache managers become services on one
client.

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="MODEL_ID", contents="Hello"
)
```

```javascript
import {GoogleGenAI} from "@google/genai";

const ai = new GoogleGenAI({apiKey: process.env.GEMINI_API_KEY});
const response = await ai.models.generateContent({
  model: "MODEL_ID",
  contents: "Hello",
});
```

```go
import "google.golang.org/genai"

client, err := genai.NewClient(ctx, nil)
result, err := client.Models.GenerateContent(
    ctx, "MODEL_ID", genai.Text("Hello"), nil)
```

## Put configuration on each call

Generation settings no longer live on a model instance. Pass optional inputs
under each call's `config`, using dictionaries or classes from
`google.genai.types`.

Python async methods mirror the synchronous services under `client.aio`; they
do not use an `_async` suffix:

```python
response = await client.aio.models.generate_content(
    model="MODEL_ID",
    contents="Hello",
    config={"max_output_tokens": 200},
)
```

## Update JavaScript response and stream access

Generation returns the response itself. Read the `response.text` property,
not `result.response.text()`. `generateContentStream` returns the async
iterable directly rather than an object with a `.stream` member:

```javascript
const stream = await ai.models.generateContentStream({
  model: "MODEL_ID",
  contents: "Write a story.",
});
for await (const chunk of stream) process.stdout.write(chunk.text);
```

## Control automatic Python function execution

Passing a Python callable in `tools` to `generate_content` executes it
automatically by default. Disable automatic function calling when the
application must inspect and dispatch the call itself:

```python
response = client.models.generate_content(
    model="MODEL_ID",
    contents="What is the weather?",
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling={"disable": True},
    ),
)
call = response.candidates[0].content.parts[0].function_call
```

The legacy SDK only performed automatic calling in chat and only when it was
explicitly enabled, so audit migrations for unintended function execution.

## Parse structured responses into Pydantic models

Python accepts Pydantic model classes as structured-output schemas. The SDK
validates returned JSON and exposes the instance at `response.parsed`:

```python
class Answer(BaseModel):
    value: str

response = client.models.generate_content(
    model="MODEL_ID",
    contents="Answer the question.",
    config={
        "response_mime_type": "application/json",
        "response_schema": Answer,
    },
)
answer = response.parsed
```

## Reference cached content by name

Create caches through `client.caches`, then pass the returned cache name in
generation configuration. Do not construct a replacement model object from
the cache.

```python
cache = client.caches.create(
    model="MODEL_ID", config={"contents": [document]}
)
response = client.models.generate_content(
    model="MODEL_ID",
    contents="Summarize it.",
    config=types.GenerateContentConfig(cached_content=cache.name),
)
```

## Read plural JavaScript embeddings

`ai.models.embedContent` accepts `contents` and returns `result.embeddings`,
not the legacy singular `result.embedding`. Put output dimensionality in the
request `config`:

```javascript
const result = await ai.models.embedContent({
  model: "EMBEDDING_MODEL_ID",
  contents: "Hello world",
  config: {outputDimensionality: 10},
});
console.log(result.embeddings);
```

Batch attribution: `genai-sdk-migration`.
