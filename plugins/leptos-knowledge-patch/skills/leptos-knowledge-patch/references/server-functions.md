# Server Functions

## `Bitcode` Encoding (0.8.11)

New `Bitcode` encoding option for server function IO, alongside existing `Json`, `Cbor`, `GetUrl`, `PostUrl`, `Streaming`, and `SerdeLite` encodings. Bitcode is a compact binary format.

**Requires:** the `bitcode` feature on `server_fn`.

```rust
#[server(endpoint = "my_fn", encoding = "Bitcode")]
pub async fn my_server_fn(data: MyData) -> Result<MyResponse, ServerFnError> {
    // ...
}
```

### Available encodings reference

| Encoding | Format | Feature flag |
|---|---|---|
| `Json` | JSON (default) | — |
| `PostUrl` | URL-encoded POST | — |
| `GetUrl` | URL-encoded GET | — |
| `Cbor` | CBOR binary | `cbor` |
| `Bitcode` | Bitcode binary | `bitcode` |
| `SerdeLite` | Lightweight serde | `serde-lite` |
| `Streaming` | Streaming response | — |
