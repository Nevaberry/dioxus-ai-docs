# Strings and Paths

## `String::extend_from_within`

Extend a string by copying a range from itself.

```rust
let mut s = String::from("Hello");
s.extend_from_within(0..3);  // Copy "Hel"
assert_eq!(s, "HelloHel");
```

## `String::into_raw_parts` / `Vec::into_raw_parts`

Decompose owned collections into raw components.

```rust
let s = String::from("Hello");
let (ptr, len, capacity) = s.into_raw_parts();
let s = unsafe { String::from_raw_parts(ptr, len, capacity) };

let v = vec![1, 2, 3];
let (ptr, len, capacity) = v.into_raw_parts();
let v = unsafe { Vec::from_raw_parts(ptr, len, capacity) };
```

## `OsStr::display` / `OsString::display`

Display OS strings with lossy UTF-8 conversion.

```rust
use std::ffi::OsStr;
let path = OsStr::new("/tmp/файл.txt");
println!("Path: {}", path.display());
```

## `OsString::leak` / `PathBuf::leak`

Leak to get `&'static` references.

```rust
let os_string = OsString::from("hello");
let leaked: &'static OsStr = os_string.leak();

let path_buf = PathBuf::from("/tmp/file.txt");
let leaked_path: &'static Path = path_buf.leak();
```

## `Path::file_prefix`

Get filename without any extensions (unlike `file_stem` which only removes the last).

```rust
use std::path::Path;

let path = Path::new("/tmp/archive.tar.gz");
assert_eq!(path.file_stem(), Some("archive.tar".as_ref()));   // Removes .gz only
assert_eq!(path.file_prefix(), Some("archive".as_ref()));     // Removes all extensions
```

## `PathBuf::add_extension` / `with_added_extension`

Add extensions without replacing existing ones.

```rust
use std::path::PathBuf;

let mut path = PathBuf::from("archive.tar");
path.add_extension("gz");
assert_eq!(path, PathBuf::from("archive.tar.gz"));

let path = PathBuf::from("data.json");
let backup = path.with_added_extension("bak");
assert_eq!(backup, PathBuf::from("data.json.bak"));
```

## `str::from_utf8` Inherent Methods

UTF-8 conversion directly on `str`.

```rust
let bytes = b"hello";
let s = str::from_utf8(bytes)?;
let s = str::from_utf8_mut(&mut bytes.clone())?;
```

## CStr/CString Cross-Type Comparison

Compare C strings directly across types.

```rust
use std::ffi::{CStr, CString};
use std::borrow::Cow;

let cstr: &CStr = c"hello";
let cstring: CString = CString::new("hello").unwrap();
let cow: Cow<CStr> = Cow::Borrowed(c"hello");

assert!(cstr == cstring);
assert!(cstring == cow);
```
