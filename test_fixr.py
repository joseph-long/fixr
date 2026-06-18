import time
import pytest
import importlib
import fixr
import os.path

@pytest.fixture
def wfs_example_fh():
    return open(os.path.join(os.path.dirname(__file__), 'example_data', 'camwfs_20240315225750994842000.xrif'), 'rb')

def test_one(wfs_example_fh):
    result = fixr.xrif2numpy(wfs_example_fh)
    assert result.shape == (512, 1, 120, 120)

def test_oo_api(wfs_example_fh):
    reader = fixr.XrifReader(wfs_example_fh)
    assert reader.array.shape == (512, 1, 120, 120)

def test_skip(wfs_example_fh):
    fixr.skip(wfs_example_fh)
    result = fixr.xrif2numpy(wfs_example_fh)
    assert result.shape == (512, 1, 1, 5)

def test_read_timings(wfs_example_fh):
    timings = fixr.read_streamwriter_timings(wfs_example_fh)
    assert timings.shape == (512, 1, 1, 5)

def test_read_archive(wfs_example_fh):
    data, timings = fixr.read_streamwriter_archive(wfs_example_fh)
    assert timings.shape == (512, 1, 1, 5)
    assert data.shape == (512, 1, 120, 120)
