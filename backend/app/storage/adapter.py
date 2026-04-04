"""
JSON File Storage Adapter - 基于 JSON 文件的存储适配器

实现 StorageAdapter 接口，将数据以 JSON 格式存储到文件系统。
未来可替换为数据库适配器而无需修改使用方代码。
"""

import os
import json
import logging
import tempfile
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .paths import get_upload_dir, ensure_dir

logger = logging.getLogger(__name__)


class StorageAdapter(ABC):
    """
    存储适配器抽象接口

    所有存储实现必须实现此接口，确保可替换性。
    """

    @abstractmethod
    def save(self, key: str, data: Dict[str, Any], **kwargs) -> None:
        """保存数据"""
        pass

    @abstractmethod
    def load(self, key: str, **kwargs) -> Optional[Dict[str, Any]]:
        """加载数据"""
        pass

    @abstractmethod
    def delete(self, key: str, **kwargs) -> bool:
        """删除数据"""
        pass

    @abstractmethod
    def exists(self, key: str, **kwargs) -> bool:
        """检查数据是否存在"""
        pass

    @abstractmethod
    def list_keys(self, prefix: str = "", **kwargs) -> List[str]:
        """列出所有键"""
        pass


class JSONFileStorageAdapter(StorageAdapter):
    """
    JSON 文件存储适配器

    将数据存储为 JSON 文件，支持子目录组织。
    键格式: "file.json" 或 "subdir/file.json"
    """

    def __init__(self, base_subdir: str = ""):
        """
        初始化适配器

        Args:
            base_subdir: 基础子目录，如 "divination/charts"
        """
        self.base_subdir = base_subdir
        self._base_path = get_upload_dir() if not base_subdir else get_upload_dir(*base_subdir.split('/'))

    def _resolve_path(self, key: str) -> str:
        """将键转换为完整文件路径"""
        # 确保 key 是安全的文件路径
        key = key.lstrip('/')
        return os.path.join(self._base_path, key)

    def save(self, key: str, data: Dict[str, Any], **kwargs) -> None:
        """
        保存数据到 JSON 文件

        Args:
            key: 文件键，如 "chart.json" 或 "charts/abc123/chart.json"
            data: 要存储的字典数据
        """
        filepath = self._resolve_path(key)

        # 确保父目录存在
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)

        # 原子写入: 先写临时文件再 rename（同一文件系统下原子操作）
        dirname, basename = os.path.dirname(filepath), os.path.basename(filepath)
        tmp_fd, tmp_path = tempfile.mkstemp(dir=dirname or '.', prefix=f'.{basename}.', suffix='.tmp')
        try:
            with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, **kwargs)
            os.replace(tmp_path, filepath)  # 原子替换
        except Exception:
            # 写入失败时清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def load(self, key: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        从 JSON 文件加载数据

        Args:
            key: 文件键

        Returns:
            字典数据，不存在则返回 None
        """
        filepath = self._resolve_path(key)
        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f, **kwargs)

    def delete(self, key: str, **kwargs) -> bool:
        """
        删除 JSON 文件

        Args:
            key: 文件键

        Returns:
            是否成功删除
        """
        filepath = self._resolve_path(key)
        if not os.path.exists(filepath):
            return False

        os.remove(filepath)

        # 尝试清理空父目录
        parent = os.path.dirname(filepath)
        try:
            if parent and os.path.isdir(parent) and not os.listdir(parent):
                os.rmdir(parent)
        except OSError:
            pass  # 忽略删除失败

        return True

    def exists(self, key: str, **kwargs) -> bool:
        """检查文件是否存在"""
        filepath = self._resolve_path(key)
        return os.path.exists(filepath)

    def list_keys(self, prefix: str = "", **kwargs) -> List[str]:
        """
        列出所有键

        Args:
            prefix: 只返回以此前缀开头的键

        Returns:
            键列表
        """
        if not os.path.exists(self._base_path):
            return []

        keys = []
        for root, dirs, files in os.walk(self._base_path):
            for filename in files:
                if filename.endswith('.json'):
                    rel_path = os.path.relpath(os.path.join(root, filename), self._base_path)
                    if prefix and not rel_path.startswith(prefix):
                        continue
                    keys.append(rel_path)

        return sorted(keys)


class UserStorageAdapter(JSONFileStorageAdapter):
    """用户存储适配器"""

    def __init__(self):
        super().__init__(base_subdir="users")

    def get_user_file(self, user_id: str) -> str:
        """获取用户文件路径"""
        return f"{user_id}.json"

    def get_subscription_file(self, user_id: str) -> str:
        """获取订阅文件路径"""
        return f"{user_id}_subscription.json"


class DivinationChartStorageAdapter(JSONFileStorageAdapter):
    """命盘存储适配器"""

    def __init__(self):
        super().__init__(base_subdir="divination/charts")

    def get_chart_meta_path(self, chart_id: str) -> str:
        """获取命盘元数据路径"""
        return f"{chart_id}/chart.json"


class DivinationReportStorageAdapter(JSONFileStorageAdapter):
    """报告存储适配器"""

    def __init__(self):
        super().__init__(base_subdir="divination/reports")

    def get_report_meta_path(self, report_id: str) -> str:
        """获取报告元数据路径"""
        return f"{report_id}/report.json"


class SimulationStorageAdapter(JSONFileStorageAdapter):
    """Simulation存储适配器

    统一管理 simulation 域的元数据存储（state.json, config.json）。
    其他仿真数据文件（profiles, agent logs, databases）由 SimulationManager
    和 SimulationRunner 直接管理，通过 Config.get_simulation_data_dir() 获取路径。
    """

    def __init__(self):
        super().__init__(base_subdir="simulations")

    def get_simulation_meta_path(self, simulation_id: str) -> str:
        """获取模拟元数据路径"""
        return f"{simulation_id}/state.json"

    def get_simulation_config_path(self, simulation_id: str) -> str:
        """获取模拟配置路径"""
        return f"{simulation_id}/config.json"


# 全局单例实例 (延迟初始化)
_user_storage: Optional[UserStorageAdapter] = None
_chart_storage: Optional[DivinationChartStorageAdapter] = None
_report_storage: Optional[DivinationReportStorageAdapter] = None
_simulation_storage: Optional[SimulationStorageAdapter] = None


def get_user_storage() -> UserStorageAdapter:
    """获取用户存储适配器单例"""
    global _user_storage
    if _user_storage is None:
        _user_storage = UserStorageAdapter()
        ensure_dir(get_upload_dir("users"))
    return _user_storage


def get_chart_storage() -> DivinationChartStorageAdapter:
    """获取命盘存储适配器单例"""
    global _chart_storage
    if _chart_storage is None:
        _chart_storage = DivinationChartStorageAdapter()
        ensure_dir(get_upload_dir("divination", "charts"))
    return _chart_storage


def get_report_storage() -> DivinationReportStorageAdapter:
    """获取报告存储适配器单例"""
    global _report_storage
    if _report_storage is None:
        _report_storage = DivinationReportStorageAdapter()
        ensure_dir(get_upload_dir("divination", "reports"))
    return _report_storage


def get_simulation_storage() -> SimulationStorageAdapter:
    """获取Simulation存储适配器单例"""
    global _simulation_storage
    if _simulation_storage is None:
        _simulation_storage = SimulationStorageAdapter()
        ensure_dir(get_upload_dir("simulations"))
    return _simulation_storage
