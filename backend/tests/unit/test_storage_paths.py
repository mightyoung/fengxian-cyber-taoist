"""
Unit tests for storage paths - verifies get_data_dir() returns correct values per environment.
"""

import pytest
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)


class TestGetDataDir:
    """Test get_data_dir() returns correct path per FLASK_ENV."""

    def test_development_default_path(self, monkeypatch):
        """开发环境: 默认 ~/.fengxian-data"""
        monkeypatch.delenv('FLASK_ENV', raising=False)
        monkeypatch.delenv('DATA_DIR', raising=False)
        monkeypatch.delenv('TEST_DATA_DIR', raising=False)

        # Force reload to pick up env changes
        import importlib
        import app.storage.paths as paths_mod
        importlib.reload(paths_mod)

        result = paths_mod.get_data_dir()
        assert result == os.path.expanduser('~/.fengxian-data')

    def test_development_custom_data_dir(self, monkeypatch):
        """开发环境: DATA_DIR 环境变量优先"""
        monkeypatch.delenv('FLASK_ENV', raising=False)
        monkeypatch.setenv('DATA_DIR', '/custom/dev/path')
        monkeypatch.delenv('TEST_DATA_DIR', raising=False)

        import importlib
        import app.storage.paths as paths_mod
        importlib.reload(paths_mod)

        result = paths_mod.get_data_dir()
        assert result == '/custom/dev/path'

    def test_test_env_uses_test_data_dir(self, monkeypatch):
        """测试环境: TEST_DATA_DIR 环境变量优先"""
        monkeypatch.setenv('FLASK_ENV', 'test')
        monkeypatch.setenv('TEST_DATA_DIR', '/custom/test/path')
        monkeypatch.delenv('DATA_DIR', raising=False)

        import importlib
        import app.storage.paths as paths_mod
        importlib.reload(paths_mod)

        result = paths_mod.get_data_dir()
        assert result == '/custom/test/path'

    def test_test_env_uses_process_cache(self, monkeypatch):
        """测试环境: 无 TEST_DATA_DIR 时使用进程级缓存"""
        monkeypatch.setenv('FLASK_ENV', 'test')
        monkeypatch.delenv('TEST_DATA_DIR', raising=False)
        monkeypatch.delenv('DATA_DIR', raising=False)

        # Reset the module-level cache
        import importlib
        import app.storage.paths as paths_mod
        paths_mod._test_data_dir = None
        importlib.reload(paths_mod)

        result = paths_mod.get_data_dir()
        assert result.startswith('/tmp/fengxian-test-')
        assert os.path.dirname(result) == '/tmp'

    def test_production_requires_data_dir(self, monkeypatch):
        """生产环境: 必须设置 DATA_DIR"""
        monkeypatch.setenv('FLASK_ENV', 'production')
        monkeypatch.delenv('DATA_DIR', raising=False)
        monkeypatch.delenv('TEST_DATA_DIR', raising=False)

        import importlib
        import app.storage.paths as paths_mod
        importlib.reload(paths_mod)

        with pytest.raises(ValueError, match="生产环境必须设置 DATA_DIR"):
            paths_mod.get_data_dir()

    def test_production_with_data_dir(self, monkeypatch):
        """生产环境: DATA_DIR 设置后正常返回"""
        monkeypatch.setenv('FLASK_ENV', 'production')
        monkeypatch.setenv('DATA_DIR', '/var/lib/fengxian/data')
        monkeypatch.delenv('TEST_DATA_DIR', raising=False)

        import importlib
        import app.storage.paths as paths_mod
        importlib.reload(paths_mod)

        result = paths_mod.get_data_dir()
        assert result == '/var/lib/fengxian/data'
