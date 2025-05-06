#!/usr/bin/env bash
set -x
which python
which pip
git submodule update --init --recursive

mkdir _build
cd _build
SED_INPLACE="-i .new"

if [[ $(uname) == "Darwin" ]]; then
    extraDefines='-DCMAKE_C_FLAGS="-DXRIF_NO_OMP"'
    extraDefines="$extraDefines -DCMAKE_OSX_SYSROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"
    libExtension=dylib
    if ! command -v clang; then
        xcode-select --install
    fi
else
    # sudo apt install -y libclang-dev clang python3 python3-pip python3-venv || exit 1
    yum install -y clang clang-devel clang-libs glibc-devel
    extraDefines=''
    libExtension=so

fi

rm -rf ./env
python -m venv ./env
source ./env/bin/activate

clangVersion=$(clang --version | head -n 1)
if [[ $clangVersion = *'version 14'* ]]; then
    pip install 'clang>=14,<15'
    clangVersion=14
elif [[ $clangVersion = *'version 15'* ]]; then
    pip install 'clang>=15,<16'
    clangVersion=15
elif [[ $clangVersion = *'version 16'* ]]; then
    pip install 'clang>=16,<17'
    clangVersion=16
elif [[ $clangVersion = *'version 17'* ]]; then
    pip install 'clang>=17,<18'
    clangVersion=17
elif [[ $clangVersion = *'version 18'* ]]; then
    pip install 'clang>=18,<19'
    clangVersion=18
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
    git clone -b further-quirks --depth=1 https://github.com/joseph-long/ctypeslib.git
fi
cd ctypeslib
pip install --no-deps -e ./


cd ../../src/fixr/

# generate bindings

CLANG_INCLUDE_FLAGS=$(clang -E -x c - -v < /dev/null 2>&1 | \
  awk '/#include <...> search starts here:/{flag=1; next} /End of search list./{flag=0} flag {print "-I" $1}')

clang2py \
    -k cdefstum \
    --clang-args="$CLANG_INCLUDE_FLAGS" \
    -l ../../xrif/build/src/libxrif.$libExtension ../../xrif/src/xrif.h > ./_xrif_generated.py \
    || exit 1

# massage codegen output
TARGET="'../../xrif/build/src/libxrif.dylib'"
REPLACEMENT="bundled_lib_path"
sed -i.bak "s|$TARGET|$REPLACEMENT|g" _xrif_generated.py
echo "import os.path" > ./_xrif.py
echo "bundled_lib_path = libname = os.path.abspath(os.path.join(os.path.dirname(__file__), \"libxrif.$libExtension\"))" >> ./_xrif.py
cat ./_xrif_generated.py >> ./_xrif.py
rm ./_xrif_generated.py{,.bak}

# smoke test to ensure it will import and load the C library
python -c 'import _xrif' || exit 1
