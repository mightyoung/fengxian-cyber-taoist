"""
Storage Adapter - 存储适配器接口

提供统一的数据存储接口，支持文件系统和未来扩展到数据库。

主要组件:
- StorageAdapter: 存储适配器抽象接口
- JSONFileStorageAdapter: 基于 JSON 文件的存储实现
- get_user_storage() / get_chart_storage() / get_report_storage(): 存储单例访问函数

环境配置:
- DATA_DIR: 数据存储根目录
- FLASK_ENV: development | test | production
  - development: 使用 DATA_DIR 或默认 backend/app/uploads
  - test: 使用临时目录 /tmp/fengxian-test-{uuid}
  - production: 必须设置 DATA_DIR
"""

from .adapter import (
    StorageAdapter,
    JSONFileStorageAdapter,
    UserStorageAdapter,
    DivinationChartStorageAdapter,
    DivinationReportStorageAdapter,
    get_user_storage,
    get_chart_storage,
    get_report_storage,
)
from .paths import get_data_dir, get_upload_dir, ensure_dir

__all__ = [
    "StorageAdapter",
    "JSONFileStorageAdapter",
    "UserStorageAdapter",
    "DivinationChartStorageAdapter",
    "DivinationReportStorageAdapter",
    "get_user_storage",
    "get_chart_storage",
    "get_report_storage",
    "get_data_dir",
    "get_upload_dir",
    "ensure_dir",
]
