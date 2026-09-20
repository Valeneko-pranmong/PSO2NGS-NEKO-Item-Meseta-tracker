import os
import pytest

@pytest.fixture(autouse=True, scope="session")
def isolate_test_environment(tmp_path_factory):
    """Isolate APPDATA so test runs never overwrite user data."""
    tmp_dir = tmp_path_factory.mktemp("test_env")
    orig_appdata = os.environ.get("APPDATA")
    os.environ["APPDATA"] = str(tmp_dir)
    yield
    if orig_appdata:
        os.environ["APPDATA"] = orig_appdata
    elif "APPDATA" in os.environ:
        del os.environ["APPDATA"]
