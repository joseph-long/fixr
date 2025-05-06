# fiXr

Open xrif archives from Python directly using the [xrif](https://github.com/jaredmales/xrif) library.

## Example

```python
from fixr import xrif2numpy
import logging
logging.basicConfig(level='DEBUG')
fh = open('example_data/camwfs_20240315225750994842000.xrif', 'rb')
data = xrif2numpy(fh)
```
which will print something like

```
DEBUG:fixr:xrif compression details:
  difference method:  previous
  reorder method:     bytepack
  compression method: LZ4
    LZ4 acceleration: 1
  dimensions:         120 x 120 x 1 x 512
  raw size:           14745600 bytes
  encoded size:       7446095 bytes
  ratio:              0.505
```

The file ends with the timing information for the frames, stored as a separate xrif section:

```python
timings = xrif2numpy(fh)
```

Each row contains the frame index, acquisition timestamp (as integer seconds and integer nanoseconds), and write timestamp (again as two integers).

```
>>> timings.shape
(787, 1, 1, 5)
```

For an example that uses the C xrif lib more directly, see [minimal_ex.py](https://github.com/joseph-long/fixr/blob/main/minimal_ex.py).

## Changelog

### 0.2.1

 - Fix macOS-ism (using `.dylib` instead of `.so` to load library)
 - Declare NumPy >= 2.0 dependency
 - Update various bits of CI machinery

### 0.2.0

 - Add missing typecodes ([#1](https://github.com/joseph-long/fixr/issues/1), [#2](https://github.com/joseph-long/fixr/pull/2))

### 0.1.0

 - Initial release