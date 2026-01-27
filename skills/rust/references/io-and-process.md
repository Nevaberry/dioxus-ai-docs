# I/O and Process

## Anonymous Pipes

Cross-platform anonymous pipes for capturing output.

```rust
use std::io::{self, Read};
use std::process::Command;

let (mut recv, send) = io::pipe()?;

let mut child = Command::new("cargo")
    .arg("build")
    .stdout(send.try_clone()?)
    .stderr(send)
    .spawn()?;

let mut output = String::new();
recv.read_to_string(&mut output)?;
child.wait()?;
```

New types: `io::PipeReader`, `io::PipeWriter`.

## `i128`/`u128` in FFI

128-bit integers work in `extern "C"` without warnings. ABI-compatible with C's `__int128` where available.

```rust
extern "C" {
    fn process_big_int(value: i128) -> u128;
}

#[no_mangle]
pub extern "C" fn export_big_int(x: i128, y: i128) -> i128 {
    x + y
}
```

## Cross-Compiled Doctests

Run doctests for different targets:

```bash
cargo test --doc --target <target>
```

Skip platform-specific doctests:

```rust
/// ```ignore-x86_64
/// // Won't run on x86_64
/// ```
///
/// ```ignore-macos,ignore-windows
/// // Linux-specific test
/// ```
pub fn platform_specific() {}
```

## TCP Quick ACK (Linux)

Control TCP delayed acknowledgment.

```rust
use std::net::TcpStream;
use std::os::linux::net::TcpStreamExt;

let stream = TcpStream::connect("127.0.0.1:8080")?;
stream.set_quickack(true)?;  // Disable delayed ACK
let quickack = stream.quickack()?;
```

## New `io::ErrorKind` Variants

- `QuotaExceeded`
- `CrossesDevices`
