import ctypes
import numpy as np
from fixr import _xrif as xrif
# open file in binary mode
fh = open('./example_data/camwfs_20240315225750994842000.xrif', 'rb')

# allocate and initialize xrif handle
reader = xrif.xrif_t()
xrif.xrif_new(reader)

# read one header's worth of bytes
buf = fh.read(xrif.XRIF_HEADER_SIZE)
header_size_ptr = ctypes.c_uint32()
# populate header fields in reader
xrif.xrif_read_header(reader, header_size_ptr, buf)


def describe_xrif(reader):
    # helper to turn turn byte strings into Python strings
    get_string = lambda x: xrif.string_cast(x)

    # construct a report like xrif2fits has
    s = 'xrif compression details:\n'
    difference_method = get_string(xrif.xrif_difference_method_string(reader.contents.difference_method))
    s += f"  difference method:  {difference_method}\n"
    reorder_method = get_string(xrif.xrif_reorder_method_string(reader.contents.reorder_method))
    s += f"  reorder method:     {reorder_method}\n"
    compress_method = get_string(xrif.xrif_compress_method_string(reader.contents.compress_method))
    s += f"  compression method: {compress_method}\n"
    if reader.contents.compress_method == xrif.XRIF_COMPRESS_LZ4:
        s += f"    LZ4 acceleration: {int(reader.contents.lz4_acceleration)}\n"

    s += f"  dimensions:         {reader.contents.width} x {reader.contents.height} x {reader.contents.depth} x {reader.contents.frames}\n"
    raw_size = reader.contents.width * reader.contents.height * reader.contents.depth * reader.contents.frames * reader.contents.data_size
    s += f"  raw size:           {raw_size} bytes\n"
    compressed_size = int(reader.contents.compressed_size)
    s += f"  encoded size:       {compressed_size} bytes\n"
    s += f"  ratio:              {compressed_size / raw_size:.3f}\n"

    return s
print(describe_xrif(reader))

# we don't need the reordering buffer, let xrif handle it (remember to free later)
rv = xrif.xrif_allocate_reordered(reader)
if rv != xrif.XRIF_NOERROR:
    raise RuntimeError("??")

# xrif can save you a buffer by decompressing into the raw buffer but that
# means it needs to be bigger than just `compressed_size`
min_buf_size = xrif.xrif_min_raw_size(reader)
# we need to own the raw (and then decompressed) buffer
buf = ctypes.c_buffer(min_buf_size)
# we're only filling the first `compressed_size` bytes
buf[:reader.contents.compressed_size] = fh.read(reader.contents.compressed_size)
# acquaint xrif with our arrangements
xrif.xrif_set_raw(reader, buf, min_buf_size)
# do the business
xrif.xrif_decode(reader)

if rv != xrif.XRIF_NOERROR:
    raise RuntimeError("??")

# Now we need to make it intelligible to Python code.
# Fortunately xrif's data types are all available in NumPy

xrif_to_numpy_types_mapping = {
    xrif.XRIF_TYPECODE_UINT8: np.uint8,
    xrif.XRIF_TYPECODE_INT8: np.int8,
    xrif.XRIF_TYPECODE_UINT16: np.uint16,
    xrif.XRIF_TYPECODE_INT16: np.int16,
    xrif.XRIF_TYPECODE_UINT32: np.uint32,
    xrif.XRIF_TYPECODE_INT32: np.int32,
    xrif.XRIF_TYPECODE_UINT64: np.uint64,
    xrif.XRIF_TYPECODE_INT64: np.int64,
}
dtype = xrif_to_numpy_types_mapping[reader.contents.type_code]

# figure out how many bytes it is now that it's decompressed
raw_size = reader.contents.width * reader.contents.height * reader.contents.depth * reader.contents.frames * reader.contents.data_size

# make a NumPy array from a buffer
out = np.frombuffer(buf[:raw_size], dtype).reshape((
    reader.contents.frames,
    reader.contents.depth,
    reader.contents.height,
    reader.contents.width,
))

# bask
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.imshow(out[0,0], origin='lower')
plt.savefig('./minimal_ex_frame.png')

# hack

import IPython
IPython.embed()