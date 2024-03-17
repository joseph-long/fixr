# fiXr

Open xrif archives from Python directly using the [xrif](https://github.com/jaredmales/xrif) library.

## Example

```python
from fixr import xrif2numpy
fh = open('camwfs_20240315225750994842000.xrif', 'rb')
data = xrif2numpy(fh)
timings = xrif2numpy(fh)
```