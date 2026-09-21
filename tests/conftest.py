import os
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture(autouse=True, scope="session")
def isolate_test_environment(tmp_path_factory):
    """Isolate APPDATA so test runs never overwrite user data."""
    tmp_dir = tmp_path_factory.mktemp("test_env")
    orig_appdata = os.environ.get("APPDATA")
    os.environ["APPDATA"] = str(tmp_dir)
    
    # Intercept all real network calls to production Firebase RTDB during tests
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"success": true}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        yield
        
    if orig_appdata:
        os.environ["APPDATA"] = orig_appdata
    elif "APPDATA" in os.environ:
        del os.environ["APPDATA"]

@pytest.fixture(scope="session")
def shared_app():
    """Shared GUI app instance for tests to prevent repeated Tk re-initialization crashes."""
    from meseta_tracker import NGSTrackerApp
    app = NGSTrackerApp()
    app.update_idletasks()
    yield app
    try:
        app.destroy()
    except Exception:
        pass
