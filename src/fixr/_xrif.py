import os.path
bundled_lib_path = libname = os.path.abspath(os.path.join(os.path.dirname(__file__), "libxrif.dylib"))
# -*- coding: utf-8 -*-
#
# TARGET arch is: ['-isysroot', '/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk']
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 8
#
import ctypes


class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                if not hasattr(type_, "as_dict"):
                    value = [v for v in value]
                else:
                    type_ = type_._type_
                    value = [type_.as_dict(v) for v in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass



def string_cast(char_pointer, encoding='utf-8', errors='strict'):
    value = ctypes.cast(char_pointer, ctypes.c_char_p).value
    if value is not None and encoding is not None:
        value = value.decode(encoding, errors=errors)
    return value


def char_pointer_cast(string, encoding='utf-8'):
    if encoding is not None:
        try:
            string = string.encode(encoding)
        except AttributeError:
            # In Python3, bytes has no encode attribute
            pass
    string = ctypes.c_char_p(string)
    return ctypes.cast(string, ctypes.POINTER(ctypes.c_char))



_libraries = {}
_libraries['libxrif.dylib'] = ctypes.CDLL('../../xrif/build/src/libxrif.dylib')
c_int128 = ctypes.c_ubyte*16
c_uint128 = c_int128
void = None
if ctypes.sizeof(ctypes.c_longdouble) == 8:
    c_long_double_t = ctypes.c_longdouble
else:
    c_long_double_t = ctypes.c_ubyte*8

class FunctionFactoryStub:
    def __getattr__(self, _):
      return ctypes.CFUNCTYPE(lambda y:y)

# libraries['FIXME_STUB'] explanation
# As you did not list (-l libraryname.so) a library that exports this function
# This is a non-working stub instead. 
# You can either re-run clan2py with -l /path/to/library.so
# Or manually fix this by comment the ctypes.CDLL loading
_libraries['FIXME_STUB'] = FunctionFactoryStub() #  ctypes.CDLL('FIXME_STUB')


xrif_xrif_h = True # macro
_POSIX_C_SOURCE = 199309 # macro
LZ4_MEMORY_USAGE = (20) # macro
XRIF_VERSION = (0) # macro
XRIF_HEADER_SIZE = (48) # macro
XRIF_DIFFERENCE_NONE = (-1) # macro
XRIF_DIFFERENCE_DEFAULT = (100) # macro
XRIF_DIFFERENCE_PREVIOUS = (100) # macro
XRIF_DIFFERENCE_FIRST = (200) # macro
XRIF_DIFFERENCE_PIXEL = (300) # macro
XRIF_REORDER_NONE = (-1) # macro
XRIF_REORDER_DEFAULT = (100) # macro
XRIF_REORDER_BYTEPACK = (100) # macro
XRIF_REORDER_BYTEPACK_RENIBBLE = (200) # macro
XRIF_REORDER_BITPACK = (300) # macro
XRIF_COMPRESS_NONE = (-1) # macro
XRIF_COMPRESS_DEFAULT = (100) # macro
XRIF_COMPRESS_LZ4 = (100) # macro
XRIF_LZ4_ACCEL_MIN = (1) # macro
XRIF_LZ4_ACCEL_MAX = (65537) # macro
XRIF_NOERROR = (0) # macro
XRIF_ERROR_NULLPTR = (-5) # macro
XRIF_ERROR_NOT_SETUP = (-10) # macro
XRIF_ERROR_INVALID_SIZE = (-20) # macro
XRIF_ERROR_INVALID_TYPE = (-22) # macro
XRIF_ERROR_INSUFFICIENT_SIZE = (-25) # macro
XRIF_ERROR_MALLOC = (-30) # macro
XRIF_ERROR_NOTIMPL = (-100) # macro
XRIF_ERROR_BADARG = (-110) # macro
XRIF_ERROR_BADHEADER = (-1000) # macro
XRIF_ERROR_WRONGVERSION = (-1010) # macro
XRIF_ERROR_LIBERR = (-10000) # macro
# def XRIF_ERROR_PRINT(function, msg):  # macro
#    return fprintf(stderr,"%s: %s\n",function,msg)  
XRIF_TYPECODE_UINT8 = (1) # macro
XRIF_TYPECODE_INT8 = (2) # macro
XRIF_TYPECODE_UINT16 = (3) # macro
XRIF_TYPECODE_INT16 = (4) # macro
XRIF_TYPECODE_UINT32 = (5) # macro
XRIF_TYPECODE_INT32 = (6) # macro
XRIF_TYPECODE_UINT64 = (7) # macro
XRIF_TYPECODE_INT64 = (8) # macro
XRIF_TYPECODE_HALF = (13) # macro
XRIF_TYPECODE_FLOAT = (9) # macro
XRIF_TYPECODE_DOUBLE = (10) # macro
XRIF_TYPECODE_COMPLEX_FLOAT = (11) # macro
XRIF_TYPECODE_COMPLEX_DOUBLE = (12) # macro
xrif_dimension_t = ctypes.c_uint32
xrif_error_t = ctypes.c_int32
xrif_typecode_t = ctypes.c_ubyte
class struct_xrif_handle(Structure):
    pass

class struct_timespec(Structure):
    pass

struct_timespec._pack_ = 1 # source:False
struct_timespec._fields_ = [
    ('tv_sec', ctypes.c_int64),
    ('tv_nsec', ctypes.c_int64),
]

struct_xrif_handle._pack_ = 1 # source:False
struct_xrif_handle._fields_ = [
    ('width', ctypes.c_uint32),
    ('height', ctypes.c_uint32),
    ('depth', ctypes.c_uint32),
    ('frames', ctypes.c_uint32),
    ('type_code', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 7),
    ('data_size', ctypes.c_uint64),
    ('raw_size', ctypes.c_uint64),
    ('compressed_size', ctypes.c_uint64),
    ('difference_method', ctypes.c_int32),
    ('reorder_method', ctypes.c_int32),
    ('compress_method', ctypes.c_int32),
    ('lz4_acceleration', ctypes.c_int32),
    ('omp_parallel', ctypes.c_int32),
    ('omp_numthreads', ctypes.c_int32),
    ('compress_on_raw', ctypes.c_ubyte),
    ('own_raw', ctypes.c_ubyte),
    ('PADDING_1', ctypes.c_ubyte * 6),
    ('raw_buffer', ctypes.POINTER(ctypes.c_char)),
    ('raw_buffer_size', ctypes.c_uint64),
    ('own_reordered', ctypes.c_ubyte),
    ('PADDING_2', ctypes.c_ubyte * 7),
    ('reordered_buffer', ctypes.POINTER(ctypes.c_char)),
    ('reordered_buffer_size', ctypes.c_uint64),
    ('own_compressed', ctypes.c_ubyte),
    ('PADDING_3', ctypes.c_ubyte * 7),
    ('compressed_buffer', ctypes.POINTER(ctypes.c_char)),
    ('compressed_buffer_size', ctypes.c_uint64),
    ('calc_performance', ctypes.c_ubyte),
    ('PADDING_4', ctypes.c_ubyte * 7),
    ('compression_ratio', ctypes.c_double),
    ('encode_time', ctypes.c_double),
    ('encode_rate', ctypes.c_double),
    ('difference_time', ctypes.c_double),
    ('difference_rate', ctypes.c_double),
    ('reorder_time', ctypes.c_double),
    ('reorder_rate', ctypes.c_double),
    ('compress_time', ctypes.c_double),
    ('compress_rate', ctypes.c_double),
    ('ts_difference_start', struct_timespec),
    ('ts_reorder_start', struct_timespec),
    ('ts_compress_start', struct_timespec),
    ('ts_compress_done', struct_timespec),
    ('ts_decompress_start', struct_timespec),
    ('ts_unreorder_start', struct_timespec),
    ('ts_undifference_start', struct_timespec),
    ('ts_undifference_done', struct_timespec),
]

xrif_handle = struct_xrif_handle
xrif_t = ctypes.POINTER(struct_xrif_handle)
xrif_new = _libraries['libxrif.dylib'].xrif_new
xrif_new.restype = xrif_error_t
xrif_new.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_xrif_handle))]
xrif_set_size = _libraries['libxrif.dylib'].xrif_set_size
xrif_set_size.restype = xrif_error_t
xrif_set_size.argtypes = [xrif_t, xrif_dimension_t, xrif_dimension_t, xrif_dimension_t, xrif_dimension_t, xrif_typecode_t]
xrif_configure = _libraries['libxrif.dylib'].xrif_configure
xrif_configure.restype = xrif_error_t
xrif_configure.argtypes = [xrif_t, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
xrif_allocate = _libraries['libxrif.dylib'].xrif_allocate
xrif_allocate.restype = xrif_error_t
xrif_allocate.argtypes = [xrif_t]
xrif_reset = _libraries['libxrif.dylib'].xrif_reset
xrif_reset.restype = xrif_error_t
xrif_reset.argtypes = [xrif_t]
xrif_delete = _libraries['libxrif.dylib'].xrif_delete
xrif_delete.restype = xrif_error_t
xrif_delete.argtypes = [xrif_t]
xrif_initialize_handle = _libraries['libxrif.dylib'].xrif_initialize_handle
xrif_initialize_handle.restype = xrif_error_t
xrif_initialize_handle.argtypes = [xrif_t]
xrif_set_difference_method = _libraries['libxrif.dylib'].xrif_set_difference_method
xrif_set_difference_method.restype = xrif_error_t
xrif_set_difference_method.argtypes = [xrif_t, ctypes.c_int32]
xrif_set_reorder_method = _libraries['libxrif.dylib'].xrif_set_reorder_method
xrif_set_reorder_method.restype = xrif_error_t
xrif_set_reorder_method.argtypes = [xrif_t, ctypes.c_int32]
xrif_set_compress_method = _libraries['libxrif.dylib'].xrif_set_compress_method
xrif_set_compress_method.restype = xrif_error_t
xrif_set_compress_method.argtypes = [xrif_t, ctypes.c_int32]
int32_t = ctypes.c_int32
xrif_set_lz4_acceleration = _libraries['libxrif.dylib'].xrif_set_lz4_acceleration
xrif_set_lz4_acceleration.restype = xrif_error_t
xrif_set_lz4_acceleration.argtypes = [xrif_t, int32_t]
size_t = ctypes.c_uint64
xrif_min_raw_size = _libraries['libxrif.dylib'].xrif_min_raw_size
xrif_min_raw_size.restype = size_t
xrif_min_raw_size.argtypes = [xrif_t]
xrif_min_reordered_size = _libraries['libxrif.dylib'].xrif_min_reordered_size
xrif_min_reordered_size.restype = size_t
xrif_min_reordered_size.argtypes = [xrif_t]
xrif_min_compressed_size = _libraries['libxrif.dylib'].xrif_min_compressed_size
xrif_min_compressed_size.restype = size_t
xrif_min_compressed_size.argtypes = [xrif_t]
xrif_set_raw = _libraries['libxrif.dylib'].xrif_set_raw
xrif_set_raw.restype = xrif_error_t
xrif_set_raw.argtypes = [xrif_t, ctypes.POINTER(None), size_t]
xrif_allocate_raw = _libraries['libxrif.dylib'].xrif_allocate_raw
xrif_allocate_raw.restype = xrif_error_t
xrif_allocate_raw.argtypes = [xrif_t]
xrif_set_reordered = _libraries['libxrif.dylib'].xrif_set_reordered
xrif_set_reordered.restype = xrif_error_t
xrif_set_reordered.argtypes = [xrif_t, ctypes.POINTER(None), size_t]
xrif_allocate_reordered = _libraries['libxrif.dylib'].xrif_allocate_reordered
xrif_allocate_reordered.restype = xrif_error_t
xrif_allocate_reordered.argtypes = [xrif_t]
xrif_set_compressed = _libraries['libxrif.dylib'].xrif_set_compressed
xrif_set_compressed.restype = xrif_error_t
xrif_set_compressed.argtypes = [xrif_t, ctypes.POINTER(None), size_t]
xrif_allocate_compressed = _libraries['libxrif.dylib'].xrif_allocate_compressed
xrif_allocate_compressed.restype = xrif_error_t
xrif_allocate_compressed.argtypes = [xrif_t]
xrif_width = _libraries['libxrif.dylib'].xrif_width
xrif_width.restype = xrif_dimension_t
xrif_width.argtypes = [xrif_t]
xrif_height = _libraries['libxrif.dylib'].xrif_height
xrif_height.restype = xrif_dimension_t
xrif_height.argtypes = [xrif_t]
xrif_depth = _libraries['libxrif.dylib'].xrif_depth
xrif_depth.restype = xrif_dimension_t
xrif_depth.argtypes = [xrif_t]
xrif_frames = _libraries['libxrif.dylib'].xrif_frames
xrif_frames.restype = xrif_dimension_t
xrif_frames.argtypes = [xrif_t]
xrif_write_header = _libraries['libxrif.dylib'].xrif_write_header
xrif_write_header.restype = xrif_error_t
xrif_write_header.argtypes = [ctypes.POINTER(ctypes.c_char), xrif_t]
xrif_read_header = _libraries['libxrif.dylib'].xrif_read_header
xrif_read_header.restype = xrif_error_t
xrif_read_header.argtypes = [xrif_t, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_char)]
xrif_encode = _libraries['libxrif.dylib'].xrif_encode
xrif_encode.restype = xrif_error_t
xrif_encode.argtypes = [xrif_t]
xrif_decode = _libraries['libxrif.dylib'].xrif_decode
xrif_decode.restype = xrif_error_t
xrif_decode.argtypes = [xrif_t]
xrif_difference = _libraries['libxrif.dylib'].xrif_difference
xrif_difference.restype = xrif_error_t
xrif_difference.argtypes = [xrif_t]
xrif_undifference = _libraries['libxrif.dylib'].xrif_undifference
xrif_undifference.restype = xrif_error_t
xrif_undifference.argtypes = [xrif_t]
xrif_difference_previous = _libraries['libxrif.dylib'].xrif_difference_previous
xrif_difference_previous.restype = xrif_error_t
xrif_difference_previous.argtypes = [xrif_t]
xrif_difference_first = _libraries['libxrif.dylib'].xrif_difference_first
xrif_difference_first.restype = xrif_error_t
xrif_difference_first.argtypes = [xrif_t]
xrif_difference_pixel = _libraries['libxrif.dylib'].xrif_difference_pixel
xrif_difference_pixel.restype = xrif_error_t
xrif_difference_pixel.argtypes = [xrif_t]
xrif_undifference_previous = _libraries['libxrif.dylib'].xrif_undifference_previous
xrif_undifference_previous.restype = xrif_error_t
xrif_undifference_previous.argtypes = [xrif_t]
xrif_undifference_first = _libraries['libxrif.dylib'].xrif_undifference_first
xrif_undifference_first.restype = xrif_error_t
xrif_undifference_first.argtypes = [xrif_t]
xrif_undifference_pixel = _libraries['libxrif.dylib'].xrif_undifference_pixel
xrif_undifference_pixel.restype = xrif_error_t
xrif_undifference_pixel.argtypes = [xrif_t]
xrif_reorder = _libraries['libxrif.dylib'].xrif_reorder
xrif_reorder.restype = xrif_error_t
xrif_reorder.argtypes = [xrif_t]
xrif_unreorder = _libraries['libxrif.dylib'].xrif_unreorder
xrif_unreorder.restype = xrif_error_t
xrif_unreorder.argtypes = [xrif_t]
xrif_reorder_none = _libraries['libxrif.dylib'].xrif_reorder_none
xrif_reorder_none.restype = xrif_error_t
xrif_reorder_none.argtypes = [xrif_t]
xrif_reorder_bytepack = _libraries['libxrif.dylib'].xrif_reorder_bytepack
xrif_reorder_bytepack.restype = xrif_error_t
xrif_reorder_bytepack.argtypes = [xrif_t]
xrif_reorder_bytepack_sint16 = _libraries['libxrif.dylib'].xrif_reorder_bytepack_sint16
xrif_reorder_bytepack_sint16.restype = xrif_error_t
xrif_reorder_bytepack_sint16.argtypes = [xrif_t]
xrif_reorder_bytepack_renibble = _libraries['libxrif.dylib'].xrif_reorder_bytepack_renibble
xrif_reorder_bytepack_renibble.restype = xrif_error_t
xrif_reorder_bytepack_renibble.argtypes = [xrif_t]
xrif_reorder_bytepack_renibble_sint16 = _libraries['FIXME_STUB'].xrif_reorder_bytepack_renibble_sint16
xrif_reorder_bytepack_renibble_sint16.restype = xrif_error_t
xrif_reorder_bytepack_renibble_sint16.argtypes = [xrif_t]
xrif_reorder_bitpack = _libraries['libxrif.dylib'].xrif_reorder_bitpack
xrif_reorder_bitpack.restype = xrif_error_t
xrif_reorder_bitpack.argtypes = [xrif_t]
xrif_reorder_bitpack_sint16 = _libraries['FIXME_STUB'].xrif_reorder_bitpack_sint16
xrif_reorder_bitpack_sint16.restype = xrif_error_t
xrif_reorder_bitpack_sint16.argtypes = [xrif_t]
xrif_unreorder_none = _libraries['libxrif.dylib'].xrif_unreorder_none
xrif_unreorder_none.restype = xrif_error_t
xrif_unreorder_none.argtypes = [xrif_t]
xrif_unreorder_bytepack = _libraries['libxrif.dylib'].xrif_unreorder_bytepack
xrif_unreorder_bytepack.restype = xrif_error_t
xrif_unreorder_bytepack.argtypes = [xrif_t]
xrif_unreorder_bytepack_sint16 = _libraries['libxrif.dylib'].xrif_unreorder_bytepack_sint16
xrif_unreorder_bytepack_sint16.restype = xrif_error_t
xrif_unreorder_bytepack_sint16.argtypes = [xrif_t]
xrif_unreorder_bytepack_renibble = _libraries['libxrif.dylib'].xrif_unreorder_bytepack_renibble
xrif_unreorder_bytepack_renibble.restype = xrif_error_t
xrif_unreorder_bytepack_renibble.argtypes = [xrif_t]
xrif_unreorder_bitpack = _libraries['libxrif.dylib'].xrif_unreorder_bitpack
xrif_unreorder_bitpack.restype = xrif_error_t
xrif_unreorder_bitpack.argtypes = [xrif_t]
xrif_compress = _libraries['libxrif.dylib'].xrif_compress
xrif_compress.restype = xrif_error_t
xrif_compress.argtypes = [xrif_t]
xrif_decompress = _libraries['libxrif.dylib'].xrif_decompress
xrif_decompress.restype = xrif_error_t
xrif_decompress.argtypes = [xrif_t]
xrif_compress_none = _libraries['libxrif.dylib'].xrif_compress_none
xrif_compress_none.restype = xrif_error_t
xrif_compress_none.argtypes = [xrif_t]
xrif_decompress_none = _libraries['libxrif.dylib'].xrif_decompress_none
xrif_decompress_none.restype = xrif_error_t
xrif_decompress_none.argtypes = [xrif_t]
xrif_compress_lz4 = _libraries['libxrif.dylib'].xrif_compress_lz4
xrif_compress_lz4.restype = xrif_error_t
xrif_compress_lz4.argtypes = [xrif_t]
xrif_decompress_lz4 = _libraries['libxrif.dylib'].xrif_decompress_lz4
xrif_decompress_lz4.restype = xrif_error_t
xrif_decompress_lz4.argtypes = [xrif_t]
xrif_compression_ratio = _libraries['libxrif.dylib'].xrif_compression_ratio
xrif_compression_ratio.restype = ctypes.c_double
xrif_compression_ratio.argtypes = [xrif_t]
xrif_encode_time = _libraries['libxrif.dylib'].xrif_encode_time
xrif_encode_time.restype = ctypes.c_double
xrif_encode_time.argtypes = [xrif_t]
xrif_encode_rate = _libraries['libxrif.dylib'].xrif_encode_rate
xrif_encode_rate.restype = ctypes.c_double
xrif_encode_rate.argtypes = [xrif_t]
xrif_difference_time = _libraries['libxrif.dylib'].xrif_difference_time
xrif_difference_time.restype = ctypes.c_double
xrif_difference_time.argtypes = [xrif_t]
xrif_difference_rate = _libraries['libxrif.dylib'].xrif_difference_rate
xrif_difference_rate.restype = ctypes.c_double
xrif_difference_rate.argtypes = [xrif_t]
xrif_reorder_time = _libraries['libxrif.dylib'].xrif_reorder_time
xrif_reorder_time.restype = ctypes.c_double
xrif_reorder_time.argtypes = [xrif_t]
xrif_reorder_rate = _libraries['libxrif.dylib'].xrif_reorder_rate
xrif_reorder_rate.restype = ctypes.c_double
xrif_reorder_rate.argtypes = [xrif_t]
xrif_compress_time = _libraries['libxrif.dylib'].xrif_compress_time
xrif_compress_time.restype = ctypes.c_double
xrif_compress_time.argtypes = [xrif_t]
xrif_compress_rate = _libraries['libxrif.dylib'].xrif_compress_rate
xrif_compress_rate.restype = ctypes.c_double
xrif_compress_rate.argtypes = [xrif_t]
xrif_decode_time = _libraries['libxrif.dylib'].xrif_decode_time
xrif_decode_time.restype = ctypes.c_double
xrif_decode_time.argtypes = [xrif_t]
xrif_decode_rate = _libraries['libxrif.dylib'].xrif_decode_rate
xrif_decode_rate.restype = ctypes.c_double
xrif_decode_rate.argtypes = [xrif_t]
xrif_undifference_time = _libraries['libxrif.dylib'].xrif_undifference_time
xrif_undifference_time.restype = ctypes.c_double
xrif_undifference_time.argtypes = [xrif_t]
xrif_undifference_rate = _libraries['libxrif.dylib'].xrif_undifference_rate
xrif_undifference_rate.restype = ctypes.c_double
xrif_undifference_rate.argtypes = [xrif_t]
xrif_unreorder_time = _libraries['libxrif.dylib'].xrif_unreorder_time
xrif_unreorder_time.restype = ctypes.c_double
xrif_unreorder_time.argtypes = [xrif_t]
xrif_unreorder_rate = _libraries['libxrif.dylib'].xrif_unreorder_rate
xrif_unreorder_rate.restype = ctypes.c_double
xrif_unreorder_rate.argtypes = [xrif_t]
xrif_decompress_time = _libraries['libxrif.dylib'].xrif_decompress_time
xrif_decompress_time.restype = ctypes.c_double
xrif_decompress_time.argtypes = [xrif_t]
xrif_decompress_rate = _libraries['libxrif.dylib'].xrif_decompress_rate
xrif_decompress_rate.restype = ctypes.c_double
xrif_decompress_rate.argtypes = [xrif_t]
xrif_typesize = _libraries['libxrif.dylib'].xrif_typesize
xrif_typesize.restype = size_t
xrif_typesize.argtypes = [xrif_typecode_t]
xrif_ts_difference = _libraries['libxrif.dylib'].xrif_ts_difference
xrif_ts_difference.restype = ctypes.c_double
xrif_ts_difference.argtypes = [ctypes.POINTER(struct_timespec), ctypes.POINTER(struct_timespec)]
xrif_difference_method_string = _libraries['libxrif.dylib'].xrif_difference_method_string
xrif_difference_method_string.restype = ctypes.POINTER(ctypes.c_char)
xrif_difference_method_string.argtypes = [ctypes.c_int32]
xrif_reorder_method_string = _libraries['libxrif.dylib'].xrif_reorder_method_string
xrif_reorder_method_string.restype = ctypes.POINTER(ctypes.c_char)
xrif_reorder_method_string.argtypes = [ctypes.c_int32]
xrif_compress_method_string = _libraries['libxrif.dylib'].xrif_compress_method_string
xrif_compress_method_string.restype = ctypes.POINTER(ctypes.c_char)
xrif_compress_method_string.argtypes = [ctypes.c_int32]
__all__ = \
    ['LZ4_MEMORY_USAGE', 'XRIF_COMPRESS_DEFAULT', 'XRIF_COMPRESS_LZ4',
    'XRIF_COMPRESS_NONE', 'XRIF_DIFFERENCE_DEFAULT',
    'XRIF_DIFFERENCE_FIRST', 'XRIF_DIFFERENCE_NONE',
    'XRIF_DIFFERENCE_PIXEL', 'XRIF_DIFFERENCE_PREVIOUS',
    'XRIF_ERROR_BADARG', 'XRIF_ERROR_BADHEADER',
    'XRIF_ERROR_INSUFFICIENT_SIZE', 'XRIF_ERROR_INVALID_SIZE',
    'XRIF_ERROR_INVALID_TYPE', 'XRIF_ERROR_LIBERR',
    'XRIF_ERROR_MALLOC', 'XRIF_ERROR_NOTIMPL', 'XRIF_ERROR_NOT_SETUP',
    'XRIF_ERROR_NULLPTR', 'XRIF_ERROR_WRONGVERSION',
    'XRIF_HEADER_SIZE', 'XRIF_LZ4_ACCEL_MAX', 'XRIF_LZ4_ACCEL_MIN',
    'XRIF_NOERROR', 'XRIF_REORDER_BITPACK', 'XRIF_REORDER_BYTEPACK',
    'XRIF_REORDER_BYTEPACK_RENIBBLE', 'XRIF_REORDER_DEFAULT',
    'XRIF_REORDER_NONE', 'XRIF_TYPECODE_COMPLEX_DOUBLE',
    'XRIF_TYPECODE_COMPLEX_FLOAT', 'XRIF_TYPECODE_DOUBLE',
    'XRIF_TYPECODE_FLOAT', 'XRIF_TYPECODE_HALF',
    'XRIF_TYPECODE_INT16', 'XRIF_TYPECODE_INT32',
    'XRIF_TYPECODE_INT64', 'XRIF_TYPECODE_INT8',
    'XRIF_TYPECODE_UINT16', 'XRIF_TYPECODE_UINT32',
    'XRIF_TYPECODE_UINT64', 'XRIF_TYPECODE_UINT8', 'XRIF_VERSION',
    '_POSIX_C_SOURCE', 'int32_t', 'size_t', 'struct_timespec',
    'struct_xrif_handle', 'xrif_allocate', 'xrif_allocate_compressed',
    'xrif_allocate_raw', 'xrif_allocate_reordered', 'xrif_compress',
    'xrif_compress_lz4', 'xrif_compress_method_string',
    'xrif_compress_none', 'xrif_compress_rate', 'xrif_compress_time',
    'xrif_compression_ratio', 'xrif_configure', 'xrif_decode',
    'xrif_decode_rate', 'xrif_decode_time', 'xrif_decompress',
    'xrif_decompress_lz4', 'xrif_decompress_none',
    'xrif_decompress_rate', 'xrif_decompress_time', 'xrif_delete',
    'xrif_depth', 'xrif_difference', 'xrif_difference_first',
    'xrif_difference_method_string', 'xrif_difference_pixel',
    'xrif_difference_previous', 'xrif_difference_rate',
    'xrif_difference_time', 'xrif_dimension_t', 'xrif_encode',
    'xrif_encode_rate', 'xrif_encode_time', 'xrif_error_t',
    'xrif_frames', 'xrif_handle', 'xrif_height',
    'xrif_initialize_handle', 'xrif_min_compressed_size',
    'xrif_min_raw_size', 'xrif_min_reordered_size', 'xrif_new',
    'xrif_read_header', 'xrif_reorder', 'xrif_reorder_bitpack',
    'xrif_reorder_bitpack_sint16', 'xrif_reorder_bytepack',
    'xrif_reorder_bytepack_renibble',
    'xrif_reorder_bytepack_renibble_sint16',
    'xrif_reorder_bytepack_sint16', 'xrif_reorder_method_string',
    'xrif_reorder_none', 'xrif_reorder_rate', 'xrif_reorder_time',
    'xrif_reset', 'xrif_set_compress_method', 'xrif_set_compressed',
    'xrif_set_difference_method', 'xrif_set_lz4_acceleration',
    'xrif_set_raw', 'xrif_set_reorder_method', 'xrif_set_reordered',
    'xrif_set_size', 'xrif_t', 'xrif_ts_difference',
    'xrif_typecode_t', 'xrif_typesize', 'xrif_undifference',
    'xrif_undifference_first', 'xrif_undifference_pixel',
    'xrif_undifference_previous', 'xrif_undifference_rate',
    'xrif_undifference_time', 'xrif_unreorder',
    'xrif_unreorder_bitpack', 'xrif_unreorder_bytepack',
    'xrif_unreorder_bytepack_renibble',
    'xrif_unreorder_bytepack_sint16', 'xrif_unreorder_none',
    'xrif_unreorder_rate', 'xrif_unreorder_time', 'xrif_width',
    'xrif_write_header', 'xrif_xrif_h']
