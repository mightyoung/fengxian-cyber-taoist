"""
化解智能体 - 紫微斗数命盘化解建议
识别凶格和不利配置，提供化解方法
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import os


# ============ 数据结构 ============

class Severity(Enum):
    """严重程度"""
    MILD = "轻度"
    MODERATE = "中度"
    SEVERE = "重度"


class IssueType(Enum):
    """问题类型"""
    SHA_STAR = "煞星汇聚"        # 煞星（擎羊、陀罗、火星、铃星、地空、地劫）
    PATTERN = "凶格"            # 格局问题
    TRANSFORM = "化忌冲破"       # 四化问题
    COMBINATION = "星曜组合"     # 星曜配合问题


@dataclass
class IdentifiedIssue:
    """识别出的问题"""
    issue: str                    # 问题描述
    palace: str                   # 宫位
    severity: str                 # 严重程度
    issue_type: str               # 问题类型
    star_or_pattern: str = ""     # 涉及的星曜或格局
    details: str = ""             # 详细说明

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue": self.issue,
            "palace": self.palace,
            "severity": self.severity,
            "issue_type": self.issue_type,
            "star_or_pattern": self.star_or_pattern,
            "details": self.details
        }


@dataclass
class ResolutionMethod:
    """化解方法"""
    type: str                     # 方法类型（星曜化解、风水分解、颜色化解等）
    description: str              # 描述
    actions: List[str] = field(default_factory=list)  # 具体行动
    priority: int = 1             # 优先级
    when_to_use: str = ""         # 使用条件

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "description": self.description,
            "actions": self.actions,
            "priority": self.priority,
            "when_to_use": self.when_to_use
        }


@dataclass
class Resolution:
    """化解建议"""
    issue: str                    # 对应问题
    methods: List[str] = field(default_factory=list)  # 化解方法列表
    advice: str = ""              # 建议
    timing: str = ""              # 时机建议
    precautions: List[str] = field(default_factory=list)  # 注意事项

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue": self.issue,
            "methods": self.methods,
            "advice": self.advice,
            "timing": self.timing,
            "precautions": self.precautions
        }


@dataclass
class ResolutionAnalysis:
    """化解分析结果"""
    identified_issues: List[IdentifiedIssue] = field(default_factory=list)
    resolutions: List[Resolution] = field(default_factory=list)
    interpretation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identified_issues": [i.to_dict() for i in self.identified_issues],
            "resolutions": [r.to_dict() for r in self.resolutions],
            "interpretation": self.interpretation
        }


# ============ 知识库加载 ============

def load_resolution_knowledge() -> Dict[str, Any]:
    """加载化解知识库"""
    base_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..", "..",
        "data_source", "mlx", "data", "knowledge", "resolution"
    )

    knowledge = {
        "index": {},
        "methods": {},
        "guides": {},
        "patterns": {},
        "transforms": {},
        "key_principles": {}
    }

    # 加载 index.json
    index_path = os.path.join(base_path, "index.json")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            knowledge["index"] = json.load(f)

    # 加载 resolution-methods.json
    methods_path = os.path.join(base_path, "resolution-methods.json")
    if os.path.exists(methods_path):
        with open(methods_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            knowledge["methods"] = data.get("data", {})

    # 加载 resolution-guides.json
    guides_path = os.path.join(base_path, "resolution-guides.json")
    if os.path.exists(guides_path):
        with open(guides_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            knowledge["guides"] = data.get("data", {})

    # 加载 key-principles.json
    principles_path = os.path.join(base_path, "key-principles.json")
    if os.path.exists(principles_path):
        with open(principles_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            knowledge["key_principles"] = data.get("data", {})

    return knowledge


def load_pattern_rules() -> Dict[str, Any]:
    """加载格局规则"""
    rules_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..", "..",
        "data_source", "mlx", "data", "knowledge", "patterns", "inauspicious-patterns.json"
    )

    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ============ 煞星定义 ============

SIX_SHA_STARS = ["擎羊", "陀罗", "火星", "铃星", "地空", "地劫"]

SINI_STAR_NATURES = {
    "擎羊": "阳金，主竞争、刑克、伤害",
    "陀罗": "阴金，主延缓、出错、纠结",
    "火星": "阳火，主刚烈、急速、爆发",
    "铃星": "阴火，主暗昧、阴柔、持久",
    "地空": "阴火，空亡之气，主变动、破耗",
    "地劫": "阳火，破耗之星，主破败、消耗"
}


# ============ ResolutionAgent ============

class ResolutionAgent:
    """
    化解智能体

    识别命盘中的凶格和不利配置，
    从知识库查找对应的化解方法，
    输出化解建议
    """

    def __init__(self, chart_data: Any = None):
        """
        初始化化解智能体

        Args:
            chart_data: 命盘数据，包含宫位星曜信息
        """
        self.chart = chart_data
        self.knowledge = load_resolution_knowledge()
        self.pattern_rules = load_pattern_rules()

    def _extract_stars_from_palace(self, palace_stars: Any) -> Set[str]:
        """从宫位星曜数据中提取星曜列表"""
        stars: Set[str] = set()

        if isinstance(palace_stars, dict):
            for palace, star_list in palace_stars.items():
                if isinstance(star_list, list):
                    for star in star_list:
                        if isinstance(star, dict):
                            name = star.get("name", "")
                            if name:
                                stars.add(name)
                        elif isinstance(star, str):
                            stars.add(star)
        elif isinstance(palace_stars, list):
            for star in palace_stars:
                if isinstance(star, dict):
                    name = star.get("name", "")
                    if name:
                        stars.add(name)
                elif isinstance(star, str):
                    stars.add(star)

        return stars

    def _get_palace_stars_dict(self) -> Dict[str, List[str]]:
        """获取宫位星曜字典"""
        if self.chart is None:
            return {}

        palace_stars: Dict[str, List[str]] = {}

        # 尝试从 chart_data 中提取宫位星曜
        if isinstance(self.chart, dict):
            # 优先使用 palaces 字段
            if "palaces" in self.chart:
                palaces = self.chart["palaces"]
                if isinstance(palaces, dict):
                    for palace_name, stars in palaces.items():
                        star_list = []
                        if isinstance(stars, list):
                            for star in stars:
                                if isinstance(star, dict):
                                    name = star.get("name", "")
                                    if name:
                                        star_list.append(name)
                                elif isinstance(star, str):
                                    star_list.append(star)
                        palace_stars[palace_name] = star_list

            # 备选：从每个宫位字段提取
            elif "命宫" in self.chart or "身宫" in self.chart:
                for palace_name in ["命宫", "身宫", "父母宫", "福德宫", "田宅宫",
                                    "官禄宫", "仆役宫", "迁移宫", "疾厄宫",
                                    "财帛宫", "子女宫", "夫妻宫"]:
                    if palace_name in self.chart:
                        stars = self.chart[palace_name]
                        star_list = []
                        if isinstance(stars, list):
                            for star in stars:
                                if isinstance(star, dict):
                                    name = star.get("name", "")
                                    if name:
                                        star_list.append(name)
                                elif isinstance(star, str):
                                    star_list.append(star)
                        palace_stars[palace_name] = star_list

        return palace_stars

    def _identify_sha_star_issues(self, palace_stars: Dict[str, List[str]]) -> List[IdentifiedIssue]:
        """识别煞星问题"""
        issues: List[IdentifiedIssue] = []

        for palace, stars in palace_stars.items():
            stars_set = set(stars)

            # 检查每个煞星
            for sha in SIX_SHA_STARS:
                if sha in stars_set:
                    # 评估严重程度
                    severity = self._assess_sha_severity(sha, stars, palace, palace_stars)

                    # 构建问题描述
                    issue_desc = self._get_sha_issue_description(sha, palace, stars)

                    issues.append(IdentifiedIssue(
                        issue=issue_desc,
                        palace=palace,
                        severity=severity,
                        issue_type=IssueType.SHA_STAR.value,
                        star_or_pattern=sha,
                        details=SINI_STAR_NATURES.get(sha, "")
                    ))

        return issues

    def _assess_sha_severity(self, sha: str, stars: List[str],
                             palace: str, palace_stars: Dict[str, List[str]]) -> str:
        """评估煞星严重程度"""
        # 羊陀夹忌是最凶配置
        if sha in ["擎羊", "陀罗"]:
            # 检查是否有羊陀夹忌
            stars_set = set(stars)
            has_yang = "擎羊" in stars_set
            has_tuo = "陀罗" in stars_set
            has_ji = any("化忌" in s for s in stars)

            if has_yang and has_tuo and has_ji:
                return Severity.SEVERE.value

        # 火铃同会
        if sha in ["火星", "铃星"]:
            stars_set = set(stars)
            has_huo = "火星" in stars_set
            has_ling = "铃星" in stars_set
            if has_huo and has_ling:
                return Severity.SEVERE.value

        # 检查化忌
        has_ji = any("化忌" in s for s in stars)
        if has_ji:
            return Severity.SEVERE.value

        # 检查煞星数量
        sha_count = sum(1 for s in stars if s in SIX_SHA_STARS)
        if sha_count >= 2:
            return Severity.MODERATE.value

        # 独守
        if len(stars) <= 2:
            return Severity.MODERATE.value

        return Severity.MILD.value

    def _get_sha_issue_description(self, sha: str, palace: str, stars: List[str]) -> str:
        """获取煞星问题描述"""
        descriptions = {
            "擎羊": f"擎羊在{palace}宫，性格刚强、好斗、容易得罪人",
            "陀罗": f"陀罗在{palace}宫，做事拖延、犹豫不决、常错失良机",
            "火星": f"火星在{palace}宫，性格急躁、冲动易怒、容易得罪人",
            "铃星": f"铃星在{palace}宫，性格阴沉、暗中作祟、持久影响",
            "地空": f"地空在{palace}宫，理想主义、变动大、难聚财",
            "地劫": f"地劫在{palace}宫，财来财去、难聚财、破败消耗"
        }

        base_desc = descriptions.get(sha, f"{sha}在{palace}宫")

        # 检查加剧因素
        stars_set = set(stars)
        intensifying_factors = []

        if sha in ["擎羊", "陀罗"]:
            if "化忌" in stars_set:
                intensifying_factors.append("化忌加重刑克")
            if sha == "擎羊" and "陀罗" in stars_set:
                intensifying_factors.append("羊陀夹忌最凶")
            if sha == "陀罗" and "擎羊" in stars_set:
                intensifying_factors.append("羊陀夹忌最凶")

        if sha in ["火星", "铃星"]:
            if "铃星" in stars_set and sha == "火星":
                intensifying_factors.append("火铃齐发最凶")
            if "火星" in stars_set and sha == "铃星":
                intensifying_factors.append("火铃齐发最凶")

        if "地空" in stars_set or "地劫" in stars_set:
            if sha not in ["地空", "地劫"]:
                intensifying_factors.append("地空地劫加重破耗")

        if intensifying_factors:
            base_desc += "（" + "，".join(intensifying_factors) + "）"

        return base_desc

    def _identify_pattern_issues(self, palace_stars: Dict[str, List[str]]) -> List[IdentifiedIssue]:
        """识别格局问题"""
        issues: List[IdentifiedIssue] = []

        # 从知识库获取凶格列表
        pattern_data = self.knowledge.get("methods", {}).get("pattern_resolution", {})

        if not pattern_data:
            return issues

        # 遍历每个凶格，检查是否匹配
        for pattern_name, pattern_info in pattern_data.items():
            conditions = pattern_info.get("conditions", [])
            matched = self._check_pattern_match(conditions, palace_stars)

            if matched:
                issues.append(IdentifiedIssue(
                    issue=f"命盘存在【{pattern_name}】格局：{pattern_info.get('description', '')}",
                    palace=self._get_pattern_palace(conditions, palace_stars),
                    severity=self._assess_pattern_severity(pattern_name, palace_stars),
                    issue_type=IssueType.PATTERN.value,
                    star_or_pattern=pattern_name,
                    details=pattern_info.get("effects", "")
                ))

        return issues

    def _check_pattern_match(self, conditions: List[str], palace_stars: Dict[str, List[str]]) -> bool:
        """检查格局条件是否匹配"""
        if not conditions:
            return False

        # 收集所有宫位的星曜
        all_stars: Set[str] = set()
        for stars in palace_stars.values():
            for star in stars:
                if isinstance(star, dict):
                    name = star.get("name", "")
                    if name:
                        all_stars.add(name)
                elif isinstance(star, str):
                    all_stars.add(star)

        # 检查每个条件是否满足
        matched_count = 0
        for condition in conditions:
            # 宫位条件
            if "/" in condition:
                # 如 "子/亥/寅宫"
                palaces = condition.replace("宫", "").split("/")
                if any(p + "宫" in palace_stars for p in palaces):
                    matched_count += 1
            elif any(condition in star for star in all_stars):
                matched_count += 1

        # 至少满足一半条件
        return matched_count >= len(conditions) // 2 + 1

    def _get_pattern_palace(self, conditions: List[str], palace_stars: Dict[str, List[str]]) -> str:
        """获取格局涉及的宫位"""
        palace_map = {
            "命宫": "命宫", "身宫": "身宫", "财帛宫": "财帛宫",
            "官禄宫": "官禄宫", "迁移宫": "迁移宫", "夫妻宫": "夫妻宫",
            "子女宫": "子女宫", "父母宫": "父母宫", "福德宫": "福德宫",
            "田宅宫": "田宅宫", "疾厄宫": "疾厄宫", "仆役宫": "仆役宫"
        }

        for condition in conditions:
            for key, value in palace_map.items():
                if key in condition:
                    return value

        return "命宫"

    def _assess_pattern_severity(self, pattern_name: str, palace_stars: Dict[str, List[str]]) -> str:
        """评估格局严重程度"""
        severe_patterns = ["羊陀夹忌", "火铃夹命", "刑囚夹印"]

        if pattern_name in severe_patterns:
            return Severity.SEVERE.value

        return Severity.MODERATE.value

    def _identify_transform_issues(self, palace_stars: Dict[str, List[str]]) -> List[IdentifiedIssue]:
        """识别四化问题"""
        issues: List[IdentifiedIssue] = []

        transform_data = self.knowledge.get("methods", {}).get("transformation_resolution", {})

        for palace, stars in palace_stars.items():
            stars_set = set(stars)

            # 检查化忌
            for star in stars:
                if "化忌" in star:
                    # 获取原星
                    original_star = star.replace("化忌", "")

                    issues.append(IdentifiedIssue(
                        issue=f"{original_star}化忌冲{palace}宫，收敛、应期、挑战",
                        palace=palace,
                        severity=self._assess_transform_severity(star, stars, palace_stars),
                        issue_type=IssueType.TRANSFORM.value,
                        star_or_pattern=f"{original_star}化忌",
                        details=transform_data.get("化忌", {}).get("description", "收敛、应期、挑战")
                    ))

        return issues

    def _assess_transform_severity(self, transform_star: str, stars: List[str],
                                  palace_stars: Dict[str, List[str]]) -> str:
        """评估四化严重程度"""
        stars_set = set(stars)

        # 忌忌（双重化忌）
        if stars_set.intersection({"化忌"}):
            return Severity.SEVERE.value

        # 禄忌同宫
        if "化禄" in stars_set and "化忌" in stars_set:
            return Severity.MODERATE.value

        return Severity.MILD.value

    def _find_resolution_for_issue(self, issue: IdentifiedIssue) -> Resolution:
        """为问题查找化解方法"""
        resolution = Resolution(issue=issue.issue)

        if issue.issue_type == IssueType.SHA_STAR.value:
            self._find_sha_resolution(issue, resolution)
        elif issue.issue_type == IssueType.PATTERN.value:
            self._find_pattern_resolution(issue, resolution)
        elif issue.issue_type == IssueType.TRANSFORM.value:
            self._find_transform_resolution(issue, resolution)

        return resolution

    def _find_sha_resolution(self, issue: IdentifiedIssue, resolution: Resolution):
        """查找煞星化解方法"""
        sha = issue.star_or_pattern

        # 从知识库获取煞星化解指南
        guides = self.knowledge.get("guides", {}).get("sha_star_guides", [])

        for guide in guides:
            if guide.get("star") == sha:
                step_by_step = guide.get("step_by_step_resolution", {})

                # 获取化解方法
                resolve = step_by_step.get("step3_resolve", {})
                methods_list = resolve.get("methods", [])

                for method in methods_list:
                    method_type = method.get("type", "")
                    actions = method.get("actions", [])
                    description = method.get("description", "")

                    if actions:
                        resolution.methods.append(f"【{method_type}】{description}")
                        resolution.methods.extend(actions)

                # 获取时机
                support = step_by_step.get("step4_support", {})
                timing = support.get("timing", {})
                if timing:
                    resolution.timing = f"最佳时间: {timing.get('最佳时间', '需结合流年')}"
                    resolution.timing += f"；不宜时间: {timing.get('不宜时间', '羊陀迭现时')}"

                # 获取注意事项
                contra = guide.get("contraindications", {})
                do_not_do = contra.get("do_not_do", [])
                if do_not_do:
                    resolution.precautions = do_not_do[:3]  # 只取前3条

                return

        # 备用：从 resolution-methods.json 获取
        methods = self.knowledge.get("methods", {})
        shaxing_res = methods.get("shaxing_resolution", {}).get(sha, {})

        if shaxing_res:
            resolution.methods = shaxing_res.get("resolution", [])
            resolution.advice = f"借助吉星（禄存、紫微、天府）调和"

    def _find_pattern_resolution(self, issue: IdentifiedIssue, resolution: Resolution):
        """查找格局化解方法"""
        pattern_name = issue.star_or_pattern

        # 从知识库获取格局化解方法
        pattern_data = self.knowledge.get("methods", {}).get("pattern_resolution", {}).get(pattern_name, {})

        if pattern_data:
            resolution.methods = pattern_data.get("resolution", [])
            resolution.advice = pattern_data.get("effects", "")

    def _find_transform_resolution(self, issue: IdentifiedIssue, resolution: Resolution):
        """查找四化化解方法"""
        transform_star = issue.star_or_pattern

        # 从知识库获取四化化解方法
        transform_data = self.knowledge.get("methods", {}).get("transformation_resolution", {})

        if "化忌" in transform_star:
            ji_info = transform_data.get("化忌", {})
            resolution.methods = ji_info.get("resolution", [])

            combinations = ji_info.get("combinations", {})
            if combinations:
                advice_parts = []
                for combo, meaning in combinations.items():
                    advice_parts.append(f"{combo}：{meaning}")
                resolution.advice = "；".join(advice_parts)

        elif "忌冲" in issue.issue:
            ji_info = transform_data.get("忌冲", {})
            resolution.methods = ji_info.get("resolution", [])

    def _generate_interpretation(self, issues: List[IdentifiedIssue],
                                resolutions: List[Resolution]) -> str:
        """生成化解分析解释"""
        lines = []

        lines.append("【命盘化解分析】")
        lines.append("")

        # 问题概述
        if issues:
            severe_count = sum(1 for i in issues if i.severity == Severity.SEVERE.value)
            moderate_count = sum(1 for i in issues if i.severity == Severity.MODERATE.value)
            mild_count = sum(1 for i in issues if i.severity == Severity.MILD.value)

            lines.append("一、问题概述")
            lines.append(f"  共发现 {len(issues)} 个问题：")
            lines.append(f"    - 重度问题: {severe_count} 个")
            lines.append(f"    - 中度问题: {moderate_count} 个")
            lines.append(f"    - 轻度问题: {mild_count} 个")
            lines.append("")

        # 化解建议
        if resolutions:
            lines.append("二、化解建议")
            for i, res in enumerate(resolutions, 1):
                lines.append(f"  {i}. {res.issue}")
                if res.methods:
                    lines.append("    化解方法:")
                    for method in res.methods[:3]:  # 最多显示3个方法
                        lines.append(f"      - {method}")
                if res.timing:
                    lines.append(f"    时机: {res.timing}")
                if res.precautions:
                    lines.append(f"    注意: {', '.join(res.precautions[:2])}")
                lines.append("")

        # 核心原则
        key_principles = self.knowledge.get("key_principles", {})
        if key_principles:
            lines.append("三、化解核心原则")
            principles = key_principles.get("制煞为用", [])
            if principles:
                for p in principles[:3]:
                    lines.append(f"  - {p}")
            lines.append("")

        # 总结
        lines.append("四、总体建议")
        if severe_count > 0:
            lines.append("  命盘存在重度问题，建议寻求专业命理师指导。")
            lines.append("  化解需要多方配合，且需要当事人主动配合方能见效。")
        elif moderate_count > 0:
            lines.append("  命盘存在中度问题，建议配合化解方法进行调整。")
            lines.append("  重点关注煞星所在宫位对应的方位和颜色调整。")
        elif mild_count > 0:
            lines.append("  命盘问题较轻，可通过颜色、方位等简单方法化解。")
        else:
            lines.append("  命盘无明显凶格，保持良好心态即可。")

        return "\n".join(lines)

    def analyze_issues_and_solutions(self, chart_data: Any = None) -> ResolutionAnalysis:
        """
        分析命盘问题并提供化解建议

        Args:
            chart_data: 命盘数据，包含宫位星曜信息

        Returns:
            ResolutionAnalysis: 化解分析结果
        """
        # 更新命盘数据
        if chart_data is not None:
            self.chart = chart_data

        # 获取宫位星曜
        palace_stars = self._get_palace_stars_dict()

        # 识别问题
        issues: List[IdentifiedIssue] = []

        # 1. 煞星问题
        issues.extend(self._identify_sha_star_issues(palace_stars))

        # 2. 格局问题
        issues.extend(self._identify_pattern_issues(palace_stars))

        # 3. 四化问题
        issues.extend(self._identify_transform_issues(palace_stars))

        # 去除重复问题
        seen = set()
        unique_issues = []
        for issue in issues:
            key = (issue.star_or_pattern, issue.palace, issue.issue_type)
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        # 按严重程度排序
        severity_order = {Severity.SEVERE.value: 0, Severity.MODERATE.value: 1, Severity.MILD.value: 2}
        unique_issues.sort(key=lambda x: severity_order.get(x.severity, 3))

        # 查找化解方法
        resolutions = [self._find_resolution_for_issue(issue) for issue in unique_issues]

        # 生成解释
        interpretation = self._generate_interpretation(unique_issues, resolutions)

        return ResolutionAnalysis(
            identified_issues=unique_issues,
            resolutions=resolutions,
            interpretation=interpretation
        )


# ============ 便捷函数 ============

def analyze_chart_resolutions(chart_data: Any = None) -> ResolutionAnalysis:
    """
    快捷函数：分析命盘化解

    Args:
        chart_data: 命盘数据

    Returns:
        化解分析结果
    """
    agent = ResolutionAgent(chart_data)
    return agent.analyze_issues_and_solutions(chart_data)
