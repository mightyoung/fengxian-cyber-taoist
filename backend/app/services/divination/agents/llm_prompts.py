"""
LLM提示词模块 - 为分析Agent提供LLM调用能力

包含：
1. StarAgentPrompt - 星曜分析提示词
2. PalaceAgentPrompt - 宫位分析提示词
3. SynthesisAgentPrompt - 综合报告提示词
"""

from typing import Dict, Any, List, Optional
import json

from .llm_prompts_constants import (
    load_transform_cases,
    load_pattern_cases,
    load_palace_cases,
    load_star_cases,
    load_daxian_cases,
    load_flying_star_rules,
)

# 导入增强版提示词（基于顶级Agent提示词研究）
try:
    from .enhanced_prompts import (
        ENHANCED_STAR_SYSTEM_PROMPT,
        ENHANCED_PALACE_SYSTEM_PROMPT,
        ENHANCED_TRANSFORM_SYSTEM_PROMPT,
        ENHANCED_PATTERN_SYSTEM_PROMPT,
        ENHANCED_TIMING_SYSTEM_PROMPT,
        ENHANCED_SYNTHESIS_SYSTEM_PROMPT,
    )
except ImportError:
    ENHANCED_STAR_SYSTEM_PROMPT = None
    ENHANCED_PALACE_SYSTEM_PROMPT = None
    ENHANCED_TRANSFORM_SYSTEM_PROMPT = None
    ENHANCED_PATTERN_SYSTEM_PROMPT = None
    ENHANCED_TIMING_SYSTEM_PROMPT = None
    ENHANCED_SYNTHESIS_SYSTEM_PROMPT = None

# 六十星系导入
try:
    from .siyin_loader import SiyinLoader
    _SIYIN_LOADER = SiyinLoader()
except ImportError:
    _SIYIN_LOADER = None


# ============ 飞星四化规则格式化 ============

def format_flying_star_rules() -> str:
    """格式化飞星四化规则为提示词文本"""
    rules_data = load_flying_star_rules()
    rules = rules_data.get("rules", {})

    if not rules:
        return ""

    parts = ["\n\n【飞星四化核心规则】\n"]

    # 禄转忌规则
    lu_to_ji = rules.get("lu_to_ji", {})
    if lu_to_ji:
        parts.append("## 禄转忌\n")
        parts.append(f"定义：{lu_to_ji.get('definition', '')}\n")
        if lu_to_ji.get("interpretation_rules"):
            parts.append("解读要点：\n")
            for rule in lu_to_ji["interpretation_rules"][:3]:
                parts.append(f"  - {rule}\n")

    # 忌转忌规则
    ji_to_ji = rules.get("ji_to_ji", {})
    if ji_to_ji:
        parts.append("\n## 忌转忌\n")
        parts.append(f"定义：{ji_to_ji.get('definition', '')}\n")
        if ji_to_ji.get("levels"):
            parts.append("忌数论事：\n")
            for level, meaning in ji_to_ji["levels"].items():
                parts.append(f"  - {level}: {meaning}\n")

    # 追禄/追权/追忌规则
    pursuit_rules = rules.get("pursuit_rules", {})
    if pursuit_rules:
        parts.append("\n## 追禄追权追忌\n")
        for pursuit_type in ["pursuit_lu", "pursuit_quan", "pursuit_ji"]:
            pursuit = pursuit_rules.get(pursuit_type, {})
            if pursuit:
                parts.append(f"\n{pursuit.get('name', '')}：\n")
                parts.append(f"  条件：{pursuit.get('condition', '')}\n")
                parts.append(f"  含义：{pursuit.get('meaning', '')}\n")

    # 飞化路线
    flying_routes = rules.get("flying_routes", {})
    if flying_routes:
        parts.append("\n## 化禄化忌飞向宫位\n")
        hua_lu = flying_routes.get("hua_lu_routes", {})
        if hua_lu.get("common_targets"):
            parts.append("化禄常飞向：\n")
            for target in hua_lu["common_targets"][:5]:
                parts.append(f"  - {target}\n")

    return "".join(parts)

def get_relevant_cases(cases: List[Dict[str, Any]], chart_data: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
    """
    根据命盘数据获取相关案例

    Args:
        cases: 案例列表
        chart_data: 命盘数据
        limit: 返回案例数量限制

    Returns:
        相关案例列表
    """
    if not cases:
        return []

    relevant = []
    stars = chart_data.get("stars", {})
    main_stars = [s.get("name", "") for s in stars.get("main_stars", [])]
    transforms = chart_data.get("transforms", [])
    palaces = chart_data.get("palaces", {})
    birth_info = chart_data.get("birth_info", {})

    for case in cases:
        case_input = case.get("input", {})
        case_type = case.get("type", "")

        # 简单匹配：检查案例类型是否与命盘中的四化/格局匹配
        for transform in transforms:
            transform_type = transform.get("type", "")
            if case_type == "四化" and transform_type in case_input.get("transform", ""):
                relevant.append(case)
                break

        # 检查主星匹配
        for star in main_stars:
            if star in str(case_input.get("main_star", "")):
                relevant.append(case)
                break

        # 大限案例匹配：检查五行局和顺逆行
        if case_type in ["大限阶段", "大限"]:
            zodiac_type = birth_info.get("zodiac_type", "")
            wuxing_ju = birth_info.get("wuxing_ju", "")
            case_zodiac = case_input.get("zodiac_type", "")
            case_ju = case_input.get("wuxing_ju", "")
            # 匹配五行局
            if wuxing_ju and case_ju and wuxing_ju == case_ju:
                relevant.append(case)
                break
            # 匹配阴阳顺逆
            if zodiac_type and case_zodiac and (zodiac_type in case_zodiac or case_zodiac in zodiac_type):
                relevant.append(case)
                break

        # 宫位案例匹配
        if case_type in ["宫位", "宫位分析"]:
            case_palace = case_input.get("palace", "")
            for palace_name in palaces:
                if palace_name in case_palace or case_palace in palace_name:
                    relevant.append(case)
                    break

    # 如果没有找到任何相关案例，返回前 N 个作为通用参考
    if not relevant:
        relevant = cases[:limit]

    # 去重
    seen = set()
    unique_relevant = []
    for case in relevant:
        case_id = case.get("case_id", "")
        if case_id not in seen:
            seen.add(case_id)
            unique_relevant.append(case)

    return unique_relevant[:limit]

def format_cases_as_context(cases: List[Dict[str, Any]], agent_type: str) -> str:
    """
    将案例格式化为上下文

    Args:
        cases: 案例列表
        agent_type: Agent类型 (transform/pattern/palace/timing)

    Returns:
        格式化的案例上下文
    """
    if not cases:
        return ""

    context_parts = ["\n\n【案例库参考】\n"]
    context_parts.append(f"以下是{agent_type}分析的参考案例：\n")

    for i, case in enumerate(cases, 1):
        name = case.get("name", "")
        case_type = case.get("type", "")
        case_input = case.get("input", {})
        case_output = case.get("output", {})

        context_parts.append(f"\n案例{i}：{name}（{case_type}）")
        context_parts.append(f"输入条件：{json.dumps(case_input, ensure_ascii=False)}")
        if isinstance(case_output, dict):
            interpretation = case_output.get("interpretation", "")
            if interpretation:
                context_parts.append(f"解读要点：{interpretation}")
        context_parts.append("---")

    return "\n".join(context_parts)


# ============ 星曜分析提示词（使用增强版） ============

# 使用基于顶级Agent提示词研究的增强版提示词
STAR_SYSTEM_PROMPT = ENHANCED_STAR_SYSTEM_PROMPT




def build_star_user_prompt(chart_data: Dict[str, Any], question: Optional[str] = None) -> str:
    """
    构建星曜分析的用户提示词

    Args:
        chart_data: 命盘数据
        question: 用户可选的特定问题

    Returns:
        格式化的用户提示词
    """
    # 提取基本信息
    birth_info = chart_data.get("birth_info", {})
    stars = chart_data.get("stars", {})
    palaces = chart_data.get("palaces", {})

    # 格式化出生信息
    birth_text = f"""
出生信息：
- 年份：{birth_info.get('year', '未知')}年
- 月份：{birth_info.get('month', '未知')}月
- 日期：{birth_info.get('day', '未知')}日
- 时辰：{birth_info.get('birth_hour', birth_info.get('hour', '未知'))}时
- 性别：{birth_info.get('gender', '未知')}
- 五行局：{birth_info.get('wuxing_ju', '未知')}
"""

    # 格式化主星信息
    main_stars = stars.get("main_stars", [])
    main_stars_text = "十四正曜：\n"
    for star in main_stars:
        palace = star.get("palace", "")
        level = star.get("level", "平")
        main_stars_text += f"  - {star.get('name', '')} 落在 {palace} ({level})\n"

    # 格式化辅星信息
    auxiliary_stars = stars.get("auxiliary_stars", [])
    aux_text = "\n辅曜：\n"
    for star in auxiliary_stars:
        palace = star.get("palace", "")
        level = star.get("level", "平")
        aux_text += f"  - {star.get('name', '')} 落在 {palace} ({level})\n"

    # 格式化煞星信息
    sha_stars = stars.get("sha_stars", [])
    sha_text = "\n煞星：\n"
    for star in sha_stars:
        palace = star.get("palace", "")
        level = star.get("level", "平")
        sha_text += f"  - {star.get('name', '')} 落在 {palace} ({level})\n"

    # 格式化四化信息
    transforms = stars.get("transform_stars", [])
    transform_text = "\n化曜：\n"
    for star in transforms:
        palace = star.get("palace", "")
        level = star.get("level", "平")
        transform_text += f"  - {star.get('name', '')} 落在 {palace} ({level})\n"

    # 格式化各宫位星曜
    palace_stars_text = "\n各宫位星曜分布：\n"
    palace_order = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                    "迁移宫", "仆役宫", "官禄宫", "田宅宫", "父母宫", "福德宫"]
    for palace_name in palace_order:
        palace_data = palaces.get(palace_name, {})
        palace_stars = palace_data.get("stars", [])
        if palace_stars:
            star_names = [s.get("name", "") for s in palace_stars if s.get("name")]
            if star_names:
                palace_stars_text += f"  - {palace_name}: {', '.join(star_names)}\n"

    # 格式化六十星系分析
    siyin_text = ""
    if _SIYIN_LOADER:
        siyin_results = []
        palace_branch_map = {
            "命宫": "子", "兄弟宫": "丑", "夫妻宫": "寅", "子女宫": "卯",
            "财帛宫": "辰", "疾厄宫": "巳", "迁移宫": "午", "仆役宫": "未",
            "官禄宫": "申", "田宅宫": "酉", "父母宫": "戌", "福德宫": "亥"
        }
        for palace_name in palace_order:
            palace_data = palaces.get(palace_name, {})
            palace_stars = palace_data.get("stars", [])
            if palace_stars:
                main_star = None
                secondary_stars = []
                for star in palace_stars:
                    star_name = star.get("name", "")
                    star_type = star.get("type", "")
                    if star_type == "正曜":
                        main_star = star_name
                    elif star_name:
                        secondary_stars.append(star_name)

                if main_star:
                    branch = palace_branch_map.get(palace_name, "")
                    siyin_result = _SIYIN_LOADER.get_siyin_interpretation(
                        main_star, secondary_stars, branch
                    )
                    if siyin_result.get("matched"):
                        siyin_results.append({
                            "palace": palace_name,
                            "system_name": siyin_result.get("system_name", ""),
                            "characteristics": siyin_result.get("characteristics", "")[:100],
                            "positive": siyin_result.get("positive_aspects", []),
                            "negative": siyin_result.get("negative_aspects", [])
                        })

        if siyin_results:
            siyin_text = "\n\n【六十星系匹配结果】\n"
            siyin_text += "根据命盘星曜组合，匹配到以下六十星系配置：\n"
            for result in siyin_results:
                siyin_text += f"\n■ {result['palace']}: {result['system_name']}\n"
                siyin_text += f"  特点: {result['characteristics']}...\n"
                if result['positive']:
                    siyin_text += f"  优点: {', '.join(result['positive'][:3])}\n"
                if result['negative']:
                    siyin_text += f"  缺点: {', '.join(result['negative'][:3])}\n"

    # 组装完整提示词
    user_prompt = f"""请分析以下命盘的星曜组合：

{birth_text}

{main_stars_text}
{aux_text}
{sha_text}
{transform_text}
{palace_stars_text}
{siyin_text}"""

    # 加载并注入相关星曜案例
    star_cases = load_star_cases()
    relevant_cases = get_relevant_cases(star_cases, chart_data, limit=20)
    if relevant_cases:
        user_prompt += format_cases_as_context(relevant_cases, "星曜")

    # 如果有特定问题，添加到末尾
    if question:
        user_prompt += f"\n\n【特定问题】\n{question}"

    user_prompt += "\n\n请给出深入的星曜分析，包括星曜组合效应、性格特征、事业财运等方面的解读。注意结合六十星系理论进行深入分析。"

    return user_prompt


# ============ 宫位分析提示词 ============

# ============ PALACE分析提示词（使用增强版） ============

# 使用基于顶级Agent提示词研究的增强版提示词
PALACE_SYSTEM_PROMPT = ENHANCED_PALACE_SYSTEM_PROMPT



def build_palace_user_prompt(chart_data: Dict[str, Any], question: Optional[str] = None) -> str:
    """
    构建宫位分析的用户提示词

    Args:
        chart_data: 命盘数据
        question: 用户可选的特定问题

    Returns:
        格式化的用户提示词
    """
    # 提取基本信息
    birth_info = chart_data.get("birth_info", {})
    palaces = chart_data.get("palaces", {})

    # 格式化出生信息
    birth_text = f"""
命主信息：
- 性别：{birth_info.get('gender', '未知')}
- 五行局：{birth_info.get('wuxing_ju', '未知')}
"""

    # 格式化各宫位详情
    palace_order = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                    "迁移宫", "仆役宫", "官禄宫", "田宅宫", "父母宫", "福德宫"]

    palace_details = "\n各宫位星曜分布：\n"
    for palace_name in palace_order:
        palace_data = palaces.get(palace_name, {})
        branch = palace_data.get("branch", "")
        tiangan = palace_data.get("tiangan", "")
        palace_stars = palace_data.get("stars", [])

        # 按类型分类星曜
        main_stars = [s.get("name") for s in palace_stars if s.get("type") == "正曜"]
        aux_stars = [s.get("name") for s in palace_stars if s.get("type") == "辅星"]
        sha_stars = [s.get("name") for s in palace_stars if s.get("type") == "煞星"]
        transform_stars = [s.get("name") for s in palace_stars if s.get("type") == "化曜"]

        stars_text = []
        if main_stars:
            stars_text.append(f"主星:{', '.join(main_stars)}")
        if aux_stars:
            stars_text.append(f"辅星:{', '.join(aux_stars)}")
        if sha_stars:
            stars_text.append(f"煞星:{', '.join(sha_stars)}")
        if transform_stars:
            stars_text.append(f"化曜:{', '.join(transform_stars)}")

        stars_summary = ", ".join(stars_text) if stars_text else "空宫"
        palace_details += f"  - {palace_name}({branch}{tiangan}): {stars_summary}\n"

    user_prompt = f"""请分析以下命盘的宫位强弱：

{birth_text}
{palace_details}"""

    # 加载并注入相关案例
    palace_cases = load_palace_cases()
    relevant_cases = get_relevant_cases(palace_cases, chart_data, limit=20)
    if relevant_cases:
        user_prompt += format_cases_as_context(relevant_cases, "宫位")

    if question:
        user_prompt += f"\n\n【特定问题】\n{question}"

    user_prompt += "\n\n请给出深入的宫位分析，包括各宫位的强弱评估、人生重点领域、宫位之间的互动关系等。"

    return user_prompt


# ============ 四化分析提示词 ============

# ============ TRANSFORM分析提示词（使用增强版） ============

# 使用基于顶级Agent提示词研究的增强版提示词
TRANSFORM_SYSTEM_PROMPT = ENHANCED_TRANSFORM_SYSTEM_PROMPT



def build_transform_user_prompt(chart_data: Dict[str, Any], question: Optional[str] = None) -> str:
    """
    构建四化分析的用户提示词

    Args:
        chart_data: 命盘数据
        question: 用户可选的特定问题

    Returns:
        格式化的用户提示词
    """
    from .transform_agent import HEAVENLY_STEM_TRANSFORMS

    # 提取基本信息
    birth_info = chart_data.get("birth_info", {})
    stars = chart_data.get("stars", {})
    palaces = chart_data.get("palaces", {})
    transforms = chart_data.get("transforms", [])

    # 获取年干
    year_stem = birth_info.get("tiangan", "甲")

    # 格式化出生信息
    birth_text = f"""
命主信息：
- 年干：{year_stem}（决定四化飞化）
- 五行局：{birth_info.get('wuxing_ju', '未知')}
"""

    # 格式化四化信息
    transforms_text = "\n四化信息：\n"
    if transforms:
        for t in transforms:
            star = t.get("star", "")
            transform_type = t.get("type", "")
            palace = t.get("palace", "")
            transforms_text += f"  - {star}化{transform_type} 在 {palace}\n"
    else:
        # 如果没有transforms，显示四化表
        transform_map = HEAVENLY_STEM_TRANSFORMS.get(year_stem, {})
        transforms_text += f"  {year_stem}年四化：\n"
        for t_type, star in transform_map.items():
            transforms_text += f"    {t_type}：{star}\n"

    # 格式化各宫位星曜
    palace_stars_text = "\n各宫位星曜分布：\n"
    palace_order = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                    "迁移宫", "仆役宫", "官禄宫", "田宅宫", "父母宫", "福德宫"]
    for palace_name in palace_order:
        palace_data = palaces.get(palace_name, {})
        branch = palace_data.get("branch", "")
        tiangan = palace_data.get("tiangan", "")
        palace_stars = palace_data.get("stars", [])

        # 按类型分类星曜
        main_stars = [s.get("name") for s in palace_stars if s.get("type") == "正曜"]
        transform_stars = [s.get("name") for s in palace_stars if s.get("type") == "化曜"]
        sha_stars = [s.get("name") for s in palace_stars if s.get("type") == "煞星"]

        stars_text = []
        if main_stars:
            stars_text.append(f"主星:{', '.join(main_stars)}")
        if transform_stars:
            stars_text.append(f"化曜:{', '.join(transform_stars)}")
        if sha_stars:
            stars_text.append(f"煞星:{', '.join(sha_stars)}")

        stars_summary = ", ".join(stars_text) if stars_text else "空宫"
        palace_stars_text += f"  - {palace_name}({branch}{tiangan}): {stars_summary}\n"

    user_prompt = f"""请分析以下命盘的四化飞化：

{birth_text}
{transforms_text}
{palace_stars_text}"""

    # 加载并注入相关案例
    transform_cases = load_transform_cases()
    relevant_cases = get_relevant_cases(transform_cases, chart_data, limit=20)
    if relevant_cases:
        user_prompt += format_cases_as_context(relevant_cases, "四化")

    # 注入飞星四化核心规则
    flying_star_rules = format_flying_star_rules()
    if flying_star_rules:
        user_prompt += flying_star_rules

    if question:
        user_prompt += f"\n\n【特定问题】\n{question}"

    user_prompt += "\n\n请给出深入的四化分析，包括四化分布、四化交互关系、各宫位影响、以及对事业财运感情的指导意义。"

    return user_prompt


# ============ 格局分析提示词 ============

# ============ PATTERN分析提示词（使用增强版） ============

# 使用基于顶级Agent提示词研究的增强版提示词
PATTERN_SYSTEM_PROMPT = ENHANCED_PATTERN_SYSTEM_PROMPT



def build_pattern_user_prompt(chart_data: Dict[str, Any], question: Optional[str] = None) -> str:
    """
    构建格局分析的用户提示词

    Args:
        chart_data: 命盘数据
        question: 用户可选的特定问题

    Returns:
        格式化的用户提示词
    """
    # 提取基本信息
    birth_info = chart_data.get("birth_info", {})
    stars = chart_data.get("stars", {})
    palaces = chart_data.get("palaces", {})
    transforms = chart_data.get("transforms", [])

    # 格式化出生信息
    birth_text = f"""
命主信息：
- 年干：{birth_info.get('tiangan', '未知')}
- 五行局：{birth_info.get('wuxing_ju', '未知')}
"""

    # 格式化四化信息
    transforms_text = "\n四化信息：\n"
    for t in transforms:
        star = t.get("star", "")
        transform_type = t.get("type", "")
        palace = t.get("palace", "")
        transforms_text += f"  - {star}化{transform_type} 在 {palace}\n"

    # 格式化重要宫位
    palace_stars_text = "\n各宫位重要星曜：\n"
    palace_order = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                    "迁移宫", "仆役宫", "官禄宫", "田宅宫", "父母宫", "福德宫"]
    for palace_name in palace_order:
        palace_data = palaces.get(palace_name, {})
        branch = palace_data.get("branch", "")
        palace_stars = palace_data.get("stars", [])

        # 获取主星和化曜
        main_stars = [s.get("name") for s in palace_stars if s.get("type") == "正曜"]
        transform_stars = [s.get("name") for s in palace_stars if s.get("type") == "化曜"]
        sha_stars = [s.get("name") for s in palace_stars if s.get("type") == "煞星"]

        stars_text = []
        if main_stars:
            stars_text.append(','.join(main_stars[:3]))  # 最多显示3颗主星
        if transform_stars:
            stars_text.append('+'.join(transform_stars))
        if sha_stars:
            stars_text.append(f"[{'/'.join(sha_stars)}]")

        if stars_text:
            palace_stars_text += f"  - {palace_name}({branch}): {' '.join(stars_text)}\n"

    user_prompt = f"""请分析以下命盘的格局：

{birth_text}
{transforms_text}
{palace_stars_text}

请识别命盘中的格局（包括紫府同宫、杀破狼、机月同梁等重要格局），并评估格局的完整程度和影响。"""

    # 加载并注入相关案例
    pattern_cases = load_pattern_cases()
    relevant_cases = get_relevant_cases(pattern_cases, chart_data, limit=20)
    if relevant_cases:
        user_prompt += format_cases_as_context(relevant_cases, "格局")

    if question:
        user_prompt += f"\n\n【特定问题】\n{question}"

    user_prompt += "\n\n请给出格局的详细分析，包括格局识别、格局评价、以及对人生各方面的影响。"

    return user_prompt


# ============ 运限分析提示词 ============

# ============ TIMING分析提示词（使用增强版） ============

# 使用基于顶级Agent提示词研究的增强版提示词
TIMING_SYSTEM_PROMPT = ENHANCED_TIMING_SYSTEM_PROMPT



def build_timing_user_prompt(chart_data: Dict[str, Any], question: Optional[str] = None,
                            include_multi_year: bool = True) -> str:
    """
    构建运限分析的用户提示词

    Args:
        chart_data: 命盘数据
        question: 用户可选的特定问题
        include_multi_year: 是否包含多年流年数据（默认True）

    Returns:
        格式化的用户提示词
    """
    # 提取基本信息
    birth_info = chart_data.get("birth_info", {})
    palaces = chart_data.get("palaces", {})
    stars = chart_data.get("stars", {})

    # 计算年龄等信息
    import datetime
    current_year = datetime.datetime.now().year
    birth_year = birth_info.get('year', 1990)
    age = current_year - birth_year

    # 格式化出生信息
    birth_text = f"""
命主信息：
- 出生年份：{birth_year}年
- 当前年份：{current_year}年
- 当前年龄：{age}岁
- 性别：{birth_info.get('gender', '未知')}
- 五行局：{birth_info.get('wuxing_ju', '未知')}
"""

    # 格式化命宫信息
    ming_gong = palaces.get("命宫", {})
    ming_stars = [s.get("name") for s in ming_gong.get("stars", []) if s.get("type") == "正曜"]
    ming_text = f"""
命宫信息：
- 主星：{', '.join(ming_stars) if ming_stars else '空宫'}
- 宫位：{ming_gong.get('branch', '')}{ming_gong.get('tiangan', '')}
"""

    # 格式化各宫位重要星曜
    palace_order = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                    "迁移宫", "仆役宫", "官禄宫", "田宅宫", "父母宫", "福德宫"]
    palace_stars_text = "\n各宫位重要星曜：\n"
    for palace_name in palace_order:
        palace_data = palaces.get(palace_name, {})
        palace_stars = palace_data.get("stars", [])
        main_stars = [s.get("name") for s in palace_stars if s.get("type") == "正曜"]
        transform_stars = [s.get("name") for s in palace_stars if s.get("type") == "化曜"]
        if main_stars or transform_stars:
            stars_str = []
            if main_stars:
                stars_str.append(','.join(main_stars[:3]))
            if transform_stars:
                stars_str.append('+'.join(transform_stars))
            palace_stars_text += f"  - {palace_name}: {' '.join(stars_str)}\n"

    # 格式化流年星曜
    transform_stars = stars.get("transform_stars", [])
    year_transforms = [f"{s.get('name', '')}在{s.get('palace', '')}" for s in transform_stars]

    year_text = f"""
当前流年（{current_year}年）信息：
- 流年四化：{', '.join(year_transforms) if year_transforms else '无特殊四化'}
"""

    user_prompt = f"""请分析以下命盘的运限运势：

{birth_text}
{ming_text}
{year_text}
{palace_stars_text}"""

    if question:
        user_prompt += f"\n\n【特定问题】\n{question}"

    # 构建多年预测请求
    years_ahead = 10
    end_year = current_year + years_ahead

    if include_multi_year:
        user_prompt += f"""

## 重要要求

1. **大限表格**：必须输出12步大限的完整表格，包含每步大限的名称、年龄范围、运势评级（A/B/C+）

2. **流年预测**：必须逐年预测从{current_year}年到{end_year}年（共{years_ahead}年）的运势，包含以下信息：
   - 每年的太岁落宫
   - 每年的关键星曜
   - 每年的运势评级

3. **时间锚点**：必须识别出具体哪几年有重大机遇（最好年份）或挑战（最差年份），并给出具体年份如"2025年"、"2028年"

4. **时间敏感建议**：必须给出如"2028年适合..."这样的具体年份建议，而非泛泛而谈"""

    user_prompt += f"\n\n请给出详细的运限分析，包括：\n- 12步大限的完整分析表格\n- 未来{years_ahead}年的逐年运势预测\n- 具体的时间锚点（机遇年份和挑战年份）\n- 可执行的时间敏感建议"

    # 加载并注入大限案例
    daxian_cases = load_daxian_cases()
    relevant_cases = get_relevant_cases(daxian_cases, chart_data, limit=20)
    if relevant_cases:
        user_prompt += format_cases_as_context(relevant_cases, "大限")

    return user_prompt


# ============ 综合报告提示词 ============

# ============ SYNTHESIS分析提示词（使用增强版） ============

# 使用基于顶级Agent提示词研究的增强版提示词
SYNTHESIS_SYSTEM_PROMPT = ENHANCED_SYNTHESIS_SYSTEM_PROMPT



def build_synthesis_user_prompt(
    chart_data: Dict[str, Any],
    star_analysis: Optional[Dict[str, Any]] = None,
    palace_analysis: Optional[Dict[str, Any]] = None,
    pattern_analysis: Optional[Dict[str, Any]] = None,
    transform_analysis: Optional[Dict[str, Any]] = None,
    question: Optional[str] = None
) -> str:
    """
    构建综合分析的用户提示词

    Args:
        chart_data: 命盘数据
        star_analysis: 星曜分析结果（可选）
        palace_analysis: 宫位分析结果（可选）
        pattern_analysis: 格局分析结果（可选）
        transform_analysis: 四化分析结果（可选）
        question: 用户可选的特定问题

    Returns:
        格式化的用户提示词
    """
    # 提取基本信息
    birth_info = chart_data.get("birth_info", {})
    stars = chart_data.get("stars", {})
    palaces = chart_data.get("palaces", {})
    transforms = chart_data.get("transforms", [])

    # 格式化出生信息
    birth_text = f"""
命盘基本信息：
- 出生年份：{birth_info.get('year', '未知')}年
- 出生月份：{birth_info.get('month', '未知')}月
- 出生日期：{birth_info.get('day', '未知')}日
- 出生时辰：{birth_info.get('birth_hour', birth_info.get('hour', '未知'))}时
- 性别：{birth_info.get('gender', '未知')}
- 五行局：{birth_info.get('wuxing_ju', '未知')}
- 命宫主星：{birth_info.get('ming_zhu', stars.get('main_stars', [{}])[0].get('name', '未知') if stars.get('main_stars') else '未知')}
"""

    # 格式化十四正曜
    main_stars = stars.get("main_stars", [])
    main_stars_text = "十四正曜："
    for star in main_stars[:14]:
        palace = star.get("palace", "")
        level = star.get("level", "平")
        main_stars_text += f"\n  {star.get('name', '')} ({palace} {level})"

    # 格式化四化
    transform_text = "\n\n四化信息："
    for t in transforms:
        star = t.get("star", "")
        transform_type = t.get("type", "")
        palace = t.get("palace", "")
        transform_text += f"\n  {star}化{transform_type} 在 {palace}"

    # 格式化重要宫位
    key_palaces = "\n\n重要宫位："
    palace_data = palaces.get("命宫", {})
    ming_stars = [s.get("name") for s in palace_data.get("stars", [])]
    key_palaces += f"\n  命宫: {', '.join(ming_stars) if ming_stars else '空宫'}"

    palace_data = palaces.get("官禄宫", {})
    guanlu_stars = [s.get("name") for s in palace_data.get("stars", [])]
    key_palaces += f"\n  官禄宫: {', '.join(guanlu_stars) if guanlu_stars else '空宫'}"

    palace_data = palaces.get("财帛宫", {})
    caifu_stars = [s.get("name") for s in palace_data.get("stars", [])]
    key_palaces += f"\n  财帛宫: {', '.join(caifu_stars) if caifu_stars else '空宫'}"

    palace_data = palaces.get("夫妻宫", {})
    couple_stars = [s.get("name") for s in palace_data.get("stars", [])]
    key_palaces += f"\n  夫妻宫: {', '.join(couple_stars) if couple_stars else '空宫'}"

    # 如果有各Agent的分析结果，添加进去
    analysis_text = ""
    if star_analysis:
        analysis_text += "\n\n【星曜分析结果】\n"
        if isinstance(star_analysis, dict):
            analysis_text += star_analysis.get("summary", str(star_analysis))
        else:
            analysis_text += str(star_analysis)

    if palace_analysis:
        analysis_text += "\n\n【宫位分析结果】\n"
        if isinstance(palace_analysis, dict):
            analysis_text += palace_analysis.get("summary", str(palace_analysis))
        else:
            analysis_text += str(palace_analysis)

    if pattern_analysis:
        analysis_text += "\n\n【格局分析结果】\n"
        if isinstance(pattern_analysis, dict):
            analysis_text += pattern_analysis.get("summary", str(pattern_analysis))
        else:
            analysis_text += str(pattern_analysis)

    if transform_analysis:
        analysis_text += "\n\n【四化分析结果】\n"
        if isinstance(transform_analysis, dict):
            analysis_text += transform_analysis.get("summary", str(transform_analysis))
        else:
            analysis_text += str(transform_analysis)

    user_prompt = f"""请对以下命盘进行综合分析：

{birth_text}
{main_stars_text}
{transform_text}
{key_palaces}
{analysis_text}"""

    if question:
        user_prompt += f"\n\n【用户特定问题】\n{question}"

    user_prompt += "\n\n请给出完整的综合分析报告，包括整体格局、性格特征、事业财运感情分析、运势预测、以及趋吉避凶的具体建议。"

    return user_prompt


# ============ 剖腹产良辰吉日提示词 ============

BIRTH_TIMING_SYSTEM_PROMPT = """你是一位紫微斗数专家，专注于剖腹产良辰吉日（剖腹产择吉）分析。你的职责是评估多个剖腹产时间候选方案，从中选择最优时间，并提供详细的分析理由。

## 角色定义
你是一位精通紫微斗数择日学的专业命理师，拥有30年剖腹产择吉实践经验。你能够：
- 根据父母的命盘分析其与子女命盘的关系
- 评估不同时间出生的孩子命盘质量
- 综合考虑五行平衡、星曜格局、宫位配置
- 权衡孩子的命格优劣与母亲的安产安全
- 给出明确的时间推荐和置信度

## 优先级原则
1. **首要**：母亲安全和胎儿健康（必须保障）
2. **其次**：孩子的命盘质量（一生运势基础）
3. **参考**：父母的命盘配合度（家庭和谐）
4. **考虑**：实际操作可行性（医院时间安排）

## 评估维度（每个时辰需从以下维度分析）

### 1. 五行平衡
- 分析该时间出生孩子的命盘五行配置
- 检查五行是否平衡（过偏则不吉）
- 考虑与父母命盘的五行相生相克关系

### 2. 星曜格局
- 命宫主星是否得力（紫微、天府最佳）
- 是否有重要辅星会照（左辅、右弼、文昌、文曲等）
- 是否构成有利格局（紫府同垣格、机月同梁格等）
- 煞星数量和分布（过多则凶）

### 3. 宫位配置
- 重点宫位（命宫、官禄宫、财帛宫、迁移宫）的强弱
- 宫位三方四正的配合情况
- 空宫数量和对宫投影影响

### 4. 时辰吉凶
- 该时辰本身在择日学中的吉凶
- 与年月日的配合关系
- 是否有冲煞日时

## 输出格式要求

请以JSON格式返回分析结果，包含以下字段：

```json
{
  "analysis_type": "birth_timing",
  "recommended_option": 1,  // 推荐的时辰序号
  "confidence": 0.85,  // 置信度 0-1

  "option_analyses": [
    {
      "rank": 1,
      "date": "2026-09-15",
      "hour": "午时",
      "score": 88.5,
      "level": "极佳",

      "five_elements_analysis": "五行配置分析",
      "star_pattern_analysis": "星曜格局分析",
      "palace_analysis": "宫位配置分析",
      "timing_analysis": "时辰吉凶分析",

      "strengths": ["优势1", "优势2"],
      "weaknesses": ["劣势1"],

      "maternal_compatibility": "与母亲的命盘配合度分析",
      "paternal_compatibility": "与父亲的命盘配合度分析（如有）",

      "child_destiny_quality": "孩子的命格质量评估",
      "long_term_prospects": "一生运势展望",

      "recommendation": "明确的推荐理由",
      "warnings": ["注意事项（如有）"]
    }
  ],

  "comparative_analysis": {
    "best_aspects": ["该时间表现最好的方面"],
    "main_differences": ["与其他候选时间的主要差异"],
    "trade_offs": "需要权衡的因素"
  },

  "final_recommendation": "最终推荐意见及理由"
}
```

## 关键原则

1. **禁止空泛评价**：每项分析必须有具体、实质的内容，不能使用"尚可"、"一般"等模糊词汇
2. **对比分析**：必须明确指出各时辰之间的差异和优劣
3. **明确推荐**：必须给出唯一推荐，不能模棱两可
4. **置信度说明**：置信度需结合数据充分度和命盘质量综合判断
5. **母亲安全第一**：任何可能影响母亲安全的时间都应标注警告

## Few-Shot示例

**输入**：
- 母亲命盘：命宫紫微星，官禄宫有化禄
- 父亲命盘：命宫天府星
- 候选时辰1：2026年9月15日午时，命宫紫微贪狼
- 候选时辰2：2026年9月16日巳时，命宫天同太阴

**输出示例**：
```json
{
  "analysis_type": "birth_timing",
  "recommended_option": 1,
  "confidence": 0.88,
  "option_analyses": [
    {
      "rank": 1,
      "date": "2026-09-15",
      "hour": "午时",
      "score": 85.5,
      "level": "极佳",
      "five_elements_analysis": "午时属火，与孩子命盘火六局相呼应，五行流通较好。...",
      "star_pattern_analysis": "紫微贪狼同宫，紫微为帝王星，贪狼为欲望星，两者相配...",
      "palace_analysis": "命宫紫微星坐守，格局尊贵。官禄宫太阳星旺照...",
      "timing_analysis": "午时为阳气最盛之时，与紫微星性质相合...",
      "strengths": ["命宫紫微星尊贵", "官禄宫太阳星旺照", "无煞星冲破"],
      "weaknesses": ["贪狼桃花特性需注意"],
      "maternal_compatibility": "母亲命宫紫微星与孩子命宫紫微星同气相求...",
      "paternal_compatibility": "父亲天府星与孩子紫微星相合...",
      "child_destiny_quality": "具有领导才能，适合管理岗位...",
      "long_term_prospects": "一生运势平稳，中年后事业有成...",
      "recommendation": "推荐该时间，孩子命格贵重，与父母命盘配合良好...",
      "warnings": []
    }
  ],
  "comparative_analysis": {...},
  "final_recommendation": "综合评估后，首选2026年9月15日午时..."
}
```
"""


def build_birth_timing_user_prompt(
    birth_timing_result: Dict[str, Any],
    mother_chart: Optional[Dict[str, Any]] = None,
    father_chart: Optional[Dict[str, Any]] = None,
    question: Optional[str] = None
) -> str:
    """
    构建剖腹产良辰吉日分析的用户提示词

    Args:
        birth_timing_result: BirthTimingResult 结构（包含 options 等）
        mother_chart: 母亲命盘数据
        father_chart: 父亲命盘数据
        question: 用户可选的特定问题

    Returns:
        格式化的用户提示词
    """
    # 格式化父母信息
    parents_info = ""

    if mother_chart:
        mother_birth = mother_chart.get("birth_info", {})
        mother_stars = mother_chart.get("stars", {})
        mother_main_stars = [s.get("name", "") for s in mother_stars.get("main_stars", [])]
        parents_info += f"""
【母亲命盘信息】
- 出生：{mother_birth.get('year', '未知')}年{mother_birth.get('month', '')}月{mother_birth.get('day', '')}日
- 五行局：{mother_birth.get('wuxing_ju', '未知')}
- 命宫主星：{', '.join(mother_main_stars[:3]) if mother_main_stars else '未知'}
"""

    if father_chart:
        father_birth = father_chart.get("birth_info", {})
        father_stars = father_chart.get("stars", {})
        father_main_stars = [s.get("name", "") for s in father_stars.get("main_stars", [])]
        parents_info += f"""
【父亲命盘信息】
- 出生：{father_birth.get('year', '未知')}年{father_birth.get('month', '')}月{father_birth.get('day', '')}日
- 五行局：{father_birth.get('wuxing_ju', '未知')}
- 命宫主星：{', '.join(father_main_stars[:3]) if father_main_stars else '未知'}
"""

    # 格式化候选时辰选项
    options = birth_timing_result.get("options", [])
    options_text = "\n【候选时辰选项】\n"

    if options:
        for i, opt in enumerate(options[:10], 1):  # 最多显示10个
            chart_summary = opt.get("chart_summary", {})
            options_text += f"""
--- 时辰 {i} ---
日期：{opt.get('date', '未知')}
时辰：{opt.get('hour', '未知')}
农历：{opt.get('lunar_date', '未知')}
评分：{opt.get('score', 0)}分（{opt.get('level', '未知')}）
命宫主星：{chart_summary.get('main_star', '未知')}
五行局：{chart_summary.get('wuxing_ju', '未知')}
四化：{', '.join(chart_summary.get('transforms', [])) if chart_summary.get('transforms') else '无'}
优势：{', '.join(opt.get('strengths', [])[:3]) if opt.get('strengths') else '无明显优势'}
劣势：{', '.join(opt.get('weaknesses', [])[:2]) if opt.get('weaknesses') else '无明显劣势'}
推荐理由：{', '.join(opt.get('reasons', [])[:2]) if opt.get('reasons') else '无'}
"""
    else:
        options_text += "暂无候选时辰数据"

    # 格式化最佳选项
    best_option = birth_timing_result.get("best_option")
    best_text = ""
    if best_option:
        best_text = f"""
【当前规则引擎最佳选择】
日期：{best_option.get('date', '未知')}
时辰：{best_option.get('hour', '未知')}
评分：{best_option.get('score', 0)}分
置信度：{birth_timing_result.get('confidence', 0) * 100:.0f}%
"""

    # 核心问题
    core_question = """
【核心问题】
基于以上父母命盘和候选时辰，请分析：
1. 哪个时辰最适合剖腹产？（考虑孩子命格、父母配合、实际操作）
2. 各时辰之间的主要差异是什么？
3. 有没有需要特别注意或避免的时辰？
4. 请给出明确的推荐和置信度。
"""

    # 组装完整提示词
    user_prompt = f"""请分析以下剖腹产良辰吉日候选方案：

{parents_info}
{options_text}
{best_text}
{core_question}"""

    # 添加特定问题
    if question:
        user_prompt += f"\n\n【用户特定问题】\n{question}"

    return user_prompt


# ============ 事件预测分析提示词 ============

EVENT_PREDICT_SYSTEM_PROMPT = """你是一位紫微斗数事件预测专家。你的职责是基于命盘数据预测具体事件的成功率、时机和吉凶。

## 角色定义
你是一位精通紫微斗数事件预测的专业命理师，拥有30年实践经验。你能够：
- 分析具体事件的宫位配置和星曜组合
- 评估事件成功的有利和不利因素
- 预测最佳和最坏情况
- 识别最优时机窗口
- 评估可能的风险因素

## 核心概念

### 命与运的关系
- 命（命盘结构）：先天禀赋，代表事件的基础概率
- 运（时机）：后天运势，包括流年、流月、流日的时机
- 成功 = 命的可能性 × 运的时机配合

### 事件类型与宫位对应
- 跳槽、晋升、创业、求职面试 → 官禄宫
- 官司诉讼、考试升学、出行远行、求学申请 → 迁移宫
- 商务签约、投资理财 → 财帛宫
- 结婚嫁娶 → 夫妻宫
- 搬家乔迁 → 田宅宫

### 时间层次分析
1. **流年**：整年运势，影响事件能否在该年发生
2. **流月**：月度运势，影响最佳行动月份
3. **流日**：日运势，影响具体日期选择

### 四化对事件的影响
- **化禄**：增加机会和财运，利于事件发生
- **化权**：增强执行力，提高成功概率
- **化科**：带来声誉和贵人相助
- **化忌**：带来阻碍和波折，需特别注意

### 煞星影响
- 擎羊、陀罗：增加冲突和阻碍
- 火星、铃星：增加意外和变动
- 地空、地劫：增加不确定性和挫折

## 分析方法

### 1. 宫位分析
分析目标宫位的：
- 主星配置（庙旺平陷）
- 辅星辅助（贵人相助）
- 煞星破坏（阻碍因素）
- 化曜影响（四化效应）

### 2. 时机分析
- 流年太岁落宫与目标宫位的关系
- 流月走势
- 是否有利的流日

### 3. 风险评估
- 识别可能导致失败的风险因素
- 评估风险的严重程度
- 提供化解建议

## 质量标准

1. **概率表述**：使用概率范围而非绝对表述
   - 85-95%：极大可能
   - 70-85%：很可能
   - 50-70%：有一定可能
   - 30-50%：不确定
   - 10-30%：可能性较低
   - <10%：可能性很低

2. **最佳/最坏情况**：必须提供概率区间的两端

3. **时机窗口**：给出具体的时间范围

4. **可执行建议**：每条建议都应具体可执行

## 输出格式要求

请以JSON格式返回分析结果，包含以下字段：
```json
{
  "analysis_type": "event_prediction",
  "event_type": "事件类型",
  "target_palace": "目标宫位",
  "success_probability": {
    "base_probability": 基础概率(0-100),
    "adjusted_probability": 调整后概率(0-100),
    "confidence": 置信度(0-1),
    "best_case": 最佳情况概率,
    "worst_case": 最坏情况概率
  },
  "timing_analysis": {
    "year_timing": "流年时机评估",
    "month_timing": "最佳月份",
    "day_timing": "日期选择建议",
    "optimal_window": "最优时间窗口"
  },
  "favorable_factors": [
    {
      "factor": "有利因素描述",
      "palace": "相关宫位",
      "impact": "影响程度(0-100)"
    }
  ],
  "risk_factors": [
    {
      "factor": "风险因素描述",
      "palace": "相关宫位",
      "impact": "影响程度(负值)",
      "mitigation": "化解建议"
    }
  ],
  "scenario_analysis": {
    "best_scenario": "最佳情况描述",
    "most_likely": "最可能情况描述",
    "worst_scenario": "最坏情况描述"
  },
  "actionable_advice": [
    {
      "advice": "具体建议",
      "timing": "执行时机",
      "priority": "优先级(high/medium/low)"
    }
  ],
  "overall_reasoning": "综合分析理由"
}
```

## 注意事项
- 所有概率和评分必须基于命盘数据分析
- 不要凭空给出高分或低分
- 如果信息不足以判断某项，明确说明
- 建议应具体可执行，避免空泛的通用建议"""


def build_event_predict_user_prompt(
    chart_data: Dict[str, Any],
    event_type: str,
    target_year: Optional[int] = None,
    target_month: Optional[int] = None,
    rule_based_result: Optional[Dict[str, Any]] = None
) -> str:
    """
    构建事件预测的用户提示词

    Args:
        chart_data: 命盘数据
        event_type: 事件类型
        target_year: 目标年份
        target_month: 目标月份
        rule_based_result: 基于规则的分析结果

    Returns:
        格式化的用户提示词
    """
    birth_info = chart_data.get("birth_info", {})
    palaces = chart_data.get("palaces", {})
    stars = chart_data.get("stars", {})
    flowing_year = chart_data.get("flowing_year", {})
    flowing_month = chart_data.get("flowing_month", {})

    # 格式化出生信息
    birth_text = f"""
命主信息：
- 年份：{birth_info.get('year', '未知')}年
- 月份：{birth_info.get('month', '未知')}月
- 日期：{birth_info.get('day', '未知')}日
- 时辰：{birth_info.get('birth_hour', birth_info.get('hour', '未知'))}时
- 性别：{birth_info.get('gender', '未知')}
- 五行局：{birth_info.get('wuxing_ju', '未知')}
"""

    # 事件信息
    event_text = f"""
【预测事件】
- 事件类型：{event_type}
- 目标年份：{target_year if target_year else '未指定（使用当前流年）'}
- 目标月份：{target_month if target_month else '未指定'}
"""

    # 事件与宫位映射
    event_palace_map = {
        "跳槽": "官禄宫",
        "晋升": "官禄宫",
        "创业": "官禄宫",
        "求职面试": "官禄宫",
        "官司诉讼": "迁移宫",
        "考试升学": "迁移宫",
        "出行远行": "迁移宫",
        "求学申请": "迁移宫",
        "商务签约": "财帛宫",
        "投资理财": "财帛宫",
        "结婚嫁娶": "夫妻宫",
        "搬家乔迁": "田宅宫",
    }
    target_palace = event_palace_map.get(event_type, "命宫")

    # 目标宫位信息
    palace_data = palaces.get(target_palace, {})
    palace_stars = palace_data.get("stars", [])

    palace_text = f"""
【目标宫位：{target_palace}】
"""
    if palace_stars:
        main_stars = [s.get("name") for s in palace_stars if s.get("type") == "正曜"]
        auxiliary_stars = [s.get("name") for s in palace_stars if s.get("type") == "辅星"]
        sha_stars = [s.get("name") for s in palace_stars if s.get("type") == "煞星"]
        transform_stars = [s.get("name") for s in palace_stars if s.get("type") == "化曜"]

        if main_stars:
            palace_text += f"  主星：{', '.join(main_stars)}\n"
        if auxiliary_stars:
            palace_text += f"  辅星：{', '.join(auxiliary_stars)}\n"
        if sha_stars:
            palace_text += f"  煞星：{', '.join(sha_stars)}\n"
        if transform_stars:
            palace_text += f"  化曜：{', '.join(transform_stars)}\n"
    else:
        palace_text += "  （空宫）\n"

    # 流年信息
    year_text = ""
    if flowing_year:
        year_score = flowing_year.get("score", 50)
        year_stars = flowing_year.get("stars", [])
        year_text = f"""
【当前流年运势】
- 运势评分：{year_score}/100
- 流年星曜：{', '.join(year_stars) if year_stars else '暂无'}
"""
    elif target_year:
        year_text = f"""
【目标流年运势】
- 目标年份：{target_year}年
- （详细流年数据需进一步计算）
"""

    # 流月信息
    month_text = ""
    if flowing_month:
        month_score = flowing_month.get("score", 50)
        month_text = f"""
【当前流月运势】
- 月运势评分：{month_score}/100
"""

    # 规则基础分析结果
    rule_text = ""
    if rule_based_result:
        rule_text = f"""
【规则基础分析结果（仅供参考）】
- 成功率：{rule_based_result.get('success_rate', 'N/A')}%
- 时机评分：{rule_based_result.get('timing_score', 'N/A')}/100
- 置信度：{rule_based_result.get('confidence', 'N/A')}
- 风险因素：{len(rule_based_result.get('risk_factors', []))}个
- 机遇因素：{len(rule_based_result.get('opportunity_factors', []))}个
"""
        if rule_based_result.get("risk_factors"):
            rule_text += "\n风险因素详情：\n"
            for rf in rule_based_result["risk_factors"][:3]:
                rule_text += f"  - {rf.get('description', '')}: {rf.get('impact_score', 0)}\n"
        if rule_based_result.get("opportunity_factors"):
            rule_text += "\n机遇因素详情：\n"
            for of in rule_based_result["opportunity_factors"][:3]:
                rule_text += f"  - {of.get('description', '')}: {of.get('impact_score', 0)}\n"

    # 组装提示词
    user_prompt = f"""请分析以下命盘，对【{event_type}】事件进行预测：

{birth_text}
{event_text}
{palace_text}
{year_text}
{month_text}
{rule_text}

请基于命盘数据分析：
1. {target_palace}的星曜配置对该事件的影响
2. 当前流年/流月运势对该事件的时机是否有利
3. 预测该事件的最佳和最坏情况
4. 识别有利因素和风险因素
5. 提供具体的行动建议和最优时机窗口"""

    return user_prompt


def format_analysis_as_text(analysis_result: Dict[str, Any]) -> str:
    """
    将分析结果格式化为易读的文本格式

    Args:
        analysis_result: 分析结果字典

    Returns:
        格式化的文本
    """
    analysis_type = analysis_result.get("analysis_type", "unknown")

    lines = []

    if analysis_type == "star_analysis":
        lines.append("=" * 50)
        lines.append("星曜分析")
        lines.append("=" * 50)

        if "main_star_interpretations" in analysis_result:
            lines.append("\n【主星解读】")
            for item in analysis_result["main_star_interpretations"]:
                lines.append(f"\n{item.get('star_name', '')} 在 {item.get('palace', '')}")
                lines.append(f"  庙旺平陷: {item.get('level', '')}")
                lines.append(f"  解读: {item.get('interpretation', '')}")

        if "key_observations" in analysis_result:
            lines.append("\n\n【关键观察】")
            for obs in analysis_result["key_observations"]:
                lines.append(f"  • {obs}")

        if "personality_summary" in analysis_result:
            lines.append(f"\n\n【性格特征】\n{analysis_result['personality_summary']}")

        if "career_recommendations" in analysis_result:
            lines.append(f"\n\n【事业建议】\n{analysis_result['career_recommendations']}")

    elif analysis_type == "palace_analysis":
        lines.append("=" * 50)
        lines.append("宫位分析")
        lines.append("=" * 50)

        if "palace_strengths" in analysis_result:
            lines.append("\n【宫位强弱】")
            for palace, strength in analysis_result["palace_strengths"].items():
                lines.append(f"  {palette}: {strength}分")

        if "strongest_palaces" in analysis_result:
            lines.append(f"\n【最强宫位】\n  {', '.join(analysis_result['strongest_palaces'])}")

        if "weakest_palaces" in analysis_result:
            lines.append(f"\n【最弱宫位】\n  {', '.join(analysis_result['weakest_palaces'])}")

        if "life_focus" in analysis_result:
            lines.append(f"\n【人生重点】\n{analysis_result['life_focus']}")

    elif analysis_type == "transform_analysis":
        lines.append("=" * 50)
        lines.append("四化分析")
        lines.append("=" * 50)

        if "transform_distribution" in analysis_result:
            lines.append("\n【四化分布】")
            for t_type, palaces in analysis_result["transform_distribution"].items():
                if palaces:
                    lines.append(f"  {t_type}: {', '.join(palaces)}")

        if "key_transforms" in analysis_result:
            lines.append("\n【关键四化】")
            for item in analysis_result["key_transforms"]:
                lines.append(f"  • {item}")

        if "transform_interactions" in analysis_result:
            lines.append("\n【四化交互】")
            for interaction in analysis_result["transform_interactions"]:
                lines.append(f"  {interaction}")

        if "overall_assessment" in analysis_result:
            lines.append(f"\n【总体评价】\n{analysis_result['overall_assessment']}")

    elif analysis_type == "pattern_analysis":
        lines.append("=" * 50)
        lines.append("格局分析")
        lines.append("=" * 50)

        if "matched_patterns" in analysis_result:
            lines.append("\n【匹配格局】")
            for pattern in analysis_result["matched_patterns"]:
                name = pattern.get("name", "")
                quality = pattern.get("quality", "")
                desc = pattern.get("description", "")
                lines.append(f"  {name} ({quality}): {desc}")

        if "pattern_summary" in analysis_result:
            lines.append(f"\n【格局总评】\n{analysis_result['pattern_summary']}")

        if "auspicious_patterns" in analysis_result:
            lines.append("\n【吉格】")
            for p in analysis_result["auspicious_patterns"]:
                lines.append(f"  • {p}")

        if "inauspicious_patterns" in analysis_result:
            lines.append("\n【凶格】")
            for p in analysis_result["inauspicious_patterns"]:
                lines.append(f"  • {p}")

        if "pattern_impact" in analysis_result:
            lines.append(f"\n【格局影响】\n{analysis_result['pattern_impact']}")

    elif analysis_type == "timing_analysis":
        lines.append("=" * 50)
        lines.append("运限分析")
        lines.append("=" * 50)

        # 大限表格
        if "major_fate_table" in analysis_result:
            lines.append("\n【大限时间线】")
            for mf in analysis_result["major_fate_table"]:
                rating = mf.get("rating", "")
                lines.append(f"  {mf.get('name', '')}（{mf.get('age_range', '')}）：{rating} - {mf.get('summary', '')}")

        # 当前大限
        if "current_major_fate" in analysis_result:
            lines.append("\n【当前大限】")
            mf = analysis_result["current_major_fate"]
            lines.append(f"  年龄：{mf.get('age_range', '')}岁")
            lines.append(f"  宫位：{mf.get('palace', '')}")
            lines.append(f"  枢纽：{mf.get('hub_palace', '')}")
            lines.append(f"  四化：{mf.get('transformation', '')}")
            if mf.get("description"):
                lines.append(f"  概述：{mf.get('description', '')}")

        # 流年预测
        if "year_predictions" in analysis_result:
            lines.append("\n【流年预测】")
            for yp in analysis_result["year_predictions"][:5]:  # 只显示前5年
                lines.append(f"  {yp.get('year', '')}年（{yp.get('age', '')}岁）：{yp.get('rating', '')} - {yp.get('summary', '')}")

        # 时间锚点
        if "time_anchors" in analysis_result:
            lines.append("\n【时间锚点】")
            for anchor in analysis_result["time_anchors"]:
                anchor_type = anchor.get("type", "")
                year = anchor.get("year", "")
                age = anchor.get("age", "")
                advice = anchor.get("advice", "")
                lines.append(f"  {anchor_type}：{year}年（{age}岁）- {advice}")

        # 命运转换节点
        if "fate_transitions" in analysis_result:
            lines.append("\n【命运转换节点】")
            for ft in analysis_result["fate_transitions"]:
                lines.append(f"  {ft.get('age', '')}岁：{ft.get('description', '')}")

        # 当前流年
        if "current_year_fate" in analysis_result:
            lines.append("\n【当前流年】")
            yf = analysis_result["current_year_fate"]
            if isinstance(yf, dict):
                lines.append(f"  年份：{yf.get('year', '')}年")
                lines.append(f"  太岁落宫：{yf.get('tai_sui_palace', '')}")
                lines.append(f"  与命宫关系：{yf.get('tai_sui_relationship', '')}")
            else:
                lines.append(f"  {yf}")

        # 建议
        if "recommendations" in analysis_result:
            lines.append("\n【时间敏感建议】")
            recs = analysis_result["recommendations"]
            if isinstance(recs, list):
                for rec in recs:
                    if isinstance(rec, dict):
                        lines.append(f"  {rec.get('time', '')}：{rec.get('advice', '')}")
                    else:
                        lines.append(f"  • {rec}")
            else:
                lines.append(f"  {recs}")

    elif analysis_type == "synthesis_report":
        lines.append("=" * 50)
        lines.append("综合分析报告")
        lines.append("=" * 50)

        if "chart_overview" in analysis_result:
            lines.append(f"\n【命盘概览】\n{analysis_result['chart_overview']}")

        if "overall_pattern" in analysis_result:
            lines.append(f"\n【整体格局】\n{analysis_result['overall_pattern']}")

        if "personality_profile" in analysis_result:
            lines.append(f"\n【性格特征】\n{analysis_result['personality_profile']}")

        if "career_analysis" in analysis_result:
            lines.append(f"\n【事业分析】\n{analysis_result['career_analysis']}")

        if "wealth_analysis" in analysis_result:
            lines.append(f"\n【财运分析】\n{analysis_result['wealth_analysis']}")

        if "relationship_analysis" in analysis_result:
            lines.append(f"\n【感情分析】\n{analysis_result['relationship_analysis']}")

        if "health_insights" in analysis_result:
            lines.append(f"\n【健康建议】\n{analysis_result['health_insights']}")

        # 时间线分析
        if "timing_analysis" in analysis_result:
            lines.append("\n" + "=" * 40)
            lines.append("【时间线分析】")
            lines.append("=" * 40)

            ta = analysis_result["timing_analysis"]

            # 大限时间线
            if "major_fate_timeline" in ta:
                lines.append("\n大限时间线：")
                for mf in ta["major_fate_timeline"]:
                    lines.append(f"  {mf.get('period', '')}：{mf.get('rating', '')} - {mf.get('description', '')}")

            # 关键年份
            if "key_years" in ta:
                lines.append("\n关键年份：")
                for ky in ta["key_years"]:
                    lines.append(f"  {ky.get('year', '')}年（{ky.get('type', '')}）：{ky.get('description', '')}")
                    lines.append(f"    建议：{ky.get('action', '')}")

            # 时间锚点
            if "time_anchors" in ta:
                lines.append("\n时间锚点：")
                for anchor in ta["time_anchors"]:
                    lines.append(f"  {anchor.get('age', '')}岁 - {anchor.get('event', '')}：{anchor.get('description', '')}")

        if "strengths" in analysis_result:
            lines.append("\n【优势】")
            for s in analysis_result["strengths"]:
                lines.append(f"  • {s}")

        if "weaknesses" in analysis_result:
            lines.append("\n【劣势】")
            for w in analysis_result["weaknesses"]:
                lines.append(f"  • {w}")

        if "recommendations" in analysis_result:
            lines.append("\n【趋吉避凶建议】")
            recs = analysis_result["recommendations"]
            if isinstance(recs, list):
                for i, rec in enumerate(recs, 1):
                    if isinstance(rec, dict):
                        lines.append(f"  {i}. {rec.get('area', '')}：{rec.get('time_specific', rec)}")
                        if rec.get('action'):
                            lines.append(f"     具体行动：{rec.get('action', '')}")
                    else:
                        lines.append(f"  {i}. {rec}")
            else:
                lines.append(f"  {recs}")

        if "conclusion" in analysis_result:
            lines.append(f"\n【综合结论】\n{analysis_result['conclusion']}")

    return "\n".join(lines)


# ============ 姻缘配对分析提示词 ============

MARRIAGE_COMPAT_SYSTEM_PROMPT = """你是一位紫微斗数姻缘配对专家，专注于分析两个人之间的姻缘契合度。

## 角色定义
你是一位拥有30年命理实践经验的紫微斗数专家，精通姻缘配对分析。你能够：
- 分析两个人的命盘特点
- 评估双方的性格契合度
- 解读夫妻宫与命宫的关系
- 分析财运、事业、健康等维度的互补性
- 识别配对中的优势与挑战
- 提供建设性的关系发展建议

## 核心分析维度

### 1. 感情模式分析
- 命宫主星代表个人的性格和行为模式
- 夫妻宫代表对感情的态度和需求
- 福德宫代表精神层面的满足感
- 评估双方在感情中的角色定位

### 2. 沟通方式分析
- 根据命宫星曜判断沟通风格
- 分析迁移宫对沟通的影响
- 评估双方能否有效表达和理解彼此

### 3. 财运配合分析
- 财帛宫对比：双方财运基础
- 一方财帛宫强+另一方官禄宫强=互补
- 评估财务管理的协调性

### 4. 性格互补分析
- 五行相生相克关系
- 主星特性对比
- 评估能否互相补足对方短板

### 5. 运势同步分析
- 大运同步性
- 流年对感情的影响
- 评估关键时间节点

## 分析原则

1. **公平客观**：同时考虑甲乙双方的需求和特点
2. **积极建设**：不夸大负面因素，将挑战视为成长机会
3. **具体实用**：建议要具有可操作性
4. **文化敏感**：尊重传统命理文化，结合现代关系观念
5. **关注成长**：帮助双方了解如何共同成长

## 输出要求

请用JSON格式返回分析结果，包含：
- overall_assessment: 综合评估（100-200字的总体描述）
- emotional_analysis: 感情模式深度分析
- communication_insights: 沟通特点分析
- financial_harmony: 财运配合分析
- personality_synergy: 性格互补分析
- timing_guidance: 时机与运势分析
- relationship_strengths: 关系优势列表（3-5条）
- potential_challenges: 潜在挑战分析
- growth_suggestions: 成长建议列表（3-5条）
- final_recommendation: 最终建议（50-100字）

## 质量标准
- 分析要有深度，不只是表面描述
- 要结合双方命盘具体分析
- 建议要具体可执行
- 保持积极正面的态度"""


def build_marriage_compat_user_prompt(
    chart_a: Dict[str, Any],
    chart_b: Dict[str, Any],
    compatibility_result: Dict[str, Any],
    name_a: str = "甲方",
    name_b: str = "乙方",
    question: Optional[str] = None
) -> str:
    """
    构建姻缘配对分析的用户提示词

    Args:
        chart_a: 甲方命盘数据
        chart_b: 乙方命盘数据
        compatibility_result: 规则基础分析结果
        name_a: 甲方名称
        name_b: 乙方名称
        question: 可选的特定问题

    Returns:
        格式化的用户提示词
    """
    prompt_parts = []

    # 标题
    prompt_parts.append(f"# 姻缘配对分析请求\n")
    prompt_parts.append(f"## 分析对象")
    prompt_parts.append(f"- {name_a} vs {name_b}\n")

    # 基础配对指数
    prompt_parts.append("## 规则基础分析结果")
    prompt_parts.append(f"- 综合配对指数: {compatibility_result.get('overall_score', 0):.1f}分")
    prompt_parts.append(f"- 配对等级: {compatibility_result.get('overall_level', '')}\n")

    # 各维度分数
    prompt_parts.append("### 分维度评分")
    dimensions = compatibility_result.get('dimensions', [])
    for dim in dimensions:
        prompt_parts.append(
            f"- {dim.get('dimension', '')}: {dim.get('score', 0):.1f}分 ({dim.get('level', '')})"
        )
    prompt_parts.append("")

    # 甲方命盘信息
    prompt_parts.append(f"## {name_a}命盘信息")
    birth_a = chart_a.get("birth_info", {})
    prompt_parts.append(f"出生：{birth_a.get('year', '?')}年{birth_a.get('month', '?')}月{birth_a.get('day', '?')}日")
    prompt_parts.append(f"五行局：{birth_a.get('wuxing_ju', '未知')}\n")

    prompt_parts.append("### 各宫位星曜")
    palaces_a = chart_a.get("palaces", {})
    palace_order = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                    "迁移宫", "仆役宫", "官禄宫", "田宅宫", "父母宫", "福德宫"]
    for palace_name in palace_order:
        palace_data = palaces_a.get(palace_name, {})
        stars = palace_data.get("stars", [])
        if stars:
            star_names = []
            for s in stars:
                if isinstance(s, dict):
                    star_names.append(s.get("name", ""))
                elif isinstance(s, str):
                    star_names.append(s)
            if star_names:
                prompt_parts.append(f"- {palace_name}: {', '.join(star_names)}")

    # 甲方四化
    transforms_a = chart_a.get("transforms", [])
    if transforms_a:
        prompt_parts.append("\n### 四化")
        for t in transforms_a:
            if isinstance(t, dict):
                prompt_parts.append(f"- {t.get('star', '')}化{t.get('type', '')} → {t.get('to_palace', '')}")

    # 乙方命盘信息
    prompt_parts.append(f"\n## {name_b}命盘信息")
    birth_b = chart_b.get("birth_info", {})
    prompt_parts.append(f"出生：{birth_b.get('year', '?')}年{birth_b.get('month', '?')}月{birth_b.get('day', '?')}日")
    prompt_parts.append(f"五行局：{birth_b.get('wuxing_ju', '未知')}\n")

    prompt_parts.append("### 各宫位星曜")
    palaces_b = chart_b.get("palaces", {})
    for palace_name in palace_order:
        palace_data = palaces_b.get(palace_name, {})
        stars = palace_data.get("stars", [])
        if stars:
            star_names = []
            for s in stars:
                if isinstance(s, dict):
                    star_names.append(s.get("name", ""))
                elif isinstance(s, str):
                    star_names.append(s)
            if star_names:
                prompt_parts.append(f"- {palace_name}: {', '.join(star_names)}")

    # 乙方四化
    transforms_b = chart_b.get("transforms", [])
    if transforms_b:
        prompt_parts.append("\n### 四化")
        for t in transforms_b:
            if isinstance(t, dict):
                prompt_parts.append(f"- {t.get('star', '')}化{t.get('type', '')} → {t.get('to_palace', '')}")

    # 规则分析亮点和警告
    highlights = compatibility_result.get('compatibility_highlights', [])
    if highlights:
        prompt_parts.append("\n## 规则分析发现的亮点")
        for h in highlights:
            prompt_parts.append(f"- {h}")

    warnings = compatibility_result.get('compatibility_warnings', [])
    if warnings:
        prompt_parts.append("\n## 需要注意的问题")
        for w in warnings:
            prompt_parts.append(f"- {w}")

    # 维度详细分析
    prompt_parts.append("\n## 各维度详细分析")
    for dim in dimensions:
        prompt_parts.append(f"\n### {dim.get('dimension', '')} ({dim.get('score', 0):.1f}分)")
        prompt_parts.append(f"分析：{dim.get('analysis', '')}")
        if dim.get('positive_factors'):
            prompt_parts.append(f"优势：{'；'.join(dim.get('positive_factors', []))}")
        if dim.get('negative_factors'):
            prompt_parts.append(f"注意：{'；'.join(dim.get('negative_factors', []))}")

    # 建议
    suggestions = compatibility_result.get('suggestions', [])
    if suggestions:
        prompt_parts.append("\n## 基础建议")
        for s in suggestions:
            prompt_parts.append(f"- {s}")

    # 特定问题
    if question:
        prompt_parts.append(f"\n## 特定问题\n{question}")

    # 分析要求
    prompt_parts.append("""
## 分析要求

请基于以上规则分析结果，结合双方的命盘特点，进行深度姻缘配对分析。

重点关注：
1. 双方命宫主星的互动关系
2. 夫妻宫对命宫的投射
3. 福德宫的契合度
4. 大运同步性
5. 如何发挥优势、管理挑战

请给出全面、深入、具有建设性的分析报告。""")

    return "\n".join(prompt_parts)


# ============ 择日分析提示词 ============

DATE_SELECTION_SYSTEM_PROMPT = """你是一位紫微斗数专家，专精于择日选时（择日）。你的职责是评估和排序多个日期/时间候选，并提供专业的择日建议。

## 角色定义
你是一位拥有30年命理实践经验的紫微斗数择日专家，精通：
- 八字干支与日柱的五行配合
- 吉神凶煞的解读与权衡
- 命盘与日期能量的匹配分析
- 不同事件类型的择日原则

## 核心能力

1. **多因素权衡**：当多个日期都有优势时，能识别哪个最符合用户需求
2. **能量匹配**：分析日期的八字/干支与用户命盘的配合度
3. **目的导向**：根据具体事件类型（结婚/开业/搬家/出行等）判断最佳日期
4. **风险识别**：识别可能的问题并提供化解建议

## 质量标准

1. **最低字数要求**：
   - 每个日期的详细分析不得少于80字
   - 推荐理由不得少于100字
   - 总体分析不得少于150字

2. **禁止占位符**：严禁使用"..."、"N/A"、"待分析"等占位符

3. **决策明确**：必须给出明确的推荐，不可以说"两个都好"而不选

4. **置信度评估**：基于分数差异、选项数量、合冲关系等因素给出置信度

## 择日关键原则

### 吉神凶煞权衡
- **吉神**：天德、月德、岁德、三合、六合等
- **凶煞**：岁破、月破、灾煞、天狗，白虎等
- 原则：吉多凶少为吉，凶多吉少需化解

### 喜神忌神配合
- 日干五行生助用神为吉
- 日干五行克制忌神为吉
- 日干五行被忌神所生需谨慎

### 事件类型与宫位
- **结婚嫁娶**：看夫妻宫、迁移宫、福德宫
- **开市开张**：看财帛宫、官禄宫、田宅宫
- **动土破土**：看田宅宫、疾厄宫、父母宫
- **出行远行**：看迁移宫、命宫

### 日柱五行与命主配合
- 日干与命主年干同阴阳：+15分
- 日干五行生助命主年干：+20分
- 日干与命宫天干相生：+10分
- 日柱地支与命宫地支相合：+10分

### 凶日识别
- 岁破日：地支与当年太岁相冲
- 月破日：地支与月令相冲
- 四离日：节气交替前一天
- 杨公忌日：传统凶日

## 输出格式要求

请以JSON格式返回分析结果，包含以下字段：

```json
{
  "analysis_type": "date_selection",
  "recommendation": {
    "best_date": "最佳日期的solar_date",
    "rank": 1,
    "confidence": 0.85,
    "reason": "推荐该日期的详细理由（100字以上）",
    "matching_aspects": ["该日期与命盘配合的方面"],
    "potential_concerns": ["需要注意的问题"],
    "mitigation_suggestions": ["化解建议"]
  },
  "alternative_options": [
    {
      "date": "备选日期",
      "rank": 2,
      "reason": "作为备选的理由",
      "when_to_use": "何时使用该日期"
    }
  ],
  "date_analysis": {
    "日期字符串": {
      "strengths": ["优势列表"],
      "weaknesses": ["劣势列表"],
      "event_suitability": "对该事件的适合程度",
      "energy_direction": "能量方向（旺财/旺感情/旺事业等）"
    }
  },
  "overall_guidance": "总体择日指导建议（150字以上）"
}
```

## Few-Shot示例

**示例1：结婚嫁娶择日**

**输入**：
- 事件：结婚嫁娶
- 命主年干：甲（木）
- 命宫天干：丙（火）
- 候选日期：
  1. 2026-04-15，丙寅日，score=78
  2. 2026-04-18，己巳日，score=75
  3. 2026-04-22，癸酉日，score=72

**输出示例**：
```json
{
  "analysis_type": "date_selection",
  "recommendation": {
    "best_date": "2026-04-15",
    "rank": 1,
    "confidence": 0.88,
    "reason": "丙寅日综合评分最高。首先，日干丙火与命主年干甲木形成木生火的相生关系，这代表婚礼的能量能够生助命主，对婚后运势有积极影响。其次，丙火与命宫天干丙火同气相求，命主在此日举办婚礼能够获得命宫能量的加持。第三，寅木为甲木之根，日柱地支与命主年干同属木性，根基稳固，象征婚姻基础扎实。丙寅日属于木火通明之象，利于感情沟通和新婚生活的开始。虽然评分略高的寅日与命宫寅字重叠（命宫地支为寅），但重叠为增强而非冲克，整体为吉。",
    "matching_aspects": [
      "日干丙火生助命主甲木年干",
      "日柱地支寅木与命宫地支同字，增强命宫能量",
      "木火通明利于感情交流"
    ],
    "potential_concerns": [
      "寅日为命宫本宫，需注意当日不宜进行与命宫冲突的活动"
    ],
    "mitigation_suggestions": [
      "婚礼时间安排在上午9-11时（巳时），避开子时与命宫相冲",
      "新娘礼服颜色可选红色系，增强喜庆能量"
    ]
  },
  "alternative_options": [
    {
      "date": "2026-04-18",
      "rank": 2,
      "reason": "己巳日天干己土虽不直接生助甲木，但与命宫天干丙火形成火生土、土生金的间接流通。巳火为命宫之禄，禄代表俸禄和福气，在巳日结婚可得命宫福气加持。",
      "when_to_use": "如果4月15日因其他原因无法使用，可作为备选"
    },
    {
      "date": "2026-04-22",
      "rank": 3,
      "reason": "癸酉日评分最低，主要因为日干癸水克命主年干甲木，形成金水阴寒之气。酉金为桃花之星，虽利感情但克伐木性，可能对命主健康或运势有轻微影响。",
      "when_to_use": "除非前两个日期都不可用，否则不建议"
    }
  ],
  "date_analysis": {
    "2026-04-15": {
      "strengths": ["木火相生", "命宫能量加持", "婚姻基础稳固"],
      "weaknesses": ["寅日与命宫重叠需注意活动安排"],
      "event_suitability": "非常适合结婚嫁娶，能生助命主运势",
      "energy_direction": "木生火-利于感情升温、事业发展"
    },
    "2026-04-18": {
      "strengths": ["巳火为命宫禄位", "福气能量充足"],
      "weaknesses": ["天干己土不直接生助命主"],
      "event_suitability": "适合结婚，但能量稍逊于丙寅日",
      "energy_direction": "火土金流通-利财运积累"
    },
    "2026-04-22": {
      "strengths": ["酉金桃花星，利感情缘分"],
      "weaknesses": ["癸水克甲木，与命主年干相克"],
      "event_suitability": "需谨慎考虑，恐对命主有轻微克伐",
      "energy_direction": "金水阴寒-需大红喜庆调和"
    }
  },
  "overall_guidance": "综合分析后，推荐2026年4月15日（丙寅日）作为结婚嫁娶的最佳日期。该日木火相生，能量与命主命盘形成良性互动。丙寅日属于甲木命主的进气之象，新婚夫妇将在婚后迎来运势上升期。建议婚礼安排在上午9-11时的巳时，避开午时冲克。若必须选择备选日期，4月18日（己巳日）的命宫禄位能量亦可考虑，但整体配合度不如丙寅日。4月22日（癸酉日）除非万不得已不建议选择，因癸水克甲木恐对命主造成不必要的压力。"
}
```

**示例2：开市开张择日**

**输入**：
- 事件：开市开张
- 命主年干：庚（金）
- 命宫天干：壬（水）
- 候选日期：
  1. 2026-05-01，庚辰日，score=82
  2. 2026-05-03，壬午日，score=79
  3. 2026-05-06，乙酉日，score=76

**输出示例**：
```json
{
  "analysis_type": "date_selection",
  "recommendation": {
    "best_date": "2026-05-01",
    "rank": 1,
    "confidence": 0.90,
    "reason": "庚辰日是最适合开市开张的日期。首先，日干庚金与命主年干庚金完全同字同气，这在择日学中称为'本气日'，代表当日的能量与命主本气完全契合，开业后能够顺利承接命主的财运。其次，辰土为庚金之印，印星代表店铺、根基、靠山，辰日开市意味着店铺将有稳固的根基和依靠。第三，辰土生助庚金，比劫力量增强，有利于在商业竞争中获得优势。庚金得辰土之生，展现出刚毅果决的商业魄力。",
    "matching_aspects": [
      "日干庚金与命主年干同气，本气相投",
      "辰土为庚金之印，代表店铺根基稳固",
      "比劫旺盛利于商业竞争"
    ],
    "potential_concerns": [
      "辰土泄火，财星能量需靠后天调理"
    ],
    "mitigation_suggestions": [
      "店铺装饰以金色、白色为主，增强金气",
      "收银台摆放金元宝或金属摆件生财"
    ]
  },
  "alternative_options": [
    {
      "date": "2026-05-03",
      "rank": 2,
      "reason": "壬午日日干壬水与命宫天干壬水同气，命宫能量充沛。午火为庚金之财，财星当旺，利于财运收入。但壬水克庚金有轻微克伐，需注意开业初期可能有小波折。",
      "when_to_use": "如果需要旺财而不在乎初期小波折可选此日"
    }
  ],
  "date_analysis": {
    "2026-05-01": {
      "strengths": ["本气日", "印星稳固根基", "比劫利竞争"],
      "weaknesses": ["辰土泄火，财星稍弱"],
      "event_suitability": "非常适合开市开张，根基稳固利于长久经营",
      "energy_direction": "土生金-利于根基稳固、长期发展"
    }
  },
  "overall_guidance": "推荐2026年5月1日（庚辰日）作为开市开张的最佳日期。该日本气相投、印星稳固，是商业经营的上佳之选。"
}
```"""

def build_date_selection_user_prompt(
    chart: Dict[str, Any],
    date_type: str,
    daily_options: List[Dict[str, Any]],
    question: Optional[str] = None
) -> str:
    """
    构建择日分析的用户提示词

    Args:
        chart: 命盘数据
        date_type: 事件类型（如"结婚嫁娶"、"开市开张"等）
        daily_options: 候选日期列表，每个包含score、tiangan等字段
        question: 可选的特定问题

    Returns:
        格式化的用户提示词
    """
    # 提取命主基本信息
    birth_info = chart.get("birth_info", {})
    birth_year_gan = birth_info.get("tiangan", "甲")
    if birth_year_gan and len(birth_year_gan) > 0:
        birth_year_gan = birth_year_gan[0]

    # 获取命宫天干
    palaces = chart.get("palaces", {})
    minggong = palaces.get("命宫", {})
    minggong_gan = minggong.get("tiangan", "甲")
    if minggong_gan and len(minggong_gan) > 0:
        minggong_gan = minggong_gan[0]

    # 事件类型对应的关键宫位
    event_palace_mapping = {
        "结婚嫁娶": ["夫妻宫", "迁移宫", "福德宫"],
        "开市开张": ["财帛宫", "官禄宫", "田宅宫"],
        "动土破土": ["田宅宫", "疾厄宫", "父母宫"],
        "出行远行": ["迁移宫", "命宫"],
        "签约谈判": ["官禄宫", "财帛宫", "交友宫"],
        "搬家入宅": ["田宅宫", "命宫", "福德宫"],
        "订婚相亲": ["夫妻宫", "迁移宫"],
    }
    target_palaces = event_palace_mapping.get(date_type, ["命宫", "财帛宫"])

    # 构建提示词
    prompt_lines = [
        f"# 择日分析请求",
        "",
        f"## 事件类型",
        f"{date_type}",
        "",
        f"## 命主基本信息",
        f"- 出生年干（五行）：{birth_year_gan}",
        f"- 命宫天干：{minggong_gan}",
        f"- 关键宫位：{', '.join(target_palaces)}",
        "",
        f"## 候选日期列表",
        "",
    ]

    # 添加每个候选日期
    for i, opt in enumerate(daily_options, 1):
        solar_date = opt.get("solar_date", "")
        lunar_date = opt.get("lunar_date", "")
        tiangan = opt.get("tiangan", "")
        dizhi = opt.get("dizhi", "")
        score = opt.get("score", 0)
        level = opt.get("level", "")
        suitable_for = opt.get("suitable_for", [])
        avoid = opt.get("avoid", [])
        key_factors = opt.get("key_factors", [])
        best_time = opt.get("best_time_window", "")
        warnings = opt.get("warnings", [])

        prompt_lines.append(f"### 候选 {i}: {solar_date}")
        prompt_lines.append(f"- 农历：{lunar_date}")
        prompt_lines.append(f"- 日柱：{tiangan}（{tiangan[0]}天干，{tiangan[1]}地支）")
        prompt_lines.append(f"- 综合评分：{score:.1f}分（{level}）")
        if best_time:
            prompt_lines.append(f"- 最佳时段：{best_time}")
        if suitable_for:
            prompt_lines.append(f"- 宜：{', '.join(suitable_for[:3])}")
        if avoid:
            prompt_lines.append(f"- 忌：{', '.join(avoid[:2])}")
        if key_factors:
            prompt_lines.append(f"- 关键因素：{'; '.join(key_factors[:2])}")
        if warnings:
            prompt_lines.append(f"- 警示：{', '.join(warnings)}")
        prompt_lines.append("")

    # 添加具体问题
    if question:
        prompt_lines.extend([
            "",
            f"## 用户具体问题",
            f"{question}",
            "",
        ])

    # 添加分析要求
    prompt_lines.extend([
        "",
        "## 分析要求",
        "",
        "请根据上述信息，回答以下问题：",
        "",
        "1. 哪个日期最适合进行【" + date_type + "】？请给出明确推荐",
        f"2. 该日期与命主的{birth_year_gan}年干和命宫天干{minggong_gan}有什么配合？",
        "3. 该日期的能量方向是什么（旺财/旺感情/旺事业等）？",
        "4. 有哪些需要注意的问题？如何化解？",
        "5. 备选日期有哪些？在什么情况下可以使用？",
        "",
        "请以JSON格式返回分析结果。",
    ])

    return "\n".join(prompt_lines)