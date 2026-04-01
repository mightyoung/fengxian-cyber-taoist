"""
Divination Persistence Manager - 紫微斗数持久化管理器

负责命盘和报告的持久化存储，使用 StorageAdapter 接口。
存储路径通过环境变量 DATA_DIR 配置。
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


class DivinationStatus(str):
    """状态枚举"""
    CHART_GENERATED = "chart_generated"
    CHART_ANALYZED = "chart_analyzed"
    REPORT_GENERATING = "report_generating"
    REPORT_COMPLETED = "report_completed"
    REPORT_FAILED = "report_failed"


@dataclass
class BirthChart:
    """命盘数据模型"""
    chart_id: str
    birth_info: Dict[str, Any]
    chart_data: Dict[str, Any]
    created_at: str
    updated_at: str
    status: str = DivinationStatus.CHART_GENERATED

    # 分析结果（分析完成后填充）
    analysis: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "chart_id": self.chart_id,
            "birth_info": self.birth_info,
            "chart_data": self.chart_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "analysis": self.analysis,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BirthChart":
        """从字典创建"""
        return cls(
            chart_id=data["chart_id"],
            birth_info=data["birth_info"],
            chart_data=data["chart_data"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            status=data.get("status", DivinationStatus.CHART_GENERATED),
            analysis=data.get("analysis"),
        )


@dataclass
class PredictionReport:
    """预测报告数据模型"""
    report_id: str
    chart_id: str
    user_name: str
    target_year: int
    report_type: str  # professional_plain, xiaohongshu, full
    markdown_content: str
    created_at: str
    completed_at: Optional[str] = None
    status: str = DivinationStatus.REPORT_GENERATING
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "report_id": self.report_id,
            "chart_id": self.chart_id,
            "user_name": self.user_name,
            "target_year": self.target_year,
            "report_type": self.report_type,
            "markdown_content": self.markdown_content,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PredictionReport":
        """从字典创建"""
        return cls(
            report_id=data["report_id"],
            chart_id=data["chart_id"],
            user_name=data["user_name"],
            target_year=data["target_year"],
            report_type=data["report_type"],
            markdown_content=data["markdown_content"],
            created_at=data["created_at"],
            completed_at=data.get("completed_at"),
            status=data.get("status", DivinationStatus.REPORT_GENERATING),
            metadata=data.get("metadata"),
        )


class DivinationManager:
    """紫微斗数持久化管理器"""

    @classmethod
    def _get_report_dir(cls, report_id: str) -> str:
        """获取报告目录路径"""
        return report_id

    # ==================== 命盘管理 ====================

    @classmethod
    def _chart_meta_key(cls, chart_id: str) -> str:
        """获取命盘元数据的存储键"""
        return f"{chart_id}/chart.json"

    @classmethod
    def save_chart(cls, chart: BirthChart) -> None:
        """保存命盘"""
        from app.storage.adapter import get_chart_storage

        chart.updated_at = datetime.now().isoformat()
        storage = get_chart_storage()
        storage.save(cls._chart_meta_key(chart.chart_id), chart.to_dict())

    @classmethod
    def get_chart(cls, chart_id: str) -> Optional[BirthChart]:
        """获取命盘"""
        from app.storage.adapter import get_chart_storage

        storage = get_chart_storage()
        data = storage.load(cls._chart_meta_key(chart_id))
        if data is None:
            return None
        return BirthChart.from_dict(data)

    @classmethod
    def create_chart(cls, birth_info: Dict[str, Any], chart_data: Dict[str, Any]) -> BirthChart:
        """创建新命盘"""
        chart_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        chart = BirthChart(
            chart_id=chart_id,
            birth_info=birth_info,
            chart_data=chart_data,
            created_at=now,
            updated_at=now,
            status=DivinationStatus.CHART_GENERATED,
        )

        cls.save_chart(chart)
        return chart

    @classmethod
    def update_chart_analysis(cls, chart_id: str, analysis: Dict[str, Any]) -> Optional[BirthChart]:
        """更新命盘分析结果"""
        chart = cls.get_chart(chart_id)
        if not chart:
            return None

        chart.analysis = analysis
        chart.status = DivinationStatus.CHART_ANALYZED
        cls.save_chart(chart)
        return chart

    @classmethod
    def list_charts(cls, limit: int = 100, offset: int = 0) -> List[BirthChart]:
        """列出命盘（按创建时间倒序）"""
        from app.storage.adapter import get_chart_storage

        storage = get_chart_storage()
        keys = storage.list_keys()
        keys = sorted(keys, reverse=True)

        charts = []
        for key in keys[offset:offset + limit]:
            # key 格式: chart_id/chart.json
            chart_id = key.split('/')[0]
            chart = cls.get_chart(chart_id)
            if chart:
                charts.append(chart)

        return charts

    @classmethod
    def delete_chart(cls, chart_id: str) -> bool:
        """删除命盘"""
        from app.storage.adapter import get_chart_storage

        storage = get_chart_storage()
        return storage.delete(cls._chart_meta_key(chart_id))

    # ==================== 报告管理 ====================

    @classmethod
    def _report_meta_key(cls, report_id: str) -> str:
        """获取报告元数据的存储键"""
        return f"{report_id}/report.json"

    @classmethod
    def save_report(cls, report: PredictionReport) -> None:
        """保存报告"""
        from app.storage.adapter import get_report_storage

        storage = get_report_storage()
        storage.save(cls._report_meta_key(report.report_id), report.to_dict())

    @classmethod
    def get_report(cls, report_id: str) -> Optional[PredictionReport]:
        """获取报告"""
        from app.storage.adapter import get_report_storage

        storage = get_report_storage()
        data = storage.load(cls._report_meta_key(report_id))
        if data is None:
            return None
        return PredictionReport.from_dict(data)

    @classmethod
    def create_report(
        cls,
        chart_id: str,
        user_name: str,
        target_year: int,
        report_type: str,
        markdown_content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PredictionReport:
        """创建新报告"""
        report_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        report = PredictionReport(
            report_id=report_id,
            chart_id=chart_id,
            user_name=user_name,
            target_year=target_year,
            report_type=report_type,
            markdown_content=markdown_content,
            created_at=now,
            completed_at=now,
            status=DivinationStatus.REPORT_COMPLETED,
            metadata=metadata,
        )

        cls.save_report(report)
        return report

    @classmethod
    def get_reports_by_chart(cls, chart_id: str) -> List[PredictionReport]:
        """获取指定命盘的所有报告"""
        from app.storage.adapter import get_report_storage

        storage = get_report_storage()
        keys = storage.list_keys()
        reports = []

        for key in keys:
            report_id = key.split('/')[0] if '/' in key else key
            report = cls.get_report(report_id)
            if report and report.chart_id == chart_id:
                reports.append(report)

        return reports

    @classmethod
    def list_reports(cls, limit: int = 100, offset: int = 0) -> List[PredictionReport]:
        """列出报告（按创建时间倒序）"""
        from app.storage.adapter import get_report_storage

        storage = get_report_storage()
        keys = sorted(storage.list_keys(), reverse=True)

        reports = []
        for key in keys[offset:offset + limit]:
            report_id = key.split('/')[0] if '/' in key else key
            report = cls.get_report(report_id)
            if report:
                reports.append(report)

        return reports

    @classmethod
    def delete_report(cls, report_id: str) -> bool:
        """删除报告"""
        from app.storage.adapter import get_report_storage

        storage = get_report_storage()
        return storage.delete(cls._report_meta_key(report_id))
