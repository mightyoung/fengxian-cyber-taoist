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
class DivinationReport:
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
    def from_dict(cls, data: Dict[str, Any]) -> "DivinationReport":
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
    def _report_markdown_key(cls, report_id: str) -> str:
        """获取报告Markdown内容的存储键"""
        return f"{report_id}/report.md"

    @classmethod
    def save_report(cls, report: DivinationReport) -> None:
        """保存报告"""
        from app.storage.adapter import get_report_storage

        storage = get_report_storage()
        # 1. 保存元数据 (JSON)
        storage.save(cls._report_meta_key(report.report_id), report.to_dict())
        # 2. 保存Markdown内容 (MD)
        if report.markdown_content:
            storage.save_text(cls._report_markdown_key(report.report_id), report.markdown_content)

    @classmethod
    def get_report(cls, report_id: str) -> Optional[DivinationReport]:
        """获取报告"""
        from app.storage.adapter import get_report_storage

        storage = get_report_storage()
        data = storage.load(cls._report_meta_key(report_id))
        if data is None:
            return None
        return DivinationReport.from_dict(data)

    @classmethod
    def create_report(
        cls,
        chart_id: str,
        user_name: str,
        target_year: int,
        report_type: str,
        markdown_content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DivinationReport:
        """创建新报告"""
        report_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        report = DivinationReport(
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
    def get_reports_by_chart(cls, chart_id: str) -> List[DivinationReport]:
        """获取指定命盘的所有报告"""
        from app.storage.adapter import get_report_storage

        storage = get_report_storage()
        keys = storage.list_keys()
        reports = []

        for key in keys:
            if key.endswith('report.json'):
                report_id = key.split('/')[0]
                report = cls.get_report(report_id)
                if report and report.chart_id == chart_id:
                    reports.append(report)

        return reports

    @classmethod
    def list_reports(cls, limit: int = 100, offset: int = 0) -> List[DivinationReport]:
        """列出报告（按创建时间倒序）"""
        from app.storage.adapter import get_report_storage

        storage = get_report_storage()
        keys = sorted([k for k in storage.list_keys() if k.endswith('report.json')], reverse=True)

        reports = []
        for key in keys[offset:offset + limit]:
            report_id = key.split('/')[0]
            report = cls.get_report(report_id)
            if report:
                reports.append(report)

        return reports

    @classmethod
    def save_report_feedback(cls, report_id: str, rating: int, comment: Optional[str] = None) -> bool:
        """保存用户对报告的反馈（用于因果校准）"""
        report = cls.get_report(report_id)
        if not report:
            return False
        
        if report.metadata is None:
            report.metadata = {}
            
        report.metadata["user_rating"] = rating
        report.metadata["user_comment"] = comment
        report.metadata["calibrated_at"] = datetime.now().isoformat()
        
        cls.save_report(report)
        logger.info(f"报告 {report_id} 已获得用户评价: {rating}")
        return True

    @classmethod
    def get_global_stats(cls, limit: int = 100) -> Dict[str, Any]:
        """聚合全服运势统计"""
        reports = cls.list_reports(limit=limit)
        if not reports:
            return {
                "total_count": 0,
                "vibe_distribution": {"吉": 0, "平": 0, "凶": 0},
                "average_year": datetime.now().year
            }
            
        vibes = {"吉": 0, "平": 0, "凶": 0}
        years = []
        
        for r in reports:
            # 1. 优先从 metadata 获取
            judgment = None
            if r.metadata and "overall_judgment" in r.metadata:
                judgment = r.metadata["overall_judgment"]
            
            # 2. 如果 metadata 没有，尝试从正文解析
            if not judgment and r.markdown_content:
                if "吉" in r.markdown_content[:500]: judgment = "吉"
                elif "凶" in r.markdown_content[:500]: judgment = "凶"
                else: judgment = "平"
            
            if judgment:
                if "吉" in judgment: vibes["吉"] += 1
                elif "凶" in judgment: vibes["凶"] += 1
                else: vibes["平"] += 1
                
            years.append(r.target_year)
            
        total = len(reports)
        return {
            "total_count": total,
            "vibe_distribution": vibes,
            "vibe_percentages": {k: round(v/total*100, 1) for k, v in vibes.items()} if total > 0 else {},
            "average_year": round(sum(years)/total) if years else datetime.now().year,
            "updated_at": datetime.now().isoformat()
        }
