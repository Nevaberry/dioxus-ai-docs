# IPC: Channels & Binary Response

## Channels (Streaming Primitive)

`tauri::ipc::Channel<T>` enables ordered, high-throughput data streaming from Rust to frontend. Use instead of events for progress/streaming.

### Rust Side

```rust
use serde::Serialize;
use tauri::ipc::Channel;

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase", tag = "event", content = "data")]
enum DownloadEvent {
    Started { url: String, content_length: usize },
    Progress { chunk_length: usize },
    Finished,
}

#[tauri::command]
fn download(url: String, on_event: Channel<DownloadEvent>) {
    on_event
        .send(DownloadEvent::Started {
            url: url.clone(),
            content_length: 1000,
        })
        .unwrap();
    on_event.send(DownloadEvent::Finished).unwrap();
}
```

### Frontend Side

```typescript
import { invoke, Channel } from '@tauri-apps/api/core';

const onEvent = new Channel<DownloadEvent>();
onEvent.onmessage = (message) => {
  console.log(message.event, message.data);
};
await invoke('download', { url: 'https://example.com', onEvent });
```

## Efficient Binary Returns with `ipc::Response`

Return large binary data without JSON serialization overhead:

```rust
use tauri::ipc::Response;

#[tauri::command]
fn read_file(path: String) -> Response {
    Response::new(std::fs::read(path).unwrap())
}
```
