# React useChat & UIMessage

## UIMessage parts-based architecture (v5)

`Message` -> `UIMessage`. Content is now `parts` array (no `.content`). Tool parts are typed `tool-${toolName}`.

```tsx
import { useChat } from '@ai-sdk/react';  // was 'ai/react'
import { DefaultChatTransport, lastAssistantMessageIsCompleteWithToolCalls } from 'ai';
import { useState } from 'react';

const [input, setInput] = useState('');  // no more managed input
const { messages, sendMessage, addToolOutput, status, regenerate } = useChat({
  transport: new DefaultChatTransport({ api: '/api/chat' }),
  sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithToolCalls,
  async onToolCall({ toolCall }) {
    const result = await executeTool(toolCall);
    addToolOutput({ tool: toolCall.toolName, toolCallId: toolCall.toolCallId, output: result });
    // Don't await addToolOutput inside onToolCall — causes deadlocks
  },
});
sendMessage({ text: input });  // was append({ role: 'user', content })
```

## Rendering UIMessage parts

```tsx
message.parts.map(part => {
  switch (part.type) {
    case 'text': return part.text;
    case 'reasoning': return part.text;  // was part.reasoning
    case 'file': return <img src={part.url} />;  // was part.data + part.mimeType
    case 'tool-weather':  // typed tool parts
      switch (part.state) {
        case 'input-streaming': ...   // was partial-call
        case 'input-available': ...   // was call
        case 'output-available': ...  // was result
        case 'output-error': ...      // new
      }
  }
});
```

## Framework-specific changes

- **Vue**: `useChat` replaced with `Chat` class + `DefaultChatTransport`
- **Svelte**: `Chat()` now takes factory function, properties readonly, use `setMessages()`
