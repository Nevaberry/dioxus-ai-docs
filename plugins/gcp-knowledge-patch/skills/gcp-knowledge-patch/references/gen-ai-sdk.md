# Google Gen AI SDK (replaces Vertex AI SDK)

The `vertexai.generative_models` module and related packages are **deprecated** (removal after June 24, 2026). Use the unified Google Gen AI SDK instead. The new SDK works with both Gemini Developer API and Vertex AI.

## Installation

| Language | Old package | New package |
|----------|------------|-------------|
| Python | `google-cloud-aiplatform` | `pip install google-genai` |
| Node.js | `@google-cloud/vertexai` | `npm install @google/genai` |
| Go | `cloud.google.com/go/vertexai/genai` | `go get google.golang.org/genai` |
| Java | `com.google.cloud:google-cloud-vertexai` | `com.google.genai:google-genai` |

## Python — Before (deprecated)

```python
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="my-project", location="us-central1")
model = GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Hello")
```

## Python — After

```python
from google import genai
from google.genai.types import HttpOptions

client = genai.Client(http_options=HttpOptions(api_version="v1"))
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello",
)
print(response.text)
```

## Node.js

```javascript
import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({
  vertexai: true,
  project: process.env.GOOGLE_CLOUD_PROJECT,
  location: process.env.GOOGLE_CLOUD_LOCATION,
});
const response = await ai.models.generateContent({
  model: 'gemini-2.5-flash',
  contents: 'Hello',
});
console.log(response.text);
```

## Go

```go
client, _ := genai.NewClient(ctx, genai.ClientConfig{
    HTTPOptions: genai.HTTPOptions{APIVersion: "v1"},
})
resp, _ := client.Models.GenerateContent(ctx,
    "gemini-2.5-flash",
    genai.Text("Hello"),
    nil,
)
fmt.Println(resp.Text())
```

## Environment Variables for Vertex AI

```bash
export GOOGLE_CLOUD_PROJECT=my-project
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_VERTEXAI=True
```

## Vertex AI Express Mode

Use API key instead of ADC:

```python
client = genai.Client(vertexai=True, api_key="YOUR_API_KEY")
```

## Key API Pattern Changes

- **Config objects**: Pass configuration via typed config objects:
  ```python
  config=types.GenerateContentConfig(system_instruction=..., temperature=0.3)
  ```

- **Function calling**: Pass Python functions directly as tools:
  ```python
  config=types.GenerateContentConfig(tools=[my_function])
  ```

- **Embeddings**:
  ```python
  client.models.embed_content(
      model="gemini-embedding-001",
      contents="text",
      config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
  )
  ```

- **Caching**:
  ```python
  client.caches.create(
      model=...,
      config=CreateCachedContentConfig(contents=..., ttl="86400s"),
  )
  ```

- **Chat**:
  ```python
  chat = client.chats.create(model="gemini-2.5-flash", config=...)
  ```
