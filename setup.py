from setuptools import setup, Extension
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

class bdist_wheel_abi_none(_bdist_wheel):
    def finalize_options(self):
        _bdist_wheel.finalize_options(self)
        self.root_is_pure = False

    def get_tag(self):
        python, abi, plat = _bdist_wheel.get_tag(self)
        return "py3", "none", plat

setup(
    ext_modules=[
        Extension(
            name="fixr._xrif",
            sources=[],  # empty list because we compile this separately
        ),
    ],
    cmdclass={"bdist_wheel": bdist_wheel_abi_none},
)
