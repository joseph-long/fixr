from setuptools import setup, Extension
from setuptools.dist import Distribution

class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(foo):
        return True

import sys

if sys.platform == 'darwin':
    lib_extension = 'dylib'
else:
    lib_extension = 'so'

setup(
    ext_modules=[
        Extension(
            name="fixr._xrif",
            sources=[],  # empty list because we compile this separately
        ),
    ],
    package_data={"fixr": [f"libxrif.{lib_extension}"]},
    distclass=BinaryDistribution,
)
