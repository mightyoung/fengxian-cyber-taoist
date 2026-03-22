"""
ReportService - 统一报告生成服务

提供从分析结果生成Markdown和PDF格式报告的统一服务。

功能：
1. 从命理分析结果生成Markdown报告
2. 支持导出为PDF格式
3. 提供REST API端点

支持的报告类型：
- 命理分析报告（紫微斗数）
- 预测报告（三层融合）
"""

import os
import uuid
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

import markdown

from ..config import Config
from ..utils.logger import get_logger

# Enhanced PDF generation with fpdf2 + CJK support
try:
    from ..utils.markdown_to_pdf import markdown_to_pdf as enhanced_markdown_to_pdf
    ENHANCED_PDF_AVAILABLE = True
except ImportError:
    ENHANCED_PDF_AVAILABLE = False
    logger.warning("Enhanced PDF not available, falling back to WeasyPrint")

# Lazy import for weasyprint (may fail on macOS without libgobject)
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    HTML = CSS = None
    WEASYPRINT_AVAILABLE = False

# MetaphysicsSwarm for emergence calculation
try:
    from ..services.divination.metaphysics_swarm import run_metaphysics_swarm
    METAPHYSICS_SWARM_AVAILABLE = True
except ImportError:
    METAPHYSICS_SWARM_AVAILABLE = False
    logger.warning("MetaphysicsSwarm not available, emergence calculation disabled")

logger = get_logger('fengxian_cyber_taoist.report_service')


class ReportFormat(str, Enum):
    """报告格式"""
    MARKDOWN = "markdown"
    PDF = "pdf"


class ReportType(str, Enum):
    """报告类型"""
    DIVINATION = "divination"           # 命理分析报告
    PREDICTION = "prediction"           # 预测报告
    ANALYSIS = "analysis"               # 综合分析报告


class ReportStatus(str, Enum):
    """报告状态"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ReportMetadata:
    """报告元数据"""
    report_id: str
    report_type: str
    chart_id: Optional[str] = None
    title: str = ""
    created_at: str = ""
    completed_at: Optional[str] = None
    target_year: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Report:
    """报告数据模型"""
    report_id: str
    report_type: str
    format: str
    status: str
    title: str
    markdown_content: str = ""
    pdf_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    created_at: str = ""
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "format": self.format,
            "status": self.status,
            "title": self.title,
            "markdown_content": self.markdown_content,
            "pdf_path": self.pdf_path,
            "metadata": self.metadata,
            "error": self.error,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }


class ReportService:
    """
    统一的报告生成服务

    提供从分析结果生成Markdown和PDF格式报告的统一接口。
    """

    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.reports_dir = Path(Config.UPLOAD_FOLDER) / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _get_report_dir(self, report_id: str) -> Path:
        """获取报告目录"""
        report_dir = self.reports_dir / report_id
        report_dir.mkdir(parents=True, exist_ok=True)
        return report_dir

    async def generate(
        self,
        chart: Dict[str, Any],
        analysis_result: Dict[str, Any],
        format: str = "markdown",
        report_type: str = "divination",
        enable_swarm: bool = False,
        swarm_rounds: int = 10,
        charts: Optional[Dict[str, bytes]] = None,
        user_info: Optional[Dict[str, Any]] = None,
        heatmap: Optional[bytes] = None,
        monthly_advice: Optional[List[Dict[str, Any]]] = None
    ) -> Report:
        """
        生成报告

        Args:
            chart: 命盘数据
            analysis_result: 分析结果数据
            format: 报告格式 (markdown/pdf)
            report_type: 报告类型
            enable_swarm: 启用MetaphysicsSwarm
            swarm_rounds: 群体模拟轮数
            charts: 图表字典 {type: image_bytes}
            user_info: 用户信息 {name, year, birth, judgment}
            heatmap: 热力图图片数据
            monthly_advice: 月度行动建议列表

        Returns:
            Report对象
        """
        report_id = f"report_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()

        # 从chart中提取用户信息
        birth_info = chart.get("birth_info", {})
        report_title = chart.get("title", "命理分析报告")

        # 如果没有传入user_info，从birth_info构建
        if not user_info and birth_info:
            user_info = {
                "name": birth_info.get("name", birth_info.get("year_gan", "") + birth_info.get("year_zhi", "") + "命主"),
                "year": str(analysis_result.get("target_year", datetime.now().year)),
                "birth": f"{birth_info.get('year', '')}年{birth_info.get('month', '')}月{birth_info.get('day', '')}日",
                "judgment": analysis_result.get("overall_judgment", "运势平稳")
            }

        report = Report(
            report_id=report_id,
            report_type=report_type,
            format=format,
            status=ReportStatus.GENERATING.value,
            title=report_title,
            created_at=now,
            metadata={
                "chart_id": chart.get("chart_id"),
                "birth_info": birth_info,
                "target_year": analysis_result.get("target_year")
            }
        )

        try:
            # 运行MetaphysicsSwarm群体涌现计算（如果启用）
            if enable_swarm and METAPHYSICS_SWARM_AVAILABLE:
                try:
                    target_year = analysis_result.get("target_year", datetime.now().year)
                    emergence_result = await run_metaphysics_swarm(
                        chart_data=chart,
                        target_year=target_year,
                        rounds=swarm_rounds
                    )
                    # 将涌现结果添加到analysis_result
                    analysis_result["emergence"] = emergence_result.to_dict() if hasattr(emergence_result, 'to_dict') else {
                        "overall_score": emergence_result.overall_score,
                        "overall_trend": emergence_result.overall_trend,
                        "dimension_scores": emergence_result.dimension_scores,
                        "key_events": emergence_result.key_events,
                        "emergence_patterns": emergence_result.emergence_patterns,
                        "suggestions": emergence_result.suggestions,
                        "confidence": emergence_result.confidence,
                    }
                    logger.info(f"MetaphysicsSwarm emergence calculated: score={emergence_result.overall_score}")
                except Exception as swarm_error:
                    logger.warning(f"MetaphysicsSwarm failed: {swarm_error}, continuing without emergence")

            # 根据报告类型生成不同的内容
            if report_type == ReportType.PREDICTION.value:
                report.markdown_content = self._generate_prediction_markdown(
                    chart, analysis_result
                )
            else:
                # 默认生成命理分析报告
                report.markdown_content = self._generate_divination_markdown(
                    chart, analysis_result
                )

            # 如果需要PDF格式，同时生成PDF
            if format == ReportFormat.PDF.value:
                pdf_path = await self._generate_pdf(
                    report_id,
                    report.markdown_content,
                    report.title,
                    charts=charts,
                    user_info=user_info,
                    heatmap=heatmap,
                    monthly_advice=monthly_advice
                )
                report.pdf_path = pdf_path

            report.status = ReportStatus.COMPLETED.value
            report.completed_at = datetime.now().isoformat()

            # 保存报告
            await self._save_report(report)

            logger.info(f"报告生成完成: {report_id}")
            return report

        except Exception as e:
            logger.error(f"报告生成失败: {str(e)}")
            report.status = ReportStatus.FAILED.value
            report.error = str(e)
            return report

    def _generate_divination_markdown(
        self,
        chart: Dict[str, Any],
        analysis_result: Dict[str, Any]
    ) -> str:
        """生成命理分析报告Markdown"""
        lines = [
            "# 紫微斗数命理分析报告\n",
            f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        ]

        # 添加基本信息
        birth_info = chart.get("birth_info", {})
        lines.append("---\n")
        lines.append("## 命盘基础信息\n")
        lines.append(f"- **姓名**: {birth_info.get('name', '未知')}\n")
        lines.append(f"- **性别**: {birth_info.get('gender', '未知')}\n")
        lines.append(f"- **出生时间**: {birth_info.get('year', '')}年 "
                    f"{birth_info.get('month', '')}月 "
                    f"{birth_info.get('day', '')}日 "
                    f"{birth_info.get('hour', '')}时\n")
        lines.append(f"- **农历**: {birth_info.get('lunar_date', '未知')}\n")
        lines.append(f"- **命宫主星**: {chart.get('main_star', '未知')}\n")

        # 添加四化分析
        if "transforms" in analysis_result:
            lines.append("---\n")
            lines.append("## 四化分析\n")
            transforms = analysis_result.get("transforms", {})
            for transform_type, transform_data in transforms.items():
                lines.append(f"### {transform_type}\n")
                if isinstance(transform_data, dict):
                    for key, value in transform_data.items():
                        lines.append(f"- **{key}**: {value}\n")
                lines.append("\n")

        # 添加格局分析
        if "patterns" in analysis_result:
            lines.append("---\n")
            lines.append("## 格局分析\n")
            patterns = analysis_result.get("patterns", [])
            for pattern in patterns:
                lines.append(f"- {pattern}\n")

        # 添加因果链分析
        if "causal_chains" in analysis_result:
            lines.append("---\n")
            lines.append("## 因果链分析\n")
            causal_chains = analysis_result.get("causal_chains", [])
            for chain in causal_chains:
                lines.append(f"- {chain}\n")

        # 添加群体涌现分析（MetaphysicsSwarm）
        if "emergence" in analysis_result:
            emergence = analysis_result.get("emergence", {})
            if emergence:
                lines.append("---\n")
                lines.append("## 群体涌现分析\n")
                lines.append(f"- **整体得分**: {emergence.get('overall_score', 'N/A')}\n")
                lines.append(f"- **整体趋势**: {emergence.get('overall_trend', 'N/A')}\n")
                lines.append(f"- **置信度**: {emergence.get('confidence', 'N/A')}\n")

                # 维度得分
                dimension_scores = emergence.get("dimension_scores", {})
                if dimension_scores:
                    lines.append("\n### 维度得分\n")
                    for dim, score in dimension_scores.items():
                        lines.append(f"- **{dim}**: {score}\n")

                # 关键事件
                key_events = emergence.get("key_events", [])
                if key_events:
                    lines.append("\n### 关键事件\n")
                    for event in key_events:
                        lines.append(f"- {event}\n")

                # 涌现模式
                emergence_patterns = emergence.get("emergence_patterns", [])
                if emergence_patterns:
                    lines.append("\n### 涌现模式\n")
                    for pattern in emergence_patterns:
                        lines.append(f"- {pattern}\n")

                # 建议
                suggestions = emergence.get("suggestions", [])
                if suggestions:
                    lines.append("\n### 群体建议\n")
                    for suggestion in suggestions:
                        lines.append(f"- {suggestion}\n")

        # 添加流年运势
        if "yearly_analysis" in analysis_result:
            lines.append("---\n")
            lines.append("## 流年运势\n")
            yearly = analysis_result.get("yearly_analysis", {})
            for year_key, year_data in yearly.items():
                lines.append(f"### {year_key}\n")
                if isinstance(year_data, dict):
                    for key, value in year_data.items():
                        lines.append(f"- **{key}**: {value}\n")
                lines.append("\n")

        # 添加趋避建议
        if "suggestions" in analysis_result:
            lines.append("---\n")
            lines.append("## 趋避建议\n")
            suggestions = analysis_result.get("suggestions", [])
            for suggestion in suggestions:
                lines.append(f"- {suggestion}\n")

        return "".join(lines)

    def _generate_prediction_markdown(
        self,
        chart: Dict[str, Any],
        analysis_result: Dict[str, Any]
    ) -> str:
        """生成预测报告Markdown"""
        lines = [
            "# 三层融合预测报告\n",
            f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**目标年份**: {analysis_result.get('target_year', '未知')}\n",
            f"**命盘ID**: {chart.get('chart_id', '未知')}\n",
            "---\n",
            "## 综合判断\n"
        ]

        # 综合判断
        overall_judgment = analysis_result.get("overall_judgment", "平")
        overall_confidence = analysis_result.get("overall_confidence", 0.5)
        lines.append(f"- **整体运势**: {overall_judgment}\n")
        lines.append(f"- **置信度**: {overall_confidence:.1%}\n")

        # 三层分析
        lines.append("---\n")
        lines.append("## 三层分析\n")

        # 因果链分析
        if "causal_chain_result" in analysis_result:
            lines.append("### 因果链推理 (权重40%)\n")
            cr = analysis_result.get("causal_chain_result", {})
            lines.append(f"- **严重程度**: {cr.get('severity_level', '未知')}\n")
            lines.append(f"- **置信度**: {cr.get('confidence', 0):.1%}\n")
            if cr.get("explanation"):
                lines.append(f"- **解释**: {cr.get('explanation')}\n")
            lines.append("\n")

        # 案例推理
        if "case_based_result" in analysis_result:
            lines.append("### 案例涌现推理 (权重35%)\n")
            cb = analysis_result.get("case_based_result", {})
            lines.append(f"- **置信度**: {cb.get('confidence', 0):.1%}\n")
            if cb.get("probability_summary"):
                lines.append(f"- **概率总结**: {cb.get('probability_summary')}\n")
            lines.append("\n")

        # 多Agent共识
        if "multi_agent_result" in analysis_result:
            lines.append("### 多Agent共识验证 (权重25%)\n")
            ma = analysis_result.get("multi_agent_result", {})
            lines.append(f"- **最终判断**: {ma.get('final_judgment', '未知')}\n")
            lines.append(f"- **置信度**: {ma.get('confidence', 0):.1%}\n")
            lines.append("\n")

        # 分维度分析
        if "dimensions" in analysis_result:
            lines.append("---\n")
            lines.append("## 分维度分析\n")
            dimensions = analysis_result.get("dimensions", {})
            for dim_name, dim_data in dimensions.items():
                lines.append(f"### {dim_name}\n")
                if isinstance(dim_data, dict):
                    judgment = dim_data.get("judgment", "平")
                    confidence = dim_data.get("confidence", 0.5)
                    reasoning = dim_data.get("reasoning", "")
                    lines.append(f"- **判断**: {judgment}\n")
                    lines.append(f"- **置信度**: {confidence:.1%}\n")
                    if reasoning:
                        lines.append(f"- **推理**: {reasoning}\n")
                lines.append("\n")

        # 趋避建议
        if "suggestions" in analysis_result:
            lines.append("---\n")
            lines.append("## 趋避建议\n")
            suggestions = analysis_result.get("suggestions", [])
            for suggestion in suggestions:
                lines.append(f"- {suggestion}\n")

        return "".join(lines)

    async def _generate_pdf(
        self,
        report_id: str,
        markdown_content: str,
        title: str,
        charts: Optional[Dict[str, bytes]] = None,
        user_info: Optional[Dict[str, Any]] = None,
        heatmap: Optional[bytes] = None,
        monthly_advice: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """生成PDF文件（使用增强版样式）"""
        report_dir = self._get_report_dir(report_id)
        pdf_path = str(report_dir / f"{report_id}.pdf")

        # 优先使用增强版PDF生成器（fpdf2 + CJK支持）
        if ENHANCED_PDF_AVAILABLE:
            try:
                enhanced_markdown_to_pdf(
                    markdown_text=markdown_content,
                    title=title,
                    output_path=pdf_path,
                    charts=charts,
                    user_info=user_info,
                    heatmap=heatmap,
                    monthly_advice=monthly_advice
                )
                logger.info(f"增强版PDF已生成: {pdf_path}")
                return pdf_path
            except Exception as e:
                logger.warning(f"增强版PDF生成失败: {e}，尝试使用WeasyPrint")

        # 降级到WeasyPrint
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError("PDF generation failed. Please install libgobject on macOS or use markdown format.")

        # 转换为HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'toc']
        )

        # 添加样式
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title}</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: "PingFang SC", "Microsoft YaHei", "SimHei", sans-serif;
                    font-size: 12pt;
                    line-height: 1.6;
                    color: #333;
                }}
                h1 {{
                    font-size: 24pt;
                    color: #1E2761;
                    border-bottom: 2px solid #1E2761;
                    padding-bottom: 10px;
                    text-align: center;
                }}
                h2 {{
                    font-size: 18pt;
                    color: #2C5F2D;
                    margin-top: 20pt;
                    border-left: 4px solid #2C5F2D;
                    padding-left: 10px;
                }}
                h3 {{
                    font-size: 14pt;
                    color: #065A82;
                    margin-top: 15pt;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15pt 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8pt;
                    text-align: left;
                }}
                th {{
                    background-color: #1E2761;
                    color: white;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                strong {{
                    color: #990011;
                }}
                .warning {{
                    background-color: #FFF3CD;
                    border-left: 4px solid #FFC107;
                    padding: 10pt;
                    margin: 10pt 0;
                }}
                .info {{
                    background-color: #D1ECF1;
                    border-left: 4px solid #17A2B8;
                    padding: 10pt;
                    margin: 10pt 0;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2pt 4pt;
                    border-radius: 3pt;
                    font-family: Consolas, monospace;
                }}
                blockquote {{
                    border-left: 4px solid #6D2E46;
                    margin: 10pt 0;
                    padding: 10pt 20pt;
                    background-color: #FCF6F5;
                    color: #6D2E46;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        HTML(string=styled_html).write_pdf(pdf_path, stylesheets=[CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
            }
        ''')])

        logger.info(f"PDF已生成: {pdf_path}")
        return pdf_path

    async def _save_report(self, report: Report) -> None:
        """保存报告到文件"""
        report_dir = self._get_report_dir(report.report_id)

        # 保存Markdown
        md_path = report_dir / f"{report.report_id}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report.markdown_content)

        # 保存元数据
        meta_path = report_dir / "metadata.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)

    async def get_report(self, report_id: str) -> Optional[Report]:
        """获取报告"""
        report_dir = self.reports_dir / report_id
        meta_path = report_dir / "metadata.json"

        if not meta_path.exists():
            return None

        with open(meta_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return Report(**data)

    async def get_markdown(self, report_id: str) -> Optional[str]:
        """获取报告Markdown内容"""
        report = await self.get_report(report_id)
        if not report:
            return None
        return report.markdown_content

    async def get_pdf_path(self, report_id: str) -> Optional[str]:
        """获取PDF文件路径"""
        report = await self.get_report(report_id)
        if not report or not report.pdf_path:
            return None

        if os.path.exists(report.pdf_path):
            return report.pdf_path
        return None

    async def export_pdf(self, report_id: str) -> Optional[str]:
        """导出PDF（如果不存在则重新生成）"""
        report = await self.get_report(report_id)
        if not report:
            return None

        # 如果PDF已存在，直接返回
        if report.pdf_path and os.path.exists(report.pdf_path):
            return report.pdf_path

        # 重新生成PDF
        if report.markdown_content:
            pdf_path = await self._generate_pdf(
                report_id,
                report.markdown_content,
                report.title
            )
            report.pdf_path = pdf_path
            await self._save_report(report)
            return pdf_path

        return None

    async def list_reports(
        self,
        report_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Report]:
        """列出报告"""
        reports = []

        if not self.reports_dir.exists():
            return reports

        for report_dir in self.reports_dir.iterdir():
            if not report_dir.is_dir():
                continue

            meta_path = report_dir / "metadata.json"
            if not meta_path.exists():
                continue

            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if report_type and data.get("report_type") != report_type:
                    continue

                reports.append(Report(**data))
            except Exception as e:
                logger.warning(f"读取报告失败: {report_dir.name}, {str(e)}")
                continue

        # 按创建时间倒序排列
        reports.sort(key=lambda r: r.created_at, reverse=True)
        return reports[:limit]

    async def delete_report(self, report_id: str) -> bool:
        """删除报告"""
        report_dir = self.reports_dir / report_id
        if not report_dir.exists():
            return False

        import shutil
        shutil.rmtree(report_dir)
        return True


# 全局服务实例
_report_service: Optional[ReportService] = None


def get_report_service() -> ReportService:
    """获取报告服务实例"""
    global _report_service
    if _report_service is None:
        _report_service = ReportService()
    return _report_service
