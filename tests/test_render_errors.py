import pytest
import sys
from unittest.mock import patch, MagicMock


# render.py imports bpy (a Blender-only module). Mock it before importing render.
@pytest.fixture(autouse=True)
def mock_bpy(monkeypatch):
    bpy_mock = MagicMock()
    monkeypatch.setitem(sys.modules, 'bpy', bpy_mock)
    # Remove cached render module so each test gets a fresh import
    monkeypatch.delitem(sys.modules, 'render', raising=False)
    yield bpy_mock


def test_check_blender_exits_when_not_on_path():
    """When blender binary isn't on PATH, check_blender() should sys.exit with message."""
    import render
    with patch("shutil.which", return_value=None):
        with pytest.raises(SystemExit):
            render.check_blender()


def test_load_config_exits_when_file_missing(tmp_path):
    """When config.ini doesn't exist, load_config() should sys.exit."""
    import render
    with pytest.raises(SystemExit):
        render.load_config(str(tmp_path / "nonexistent.ini"))
