#!/usr/bin/env bash
set -x
git submodule update --init --recursive

mkdir -p _build
cd _build

if [[ $(uname) == "Darwin" ]]; then
    extraDefines='-DCMAKE_C_FLAGS="-DXRIF_NO_OMP"'
    libExtension=dylib
    if ! command -v clang; then
        xcode-select --install
    fi
    SED_INPLACE="-i ''"
else
    sudo apt install -y libclang-dev clang python3 python3-pip python3-venv || exit 1
    extraDefines=''
    libExtension=so
    SED_INPLACE="-i"
fi
python -m venv ./env
source ./env/bin/activate
clangVersion=$(clang --version | head -n 1)
if [[ $clangVersion = *'version 14'* ]]; then
    pip install 'clang>=14,<15'
elif [[ $clangVersion = *'version 15'* ]]; then
    pip install 'clang>=15,<16'
elif [[ $clangVersion = *'version 16'* ]]; then
    pip install 'clang>=16,<17'
elif [[ $clangVersion = *'version 17'* ]]; then
    pip install 'clang>=17,<18'
elif [[ $clangVersion = *'version 18'* ]]; then
    pip install 'clang>=18,<19'
fi

cd ../xrif
mkdir -p build
cd build

# build xrif
cmake .. $extraDefines || exit 1
make -j $(getconf _NPROCESSORS_ONLN) || exit 1

# copy compiled artifact into Python module for distribution
cp ./src/libxrif.$libExtension ../../src/fixr/

cd ../../_build/

if [[ ! -d ./ctypeslib ]]; then
    git clone --depth=1 https://github.com/joseph-long/ctypeslib.git
fi
cd ctypeslib
git checkout -b macos-quirks
pip install --no-deps -e ./


cd ../../src/fixr/
# generate bindings
clang2py \
    -k cdefstum \
    -l ../../xrif/build/src/libxrif.$libExtension ../../xrif/src/xrif.h > ./_xrif_rest.py \
    || exit 1

# massage codegen output
sed $SED_INPLACE "s,'\.\./\.\./xrif/build/src/libxrif.$libExtension',bundled_lib_path," ./_xrif_rest.py
echo "import os.path" > ./_xrif.py
echo "bundled_lib_path = libname = os.path.abspath(os.path.join(os.path.dirname(__file__), \"libxrif.$libExtension\"))" >> ./_xrif.py
cat ./_xrif_rest.py >> ./_xrif.py
rm ./_xrif_rest.py

# smoke test to ensure it will import and load the C library
python -c 'import _xrif' || exit 1