import pytest
from unittest.mock import patch


def test_ensure_output_dir_exits_on_permission_error():
    """When output dir can't be created due to permissions, should sys.exit."""
    import compiler
    with patch("compiler.os.makedirs", side_effect=PermissionError("denied")):
        with pytest.raises(SystemExit):
            compiler.ensure_output_dir("/nonexistent/output")
