import os
import typing
import ctypes
import numpy as np
from . import _xrif as xrif
# monkey-patch for ARM Linux inconsistency
xrif.xrif_read_header.argtypes = [xrif.xrif_t, ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p]
import io
import logging

log = logging.getLogger(__name__)


XRIF2NUMPY_DTYPE = {
    xrif.XRIF_TYPECODE_UINT8: np.uint8,
    xrif.XRIF_TYPECODE_INT8: np.int8,
    xrif.XRIF_TYPECODE_UINT16: np.uint16,
    xrif.XRIF_TYPECODE_INT16: np.int16,
    xrif.XRIF_TYPECODE_UINT32: np.uint32,
    xrif.XRIF_TYPECODE_INT32: np.int32,
    xrif.XRIF_TYPECODE_UINT64: np.uint64,
    xrif.XRIF_TYPECODE_INT64: np.int64,
    xrif.XRIF_TYPECODE_HALF: np.float16,
    xrif.XRIF_TYPECODE_FLOAT: np.float32,
    xrif.XRIF_TYPECODE_DOUBLE: np.float64,
    xrif.XRIF_TYPECODE_COMPLEX_FLOAT: np.complex64,
    xrif.XRIF_TYPECODE_COMPLEX_DOUBLE: np.complex128,
}

class XrifReader:
    def __init__(self, fh):
        if 'b' not in fh.mode:
            raise RuntimeError("File handle must be opened in binary mode")
        self.fh = fh
        # allocate and initialize xrif handle
        self._reader = xrif.xrif_t()
        xrif.xrif_new(self._reader)
        self._decode_from_fh()

    @property
    def difference_method(self):
        return xrif.string_cast((xrif.xrif_difference_method_string(self._reader.contents.difference_method)))

    @property
    def reorder_method(self):
        return xrif.string_cast(xrif.xrif_reorder_method_string(self._reader.contents.reorder_method))

    @property
    def compress_method(self):
        return xrif.string_cast(xrif.xrif_compress_method_string(self._reader.contents.compress_method))

    @property
    def lz4_acceleration(self):
        return int(self._reader.contents.lz4_acceleration)

    @property
    def width(self):
        return int(self._reader.contents.width)

    @property
    def height(self):
        return int(self._reader.contents.height)

    @property
    def depth(self):
        return int(self._reader.contents.depth)

    @property
    def frames(self):
        return int(self._reader.contents.frames)

    @property
    def raw_size(self):
        return self._reader.contents.width * self._reader.contents.height * self._reader.contents.depth * self._reader.contents.frames * self._reader.contents.data_size

    @property
    def shape(self):
        return (
            self._reader.contents.frames,
            self._reader.contents.depth,
            self._reader.contents.height,
            self._reader.contents.width,
        )

    @property
    def compressed_size(self):
        return int(self._reader.contents.compressed_size)

    @property
    def ratio(self):
        return self.compressed_size / self.raw_size

    @property
    def min_raw_size(self):
        return xrif.xrif_min_raw_size(self._reader)

    @property
    def min_reordered_size(self):
        return xrif.xrif_min_reordered_size(self._reader)

    def describe(self):
        # construct a report like xrif2fits has
        s = 'xrif compression details:\n'
        s += f"  difference method:  {self.difference_method}\n"
        s += f"  reorder method:     {self.reorder_method}\n"
        s += f"  compression method: {self.compress_method}\n"
        if self._reader.contents.compress_method == xrif.XRIF_COMPRESS_LZ4:
            s += f"    LZ4 acceleration: {self.lz4_acceleration}\n"
        s += f"  dimensions:         {self.width} x {self.height} x {self.depth} x {self.frames}\n"

        s += f"  raw size:           {self.raw_size} bytes\n"
        s += f"  encoded size:       {self.compressed_size} bytes\n"
        s += f"  ratio:              {self.ratio:.3f}\n"
        return s

    def __del__(self):
        xrif.xrif_delete(self._reader)

    def _decode_from_fh(self):
        # read one header's worth of bytes
        buf = self.fh.read(xrif.XRIF_HEADER_SIZE)
        buf = ctypes.create_string_buffer(buf)

        header_size_ptr = ctypes.c_uint32()
        # populate header fields in reader
        rv = xrif.xrif_read_header(self._reader, header_size_ptr, buf)
        assert header_size_ptr.value == xrif.XRIF_HEADER_SIZE
        if rv != xrif.XRIF_NOERROR:
            raise RuntimeError("XRIF error reading header, check stderr")


        rv = xrif.xrif_allocate_reordered(self._reader)
        if rv != xrif.XRIF_NOERROR:
            raise RuntimeError("XRIF error allocating reordered buffer")

        # xrif can save you a buffer by decompressing into the raw buffer but that
        # means it needs to be bigger than just `compressed_size`
        min_buf_size = xrif.xrif_min_raw_size(self._reader)
        # we need to own the raw (and then decompressed) buffer
        buf = ctypes.c_buffer(min_buf_size)
        # we're only filling the first `compressed_size` bytes
        buf[:self._reader.contents.compressed_size] = self.fh.read(self._reader.contents.compressed_size)
        # acquaint xrif with our arrangements
        rv = xrif.xrif_set_raw(self._reader, buf, min_buf_size)

        if rv != xrif.XRIF_NOERROR:
            raise RuntimeError("XRIF error setting raw buffer, check stderr")

        # do the business
        xrif.xrif_decode(self._reader)

        if rv != xrif.XRIF_NOERROR:
            raise RuntimeError("XRIF decode error, check stderr")

        # Now we need to make it intelligible to Python code.
        # Fortunately xrif's data types are all available in NumPy
        dtype = XRIF2NUMPY_DTYPE[self._reader.contents.type_code]

        # figure out how many bytes it is now that it's decompressed
        raw_size = self._reader.contents.width * self._reader.contents.height * self._reader.contents.depth * self._reader.contents.frames * self._reader.contents.data_size

        # make a NumPy array from a buffer
        self._decoded = np.frombuffer(buf[:raw_size], dtype).reshape(self.shape)
        self._decoded.setflags(write=False)

    @property
    def array(self) -> np.ndarray:
        return self._decoded

    def copy_data(self) -> np.ndarray:
        arr = self.array.copy()
        arr.setflags(write=True)
        return arr

def xrif2numpy(fh, print=log.debug):
    '''Read an XRIF buffer with header + data and return the data

    Note: makes two copies (first in decompression, second in exposing
    the data to the user). For maximum memory-efficiency, use ``XrifReader``
    directly.

    Parameters
    ----------
    fh : file-like object in binary mode
    print : callable (default: log at DEBUG as 'fixr')
        If you want to skip setting up logging, you can just pass ``print=print``.
    '''
    if 'b' not in fh.mode:
        raise RuntimeError("Files must be opened in binary mode (i.e. `fh = open(filename, 'rb')`)")
    reader = XrifReader(fh)
    print(reader.describe())
    return reader.copy_data()

def skip(fh):
    '''When a file/buffer contains multiple XRIF-header + data
    chunks, this will skip the one starting at the file handle
    current seek position (and not decode it), leaving you
    free to call ``xrif2numpy`` (or similar) on the next one

    Parameters
    ----------
    fh : file-like object in binary mode
    '''
    if 'b' not in fh.mode:
        raise RuntimeError("Files must be opened in binary mode (i.e. `fh = open(filename, 'rb')`)")
    reader = xrif.xrif_t()
    xrif.xrif_new(reader)
    # read one header's worth of bytes
    buf = fh.read(xrif.XRIF_HEADER_SIZE)
    buf = ctypes.create_string_buffer(buf)

    header_size_ptr = ctypes.c_uint32()
    # populate header fields in reader
    rv = xrif.xrif_read_header(reader, header_size_ptr, buf)
    assert header_size_ptr.value == xrif.XRIF_HEADER_SIZE
    if rv != xrif.XRIF_NOERROR:
        raise RuntimeError("XRIF error reading header, check stderr")

    fh.seek(reader.contents.compressed_size, os.SEEK_CUR)

def read_streamwriter_timings(fh):
    '''StreamWriter archives from XWCL projects have
    compressed array data followed by uncompressed
    nanosecond-precision timestamps.

    This function loads just the timings, skipping the
    cost of decompressing the data.

    Parameters
    ----------
    fh : file-like object in binary mode
    '''
    skip(fh)
    reader = XrifReader(fh)
    log.debug(reader.describe())
    return reader.array

def read_streamwriter_archive(fh):
    '''StreamWriter archives from XWCL projects have
    compressed array data followed by uncompressed
    nanosecond-precision timestamps

    This function loads both in one go, returning
    a (data, timings) tuple.

    Parameters
    ----------
    fh : file-like object in binary mode
    '''
    fh.seek(0)
    data = xrif2numpy(fh)
    timings = xrif2numpy(fh)

    return data, timings
