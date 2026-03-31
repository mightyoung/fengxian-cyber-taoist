"""
因果链通俗化解说生成器 v2

将专业的因果链分析转化为通俗易懂、深入丰富的语言，
参考梁若瑜《飞星紫微斗数》理论。
"""

from typing import Dict, List, Any, Optional
from app.services.divination.utils.star_interpretations import (
    get_palace_meaning
)


# ============ 月度建议模板 ============

MONTHLY_ADVICE_TEMPLATES = {
    "1月": {
        "yi": ["新年开篇", "制定计划", "稳扎稳打", "整理思路"],
        "ji": ["冲动行事", "大幅投资", "轻信他人"],
        "finance": "年初宜保守理财，为全年打好基础，不宜冒进",
        "health": "注意防寒保暖，预防季节性疾病，早睡养精蓄锐"
    },
    "2月": {
        "yi": ["欢度春节", "走亲访友", "维系人脉", "总结过去"],
        "ji": ["过度应酬", "熬夜伤身", "口舌是非"],
        "finance": "春节期间开销较大，节后注意财务整理，量入为出",
        "health": "节日期间注意饮食节制，防范消化系统问题"
    },
    "3月": {
        "yi": ["万物复苏", "学习新知", "启动新计划", "调整节奏"],
        "ji": ["好高骛远", "犹豫不决", "错失良机"],
        "finance": "春季财运逐渐回暖，适合布局投资，但需谨慎选择",
        "health": "春季肝气旺盛，宜保持心情舒畅，预防过敏"
    },
    "4月": {
        "yi": ["把握机遇", "主动出击", "展示能力", "建立人设"],
        "ji": ["错失良机", "消极等待", "顾虑太多"],
        "finance": "四月财运上升期，适合开展新项目，但忌贪婪冒进",
        "health": "春季转换期注意呼吸道健康，适度运动增强体质"
    },
    "5月": {
        "yi": ["劳动创造", "踏实行动", "积累经验", "稳中求进"],
        "ji": ["投机取巧", "急功近利", "与人争执"],
        "finance": "五月财务上可能有波动，付出与收获需平衡看待",
        "health": "五月气候宜人，适合户外运动，注意预防中暑"
    },
    "6月": {
        "yi": ["半年总结", "调整方向", "巩固成果", "蓄势待发"],
        "ji": ["半途而废", "消极懈怠", "财务冒进"],
        "finance": "年中宜复盘财务状况，调整下半年理财策略",
        "health": "夏季来临，注意防暑降温，充足睡眠很重要"
    },
    "7月": {
        "yi": ["把握贵人", "拓展人脉", "展示才华", "主动担当"],
        "ji": ["招惹小人", "锋芒太露", "财务纠纷"],
        "finance": "七月贵人运强，合作机会增多，财务往来需谨慎",
        "health": "暑期注意防暑，多补充水分，心脑血管需关注"
    },
    "8月": {
        "yi": ["趁热打铁", "推进项目", "学习提升", "考证进修"],
        "ji": ["骄傲自满", "疏于人际", "忽略健康"],
        "finance": "八月事业运好，财运随之上升，但注意理财节奏",
        "health": "盛夏时节注意休息，避免过度劳累引发旧疾"
    },
    "9月": {
        "yi": ["收获季节", "感恩回报", "整理资产", "规划未来"],
        "ji": ["挥霍浪费", "盲目扩张", "感情波动"],
        "finance": "九月是收获时节，理财上宜稳不宜躁，见好就收",
        "health": "夏秋转换期注意润肺防燥，调整作息时间"
    },
    "10月": {
        "yi": ["长假休闲", "陪伴家人", "自我充电", "思考方向"],
        "ji": ["过度放纵", "放弃目标", "消极悲观"],
        "finance": "十一假期消费需控制，节后及时调整收支计划",
        "health": "秋季渐凉，注意添衣保暖，预防感冒流感"
    },
    "11月": {
        "yi": ["冲刺目标", "把握年末", "总结复盘", "提前布局"],
        "ji": ["虎头蛇尾", "犹豫拖延", "人际冲突"],
        "finance": "年末财运收尾阶段，稳健为主，不宜新增大额投资",
        "health": "冬季来临注意保暖，尤其是老人和体弱者"
    },
    "12月": {
        "yi": ["年度收官", "辞旧迎新", "感恩贵人", "规划新年"],
        "ji": ["透支体力", "财务冒险", "口舌是非"],
        "finance": "年终财务结算，盘点全年收支，为新一年做好预算",
        "health": "年末工作压力大，注意休息调养，迎接新一年"
    }
}


# ============ 扩展星曜详解 ============

STAR_DETAILED = {
    "天同": {
        "基础": "天同是紫微斗数中最具福气的星曜，被称为「福星」。它代表温和、享乐、知足常乐的性格。",
        "性格特点": "你是一个性格温和的人，不喜欢与人争斗，更愿意享受生活中的小确幸。你心态乐观，即使遇到挫折也能很快调整过来。",
        "优点": [
            "心态平和，不易被外界干扰",
            "善于享受生活，懂得平衡工作与休闲",
            "人缘好，相处起来让人感到舒服",
            "逆境中也能保持乐观"
        ],
        "需要注意": [
            "有时过于追求享乐，可能缺乏上进心",
            "遇到困难时可能选择逃避而非直面",
            "可能会被别人认为缺乏魄力"
        ],
        "人生启示": "天同星的特质告诉你：人生不必太较劲，有时候退一步反而能看得更清楚。但也要学会在关键时刻拿出勇气。"
    },
    "巨门": {
        "基础": "巨门是「口才星」，代表口才、表达、分析能力，也代表是非与挑剔。",
        "性格特点": "你是一个善于表达和分析的人，口才好，思路清晰，能言善辩。",
        "优点": [
            "口才出众，表达能力强",
            "思维敏锐，善于分析问题",
            "有洞察力，能看到别人看不到的细节",
            "学习能力强，知识面广"
        ],
        "需要注意": [
            "有时过于挑剔，容易得罪人",
            "可能爱掺和是非，卷入纷争",
            "过于追求完美，对自己和他人要求高",
            "有时说话太直，容易伤人"
        ],
        "人生启示": "巨门星提醒你：口才是天赋，但要用在对的地方。多说正面的话，少说伤人的话，你的分析能力可以成为很好的顾问或专家。"
    },
    "天梁": {
        "基础": "天梁是「荫星」和「寿星」，代表庇护、慈善、长寿、责任感和清贵的品格。",
        "性格特点": "你是一个有责任心的人，喜欢帮助他人，有长者风范，愿意为他人付出。",
        "优点": [
            "有责任心，靠谱可靠",
            "乐于助人，人缘好",
            "有领导才能，善于照顾团队",
            "思维成熟，看问题有远见"
        ],
        "需要注意": [
            "有时过于操心，爱管闲事",
            "容易承担过多责任，压垮自己",
            "过于严肃，可能让人有距离感",
            "有时过于坚持己见，不易妥协"
        ],
        "人生启示": "天梁星告诉你：你有很强的责任感和领导力，适合担任管理或服务他人的角色。但也要学会放手，不要什么都自己扛。"
    },
    "天机": {
        "基础": "天机是「智慧星」，代表智慧、思考、变动、机敏和创新。",
        "性格特点": "你是一个聪明机敏的人，喜欢思考，善于动脑筋，思维活跃，喜欢新鲜事物。",
        "优点": [
            "头脑聪明，学习能力强",
            "思维灵活，适应变化快",
            "善于创新，不墨守成规",
            "好奇心强，知识面广"
        ],
        "需要注意": [
            "有时想太多，优柔寡断",
            "变动太多，缺乏稳定性",
            "容易三分钟热度",
            "有时过于算计，缺乏果断"
        ],
        "人生启示": "天机星提醒你：你的智慧和机敏是很大的优势，但也要学会在关键时刻做出决定，不要总是犹疑不决。"
    },
    "太阴": {
        "基础": "太阴是「温柔星」和「暗财星」，代表温柔、细腻、内敛，也代表暗中藏财和女性缘。",
        "性格特点": "你是一个内心细腻、情感丰富的人，不善言辞但内心世界很精彩。",
        "优点": [
            "内心细腻，善于感知他人情绪",
            "思考深入，有深度",
            "财运暗藏，常有意外收入",
            "有艺术气质或文学天赋"
        ],
        "需要注意": [
            "有时过于消极悲观",
            "情绪波动大，容易想不开",
            "过于内向，不善表达真实想法",
            "可能过于敏感，容易受伤"
        ],
        "人生启示": "太阴星告诉你：你的细腻和内敛是天赋，要善用它们来发展艺术或创作。但也要学会表达自己，不要把情绪都藏在心里。"
    },
    "七杀": {
        "基础": "七杀是「冲锋星」，代表勇敢、果断、挑战、压力和爆发力。",
        "性格特点": "你是一个有冲劲、有魄力的人，敢于冲锋陷阵，不畏惧挑战。",
        "优点": [
            "敢于挑战，有勇气面对困难",
            "执行力强，说干就干",
            "抗压能力强，越挫越勇",
            "有开创精神，敢为天下先"
        ],
        "需要注意": [
            "有时过于冲动，不计后果",
            "压力过大时可能情绪失控",
            "过于刚强，不懂变通",
            "可能树敌较多"
        ],
        "人生启示": "七杀星提醒你：你的勇气和冲劲是成功的关键，但也要学会在关键时刻保持冷静，用智慧而非蛮力解决问题。"
    }
}


# ============ 四化深入解读 ============

TRANSFORM_DETAILED = {
    "化禄": {
        "生活比喻": "就像春天的种子发芽，充满生机和希望。你播下的种子开始生长了！",
        "核心含义": "机会和收获的能量流动",
        "具体表现": [
            "财运方面：可能有加薪、奖金、投资收益，或意外的财富机会",
            "事业方面：可能有晋升、合作机会，或工作上的突破",
            "感情方面：可能有新的缘分，或现有感情更进一步",
            "人际关系：可能遇到贵人相助，或得到他人的认可支持"
        ],
        "注意事项": [
            "机会来临时要把握，但不要贪心",
            "有收获时要懂得分享，好运会延续",
            "不要因为好运就放松警惕，谨慎行事"
        ],
        "心理准备": "以积极开放的心态迎接机会，但也要脚踏实地"
    },
    "化忌": {
        "生活比喻": "就像天气突然变化，需要撑伞或找地方躲避。这不是坏事，是在提醒你做好准备。",
        "核心含义": "挑战和考验的能量转化",
        "具体表现": [
            "财运方面：可能有破财、额外支出、投资亏损，或财务上的紧张",
            "事业方面：可能遇到阻碍、小人作祟、项目失败，或付出多收获少",
            "感情方面：可能有争吵、分离、误会，或感情上的挫折",
            "健康方面：可能出现小病痛，或身体亚健康状态"
        ],
        "应对策略": [
            "遇到问题不要硬碰，退一步海阔天空",
            "这是成长的考验，克服后会让你更强",
            "有时候花钱能解决的问题就花钱，不要心疼",
            "保持积极心态，危机也是转机"
        ],
        "心理准备": "以平常心面对挑战，记住这只是人生的一个阶段"
    },
    "化科": {
        "生活比喻": "就像在学习或考试中表现出色，得到老师的表扬和认可。",
        "核心含义": "声誉、学习、名声的流动",
        "具体表现": [
            "学业方面：可能有考试顺利、学习进步、得到老师认可",
            "事业方面：可能获得荣誉、嘉奖、或者得到专业认证",
            "名声方面：可能在某个领域小有名气，获得一定知名度",
            "人际关系：可能因为才华或品德得到他人赞赏"
        ],
        "把握建议": [
            "这是学习提升的好时机，适合考证书、学技能",
            "好名声要靠实力支撑，继续努力",
            "可以帮助他人，分享你的知识"
        ],
        "心理准备": "以谦逊的态度接受认可，继续学习和成长"
    },
    "化权": {
        "生活比喻": "就像从普通员工成长为团队负责人，有了更多的责任和话语权。",
        "核心含义": "权力、掌控、能力的增强",
        "具体表现": [
            "事业方面：可能有晋升机会，或者在工作中获得更多决策权",
            "能力方面：做事更有力度，说话更有分量，更能影响他人",
            "掌控感：对自己的人生或某个领域更有掌控感",
            "领导力：可能有带领团队或影响他人的机会"
        ],
        "注意事项": [
            "权力越大，责任越大，不要滥用权力",
            "不要太强势，学会倾听他人意见",
            "有话语权是好事，但也要给别人表达的机会"
        ],
        "心理准备": "以负责任的态度运用权力，成为更好的领导者"
    }
}


# ============ 因果链深入解读 ============

CAUSAL_CHAIN_DETAILED = {
    "忌转忌": {
        "比喻": "就像屋漏偏逢连夜雨，原本就有点问题，现在又雪上加霜。",
        "什么意思": "双重忌力叠加，在某个方面会有比较大的挑战或变故。",
        "具体场景": [
            "可能接连遇到不顺心的事，好像祸不单行",
            "可能在某个领域反复受挫",
            "可能有健康或财务上的连续压力"
        ],
        "应对方式": [
            "这时候最重要的是保持冷静，不要被情绪左右",
            "可以暂时放慢脚步，不要做重大决定",
            "寻求信任的人帮助，不要一个人硬扛",
            "记住，这通常是黎明前的黑暗"
        ],
        "转机提示": "这种配置往往是先苦后甜，扛过去就是晴天"
    },
    "禄忌同宫": {
        "比喻": "就像甜苦参半的药，有疗效但也有苦味。",
        "什么意思": "机遇与挑战并存，得失参半，需要谨慎把握。",
        "具体场景": [
            "有赚钱机会但也有破财风险",
            "有贵人帮助但也有小人作祟",
            "有进步空间但也需要付出代价"
        ],
        "把握原则": [
            "做事要稳，不要贪心冒进",
            "权衡利弊，三思而后行",
            "好的一面要感恩，不好的一面要警惕"
        ],
        "人生智慧": "这就是生活的真相，没有绝对的的好坏，关键在于你如何应对"
    },
    "追权": {
        "比喻": "就像在职场中努力晋升，从普通员工向管理层发展。",
        "什么意思": "代表对权力的追求或权力巩固，有进取心。",
        "具体场景": [
            "事业上有晋升或加薪的机会",
            "可能获得管理权限或决策权",
            "说话更有分量，能影响更多人"
        ],
        "正确态度": [
            "追求权力要走正道，用能力服人而非手段",
            "权力越大责任越大，要有为他人负责的觉悟",
            "不要为了权力失去本心"
        ],
        "提醒": "化权是能力的体现，但真正的领导力来自人格魅力"
    },
    "禄忌对称": {
        "比喻": "就像天平的两端，一边升起一边落下。",
        "什么意思": "阴阳对峙，两个相关方面一个变好一个变坏。",
        "具体场景": [
            "这宫有收获，那宫可能有损耗",
            "有时候顺利有时候波折",
            "需要权衡利弊做选择"
        ],
        "智慧应对": [
            "不要只看表面，要整体考量",
            "有时候失去也是另一种得到",
            "学会在不同阶段调整重心"
        ],
        "心态调整": "这是自然的平衡，接受它并顺势而为"
    },
    "本宫自化": {
        "比喻": "就像身体有自我调节功能，遇到小问题会自动修复。",
        "什么意思": "这个宫位有自我调节的能力，问题可能会自行化解。",
        "具体表现": [
            "问题可能会自行好转或淡化",
            "可能会有意想不到的转折",
            "运势会有自然的起落"
        ],
        "态度建议": [
            "顺其自然，不必过于担心",
            "给事情一些时间，让它自己发展",
            "保持积极心态，相信问题会解决"
        ],
        "启示": "有些事情不需要你干预，它会自己找到平衡"
    },
    "果报宫": {
        "比喻": "就像银行贷款，总有要还的一天。过去的因果在现在显现。",
        "什么意思": "这个宫位可能受到过去因果的影响。",
        "具体场景": [
            "可能与家宅祖产有纠葛",
            "可能在福气或精神方面有消耗",
            "可能需要偿还过去的某些'债务'"
        ],
        "正确认识": [
            "过去的因果无法改变，但可以影响现在",
            "多行善事，积德积福",
            "用积极的态度面对，转化为成长动力"
        ],
        "安慰": "因果不是宿命，而是提醒你要更加珍惜和努力"
    }
}


def generate_monthly_advice(
    four_hua: Dict[str, str],
    fortune_trend: str = "平稳",
    confidence: float = 75.0
) -> List[Dict[str, Any]]:
    """
    根据四化配置和运势趋势生成12个月度建议

    Args:
        four_hua: 四化配置，格式 {"命宫": "化禄", "夫妻宫": "化权", ...}
        fortune_trend: 运势趋势，"上升"、"平稳"或"波动"
        confidence: 置信度 0-100

    Returns:
        12个月的月度建议列表，每项包含月份宜忌、理财建议、健康提醒和运势评分
    """
    import random

    # 根据四化提取关键词
    has_huaye = any(v in ["化禄"] for v in four_hua.values())
    has_quanye = any(v in ["化忌"] for v in four_hua.values())
    has_xueye = any(v in ["化科"] for v in four_hua.values())
    has_quanxue = any(v in ["化权"] for v in four_hua.values())

    def _fortune_for_month(month_idx: int) -> tuple[float, str]:
        """计算某月的运势评分和标签"""
        # 运势趋势影响月度波动
        base = 3.0
        if fortune_trend == "上升":
            # 逐渐走高的趋势
            score = base + 0.3 * (month_idx / 11) + random.uniform(-0.3, 0.3)
            if has_huaye:
                score += 0.3
            if has_quanye:
                score -= 0.2
        elif fortune_trend == "波动":
            # 波浪形波动
            wave = 0.5 * abs((month_idx % 4) - 1.5)
            score = base + random.uniform(-wave, wave)
            if has_quanye:
                score -= 0.3
        else:  # 平稳
            score = base + random.uniform(-0.2, 0.3)
            if has_huaye:
                score += 0.2
            if has_quanxue:
                score += 0.15

        # 四化叠加微调
        if has_quanxue:
            score += 0.1  # 化权增强掌控感

        score = max(1.0, min(5.0, score))

        if score >= 4.0:
            label = "吉"
        elif score >= 2.5:
            label = "平"
        else:
            label = "凶"
        return round(score, 1), label

    def _adjust_yi_ji(month_str: str, month_idx: int) -> tuple[List[str], List[str]]:
        """根据四化配置调整宜忌列表"""
        template = MONTHLY_ADVICE_TEMPLATES.get(month_str, MONTHLY_ADVICE_TEMPLATES["1月"])
        yi_list = list(template["yi"])
        ji_list = list(template["ji"])

        # 根据四化添加个性化宜忌
        if has_huaye:
            if month_idx % 3 == 0:
                yi_list.append("把握禄运，积极行动")
            if "财" in str(four_hua):
                yi_list.append("财运加持，积极理财")

        if has_quanye:
            ji_list.append("谨慎行事，防范小人")
            if month_idx % 2 == 0:
                yi_list.append("以柔克刚，化解压力")

        if has_xueye:
            yi_list.append("学习提升，考取认证")
            if month_idx == 2 or month_idx == 8:  # 3月、9月学业佳
                yi_list.append("学业考试运佳，抓紧时机")

        if has_quanxue:
            yi_list.append("展现能力，争取机会")

        # 限制宜忌数量
        return yi_list[:5], ji_list[:4]

    def _adjust_finance(month_str: str, month_idx: int) -> str:
        """根据四化调整理财建议"""
        template = MONTHLY_ADVICE_TEMPLATES.get(month_str, MONTHLY_ADVICE_TEMPLATES["1月"])
        finance = template["finance"]

        if has_huaye and fortune_trend == "上升":
            finance = f"财运上升期，{finance}，可适当加大投资力度"
        elif has_quanye:
            finance = f"挑战月份，{finance}，建议预留应急资金"
        elif has_xueye:
            finance = f"学业/名声运佳，{finance}，可考虑知识付费或培训投资"

        return finance

    months = ["1月", "2月", "3月", "4月", "5月", "6月",
               "7月", "8月", "9月", "10月", "11月", "12月"]

    result = []
    for idx, month in enumerate(months):
        score, label = _fortune_for_month(idx)
        yi, ji = _adjust_yi_ji(month, idx)
        template = MONTHLY_ADVICE_TEMPLATES.get(month, MONTHLY_ADVICE_TEMPLATES["1月"])

        result.append({
            "month": month,
            "yi": yi,
            "ji": ji,
            "finance": _adjust_finance(month, idx),
            "health": template["health"],
            "fortune_score": score,
            "fortune_label": label
        })

    return result


def generate_markdown_monthly_advice(advice_list: List[Dict[str, Any]]) -> str:
    """将月度建议列表转换为 Markdown 格式"""
    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## 📅 2026年月度行动清单")
    lines.append("")

    for item in advice_list:
        lines.append(f"### {item['month']}  ({item['fortune_label']} · {item['fortune_score']}/5分)")
        lines.append("")

        yi_text = "、".join(item["yi"][:3])
        ji_text = "、".join(item["ji"][:2])
        lines.append(f"- **宜**: {yi_text}")
        lines.append(f"- **忌**: {ji_text}")
        lines.append(f"- **理财**: {item['finance']}")
        lines.append(f"- **健康**: {item['health']}")
        lines.append("")

    return "\n".join(lines)


def generate_plain_causal_chain_explanation_v2(
    chart_data: Dict[str, Any],
    causal_chain_result: Optional[Dict[str, Any]] = None
) -> str:
    """
    生成通俗版因果链解释 v2 - 更丰富深入
    """
    sections = []

    # ============ 第一步：四化入门 ============
    sections.append("## 🌟 入门课：什么是飞星四化？\n")
    sections.append("想象一下，天上的星星就像人一样，会'动'——它们的能量会流动变化。")
    sections.append("这种流动变化就叫做「四化」。\n")
    sections.append("---\n")
    sections.append("### 四化基础概念\n")
    sections.append("| 四化 | 生活比喻 | 核心含义 | 简单记忆 |")
    sections.append("|------|----------|----------|----------|")
    sections.append("| **化禄** | 种子发芽🌱 | 机会和收获 | 有好事来了 |")
    sections.append("| **化忌** | 天气变化🌧 | 挑战和考验 | 需要注意 |")
    sections.append("| **化科** | 花开有声🌸 | 声誉和进步 | 获得认可 |")
    sections.append("| **化权** | 小树成材🌳 | 权力和掌控 | 能力增强 |\n")
    sections.append("---\n")
    sections.append("**记住一个核心口诀：**")
    sections.append("> 禄是因，忌是果。化禄是机会，化忌是结果。\n")
    sections.append("> 禄转忌 = 得而复失；忌转忌 = 祸不单行。\n")

    # ============ 第二步：命盘四化详解 ============
    transforms = chart_data.get("transforms", [])
    chart_data.get("palaces", {})

    if transforms:
        sections.append("---\n")
        sections.append("## 🎯 你的命盘四化配置\n")
        sections.append("先来认识你命盘中最关键的四个星曜变化：\n")

        for t in transforms:
            star = t.get("star", "")
            transform = t.get("type", "")
            palace = t.get("palace", "")

            # 获取详细信息
            star_info = STAR_DETAILED.get(star, {})
            transform_info = TRANSFORM_DETAILED.get(transform, {})
            palace_info = get_palace_meaning(palace)

            sections.append(f"### ◆ {transform} {star} 在 {palace}\n")
            sections.append("─" * 30 + "\n")

            # 1. 星曜是什么
            sections.append(f"**【星曜解析】{star}是什么？**\n")
            sections.append(star_info.get("基础", ""))
            sections.append(f"\n{star_info.get('性格特点', '')}\n")

            # 2. 四化是什么
            sections.append(f"\n**【四化解析】{transform}代表什么？**\n")
            sections.append(f"💡 生活比喻：{transform_info.get('生活比喻', '')}\n")
            sections.append(f"📌 核心含义：{transform_info.get('核心含义', '')}\n")

            # 3. 综合解读
            sections.append(f"\n**【综合解读】这对{ palace_info.get('meaning', palace) }意味着什么？**\n")
            sections.append("")
            sections.append(_generate_combined_interpretation(star, transform, palace, star_info, transform_info))
            sections.append("")

    # ============ 第三步：因果链深入解读 ============
    if causal_chain_result and causal_chain_result.get("causal_chains"):
        sections.append("---\n")
        sections.append("## 🔮 因果链深入解读\n")
        sections.append("因果链是四化之间的'化学反应'，这里用生活中的场景来解释：\n")

        chains = causal_chain_result.get("causal_chains", [])
        chain_types_seen = {}

        for chain in chains[:6]:
            chain_type = chain.get("type", "")
            if chain_type in chain_types_seen:
                continue

            chain_detail = CAUSAL_CHAIN_DETAILED.get(chain_type, {})
            if not chain_detail:
                continue

            chain_types_seen[chain_type] = True

            sections.append(f"### ⚡ {chain_detail.get('比喻', chain_type)}\n")
            sections.append(f"**【什么意思】{chain_detail.get('什么意思', '')}**\n")
            sections.append("\n**【具体场景】这种情况下可能会发生：\n")
            for scene in chain_detail.get('具体场景', [])[:3]:
                sections.append(f"- {scene}")
            sections.append("\n**【如何应对】建议你这样做：\n")
            for strategy in chain_detail.get('应对方式', chain_detail.get('应对策略', chain_detail.get('把握原则', [])))[:3]:
                sections.append(f"- {strategy}")
            if chain_detail.get('转机提示') or chain_detail.get('启示') or chain_detail.get('安慰'):
                sections.append(f"\n💡 {chain_detail.get('转机提示', chain_detail.get('启示', chain_detail.get('安慰', '')))}")
            sections.append("")

    # ============ 第四步：四化联动总结 ============
    if transforms:
        sections.append("---\n")
        sections.append("## 📊 四化联动：看懂你的命运主线\n")
        sections.append("把四个四化联系起来，就像拼图一样，能看到你命运的全貌：\n")

        summary = _generate_transform_summary_v2(chart_data, transforms)
        sections.append(summary)

    # ============ 第五步：性格画像 ============
    if transforms:
        sections.append("\n---\n")
        sections.append("## 🧠 性格画像\n")
        sections.append(_generate_personality_profile(chart_data, transforms))

    # ============ 第六步：实用指南 ============
    sections.append("\n---\n")
    sections.append("## 💡 实用指南：2026年这样做\n")

    sections.append("### 🎯 事业/学业方面\n")
    sections.append("- 把握机会：遇到好机会不要犹豫，勇敢抓住\n")
    sections.append("- 展现能力：今年适合主动承担项目，展现你的实力\n")
    sections.append("- 持续学习：学业运好，适合学习新技能或考证书\n")

    sections.append("\n### 💰 财运方面\n")
    sections.append("- 稳健理财：不要盲目投资，稳健为主\n")
    sections.append("- 把握禄运：今年有财运机会，但要见好就收\n")
    sections.append("- 破财消灾：如果需要花钱解决问题，不要心疼\n")

    sections.append("\n### 💕 感情/人际方面\n")
    sections.append("- 用心经营：感情需要经营，多沟通少冷战\n")
    sections.append("- 广结善缘：多行善事，好名声会给你带来更多机会\n")
    sections.append("- 注意小人：遇到小人不要硬碰，以柔克刚\n")

    sections.append("\n### 🏃 健康方面\n")
    sections.append("- 身体是本钱：不要过度操劳，养成锻炼习惯\n")
    sections.append("- 心态平和：遇到挫折不要气馁，心态决定一切\n")

    sections.append("\n---\n")
    sections.append("## 📌 核心提醒\n")
    sections.append("> **你的命运主打「稳中求进」——有福气但也有考验，关键是把握好度。**\n")
    sections.append("> 遇到困难不要怕，这是成长的必经之路；遇到好运不要飘，这是积累的时机。\n")
    sections.append("> 记住：命理是参考，你才是主角。保持积极心态，好运自然来！\n")

    # ============ 第七步：月度行动清单 ============
    # 提取四化配置
    four_hua = {}
    if transforms:
        for t in transforms:
            palace = t.get("palace", "")
            transform_type = t.get("type", "")
            if palace and transform_type:
                four_hua[palace] = transform_type

    # 判断运势趋势
    lu_count = sum(1 for t in transforms if t.get("type") == "化禄")
    ji_count = sum(1 for t in transforms if t.get("type") == "化忌")
    if lu_count > ji_count:
        fortune_trend = "上升"
    elif ji_count > lu_count:
        fortune_trend = "波动"
    else:
        fortune_trend = "平稳"

    # 生成月度建议
    monthly_advice = generate_monthly_advice(four_hua, fortune_trend, 75.0)
    monthly_md = generate_markdown_monthly_advice(monthly_advice)
    sections.append(monthly_md)

    return "\n".join(sections)


def _generate_combined_interpretation(
    star: str,
    transform: str,
    palace: str,
    star_info: dict,
    transform_info: dict
) -> str:
    """生成星曜+四化的综合解读"""
    interpretations = []

    palace_meaning = get_palace_meaning(palace).get("meaning", palace)

    # 化禄的综合解读
    if transform == "化禄":
        interpretations.append(f"✅ **运气好！** {palace_meaning}方面有意外收获的机会。")
        if star in ["天同", "天府", "禄存"]:
            interpretations.append("   具体表现：财运明显变好，可能有加薪、奖金、投资收益，或意外的小财。")
        elif star in ["太阳", "紫微"]:
            interpretations.append("   具体表现：人缘变好，容易得到贵人相助或上级赏识。")
        elif star in ["贪狼"]:
            interpretations.append("   具体表现：社交运旺，可能遇到有趣的人脉或合作机会。")
        elif star in ["太阴"]:
            interpretations.append("   具体表现：可能有暗财或额外的收入来源，不易发现但确实存在。")
        elif star in ["天机"]:
            interpretations.append("   具体表现：可能有新的想法或机会出现，适合开始新项目或学习新技能。")
        else:
            interpretations.append("   具体表现：心想事成，机会多多。")
        interpretations.append("\n💡 **把握建议**：" + transform_info.get('注意事项', [''])[0] if transform_info.get('注意事项') else "")

    # 化忌的综合解读
    elif transform == "化忌":
        interpretations.append(f"⚠️ **需要谨慎！** {palace_meaning}方面可能会遇到一些挑战。")
        if star in ["天机", "太阴"]:
            interpretations.append("   具体表现：容易想太多、担心，要学会放宽心，别钻牛角尖。遇到事情多和信任的人聊聊。")
        elif star in ["太阳", "天梁"]:
            interpretations.append("   具体表现：可能与长辈或权威人士有些摩擦，沟通时注意方式方法。")
        elif star in ["贪狼", "廉贞"]:
            interpretations.append("   具体表现：感情上可能有波折，要注意处理感情问题的方式，不要冲动。")
        elif star in ["天同"]:
            interpretations.append("   具体表现：可能有小人作祟或付出多收获少的情况，但不要灰心，这是成长。")
        else:
            interpretations.append("   具体表现：遇到问题不要硬碰，退一步海阔天空。")
        interpretations.append("\n💪 **应对提示**：" + (transform_info.get('应对策略', [''])[0] if transform_info.get('应对策略') else "这是成长的考验，克服后会让你更强。"))

    # 化科的 종합解读
    elif transform == "化科":
        interpretations.append(f"🌟 **名声提升！** {palace_meaning}方面容易获得认可。")
        if star in ["天梁", "天同"]:
            interpretations.append("   具体表现：健康意识增强，适合开始养生或锻炼计划，对身体投资会有回报。")
        elif star in ["文昌", "文曲"]:
            interpretations.append("   具体表现：学业运、考试运变好，学习能力提升，适合考证书或进修。")
        elif star in ["紫微", "太阳"]:
            interpretations.append("   具体表现：才华被认可，可能获得荣誉或嘉奖，在团队中脱颖而出。")
        else:
            interpretations.append("   具体表现：多学习、多积累，好名声会自然而来。")
        interpretations.append("\n📚 **把握建议**：" + (transform_info.get('把握建议', [''])[0] if transform_info.get('把握建议') else "好名声要靠实力支撑，继续努力。"))

    # 化权的综合解读
    elif transform == "化权":
        interpretations.append(f"💪 **能力增强！** {palace_meaning}方面说话更有分量。")
        if star in ["紫微", "天梁"]:
            interpretations.append("   具体表现：领导能力突出，有晋升或独当一面的机会，适合承担更大责任。")
        elif star in ["武曲", "破军"]:
            interpretations.append("   具体表现：执行力变强，适合开创或推动项目，能把想法落地。")
        elif star in ["贪狼"]:
            interpretations.append("   具体表现：掌控欲变强，有展现能力的机会，但注意不要太强势。")
        else:
            interpretations.append("   具体表现：展现能力的时候到了，但要注意方式方法。")
        interpretations.append("\n👑 **领导力提示**：" + (transform_info.get('注意事项', [''])[0] if transform_info.get('注意事项') else "权力越大责任越大，不要滥用权力。"))

    return "\n".join(interpretations)


def _generate_transform_summary_v2(chart_data: Dict, transforms: List[Dict]) -> str:
    """生成四化联动总结 v2"""
    summary = []

    # 分析四个四化的组合
    lu = next((t for t in transforms if t.get("type") == "化禄"), None)
    ji = next((t for t in transforms if t.get("type") == "化忌"), None)
    ke = next((t for t in transforms if t.get("type") == "化科"), None)
    quan = next((t for t in transforms if t.get("type") == "化权"), None)

    summary.append("**【命盘特点】**\n")
    if lu:
        star = lu.get("star", "")
        palace = lu.get("palace", "")
        summary.append(f"- 🌱 有**化禄星**（{star}）在{palace}，代表你有福气，运气不错")
    if quan:
        star = quan.get("star", "")
        palace = quan.get("palace", "")
        summary.append(f"- 🌳 有**化权星**（{star}）在{palace}，代表你有进取心，能力被认可")
    if ke:
        star = ke.get("star", "")
        palace = ke.get("palace", "")
        summary.append(f"- 🌸 有**化科星**（{star}）在{palace}，代表你名声好，学习能力强")
    if ji:
        star = ji.get("star", "")
        palace = ji.get("palace", "")
        summary.append(f"- ⚠️ 有**化忌星**（{star}）在{palace}，代表你有考验，需要付出更多努力")

    # 分析格局
    summary.append("\n**【格局分析】**\n")

    stars = [t.get("star") for t in transforms]
    if "天同" in stars and "巨门" in stars:
        summary.append("- 天同+巨门组合：外柔内刚，表面温和但内心有主见，善于分析但也能享受生活")
    if "天机" in stars and "太阴" in stars:
        summary.append("- 天机+太阴组合：聪明细腻，喜欢思考和规划，内心世界丰富")
    if "天梁" in stars:
        summary.append("- 天梁入命：有责任心，喜欢帮助人，有长者风范")

    # 总结主线
    summary.append("\n**【人生主线】**\n")

    if lu and quan:
        summary.append("你的命盘既有**福气**（化禄）又有**进取心**（化权），")
        summary.append("这是很好的配置——你有机会也有能力，关键是把握好度。")
    elif lu:
        summary.append("你命中福气较重（化禄），运气不错，但可能需要主动一些才能抓住机会。")
    elif quan:
        summary.append("你命中进取心强（化权），能力被认可，适合在事业上发力。")

    if ji:
        summary.append("\n虽然有挑战（化忌），但这是成长必经之路。")
        summary.append("记住：危机中往往蕴含转机，克服后会更好。")

    summary.append("\n**整体来说，你的命运主打「稳中求进」——")
    summary.append("有机会但也有考验，关键是把握好度。**")

    return "\n".join(summary)


def _generate_personality_profile(chart_data: Dict, transforms: List[Dict]) -> str:
    """生成性格画像"""
    profile = []

    stars = [t.get("star") for t in transforms]

    profile.append("根据你的四化配置，你大概是这样的人：\n")

    if "天同" in stars:
        profile.append("🌟 **天同星特质**：")
        profile.append("   - 性格温和乐观，喜欢享受生活")
        profile.append("   - 不太与人争，心态平和")
        profile.append("   - 有福气，但有时可能缺乏一点冲劲")

    if "巨门" in stars:
        profile.append("\n💬 **巨门星特质**：")
        profile.append("   - 口才好，善于表达和分析")
        profile.append("   - 思维敏锐，有洞察力")
        profile.append("   - 要注意说话方式，别太直伤人")

    if "天机" in stars:
        profile.append("\n🧠 **天机星特质**：")
        profile.append("   - 聪明机敏，喜欢动脑筋")
        profile.append("   - 思维活跃，善于变化")
        profile.append("   - 要注意不要想太多、优柔寡断")

    if "太阴" in stars:
        profile.append("\n🌙 **太阴星特质**：")
        profile.append("   - 内心细腻，情感丰富")
        profile.append("   - 不善言辞但有内涵")
        profile.append("   - 要学会表达自己，别把情绪藏心里")

    if "天梁" in stars:
        profile.append("\n🛡️ **天梁星特质**：")
        profile.append("   - 有责任心，喜欢帮助人")
        profile.append("   - 思维成熟，有远见")
        profile.append("   - 要学会放手，别什么都自己扛")

    profile.append("\n💡 **给你的建议**：")
    profile.append("   了解自己的性格特点，发扬优点，改进缺点。")
    profile.append("   命理是参考，最终决定权在你自己手中！")

    return "\n".join(profile)


def generate_markdown_with_charts(
    chart_data: Dict[str, Any],
    causal_chain_result: Optional[Dict[str, Any]] = None,
    four_hua: Optional[Dict[str, str]] = None,
    fortune_trend: str = "平稳",
    confidence: float = 75.0,
    year: int = 2026
) -> Dict[str, Any]:
    """
    生成通俗化解说（含图表数据）的便捷函数

    Args:
        chart_data: 命盘数据
        causal_chain_result: 因果链分析结果
        four_hua: 四化配置，格式 {"命宫": "化禄", ...}，
                   若不提供则从 chart_data.transforms 自动提取
        fortune_trend: 运势趋势，"上升"、"平稳"或"波动"
        confidence: 置信度 0-100
        year: 年份，默认2026

    Returns:
        包含 markdown 文本和 chart_data 图表数据的字典
    """
    # 自动从 chart_data 提取四化配置
    if four_hua is None:
        four_hua = {}
        transforms = chart_data.get("transforms", [])
        for t in transforms:
            palace = t.get("palace", "")
            transform_type = t.get("type", "")
            if palace and transform_type:
                four_hua[palace] = transform_type

    # 生成 markdown
    markdown_content = generate_plain_causal_chain_explanation_v2(
        chart_data, causal_chain_result
    )

    # 生成图表数据
    transforms = chart_data.get("transforms", [])
    chart_data_out = {
        "summary": {
            "year": year,
            "total_transforms": len(transforms),
            "fortune_trend": fortune_trend,
            "confidence": confidence
        },
        "transforms": [
            {
                "star": t.get("star", ""),
                "type": t.get("type", ""),
                "palace": t.get("palace", "")
            }
            for t in transforms
        ],
        "monthly_fortune": generate_monthly_advice(
            four_hua, fortune_trend, confidence
        ),
        "palace_summary": [
            {
                "palace": get_palace_meaning(p.get("name", "")).get("meaning", p.get("name", "")),
                "main_stars": p.get("main_stars", []),
                "transform": p.get("transform", "")
            }
            for p in chart_data.get("palaces", {}).values()
            if p.get("transform")
        ]
    }

    return {
        "markdown": markdown_content,
        "chart_data": chart_data_out
    }
