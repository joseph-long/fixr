#!/usr/bin/env bash
git submodule update --init --recursive
cd xrif
mkdir -p build
cd build
if [[ $(uname) == "Darwin" ]]; then
    extraDefines='-DCMAKE_C_FLAGS="-DXRIF_NO_OMP"'
    libExtension=dylib
    if ! command -v clang; then
        xcode-select --install
    fi
else
    extraDefines=''
    libExtension=so
fi
# build xrif
cmake .. $extraDefines || exit 1
make -j $(getconf _NPROCESSORS_ONLN) || exit 1
cd ../../src/fixr/

# copy compiled artifact into Python module for distribution
cp ../../xrif/build/src/libxrif.$libExtension ./

python -m venv ./env
source ./env/bin/activate
git clone https://github.com/joseph-long/ctypeslib.git
cd ctypeslib
git checkout macos-quirks
clangVersion=$(clang --version | head -n 1)
if [[ $clangVersion = *'version 15'* ]]; then
    pip install 'clang>=15,<16'
elif [[ $clangVersion = *'version 16'* ]]; then
    pip install 'clang>=16,<17'
elif [[ $clangVersion = *'version 17'* ]]; then
    pip install 'clang>=17,<18'
fi
pip install -e ./
cd ..

# generate bindings
clang2py \
    -k cdefstum \
    -l ../../xrif/build/src/libxrif.$libExtension ../../xrif/src/xrif.h > ./_xrif_rest.py \
    || exit 1

# massage codegen output
sed -i '' "s,'\.\./\.\./xrif/build/src/libxrif.$libExtension',bundled_lib_path," ./_xrif_rest.py
echo "import os.path" > ./_xrif.py
echo "bundled_lib_path = libname = os.path.abspath(os.path.join(os.path.dirname(__file__), \"libxrif.$libExtension\"))" >> ./_xrif.py
cat ./_xrif_rest.py >> ./_xrif.py
rm ./_xrif_rest.py

# smoke test to ensure it will import and load the C library
python -c 'import _xrif' || exit 1