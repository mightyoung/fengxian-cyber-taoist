"""
紫微斗数运势报告生成提示词模块

为FengxianCyberTaoist紫微斗数运势报告的每个章节提供LLM提示词：
1. 命盘概览章节
2. 四化详解章节
3. 年度运势分析章节
4. 性格画像章节
5. 实用指南章节
6. 每月宜忌章节
7. 核心提醒章节

真实规则计算结果作为素材上下文，提供few-shot示例辅助生成
"""

from typing import Dict, Any, List
import json


# ============ 系统提示词 ============

REPORT_SYSTEM_PROMPT = """你是一位精通紫微斗数的命理大师，拥有30年实战经验。

## 核心能力
- 准确解读命盘四化配置与运势关系
- 结合因果链推理、案例匹配、Agent共识进行综合分析
- 生成专业、个性化、有深度的运势报告
- 用通俗易懂的语言解释复杂的命理知识

## 质量标准
1. **个性化**：每份报告必须根据用户的真实命盘数据生成，不可套用模板
2. **具体性**：必须给出具体的运势描述和建议，不可含糊其辞
3. **逻辑性**：必须基于命盘数据和四化理论进行推理，不可凭空臆测
4. **实用性**：建议必须具体可执行，不可泛泛而谈

## 禁止事项
- 禁止使用"可能"、"也许"、"大概"等模糊词汇
- 禁止生成占位符内容如"N/A"、"待分析"
- 禁止在不同用户间使用相同的套话
- 禁止生成与命盘数据不符的内容

## 输出风格
- 语言风格：专业但亲切，像一位和蔼的老先生
- 内容深度：深入分析，不止于表面
- 表达方式：用比喻和故事来解释命理
"""


# ============ 命盘概览章节提示词 ============

def build_overview_prompt(
    chart_data: Dict[str, Any],
    analysis_result: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    构建命盘概览章节的提示词

    Args:
        chart_data: 命盘数据
        analysis_result: 分析结果

    Returns:
        消息列表
    """
    # 提取命盘基本信息
    birth_info = chart_data.get("birth_info", {})
    palaces = chart_data.get("palaces", {})
    transforms = chart_data.get("transforms", [])

    # 命宫信息
    ming_gong = palaces.get("命宫", {})
    ming_gong_stars = ming_gong.get("stars", [])
    main_star = ming_gong_stars[0]["name"] if ming_gong_stars else "未知"

    # 四化配置
    transform_map = {}
    for t in transforms:
        transform_map[t["type"]] = {"star": t["star"], "palace": t["palace"]}

    # 构建素材上下文
    context = f"""
## 用户命盘素材

### 基本信息
- 姓名：{birth_info.get('name', '命主')}
- 性别：{birth_info.get('gender', '未知')}
- 出生年份：{birth_info.get('year', birth_info.get('birth_year', '未知'))}年
- 五行局：{birth_info.get('wuxing_ju', '未知')}
- 年干：{birth_info.get('year_gan', '未知')}

### 命宫信息
- 命宫主星：{main_star}
- 命宫星曜：{', '.join([s['name'] for s in ming_gong_stars]) if ming_gong_stars else '无主星'}

### 四化配置
{json.dumps(transform_map, ensure_ascii=False, indent=2)}

### 命宫星曜详情
"""

    for star in ming_gong_stars:
        context += f"- {star['name']}（{star.get('level', '未知')}）\n"

    context += f"""
### 综合判断结果
- 整体运势：{analysis_result.get('overall_judgment', '未知')}
- 置信度：{analysis_result.get('overall_confidence', 0) * 100:.1f}%
"""

    # 添加因果链推理结果
    if analysis_result.get("causal_chain_result"):
        causal = analysis_result["causal_chain_result"]
        context += f"""
### 因果链推理（权重40%）
- 严重等级：{causal.get('severity_level', '未知')}
- 关键因果链数量：{len(causal.get('key_chains', []))}条
"""

    # 添加多Agent共识结果
    if analysis_result.get("dimensions"):
        context += "\n### 分维度分析\n"
        for dim, result in analysis_result["dimensions"].items():
            context += f"- {dim}：{result.get('judgment', '未知')}（置信度{result.get('confidence', 0)*100:.0f}%)\n"

    messages = [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请根据以下命盘素材，生成"命盘概览"章节的内容。

{context}

## 输出要求

请生成JSON格式的命盘概览，包含以下内容：

```json
{{
  "section_title": "一、命盘概览",
  "basic_info": {{
    "name": "命主姓名",
    "birth_year": "出生年份",
    "ming_ge": "命格特征（如：丙子命）",
    "ming_gong_star": "命宫主星",
    "sihua_pattern": "四化格局描述"
  }},
  "sihua_config": [
    {{
      "sihua": "化禄",
      "star": "星曜名",
      "palace": "所在宫位",
      "energy": "能量属性"
    }}
  ],
  "overall_judgment": "综合判断描述",
  "judgment_description": "运势特点描述（为什么会有这样的判断，要结合四化配置和因果链推理）"
}}
```

## 注意事项
1. 命格特征格式：年干+年支+命，如"丙子命"
2. 四化格局描述：如"禄权科忌全配置"、"禄忌同宫"等
3. 综合判断描述要结合用户的具体四化配置，不要套用通用模板
4. 判断描述要具体说明为什么得出这个结论
"""}
    ]

    return messages


# ============ 四化详解章节提示词 ============

def build_transform_detail_prompt(
    chart_data: Dict[str, Any],
    analysis_result: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    构建四化详解章节的提示词
    """
    palaces = chart_data.get("palaces", {})
    transforms = chart_data.get("transforms", [])

    # 按宫位整理四化
    palace_transforms = {}
    for t in transforms:
        palace = t["palace"]
        if palace not in palace_transforms:
            palace_transforms[palace] = []
        palace_transforms[palace].append(t)

    # 获取各宫位的详细星曜信息
    palace_details = {}
    for palace_name in palace_transforms.keys():
        palace_data = palaces.get(palace_name, {})
        palace_stars = palace_data.get("stars", [])
        palace_details[palace_name] = {
            "branch": palace_data.get("branch", ""),
            "tiangan": palace_data.get("tiangan", ""),
            "stars": [
                {"name": s["name"], "type": s.get("type", ""), "level": s.get("level", "")}
                for s in palace_stars
            ]
        }

    context = f"""
## 用户命盘四化素材

### 四化星曜配置
{json.dumps(transforms, ensure_ascii=False, indent=2)}

### 四化落宫详情
{json.dumps(palace_details, ensure_ascii=False, indent=2)}

### 相关分析结果
"""

    # 添加因果链推理中的四化分析
    if analysis_result.get("causal_chain_result"):
        causal = analysis_result["causal_chain_result"]
        explanation = causal.get("explanation", "")
        # 提取与四化相关的内容
        if "禄" in explanation or "忌" in explanation:
            context += f"\n### 因果链推理分析（重要！）\n{explanation[:2000]}\n"

    messages = [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请根据以下命盘四化素材，生成"四化详解"章节的内容。

{context}

## 输出要求

请生成JSON格式的四化详解，包含以下内容：

```json
{{
  "section_title": "二、四化详解",
  "transforms": [
    {{
      "title": "2.X 化禄/化权/化科/化忌 — [星曜名] 在 [宫位名]",
      "xingyao_analysis": "星曜解析：该星曜的基本含义和特性",
      "sihua_analysis": "四化解析：该化曜代表的意义和能量",
      "palace_context": "宫位解读：该星曜落入此宫位的具体影响",
      "synthesis": "综合解读，包含：运势特征、具体表现、把握建议"
    }}
  ]
}}
```

## 注意事项
1. 每个化曜都必须有独立的详细分析
2. 必须结合宫位中的其他星曜来综合分析
3. 如果同一星曜同时化禄和化忌（如天同），必须分别说明其双化的独特含义
4. 综合解读要具体说明：
   - 运势特征：命主在这一年会遇到什么
   - 具体表现：可能会有什么具体事件或感受
   - 把握建议：如何趋吉避凶
5. 语言要生动，像老先生讲故事一样

## Few-Shot示例

**示例1：化禄在命宫**
输入：化禄天同在命宫，天同本身也化忌
输出：
```json
{{
  "title": "2.1 化禄 — 天同 在命宫",
  "xingyao_analysis": "天同是紫微斗数中最具福气的星曜，被称为「福星」。它代表温和、享乐、知足常乐的性格特点。天同坐命的人，通常性格温和乐观，不喜欢与人争斗，更愿意享受生活中的小确幸。",
  "sihua_analysis": "化禄代表星的能量往好的方向发展，带来机会和收获。就像春天播种，秋天才有收获，化禄就是那颗让种子发芽的春雨。对于天同来说，化禄增强了其福气特质，让命主更容易获得好运和意外收获。",
  "palace_context": "天同化禄落入命宫，这是非常吉利的配置。命宫代表命主本人，命宫有化禄意味着命主本人运势旺盛，容易得到他人的帮助和赏识，财运和事业都有上升的趋势。同时，由于天同也化忌，这种双化配置代表福祸相依——机遇与挑战并存，需要在顺境中保持清醒。",
  "synthesis": {{
    "fortune_feature": "运气好！本人方面有意外收获的机会",
    "specific_manifestations": [
      "财运明显变好，可能有加薪、奖金，或投资收益",
      "人际关系顺畅，容易得到贵人的帮助",
      "心情愉悦，对生活充满热情"
    ],
    "advice": "机会来临时要把握，但不要贪心。见好就收才是上策。"
  }}
}}
```
"""}
    ]

    return messages


# ============ 年度运势分析章节提示词 ============

def build_yearly_fortune_prompt(
    chart_data: Dict[str, Any],
    analysis_result: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    构建年度运势分析章节的提示词
    """
    context = f"""
## 用户年度运势素材

### 综合判断
- 整体运势：{analysis_result.get('overall_judgment', '未知')}
- 置信度：{analysis_result.get('overall_confidence', 0) * 100:.1f}%

### 分维度分析
"""

    if analysis_result.get("dimensions"):
        for dim, result in analysis_result["dimensions"].items():
            context += f"""
#### {dim}
- 判断：{result.get('judgment', '未知')}
- 置信度：{result.get('confidence', 0) * 100:.1f}%
- 推理：{result.get('reasoning', '暂无')}
"""

    # 添加月度数据
    if analysis_result.get("monthly_data"):
        context += "\n### 月度运势数据\n"
        for month in analysis_result["monthly_data"]:
            context += f"- {month.get('month', '')}：{month.get('fortune', '')}（{month.get('tip', '')}）\n"

    # 添加因果链中的关键月份信息
    if analysis_result.get("causal_chain_result"):
        causal = analysis_result["causal_chain_result"]
        context += f"""
### 因果链推理严重等级：{causal.get('severity_level', '未知')}
"""

    messages = [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请根据以下运势素材，生成"年度运势分析"章节的内容。

{context}

## 输出要求

请生成JSON格式的年度运势分析，包含以下内容：

```json
{{
  "section_title": "三、年度运势分析",
  "five_dimension_scores": [
    {{
      "dimension": "事业",
      "score": 85,
      "judgment": "吉/平/凶",
      "interpretation": "运势解读，要结合命盘数据具体分析"
    }}
  ],
  "monthly_trends": [
    {{
      "month": "1月",
      "fortune": "上升/平稳/下降",
      "tip": "具体行动建议"
    }}
  ],
  "key_months": {{
    "peak_months": ["高峰月1", "高峰月2"],
    "peak_description": "高峰期运势描述，为什么这些月份运势好",
    "challenging_months": ["挑战月"],
    "challenge_description": "挑战月运势描述，为什么这些月份需要特别注意"
  }}
}}
```

## 注意事项
1. 五维评分要合理（60-95分），并说明为什么得这个分数
2. 月度运势走势要体现波动态势，不能全是"平稳"
3. 关键月份分析要具体说明为什么这些月份特殊
4. 要结合命盘中的四化配置和因果链推理来预测月度运势
"""}
    ]

    return messages


# ============ 性格画像章节提示词 ============

def build_personality_prompt(
    chart_data: Dict[str, Any],
    analysis_result: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    构建性格画像章节的提示词
    """
    palaces = chart_data.get("palaces", {})
    ming_gong = palaces.get("命宫", {})
    ming_gong_stars = ming_gong.get("stars", [])

    # 提取正曜、辅星、煞星
    main_stars = [s for s in ming_gong_stars if s.get("type") == "正曜"]
    assistant_stars = [s for s in ming_gong_stars if s.get("type") == "辅星"]
    evil_stars = [s for s in ming_gong_stars if s.get("type") == "煞星"]
    transform_stars = [s for s in ming_gong_stars if s.get("type") == "化曜"]

    context = f"""
## 用户性格分析素材

### 命宫星曜配置
- 主星：{', '.join([f"{s['name']}（{s.get('level', '')}）" for s in main_stars]) if main_stars else '无主星'}
- 辅星：{', '.join([f"{s['name']}（{s.get('level', '')}）" for s in assistant_stars]) if assistant_stars else '无辅星'}
- 煞星：{', '.join([f"{s['name']}（{s.get('level', '')}）" for s in evil_stars]) if evil_stars else '无煞星'}
- 化曜：{', '.join([f"{s['name']}（{s.get('level', '')}）" for s in transform_stars]) if transform_stars else '无化曜'}

### 各宫位星曜汇总
"""

    # 获取所有主星
    all_main_stars = chart_data.get("stars", {}).get("main_stars", [])
    for star in all_main_stars:
        context += f"- {star['name']}在{star.get('palace', '')}（{star.get('level', '')}）\n"

    messages = [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请根据以下命盘素材，生成"性格画像"章节的内容。

{context}

## 输出要求

请生成JSON格式的性格画像，包含以下内容：

```json
{{
  "section_title": "四、性格画像",
  "star_traits": [
    {{
      "star_name": "星曜名",
      "traits_analysis": "该星曜的性格特质分析",
      "positive_traits": ["正面特质1", "正面特质2"],
      "negative_traits": ["负面特质1", "负面特质2"]
    }}
  ],
  "personality_summary": "综合性格描述，200字左右",
  "optimization_suggestions": [
    {{
      "aspect": "优势发挥",
      "suggestion": "如何发挥性格优势的建议"
    }},
    {{
      "aspect": "短板改进",
      "suggestion": "如何改进性格短板的建议"
    }}
  ]
}}
```

## 注意事项
1. 要分析所有命宫正曜的性格特质
2. 正面和负面特质都要客观分析
3. 性格描述要具体，不使用套话
4. 优化建议要可操作，不是泛泛而谈
"""}
    ]

    return messages


# ============ 实用指南章节提示词 ============

def build_practical_guide_prompt(
    chart_data: Dict[str, Any],
    analysis_result: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    构建实用指南章节的提示词
    """
    context = f"""
## 用户实用指南素材

### 综合运势
- 整体运势：{analysis_result.get('overall_judgment', '未知')}

### 分维度分析
"""

    if analysis_result.get("dimensions"):
        for dim, result in analysis_result["dimensions"].items():
            context += f"- {dim}：{result.get('judgment', '未知')} - {result.get('reasoning', '')[:100]}\n"

    # 添加趋避建议
    if analysis_result.get("suggestions"):
        context += "\n### 趋避建议\n"
        for s in analysis_result["suggestions"]:
            context += f"- {s}\n"

    # 添加四化配置
    transforms = chart_data.get("transforms", [])
    transform_summary = [f"{t['type']}({t['star']}在{t['palace']})" for t in transforms]
    context += f"\n### 四化配置\n{', '.join(transform_summary)}\n"

    messages = [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请根据以下命盘素材，生成"实用指南"章节的内容。

{context}

## 输出要求

请生成JSON格式的实用指南，包含以下内容：

```json
{{
  "section_title": "五、实用指南",
  "career_guide": {{
    "title": "5.1 事业/学业方面",
    "suggestions": [
      {{
        "title": "建议标题",
        "content": "具体建议内容，要说明为什么这样做"
      }}
    ]
  }},
  "wealth_guide": {{
    "title": "5.2 财运方面",
    "suggestions": [...]
  }},
  "relationship_guide": {{
    "title": "5.3 感情/人际方面",
    "suggestions": [...]
  }},
  "health_guide": {{
    "title": "5.4 健康方面",
    "suggestions": [...]
  }}
}}
```

## 注意事项
1. 每个维度的建议要结合命盘特点，不是通用套话
2. 建议要具体说明"做什么"和"为什么"
3. 要根据四化配置给出针对性的趋避建议
4. 财运建议要区分正财和偏财
5. 健康建议要结合命盘中的疾厄宫信息
"""}
    ]

    return messages


# ============ 每月宜忌章节提示词 ============

def build_monthly_advice_prompt(
    chart_data: Dict[str, Any],
    analysis_result: Dict[str, Any],
    target_year: int
) -> List[Dict[str, str]]:
    """
    构建每月宜忌章节的提示词
    """
    context = f"""
## 用户每月宜忌素材

### 预测年份
{target_year}年

### 年度运势判断
- 整体运势：{analysis_result.get('overall_judgment', '未知')}

### 月度运势走势
"""

    if analysis_result.get("monthly_data"):
        for month in analysis_result["monthly_data"]:
            context += f"- {month.get('month', '')}：{month.get('fortune', '')}，{month.get('tip', '')}\n"

    # 添加四化配置
    transforms = chart_data.get("transforms", [])
    transform_summary = {t["type"]: {"star": t["star"], "palace": t["palace"]} for t in transforms}

    context += f"""
### 四化配置（影响每月运势）
- 化禄：{transform_summary.get('化禄', {}).get('star', '')}在{transform_summary.get('化禄', {}).get('palace', '')}
- 化权：{transform_summary.get('化权', {}).get('star', '')}在{transform_summary.get('化权', {}).get('palace', '')}
- 化科：{transform_summary.get('化科', {}).get('star', '')}在{transform_summary.get('化科', {}).get('palace', '')}
- 化忌：{transform_summary.get('化忌', {}).get('star', '')}在{transform_summary.get('化忌', {}).get('palace', '')}
"""

    messages = [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请根据以下命盘素材，生成"每月宜忌"章节的内容。

{context}

## 输出要求

请生成JSON格式的每月宜忌，必须包含12个月的内容：

```json
{{
  "section_title": "六、每月宜忌",
  "months": [
    {{
      "month": "6.1 1月宜忌",
      "fortune_level": "平稳/上升/下降",
      "yi": ["宜做事项1", "宜做事项2"],
      "ji": ["忌做事项1", "忌做事项2"],
      "analysis": "该月运势分析，说明宜忌原因"
    }}
  ]
}}
```

## 注意事项
1. 必须生成全部12个月的宜忌
2. 宜忌内容要结合月度运势走势，不是通用模板
3. 要考虑高峰期和调整月的特殊性（根据实际分析确定哪些月份）
4. 每月宜忌要有3-5条，不要太少
5. 分析部分要说明为什么要这样做
"""}
    ]

    return messages


# ============ 核心提醒章节提示词 ============

def build_key_reminder_prompt(
    chart_data: Dict[str, Any],
    analysis_result: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    构建核心提醒章节的提示词
    """
    context = f"""
## 用户核心提醒素材

### 综合判断
- 整体运势：{analysis_result.get('overall_judgment', '未知')}
- 置信度：{analysis_result.get('overall_confidence', 0) * 100:.1f}%

### 因果链推理（重要！）
"""

    if analysis_result.get("causal_chain_result"):
        causal = analysis_result["causal_chain_result"]
        context += f"""
- 严重等级：{causal.get('severity_level', '未知')}
- 因果链类型：{causal.get('chain_type', '未知')}
- 关键链数量：{len(causal.get('key_chains', []))}条
"""

    # 添加分维度判断
    if analysis_result.get("dimensions"):
        context += "\n### 分维度判断\n"
        for dim, result in analysis_result["dimensions"].items():
            context += f"- {dim}：{result.get('judgment', '未知')}\n"

    # 添加趋避建议
    if analysis_result.get("suggestions"):
        context += "\n### 趋避建议\n"
        for s in analysis_result["suggestions"][:5]:
            context += f"- {s}\n"

    # 添加四化总结
    transforms = chart_data.get("transforms", [])
    transform_summary = [f"{t['type']}({t['star']}在{t['palace']})" for t in transforms]
    context += f"\n### 四化配置\n{', '.join(transform_summary)}\n"

    messages = [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请根据以下命盘素材，生成"核心提醒"章节的内容。

{context}

## 输出要求

请生成JSON格式的核心提醒，包含以下内容：

```json
{{
  "section_title": "七、核心提醒",
  "overall_theme": "年度运势主题，如：平——关键在于把握好度",
  "key_action_suggestions": [
    {{
      "category": "事业/财运/感情/健康",
      "suggestion": "具体行动建议，要说明原因和预期效果"
    }}
  ],
  "special_reminders": {{
    "advantage_months": {{
      "months": ["高峰月1", "高峰月2"],
      "description": "高峰期应该如何把握"
    }},
    "challenge_months": {{
      "months": ["挑战月"],
      "description": "挑战月应该如何应对"
    }},
    "balance_months": {{
      "description": "其他月份应该如何度过"
    }}
  }}
}}
```

## 注意事项
1. 核心提醒要精准、简洁、有力
2. 行动建议要具体可执行
3. 特别提醒要区分高峰期、挑战月、平衡月
4. 要基于因果链推理给出针对性的提醒
"""}
    ]

    return messages


def build_causal_chain_prompt(
    chart_data: Dict[str, Any],
    analysis_result: Dict[str, Any],
    target_year: int = 2026
) -> List[Dict[str, str]]:
    """构建因果链分析的提示词"""

    # 构建因果链上下文
    causal = analysis_result.get("causal_chain_result", {})
    if isinstance(causal, dict):
        causal_data = causal
    else:
        causal_data = causal.to_dict() if hasattr(causal, 'to_dict') else {}

    # 获取四化信息
    transforms = chart_data.get("transforms", [])
    transform_summary = []
    for t in transforms:
        transform_summary.append(f"- {t['type']}({t['star']}在{t['palace']})")

    # 获取因果链关键信息
    severity_level = causal_data.get('severity_level', '未知')
    chain_type = causal_data.get('chain_type', '未知')
    explanation = causal_data.get('explanation', '无详细分析')

    # 获取关键因果链
    key_chains = causal_data.get('key_chains', [])
    key_chains_summary = []
    for chain in key_chains[:5]:  # 只取前5条
        if isinstance(chain, dict):
            key_chains_summary.append(f"- {chain.get('type', '')}: {chain.get('description', chain.get('chain', ''))}")
        else:
            key_chains_summary.append(f"- {chain}")

    context = f"""
### 命主基本信息
- 姓名：{chart_data.get('birth_info', {}).get('name', '未知')}
- 出生年干：{chart_data.get('birth_info', {}).get('year_gan', '未知')}
- 五行局：{chart_data.get('birth_info', {}).get('wuxing_ju', '未知')}
- 命宫主星：{chart_data.get('birth_info', {}).get('ming_gong_stars', '未知')}

### 因果链分析结果
- 严重等级：{severity_level}
- 因果链类型：{chain_type}
- 关键链数量：{len(key_chains)}条

### 因果链详情
{explanation[:3000] if explanation else '无详细分析'}

### 四化配置
{chr(10).join(transform_summary) if transform_summary else '无'}
"""

    messages = [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请根据以下因果链分析素材，生成"因果链分析"章节的内容。

{context}

## 输出要求

请生成JSON格式的因果链分析章节，包含以下内容：

```json
{{
  "section_title": "三、因果链分析",
  "analysis_summary": "因果链分析的核心发现，用2-3句话概括",
  "severity_level": "严重等级：吉祥/潜在/条件/确定/重大（对应无忌/单忌/双忌/三忌/四忌+）",
  "severity_explanation": "对该严重等级的解读",
  "key_findings": [
    {{
      "chain_type": "因果链类型，如：忌转忌/禄忌同宫/禄忌对称",
      "description": "该因果链的具体描述",
      "impact": "该因果链对命主的影响",
      "suggestion": "应对建议"
    }}
  ],
  "overall_conclusion": "综合结论，用3-4句话总结因果链分析的整体含义"
}}
```

## 注意事项
1. 因果链分析要突出重点，不要面面俱到
2. 每条关键发现都要给出具体的应对建议
3. 综合结论要用通俗易懂的语言解释复杂的因果关系
4. 重点关注：忌转忌、禄忌同宫、禄忌对称等重大因果链
5. 注意关联命盘中的四化配置进行解读
"""}
    ]

    return messages


# ============ 主报告生成提示词 ============

def build_full_report_prompt(
    chart_data: Dict[str, Any],
    analysis_result: Dict[str, Any],
    target_year: int
) -> List[Dict[str, str]]:
    """
    构建完整报告生成的提示词（整合所有章节）
    """
    # 构建完整上下文
    context_parts = []

    # 1. 命盘数据
    birth_info = chart_data.get("birth_info", {})
    palaces = chart_data.get("palaces", {})
    transforms = chart_data.get("transforms", [])

    context_parts.append("## 一、命盘数据")
    context_parts.append(f"- 姓名：{birth_info.get('name', '命主')}")
    context_parts.append(f"- 性别：{birth_info.get('gender', '未知')}")
    context_parts.append(f"- 出生年份：{birth_info.get('year', birth_info.get('birth_year', '未知'))}年")
    context_parts.append(f"- 五行局：{birth_info.get('wuxing_ju', '未知')}")
    context_parts.append(f"- 年干：{birth_info.get('year_gan', '未知')}")

    # 命宫
    ming_gong = palaces.get("命宫", {})
    ming_gong_stars = ming_gong.get("stars", [])
    context_parts.append("\n### 命宫")
    context_parts.append(f"- 主星：{ming_gong_stars[0]['name'] if ming_gong_stars else '无主星'}")
    context_parts.append(f"- 全部星曜：{', '.join([s['name'] for s in ming_gong_stars])}")

    # 四化
    context_parts.append("\n### 四化配置")
    for t in transforms:
        context_parts.append(f"- {t['type']}：{t['star']}在{t['palace']}")

    # 2. 分析结果
    context_parts.append("\n## 二、分析结果")
    context_parts.append(f"- 整体运势：{analysis_result.get('overall_judgment', '未知')}")
    context_parts.append(f"- 置信度：{analysis_result.get('overall_confidence', 0) * 100:.1f}%")

    if analysis_result.get("dimensions"):
        context_parts.append("\n### 分维度")
        for dim, result in analysis_result["dimensions"].items():
            context_parts.append(f"- {dim}：{result.get('judgment', '未知')}（{result.get('confidence', 0)*100:.0f}%）")

    if analysis_result.get("causal_chain_result"):
        causal = analysis_result["causal_chain_result"]
        context_parts.append("\n### 因果链推理")
        context_parts.append(f"- 严重等级：{causal.get('severity_level', '未知')}")
        context_parts.append(f"- 因果链类型：{causal.get('chain_type', '未知')}")

    if analysis_result.get("suggestions"):
        context_parts.append("\n### 趋避建议")
        for s in analysis_result["suggestions"][:5]:
            context_parts.append(f"- {s}")

    context = "\n".join(context_parts)

    messages = [
        {"role": "system", "content": f"""{REPORT_SYSTEM_PROMPT}

## 报告格式要求

请生成完整的Markdown格式运势报告，包含以下8个章节：

1. **一、命盘概览** - 基本信息、四化配置、综合判断
2. **二、四化详解** - 每个化曜的详细分析
3. **三、年度运势分析** - 五维评分、月度走势、关键月份
4. **四、性格画像** - 星曜特质、性格分析、优化建议
5. **五、实用指南** - 事业、财运、感情、健康各维度建议
6. **六、每月宜忌** - 12个月的宜忌建议
7. **七、核心提醒** - 关键行动建议、特别提醒
8. **八、免责声明** - 系统声明

## 注意事项
1. 每份报告必须根据用户的真实命盘数据生成
2. 语言要专业但亲切，像老先生讲故事
3. 建议要具体可执行，不使用套话
4. 要体现因果链推理的结果
5. 月度运势要有波动态势，不是千篇一律
"""},
        {"role": "user", "content": f"""请根据以下命盘素材，生成{target_year}年的完整运势预测报告。

{context}

## 输出要求

直接输出Markdown格式的报告，不要使用JSON或其他格式。报告必须：
1. 包含上述8个章节的完整内容
2. 每个章节都要有实质性内容
3. 特别关注因果链推理的结果
4. 给出具体可执行的趋避建议
"""}
    ]

    return messages


# ============ 辅助函数 ============

def get_llm_temperature(section: str) -> float:
    """
    根据章节类型返回合适的LLM温度参数

    Args:
        section: 章节类型

    Returns:
        温度参数（0.0-1.0）
    """
    temperature_map = {
        "overview": 0.3,          # 命盘概览：偏低，创造性要求低
        "transform_detail": 0.4,  # 四化详解：中等偏下
        "yearly_fortune": 0.4,   # 年度运势：中等
        "personality": 0.5,       # 性格画像：中等偏上
        "practical_guide": 0.4, # 实用指南：中等
        "monthly_advice": 0.3,   # 每月宜忌：偏低
        "key_reminder": 0.5,     # 核心提醒：中等偏上
        "full_report": 0.5,     # 完整报告：中等
    }
    return temperature_map.get(section, 0.4)


def get_llm_max_tokens(section: str) -> int:
    """
    根据章节类型返回合适的最大token数

    Args:
        section: 章节类型

    Returns:
        最大token数
    """
    token_map = {
        "overview": 2048,          # 命盘概览
        "transform_detail": 4096,  # 四化详解
        "yearly_fortune": 3072,   # 年度运势
        "personality": 2048,      # 性格画像
        "practical_guide": 3072, # 实用指南
        "monthly_advice": 4096,   # 每月宜忌
        "key_reminder": 2048,     # 核心提醒
        "full_report": 8192,      # 完整报告
    }
    return token_map.get(section, 4096)
