# Environment & Compatibility (2.6–2.11)

## BREAKING: torch.load defaults to weights_only=True (2.6)

`torch.load("file.pt")` now uses `weights_only=True` by default. Loading serialized `nn.Module`s will fail. Use `weights_only=False` explicitly for those cases. For tensor subclasses/numpy arrays, use `torch.serialization.safe_globals` to allowlist classes.

```python
# Old code that breaks:
model = torch.load("model.pt")  # fails if saved with torch.save(model)

# Fix: load state_dict (recommended)
model.load_state_dict(torch.load("model.pt", weights_only=True))

# Fix: explicitly opt into unsafe loading
model = torch.load("model.pt", weights_only=False)
```

## CUDA 13 Default (2.11)

CUDA 13 is now the default installed version. CUDA 12.8 builds still available via `download.pytorch.org/whl/cu128`.

## Python 3.14 Support (2.10)

torch.compile works with Python 3.14. Python 3.14t (free-threaded) experimentally supported.

## DebugMode for Numerical Debugging (2.10)

Track dispatched ops and hash tensors to find where numerical divergence occurs.

```python
from torch.debugging import DebugMode

with DebugMode():
    output = model(x)
# Logs all dispatched ops with tensor hashes
# Compare hashes between two runs to find divergence point
```
