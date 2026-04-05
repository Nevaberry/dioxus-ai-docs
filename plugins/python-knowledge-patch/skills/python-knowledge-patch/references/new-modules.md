# New and Improved Standard Library Modules

## compression.zstd (PEP 784) — Python 3.14

New `compression` package with Zstandard support. Existing compression modules are also available under `compression.*` (old imports not deprecated).

```python
from compression import zstd

# Compress/decompress bytes
compressed = zstd.compress(b"data to compress")
original = zstd.decompress(compressed)

# Streaming
with zstd.open("data.zst", "wb") as f:
    f.write(b"streaming data")

# New preferred imports (old names still work, not deprecated):
from compression import lzma, bz2, gzip, zlib

# tarfile/zipfile/shutil support zstd archives
import tarfile

with tarfile.open("archive.tar.zst", "w:zst") as tar:
    tar.add("myfile.txt")
```

## functools.Placeholder — Python 3.14

Reserve positional argument positions in `partial()` and `partialmethod()`:

```python
from functools import partial, Placeholder as _

# Skip first arg, fix second to 2
pow_of_2 = partial(pow, _, 2)
pow_of_2(10)   # pow(10, 2) = 100

# Multiple placeholders
from operator import setitem
set_to_none = partial(setitem, _, _, None)
d = {"a": 1}
set_to_none(d, "a")  # setitem(d, "a", None)
```

## uuid Versions 6, 7, 8 (RFC 9562) — Python 3.14

```python
import uuid

# v6: reordered v1 for better database sorting
u6 = uuid.uuid6()

# v7: Unix timestamp + random — recommended for new designs
u7 = uuid.uuid7()  # sortable by creation time

# v8: custom/implementation-defined
u8 = uuid.uuid8()

# Special values
uuid.NIL  # 00000000-0000-0000-0000-000000000000
uuid.MAX  # ffffffff-ffff-ffff-ffff-ffffffffffff
```

## pathlib.Path Copy and Move — Python 3.14

```python
from pathlib import Path

# Copy file or directory tree
Path("src/project").copy("backup/project")
Path("report.pdf").copy_into("archive/")  # → archive/report.pdf

# Move file or directory tree
Path("old_name").move("new_name")
Path("file.txt").move_into("dest_dir/")  # → dest_dir/file.txt
```

## sys.remote_exec() / Remote Debugging (PEP 768) — Python 3.14

Attach to running Python processes without restart:

```python
import sys
# Execute script in another Python process
sys.remote_exec(pid, "/path/to/debug_script.py")
```

```bash
# Attach pdb to running process
python -m pdb -p 1234

# Inspect asyncio tasks in running process
python -m asyncio ps 1234
python -m asyncio pstree 1234
```

Disable: `PYTHON_DISABLE_REMOTE_DEBUG=1` or `-X disable-remote-debug`

## io.Reader and io.Writer Protocols — Python 3.14

Simpler alternatives to `typing.IO`, `typing.TextIO`, `typing.BinaryIO`:

```python
from io import Reader, Writer

def process(source: Reader) -> None:
    data = source.read()

def output(dest: Writer) -> None:
    dest.write("result")
```

## Other Notable Module Additions — Python 3.14

- `map(func, *iterables, strict=True)` — raises ValueError if iterables differ in length
- `heapq`: `heapify_max()`, `heappush_max()`, `heappop_max()`, `heapreplace_max()`, `heappushpop_max()`
- `datetime.date.strptime()` and `datetime.time.strptime()` class methods
- `http.server.HTTPSServer` — `python -m http.server --tls-cert cert.pem`
- `asyncio.capture_call_graph()` and `asyncio.print_call_graph()`
- `python -m json` replaces `python -m json.tool` (soft deprecated)
- `os.path.realpath(strict=os.path.ALLOW_MISSING)` — resolve symlinks, allow missing tail
- `types.UnionType` is now alias for `typing.Union` — `Union[int, str]` and `int | str` produce same type
