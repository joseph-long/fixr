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


def test_reused_buffer(wfs_example_fh):
    start = time.perf_counter()
    n_trials = 50
    for i in range(n_trials):
        wfs_example_fh.seek(0)
        reader = fixr.XrifReader(wfs_example_fh)
    per_it_fresh = (time.perf_counter() - start) / n_trials
    min_reordered, min_raw = reader.min_reordered_size, reader.min_raw_size
    reorder_buf = fixr.XrifBuffer(min_reordered)
    raw_buf = fixr.XrifBuffer(min_raw)
    start = time.perf_counter()
    for i in range(n_trials):
        wfs_example_fh.seek(0)
        reader2 = fixr.XrifReader(wfs_example_fh, prealloc_raw=raw_buf, prealloc_reorder=reorder_buf)
    per_it_reuse = (time.perf_counter() - start) / n_trials
    assert per_it_fresh == per_it_reuse
    assert reader.array.shape == (512, 1, 120, 120)
