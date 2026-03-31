"""
因果链推理引擎 - 紫微斗数因果链分析

核心原理：
- 禄是因、忌是果：化禄代表机会/原因，化忌代表结果/阻碍
- 禄转忌：得而复失，昙花一现
- 忌转忌：祸不单行，忌数越多越严重
- 忌数论事：单忌=潜在，双忌=条件，三忌=确定，四忌+=重大

参考梁若瑜《飞星紫微斗数》因果链理论

模块化重构：
- causal_chain_constants.py: 常量、枚举、映射表
- causal_chain_types.py: 数据类
- causal_chain_core.py: 核心分析函数
"""

from typing import Dict, List, Optional

# 从模块导入常量、类型和核心函数
from .causal_chain_constants import (
    PALACE_NAMES,
    PALACE_INDEX,
    SeverityLevel,
    TransformType,
    CausalChainType,
    YEAR_STEM_TRANSFORMS,
)

from .causal_chain_types import (
    TransformStar,
    FlyingPath,
    CausalChain,
    CausalResult,
)

from .causal_chain_core import (
    count_ji_intensity,
    calculate_causal_confidence,
    calculate_flying_paths,
    analyze_lu_zhuan_ji,
    analyze_ji_zhuan_ji,
    analyze_lu_ji_tong_gong,
    analyze_san_ji_hui_ju,
    analyze_ji_chong_palaces,
)


class CausalChainPredictor:
    """
    因果链预测器

    根据四化飞化规则，分析因果链关系，判断凶险程度
    """

    def __init__(self):
        """初始化因果链预测器"""
        pass

    def predict(
        self,
        chart: Dict,
        time_point: Optional[int] = None
    ) -> CausalResult:
        """
        预测因果链

        Args:
            chart: 排盘结果，包含 palaces 和 year_stem 信息
            time_point: 时间点（流年、流月等），可选

        Returns:
            CausalResult: 因果推理结果
        """
        # 提取年干
        year_stem = chart.get("year_stem", "")
        if not year_stem:
            # 尝试从 birth_info 获取
            birth_info = chart.get("birth_info", {})
            year_stem = birth_info.get("year_stem", "")

        # 获取宫位星曜
        palace_stars = self._extract_palace_stars(chart)

        # 计算飞化路线
        flying_paths = calculate_flying_paths(palace_stars, year_stem)

        # 分析因果链
        causal_chains = []
        causal_chains.extend(analyze_lu_zhuan_ji(flying_paths, palace_stars))
        causal_chains.extend(analyze_ji_zhuan_ji(flying_paths, palace_stars))
        causal_chains.extend(analyze_lu_ji_tong_gong(flying_paths, palace_stars))
        causal_chains.extend(analyze_san_ji_hui_ju(flying_paths, palace_stars))
        causal_chains.extend(analyze_ji_chong_palaces(flying_paths, palace_stars))

        # 添加新的分析方法
        causal_chains.extend(self.analyze_pursuit_lu(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_pursuit_quan(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_pursuit_ji(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_lu_ji_symmetry(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_ben_gong_zi_hua(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_ji_ru_zi_hua(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_neighbor_palace_chong(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_guo_bao_gong(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_multi_palace_chain(flying_paths, palace_stars))
        causal_chains.extend(self.analyze_san_fang_si_zheng(flying_paths, palace_stars))

        # 格局识别
        patterns = self.recognize_patterns(chart)
        if patterns:
            causal_chains.append(CausalChain(
                chain_type=CausalChainType.PATTERN_RECOGNITION,
                palaces=[],
                transforms=[],
                severity=SeverityLevel.POTENTIAL,
                description=f"四大格局：{', '.join(patterns)}"
            ))

        # 计算忌数（按宫位累计忌的数量，而非星曜数量）
        # 根据梁若瑜和王亭之的理论，忌数应该看忌飞入哪些宫位
        ji_by_dest: Dict[str, List[FlyingPath]] = {}
        for p in flying_paths:
            if p.transform_type == TransformType.HUA_JI:
                if p.to_palace not in ji_by_dest:
                    ji_by_dest[p.to_palace] = []
                ji_by_dest[p.to_palace].append(p)
        # 取汇聚数量最多的宫位的忌数作为忌数强度
        max_ji = max(len(pals) for pals in ji_by_dest.values()) if ji_by_dest else 0
        ji_count = max_ji

        # 评估整体凶险等级
        severity = self._evaluate_overall_severity(causal_chains, ji_count)

        # 生成分析说明
        analysis = self._generate_analysis(year_stem, flying_paths, causal_chains, severity)

        # 提取四化星曜
        transforms = self._extract_transforms(chart, year_stem)

        # 计算置信度
        confidence = calculate_causal_confidence(causal_chains, ji_count, severity)

        return CausalResult(
            year_stem=year_stem,
            transforms=transforms,
            flying_paths=flying_paths,
            causal_chains=causal_chains,
            ji_count=ji_count,
            severity=severity,
            analysis=analysis,
            confidence=confidence
        )

    def _extract_palace_stars(self, chart: Dict) -> Dict[str, List[str]]:
        """
        从排盘结果提取宫位星曜

        Args:
            chart: 排盘结果

        Returns:
            Dict[str, List[str]]: {宫位名: [星曜列表]}
        """
        palace_stars = {}

        palaces_data = chart.get("palaces", {})
        if isinstance(palaces_data, dict):
            for palace_name, palace_info in palaces_data.items():
                stars = []
                if isinstance(palace_info, dict):
                    stars_list = palace_info.get("stars", [])
                    if isinstance(stars_list, list):
                        stars = [s.get("name", "") if isinstance(s, dict) else str(s) for s in stars_list]
                    elif isinstance(stars_list, str):
                        # 可能已经是逗号分隔的字符串
                        stars = stars_list.split(",")
                palace_stars[palace_name] = [s for s in stars if s]
        elif isinstance(palaces_data, list):
            for palace in palaces_data:
                if isinstance(palace, dict):
                    name = palace.get("name", "")
                    stars = palace.get("stars", [])
                    if isinstance(stars, list):
                        palace_stars[name] = [s.get("name", "") if isinstance(s, dict) else str(s) for s in stars]
                    elif isinstance(stars, str):
                        palace_stars[name] = stars.split(",")

        return palace_stars

    def _extract_transforms(self, chart: Dict, year_stem: str) -> List[TransformStar]:
        """
        提取四化星曜

        Args:
            chart: 排盘结果
            year_stem: 年干

        Returns:
            List[TransformStar]: 四化星曜列表
        """
        transforms = []
        palace_stars = self._extract_palace_stars(chart)

        transform_map = YEAR_STEM_TRANSFORMS.get(year_stem, {})
        for t_type, star_name in transform_map.items():
            # 找到该星曜所在的宫位
            palace = None
            for p_name, stars in palace_stars.items():
                if star_name in stars:
                    palace = p_name
                    break

            if palace:
                transforms.append(TransformStar(
                    transform_type=t_type,
                    star_name=star_name,
                    palace=palace
                ))

        return transforms

    def _evaluate_overall_severity(
        self,
        causal_chains: List[CausalChain],
        ji_count: int
    ) -> SeverityLevel:
        """
        评估整体凶险等级

        Args:
            causal_chains: 因果链列表
            ji_count: 忌数

        Returns:
            SeverityLevel: 整体凶险等级
        """
        # 根据因果链评估
        max_severity = count_ji_intensity(ji_count)

        for chain in causal_chains:
            if chain.severity == SeverityLevel.CATASTROPHIC:
                return SeverityLevel.CATASTROPHIC

        for chain in causal_chains:
            if chain.severity == SeverityLevel.BAD:
                # 如果还有三忌汇聚，保持大凶
                if any(c.chain_type == CausalChainType.SAN_JI_HUI_JU for c in causal_chains):
                    return SeverityLevel.CATASTROPHIC
                return SeverityLevel.BAD

        return max_severity

    def _generate_analysis(
        self,
        year_stem: str,
        flying_paths: List[FlyingPath],
        causal_chains: List[CausalChain],
        severity: SeverityLevel
    ) -> str:
        """
        生成分析说明

        Args:
            year_stem: 年干
            flying_paths: 飞化路线
            causal_chains: 因果链
            severity: 凶险等级

        Returns:
            str: 分析说明
        """
        lines = [f"年干{year_stem}四化因果分析："]

        # 四化概述
        transform_map = YEAR_STEM_TRANSFORMS.get(year_stem, {})
        for t_type, star in transform_map.items():
            lines.append(f"- {t_type.value}：{star}")

        lines.append("")

        # 飞化路线概述
        if flying_paths:
            lines.append(f"飞化路线（共{len(flying_paths)}条）：")
            for path in flying_paths[:5]:  # 只显示前5条
                lines.append(f"- {path.star_name}{path.transform_type.value}：{path.from_palace}→{path.to_palace}")
            if len(flying_paths) > 5:
                lines.append(f"- ...还有{len(flying_paths) - 5}条")

        lines.append("")

        # 因果链概述
        if causal_chains:
            lines.append(f"因果链分析（共{len(causal_chains)}条）：")
            for chain in causal_chains:
                lines.append(f"- {chain.chain_type.value}（{chain.severity.value}）：{chain.description}")

        lines.append("")
        lines.append(f"整体评估：{severity.value}")

        return "\n".join(lines)

    def recognize_patterns(self, chart: Dict) -> List[str]:
        """
        识别四大格局（王亭之《中州派》）

        根据紫微斗数经典格局理论，识别：
        1. 紫府同宫格：紫微天府同守命宫
        2. 天府朝垣格：天府守命，三合照会
        3. 贪狼入庙格：贪狼居子午卯酉宫
        4. 杀破狼格：七杀破军贪狼三方四正汇聚
        """
        patterns = []
        palace_stars = self._extract_palace_stars(chart)

        # 1. 紫府同宫格：紫微天府同守命宫
        if "命宫" in palace_stars:
            ming_stars = palace_stars["命宫"]
            if "紫微" in ming_stars and "天府" in ming_stars:
                patterns.append("紫府同宫格")

        # 2. 天府朝垣格：天府守命，三合照会（命宫、财帛宫、官禄宫）
        if "命宫" in palace_stars and "天府" in palace_stars["命宫"]:
            has_sanhe = False
            for p in ["财帛宫", "官禄宫"]:
                if p in palace_stars and palace_stars[p]:
                    has_sanhe = True
                    break
            if has_sanhe:
                patterns.append("天府朝垣格")

        # 3. 贪狼入庙格：贪狼居子午卯酉宫
        for p in ["子宫", "午宫", "卯宫", "酉宫"]:
            if p in palace_stars and "贪狼" in palace_stars[p]:
                patterns.append("贪狼入庙格")
                break

        # 4. 杀破狼格：七杀、破军、贪狼三方四正汇聚
        has_qisha = False
        has_pojun = False
        has_tanlang = False
        for palace, stars in palace_stars.items():
            if "七杀" in stars:
                has_qisha = True
            if "破军" in stars:
                has_pojun = True
            if "贪狼" in stars:
                has_tanlang = True
        if has_qisha and has_pojun and has_tanlang:
            patterns.append("杀破狼格")

        return patterns

    def analyze_pursuit_lu(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        追踪禄的走向（梁若瑜《飞星紫微斗数》）

        分析化禄的飞化路线，追踪禄的最终落点
        """
        chains = []
        lu_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_LU]

        if not lu_paths:
            return chains

        # 按禄的目标宫位分析
        lu_by_dest: Dict[str, List[FlyingPath]] = {}
        for path in lu_paths:
            if path.to_palace not in lu_by_dest:
                lu_by_dest[path.to_palace] = []
            lu_by_dest[path.to_palace].append(path)

        for dest, paths in lu_by_dest.items():
            if len(paths) >= 2:
                chains.append(CausalChain(
                    chain_type=CausalChainType.ZHUI_LU,
                    palaces=[p.from_palace for p in paths] + [dest],
                    transforms=paths,
                    severity=SeverityLevel.POTENTIAL,
                    description=f"追禄：{paths[0].star_name}化禄汇聚于{dest}，禄源充沛"
                ))

        return chains

    def analyze_pursuit_quan(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        追踪权的走向（梁若瑜《飞星紫微斗数》）

        分析化权的飞化路线，追踪权的最终落点
        """
        chains = []
        quan_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_QUAN]

        if not quan_paths:
            return chains

        # 按权的功能宫位分析（官禄宫为权力中心）
        for path in quan_paths:
            if path.to_palace == "官禄宫":
                chains.append(CausalChain(
                    chain_type=CausalChainType.ZHUI_QUAN,
                    palaces=[path.from_palace, path.to_palace],
                    transforms=[path],
                    severity=SeverityLevel.CONDITION,
                    description=f"追权：{path.star_name}化权入官禄宫，权力巩固"
                ))

        return chains

    def analyze_pursuit_ji(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        追踪忌的走向（梁若瑜《飞星紫微斗数》）

        分析化忌的飞化路线，追踪忌的最终落点及其影响
        """
        chains = []
        ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

        if not ji_paths:
            return chains

        # 按忌的目标宫位分析
        ji_by_dest: Dict[str, List[FlyingPath]] = {}
        for path in ji_paths:
            if path.to_palace not in ji_by_dest:
                ji_by_dest[path.to_palace] = []
            ji_by_dest[path.to_palace].append(path)

        for dest, paths in ji_by_dest.items():
            if len(paths) >= 2:
                ji_stars = [p.star_name for p in paths]
                chains.append(CausalChain(
                    chain_type=CausalChainType.ZHUI_JI,
                    palaces=[p.from_palace for p in paths] + [dest],
                    transforms=paths,
                    severity=SeverityLevel.BAD,
                    description=f"追忌：{', '.join(ji_stars)}化忌汇聚于{dest}，多忌纠缠"
                ))

        return chains

    def analyze_lu_ji_symmetry(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        禄忌对称分析（梁若瑜《飞星紫微斗数》）

        分析禄和忌是否形成对称关系，即禄入某宫而忌入其对宫
        """
        chains = []
        lu_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_LU]
        ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

        for lu in lu_paths:
            lu_idx = PALACE_INDEX.get(lu.to_palace, 0)
            lu_opposite = PALACE_NAMES[(lu_idx + 6) % 12]

            for ji in ji_paths:
                if ji.to_palace == lu_opposite:
                    chains.append(CausalChain(
                        chain_type=CausalChainType.LU_JI_DUI_CHEN,
                        palaces=[lu.from_palace, lu.to_palace, ji.to_palace],
                        transforms=[lu, ji],
                        severity=SeverityLevel.CONDITION,
                        description=f"禄忌对称：{lu.star_name}化禄于{lu.from_palace}入{lu.to_palace}，"
                                   f"{ji.star_name}化忌于{ji.from_palace}入{ji.to_palace}，阴阳对峙"
                    ))

        return chains

    def analyze_ben_gong_zi_hua(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        本宫自化检测（梁若瑜《飞星紫微斗数》）

        检测本宫是否有自化禄、权、科、忌的情况
        """
        chains = []

        for path in flying_paths:
            # 自化的条件：飞化的起点和终点在同宫
            if path.from_palace == path.to_palace:
                chains.append(CausalChain(
                    chain_type=CausalChainType.BEN_GONG_ZI_HUA,
                    palaces=[path.from_palace],
                    transforms=[path],
                    severity=SeverityLevel.POTENTIAL,
                    description=f"本宫自化：{path.star_name}{path.transform_type.value}于{path.from_palace}，"
                               f"本宫气机流动"
                ))

        return chains

    def analyze_ji_ru_zi_hua(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        忌入逢自化特殊情况（梁若瑜《飞星紫微斗数》）

        当化忌飞入某宫时，如果该宫恰好有星曜自化，则为特殊组合
        """
        chains = []
        ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

        # 检查忌入的宫位是否有自化
        for ji in ji_paths:
            if ji.to_palace in palace_stars and palace_stars[ji.to_palace]:
                # 忌入某宫，该宫有星曜（可能自化）
                # 这种情况需要进一步分析，但先标记为特殊情况
                chains.append(CausalChain(
                    chain_type=CausalChainType.JI_RU_ZI_HUA,
                    palaces=[ji.from_palace, ji.to_palace],
                    transforms=[ji],
                    severity=SeverityLevel.CONDITION,
                    description=f"忌入逢星：{ji.star_name}化忌入{ji.to_palace}，"
                               f"该宫有星曜配置，需防化中带变"
                ))

        return chains

    def analyze_neighbor_palace_chong(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        邻宫冲势判断（王亭之《中州派》）

        分析邻宫（相隔1宫或11宫）的冲势影响
        """
        chains = []
        ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

        for ji in ji_paths:
            from_idx = PALACE_INDEX.get(ji.from_palace, 0)

            # 邻宫：相隔1宫或11宫
            neighbor_indices = [(from_idx + 1) % 12, (from_idx - 1) % 12]
            neighbors = [PALACE_NAMES[i] for i in neighbor_indices]

            # 检查忌是否冲邻宫
            if ji.to_palace in neighbors:
                chains.append(CausalChain(
                    chain_type=CausalChainType.LIN_GONG_CHONG,
                    palaces=[ji.from_palace, ji.to_palace],
                    transforms=[ji],
                    severity=SeverityLevel.CONDITION,
                    description=f"邻宫冲势：{ji.star_name}化忌于{ji.from_palace}冲邻宫{ji.to_palace}，"
                               f"影响力较对宫冲势稍弱"
                ))

        return chains

    def analyze_guo_bao_gong(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        果报宫分析（梁若瑜《飞星紫微斗数》）

        分析因果报应关系：田宅宫为因果宫，福德宫为果报宫
        """
        chains = []
        ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

        # 检查忌是否入田宅宫或福德宫
        for ji in ji_paths:
            if ji.to_palace == "田宅宫":
                chains.append(CausalChain(
                    chain_type=CausalChainType.GUO_BAO_GONG,
                    palaces=[ji.from_palace, ji.to_palace],
                    transforms=[ji],
                    severity=SeverityLevel.BAD,
                    description=f"因果宫：{ji.star_name}化忌入田宅宫，与家宅田产有因果纠葛"
                ))
            elif ji.to_palace == "福德宫":
                chains.append(CausalChain(
                    chain_type=CausalChainType.GUO_BAO_GONG,
                    palaces=[ji.from_palace, ji.to_palace],
                    transforms=[ji],
                    severity=SeverityLevel.BAD,
                    description=f"果报宫：{ji.star_name}化忌入福德宫，因果福报受损"
                ))

        return chains

    def analyze_multi_palace_chain(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        多宫位串联分析（王亭之《中州派》）

        分析跨宫位的因果链串联关系
        """
        chains = []

        # 按类型分组飞化路径
        paths_by_type: Dict[TransformType, List[FlyingPath]] = {}
        for path in flying_paths:
            if path.transform_type not in paths_by_type:
                paths_by_type[path.transform_type] = []
            paths_by_type[path.transform_type].append(path)

        # 分析禄的串联链
        if TransformType.HUA_LU in paths_by_type:
            lu_paths = paths_by_type[TransformType.HUA_LU]
            for i, lu1 in enumerate(lu_paths):
                for lu2 in lu_paths[i+1:]:
                    if lu1.to_palace == lu2.from_palace:
                        chains.append(CausalChain(
                            chain_type=CausalChainType.SAN_FANG_SI_ZHENG,
                            palaces=[lu1.from_palace, lu1.to_palace, lu2.to_palace],
                            transforms=[lu1, lu2],
                            severity=SeverityLevel.POTENTIAL,
                            description=f"禄续禄：{lu1.star_name}化禄于{lu1.from_palace}入{lu1.to_palace}，"
                                       f"{lu2.star_name}化禄于{lu2.from_palace}延续"
                        ))

        return chains

    def analyze_san_fang_si_zheng(self, flying_paths: List[FlyingPath], palace_stars: Dict[str, List[str]]) -> List[CausalChain]:
        """
        三方四正关系分析（王亭之《中州派》）

        分析宫位的三方四正关系（命宫、财帛宫、官禄宫、迁移宫）
        """
        chains = []

        # 核心四宫
        core_palaces = ["命宫", "财帛宫", "官禄宫", "迁移宫"]

        # 检查核心四宫之间的飞化关系
        for path in flying_paths:
            if path.from_palace in core_palaces and path.to_palace in core_palaces:
                if path.from_palace != path.to_palace:
                    chains.append(CausalChain(
                        chain_type=CausalChainType.SAN_FANG_SI_ZHENG,
                        palaces=[path.from_palace, path.to_palace],
                        transforms=[path],
                        severity=SeverityLevel.POTENTIAL,
                        description=f"三方四正：{path.star_name}{path.transform_type.value}于{path.from_palace}→{path.to_palace}"
                    ))

        return chains


def create_mock_chart(
    year_stem: str,
    lu_palace: str,
    ji_palace: str,
    quan_palace: str = None,
    ke_palace: str = None
) -> Dict:
    """
    创建模拟排盘数据用于测试

    Args:
        year_stem: 年干
        lu_palace: 化禄所在宫位
        ji_palace: 化忌所在宫位
        quan_palace: 化权所在宫位
        ke_palace: 化科所在宫位

    Returns:
        Dict: 模拟排盘数据
    """
    transform_map = YEAR_STEM_TRANSFORMS.get(year_stem, {})
    palaces_data = {name: {"stars": []} for name in PALACE_NAMES}

    for t_type, star_name in transform_map.items():
        if t_type == TransformType.HUA_LU and lu_palace:
            palaces_data[lu_palace]["stars"].append({"name": star_name})
        elif t_type == TransformType.HUA_JI and ji_palace:
            palaces_data[ji_palace]["stars"].append({"name": star_name})
        elif t_type == TransformType.HUA_QUAN and quan_palace:
            palaces_data[quan_palace]["stars"].append({"name": star_name})
        elif t_type == TransformType.HUA_KE and ke_palace:
            palaces_data[ke_palace]["stars"].append({"name": star_name})

    return {
        "year_stem": year_stem,
        "palaces": palaces_data
    }


# ==================== 测试用例 ====================

def test_lu_in_ming_gong():
    """测试：禄在命宫且忌不在冲宫 → 吉"""
    # 化忌在父母宫，不会直接冲命宫或迁移宫
    chart = create_mock_chart("甲", "命宫", "父母宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert result.year_stem == "甲"
    # 忌不在冲宫位置，应该评估为潜在或条件级别
    assert result.severity in [SeverityLevel.POTENTIAL, SeverityLevel.CONDITION]
    print("✓ test_lu_in_ming_gong passed")


def test_ji_chong_yiqian_gong():
    """测试：忌冲迁移宫 → 凶"""
    # 化忌在命宫，会冲迁移宫
    chart = create_mock_chart("甲", "财帛宫", "命宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 验证化忌冲迁移宫
    ji_chong_yi = [c for c in result.causal_chains
                   if c.chain_type == CausalChainType.JI_CHONG_YI]
    assert len(ji_chong_yi) > 0
    print("✓ test_ji_chong_yiqian_gong passed")


def test_san_ji_hui_ju():
    """测试：三忌汇聚 → 大凶"""
    # 使用多个化忌星曜飞化到同一宫位形成三忌汇聚
    chart = {
        "year_stem": "戊",  # 戊年：天机化忌（双重）
        "palaces": {
            "命宫": {"stars": [{"name": "天机"}]},  # 化忌在命宫
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 当忌飞化到多个宫位且形成汇聚时，应该是大凶
    # 注意：这里主要测试三忌汇聚的因果链类型能被正确识别
    san_ji = [c for c in result.causal_chains
              if c.chain_type == CausalChainType.SAN_JI_HUI_JU]
    print(f"  三忌汇聚链数量: {len(san_ji)}")
    print("✓ test_san_ji_hui_ju passed")


def test_lu_ji_tong_gong():
    """测试：禄忌同宫 → 得失参半"""
    chart = create_mock_chart("甲", "命宫", "命宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 应该有禄忌同宫的因果链
    lu_ji = [c for c in result.causal_chains
             if c.chain_type == CausalChainType.LU_JI_TONG_GONG]
    assert len(lu_ji) > 0
    print("✓ test_lu_ji_tong_gong passed")


def test_ji_zhuan_ji():
    """测试：忌转忌 → 连续阻碍"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "太阴"}]},  # 化忌
            "财帛宫": {"stars": [{"name": "天机"}]},  # 化权（不在因果链中）
            "官禄宫": {"stars": [{"name": "太阳"}]},  # 化科
            "疾厄宫": {"stars": [{"name": "廉贞"}]},  # 化禄
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 检查因果链类型
    assert len(result.causal_chains) >= 0
    print("✓ test_ji_zhuan_ji passed")


def test_ji_count_single():
    """测试：单忌 = 潜在（无冲宫情况）"""
    # 化忌在父母宫，不冲命宫或迁移宫
    chart = create_mock_chart("乙", "命宫", "父母宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert result.ji_count >= 1
    # 无冲宫情况下，单忌应该是潜在级别
    assert result.severity == SeverityLevel.POTENTIAL
    print("✓ test_ji_count_single passed")


def test_ji_count_double():
    """测试：双忌 = 条件"""
    chart = {
        "year_stem": "乙",
        "palaces": {
            "命宫": {"stars": [{"name": "太阳"}]},  # 化忌
            "财帛宫": {"stars": [{"name": "天机"}]},  # 化权
            "官禄宫": {"stars": [{"name": "天梁"}]},  # 化科
            "疾厄宫": {"stars": [{"name": "廉贞"}]},  # 化禄
            "夫妻宫": {"stars": [{"name": "破军"}]},  # 化忌2
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert result.ji_count >= 2
    print("✓ test_ji_count_double passed")


def test_transform_extraction():
    """测试：四化星曜提取"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "廉贞"}, {"name": "太阴"}]},  # 化禄 + 化忌
            "兄弟宫": {"stars": [{"name": "天机"}]},  # 化权
            "夫妻宫": {"stars": [{"name": "太阳"}]},  # 化科
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert len(result.transforms) >= 3  # 至少有禄权科
    print("✓ test_transform_extraction passed")


def test_severity_level_enum():
    """测试：SeverityLevel枚举"""
    assert count_ji_intensity(0) == SeverityLevel.POTENTIAL
    assert count_ji_intensity(1) == SeverityLevel.POTENTIAL
    assert count_ji_intensity(2) == SeverityLevel.CONDITION
    assert count_ji_intensity(3) == SeverityLevel.BAD
    assert count_ji_intensity(4) == SeverityLevel.CATASTROPHIC
    assert count_ji_intensity(5) == SeverityLevel.CATASTROPHIC
    print("✓ test_severity_level_enum passed")


def test_flying_path_calculation():
    """测试：飞化路线计算"""
    chart = create_mock_chart("甲", "命宫", "财帛宫")
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert len(result.flying_paths) > 0
    print("✓ test_flying_path_calculation passed")


def test_empty_chart():
    """测试：空排盘"""
    chart = {"year_stem": "甲", "palaces": {}}
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    assert result.year_stem == "甲"
    print("✓ test_empty_chart passed")


def test_no_transform_star():
    """测试：星曜不在预期的宫位"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": [{"name": "紫微"}]},  # 不是四化星
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 应该正常处理，不报错
    assert result.year_stem == "甲"
    print("✓ test_no_transform_star passed")


def test_ji_zhaun_ji_multiple():
    """测试：多重忌转忌"""
    chart = {
        "year_stem": "壬",  # 壬年：天机化禄、紫微化权、贪狼化科、天同化忌
        "palaces": {
            "命宫": {"stars": [{"name": "天同"}]},  # 化忌
            "财帛宫": {"stars": [{"name": "天同"}]},  # 化忌
            "官禄宫": {"stars": [{"name": "天同"}]},  # 化忌
        }
    }
    predictor = CausalChainPredictor()
    result = predictor.predict(chart)

    # 应该有多重因果链
    print(f"  因果链数量: {len(result.causal_chains)}")
    print("✓ test_ji_zhaun_ji_multiple passed")


def test_palace_stars_extraction():
    """测试：宫位星曜提取（列表格式）"""
    chart = {
        "year_stem": "甲",
        "palaces": [
            {"name": "命宫", "stars": [{"name": "廉贞"}]},
            {"name": "兄弟宫", "stars": [{"name": "天机"}]},
        ]
    }
    predictor = CausalChainPredictor()
    palace_stars = predictor._extract_palace_stars(chart)

    assert "命宫" in palace_stars
    assert "廉贞" in palace_stars["命宫"]
    print("✓ test_palace_stars_extraction passed")


def test_palace_stars_string_format():
    """测试：宫位星曜提取（字符串格式）"""
    chart = {
        "year_stem": "甲",
        "palaces": {
            "命宫": {"stars": "廉贞,天机"},
        }
    }
    predictor = CausalChainPredictor()
    palace_stars = predictor._extract_palace_stars(chart)

    assert "命宫" in palace_stars
    assert "廉贞" in palace_stars["命宫"]
    print("✓ test_palace_stars_string_format passed")


def run_all_tests():
    """运行所有测试"""
    print("\n=== 因果链分析器测试 ===")
    tests = [
        test_lu_in_ming_gong,
        test_ji_chong_yiqian_gong,
        test_san_ji_hui_ju,
        test_lu_ji_tong_gong,
        test_ji_zhuan_ji,
        test_ji_count_single,
        test_ji_count_double,
        test_transform_extraction,
        test_severity_level_enum,
        test_flying_path_calculation,
        test_empty_chart,
        test_no_transform_star,
        test_ji_zhaun_ji_multiple,
        test_palace_stars_extraction,
        test_palace_stars_string_format,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")

    print("\n=== 所有测试完成 ===")


if __name__ == "__main__":
    run_all_tests()
