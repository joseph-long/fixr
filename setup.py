from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            name="fixr._xrif",
            sources=[],  # empty list because we compile this separately
        ),
    ]
)