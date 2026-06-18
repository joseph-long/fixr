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
>>> timings.dtype
dtype('uint64')
```

Sometimes you don't want to decompress all the data just to read the (uncompressed) timings, so this helper function skips (using `fixr.skip()`) over the first XRIF header + data chunk.

```
>>> timings = fixr.read_streamwriter_timings(fh)
>>> timings[0], timings[-1]
(array([[[  24211485, 1710543470,  994842000, 1710543470,  994896666]]],
      dtype=uint64), array([[[  24211996, 1710543471,  278731000, 1710543471,  278787539]]],
      dtype=uint64))
```

If you need both, this convenience function returns a `(data, timings)` tuple (assuming `fh` is a seekable file containing at least two XRIF headers).

```
>>> data, timings = fixr.read_streamwriter_archive(fh)
>>> data.shape, timings.shape
((512, 1, 120, 120), (512, 1, 1, 5))
```

For an example that uses the C xrif lib more directly, see [minimal_ex.py](https://github.com/joseph-long/fixr/blob/main/minimal_ex.py).

## Changelog

### 0.2.3

 - Add `skip()` function to seek to the end of an XRIF archive
 - Add `read_streamwriter_timings()` and `read_streamwriter_archive()` helpers for XWCL streamwriters which attach timing info as a trailer following compressed data.
 - Expand docstrings, add tests for new functionality

### 0.2.2 (never pushed to PyPI)

 - Add a monkey-patch to the `_xrif.xrif_read_header` argtypes to make ARM work

### 0.2.1

 - Fix macOS-ism (using `.dylib` instead of `.so` to load library)
 - Declare NumPy >= 2.0 dependency
 - Update various bits of CI machinery

### 0.2.0

 - Add missing typecodes ([#1](https://github.com/joseph-long/fixr/issues/1), [#2](https://github.com/joseph-long/fixr/pull/2))

### 0.1.0

 - Initial release
