# Google Gen AI SDK migration

## Replace legacy packages and model objects

Use the GA packages:

| Language | Legacy | Current |
|---|---|---|
| Python | `google-generativeai` | `google-genai` |
| JavaScript | `@google/generative-ai` | `@google/genai` |
| Go | `github.com/google/generative-ai-go` | `google.golang.org/genai` |

Create one client. Models, files, caches, and other managers are services on
that client rather than separate model or manager objects.

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

## Configure each call and use `client.aio`

Generation settings belong in each call's `config`, as dictionaries or typed
classes from `google.genai.types`. Python asynchronous methods mirror the sync
surface below `client.aio`; they do not use an `_async` suffix.

```python
response = await client.aio.models.generate_content(
    model="MODEL_ID",
    contents="Hello",
    config={"max_output_tokens": 200},
)
```

## Read flattened JavaScript responses and streams

Generation returns the response itself. Read `response.text` as a property,
not `result.response.text()`. `generateContentStream` returns its async iterable
directly, not an object with a `.stream` member.

```javascript
const stream = await ai.models.generateContentStream({
  model: "MODEL_ID",
  contents: "Write a story.",
});
for await (const chunk of stream) process.stdout.write(chunk.text);
```

## Decide whether Python should execute functions

Passing a Python callable in `tools` now executes it automatically. Disable
automatic function calling when the application must inspect, authorize, or
dispatch the call itself.

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

## Use parsed Python structured responses

A Pydantic class can be the `response_schema`. The SDK validates returned JSON
and exposes an instance through `response.parsed`.

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

## Reference cached content from generation config

Create caches through `client.caches`, then pass the returned name in
generation config. Do not create a replacement model object from the cache.

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

## Handle plural JavaScript embeddings

`ai.models.embedContent` accepts `contents` and returns `result.embeddings`,
not the legacy singular `result.embedding`. Put output dimensionality in
request `config`.

```javascript
const result = await ai.models.embedContent({
  model: "EMBEDDING_MODEL_ID",
  contents: "Hello world",
  config: {outputDimensionality: 10},
});
console.log(result.embeddings);
```
