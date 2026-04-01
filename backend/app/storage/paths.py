"""
Storage Paths - 环境相关的存储路径配置

存储路径按环境分离：
- development: DATA_DIR (默认 ~/Downloads/dev/fengxian-cyber-taoist-data)
- test: 进程级缓存临时目录 /tmp/fengxian-test-{固定值}
- production: DATA_DIR (必需)

用法:
    from app.storage.paths import get_data_dir, get_upload_dir
"""

import os

# 进程级缓存 (避免测试时每次调用生成新路径)
_test_data_dir: str | None = None


def _get_env() -> str:
    """获取当前环境"""
    return os.environ.get('FLASK_ENV', 'development')


def get_data_dir() -> str:
    """
    获取数据根目录。

    开发环境: DATA_DIR 环境变量或 ~/Downloads/dev/fengxian-cyber-taoist-data
    测试环境: TEST_DATA_DIR 或进程级缓存临时目录
    生产环境: DATA_DIR 环境变量 (必需)
    """
    global _test_data_dir
    env = _get_env()

    if env == 'test':
        test_dir = os.environ.get('TEST_DATA_DIR')
        if test_dir:
            return test_dir
        if _test_data_dir is None:
            _test_data_dir = f"/tmp/fengxian-test-{os.getpid()}"
        return _test_data_dir

    if env == 'production':
        data_dir = os.environ.get('DATA_DIR')
        if not data_dir:
            raise ValueError(
                "生产环境必须设置 DATA_DIR 环境变量指定数据存储路径。\n"
                "示例: DATA_DIR=/var/lib/fengxian/data"
            )
        return data_dir

    # 开发环境: 默认到 home 目录下数据目录（避免污染源码树）
    default_dev_dir = os.path.expanduser('~/.fengxian-data')
    return os.environ.get('DATA_DIR', default_dev_dir)


def get_upload_dir(*subdirs: str) -> str:
    """
    获取上传文件存储目录。

    Args:
        *subdirs: 子目录路径，如 ('users',) 或 ('divination', 'charts')

    Returns:
        完整的目录路径
    """
    base = get_data_dir()
    if subdirs:
        return os.path.join(base, *subdirs)
    return base


def ensure_dir(*path_parts: str) -> str:
    """
    确保目录存在并返回路径。

    Args:
        *path_parts: 路径部分

    Returns:
        完整路径
    """
    path = os.path.join(*path_parts) if path_parts else get_data_dir()
    os.makedirs(path, exist_ok=True)
    return path
