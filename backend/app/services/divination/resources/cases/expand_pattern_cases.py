#!/usr/bin/env python3
"""扩充pattern_cases.json案例"""

import json
from pathlib import Path

# 主星列表
MAIN_STARS = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞", "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"]

# 辅星列表
ASSISTANT_STARS = ["左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存", "天马"]

# 煞星列表
SHA_STARS = ["擎羊", "陀罗", "火星", "铃星", "地空", "地劫"]

# 桃花星
FLOWER_STARS = ["红鸾", "天喜", "咸池", "海棠", "贪狼"]

# 格局类型
PATTERN_TYPES = ["吉格", "凶格", "中格"]

def generate_pattern_cases():
    cases = []
    case_id = 25  # 从25开始（现有24个）

    # 紫微星系格局
    ziwei_patterns = [
        {"name": "紫府同宫格", "condition": "紫微天府同宫于丑未", "meaning": "紫微破军星系，得左辅右弼相夹，可以将动荡不安的本质化为开创力。", "type": "吉格"},
        {"name": "紫微七杀格", "condition": "紫微与七杀同宫", "meaning": "紫微七杀反作祸祥，若无辅曜制化则为冷酷之徒。", "type": "凶格"},
        {"name": "紫微破军格", "condition": "紫微破军同宫于丑未", "meaning": "动荡不安的本质，需加左右才有发展。", "type": "中格"},
        {"name": "百官朝拱格", "condition": "紫微坐命，有众星环绕", "meaning": "帝座受百官朝拱，主贵，有领导力。", "type": "吉格"},
        {"name": "君臣不庆格", "condition": "紫微遇空劫", "meaning": "紫微遇空劫，理想太高，不切实际。", "type": "凶格"}
    ]

    for pattern in ziwei_patterns:
        for star in MAIN_STARS[:5]:  # 取5个年干组合
            cases.append({
                "case_id": f"PAT_{case_id:03d}",
                "agent": "PatternAgent",
                "type": pattern["type"],
                "name": pattern["name"],
                "input": {
                    "main_star": star,
                    "condition": pattern["condition"],
                    "pattern_type": pattern["type"]
                },
                "output": {
                    "interpretation": f"{pattern['name']}：{pattern['meaning']}",
                    "keywords": [pattern["name"], star, pattern["type"], pattern["meaning"].split("，")[0]]
                },
                "source": "王亭之注《太微赋》"
            })
            case_id += 1

    # 天机星系格局
    tianji_patterns = [
        {"name": "天机天梁格", "condition": "天机天梁同度于卯酉", "meaning": "善宿组合，好谈论辩，有特殊技艺，心地善良有宗教信仰。", "type": "吉格"},
        {"name": "天机太阴格", "condition": "天机太阴同度于寅申", "meaning": "探花格，聪明机敏，善于谋略。", "type": "吉格"},
        {"name": "机梁交战格", "condition": "天机天梁于辰戌相冲", "meaning": "理想与现实冲突，多变动、奔波。", "type": "凶格"},
        {"name": "天机加恶煞", "condition": "天机与煞星同宫", "meaning": "天机加恶煞同宫，鸡窃狗偷。", "type": "凶格"}
    ]

    for pattern in tianji_patterns:
        for star in MAIN_STARS[1:4]:
            cases.append({
                "case_id": f"PAT_{case_id:03d}",
                "agent": "PatternAgent",
                "type": pattern["type"],
                "name": pattern["name"],
                "input": {
                    "main_star": star,
                    "condition": pattern["condition"],
                    "pattern_type": pattern["type"]
                },
                "output": {
                    "interpretation": f"{pattern['name']}：{pattern['meaning']}",
                    "keywords": [pattern["name"], star, pattern["type"]]
                },
                "source": "王亭之注《太微赋》"
            })
            case_id += 1

    # 太阳星系格局
    taiyang_patterns = [
        {"name": "日丽中天格", "condition": "太阳居午宫", "meaning": "太阳居午谓之日丽中天，有专权之贵，敌国之富。", "type": "吉格"},
        {"name": "太阳普照格", "condition": "太阳入庙旺于卯辰巳午", "meaning": "太阳庙旺主贵，白日生人吉，夜生人需扣分。", "type": "吉格"},
        {"name": "日失光辉格", "condition": "太阳落陷于酉戌亥子", "meaning": "太阳落陷，多是非纠纷，贵而不实。", "type": "凶格"},
        {"name": "太阳会羊陀", "condition": "太阳与擎羊陀罗同宫", "meaning": "太阳会羊陀，个性刚强，多是非竞争。", "type": "凶格"}
    ]

    for pattern in taiyang_patterns:
        for star in MAIN_STARS[2:5]:
            cases.append({
                "case_id": f"PAT_{case_id:03d}",
                "agent": "PatternAgent",
                "type": pattern["type"],
                "name": pattern["name"],
                "input": {
                    "main_star": star,
                    "condition": pattern["condition"],
                    "pattern_type": pattern["type"]
                },
                "output": {
                    "interpretation": f"{pattern['name']}：{pattern['meaning']}",
                    "keywords": [pattern["name"], star, pattern["type"]]
                },
                "source": "《命理学正解》"
            })
            case_id += 1

    # 武曲星系格局
    wuqu_patterns = [
        {"name": "武曲天府格", "condition": "武曲天府同宫于子午", "meaning": "武曲天府同宫于子午，无擎羊冲破，主有高寿。", "type": "吉格"},
        {"name": "武曲贪狼格", "condition": "武曲贪狼同度", "meaning": "武曲贪狼同度，悭吝之人；若无吉相扶，反主夭寿。", "type": "凶格"},
        {"name": "武曲火星格", "condition": "武曲火星同度", "meaning": "武曲火星为寡宿凶格，女命不利婚姻。", "type": "凶格"},
        {"name": "武曲七杀格", "condition": "武曲七杀同宫", "meaning": "武曲七杀，权禄双美，财运亨通。", "type": "吉格"}
    ]

    for pattern in wuqu_patterns:
        for star in MAIN_STARS[3:6]:
            cases.append({
                "case_id": f"PAT_{case_id:03d}",
                "agent": "PatternAgent",
                "type": pattern["type"],
                "name": pattern["name"],
                "input": {
                    "main_star": star,
                    "condition": pattern["condition"],
                    "pattern_type": pattern["type"]
                },
                "output": {
                    "interpretation": f"{pattern['name']}：{pattern['meaning']}",
                    "keywords": [pattern["name"], star, pattern["type"]]
                },
                "source": "《命理学正解》"
            })
            case_id += 1

    # 天同星系格局
    tiantong_patterns = [
        {"name": "天同天梁格", "condition": "天同天梁同度于寅申", "meaning": "天同最喜会同天梁及左右，天同天梁相会，不畏凶危。", "type": "吉格"},
        {"name": "天同太阴格", "condition": "天同太阴同宫", "meaning": "福星组合，温和慈善，有福有寿。", "type": "吉格"},
        {"name": "天同擎羊格", "condition": "天同擎羊居午位", "meaning": "天同擎羊居午位，丙戊生人镇边疆。", "type": "中格"},
        {"name": "天同四煞格", "condition": "天同与煞星同宫", "meaning": "福星被煞星破坏，多劳碌奔波。", "type": "凶格"}
    ]

    for pattern in tiantong_patterns:
        for star in MAIN_STARS[4:7]:
            cases.append({
                "case_id": f"PAT_{case_id:03d}",
                "agent": "PatternAgent",
                "type": pattern["type"],
                "name": pattern["name"],
                "input": {
                    "main_star": star,
                    "condition": pattern["condition"],
                    "pattern_type": pattern["type"]
                },
                "output": {
                    "interpretation": f"{pattern['name']}：{pattern['meaning']}",
                    "keywords": [pattern["name"], star, pattern["type"]]
                },
                "source": "《命理学正解》"
            })
            case_id += 1

    # 贪狼星系格局
    tanlang_patterns = [
        {"name": "贪狼入庙格", "condition": "贪狼居辰戌丑未四墓宫", "meaning": "贪狼四墓为得地，非庙旺，喜火铃同宫则富贵。", "type": "吉格"},
        {"name": "贪狼火铃格", "condition": "贪狼四墓遇火铃", "meaning": "贪狼四墓遇火铃，豪富家资候伯贵。", "type": "吉格"},
        {"name": "贪狼七杀格", "condition": "贪狼七杀分守身命", "meaning": "男有偷窃习性而犯刑配，女有偷香淫污之丑。", "type": "凶格"},
        {"name": "泛水桃花格", "condition": "贪狼与桃花星同宫", "meaning": "贪狼遇桃花，桃花犯主，情感复杂。", "type": "凶格"}
    ]

    for pattern in tanlang_patterns:
        for star in MAIN_STARS[8:11]:
            cases.append({
                "case_id": f"PAT_{case_id:03d}",
                "agent": "PatternAgent",
                "type": pattern["type"],
                "name": pattern["name"],
                "input": {
                    "main_star": star,
                    "condition": pattern["condition"],
                    "pattern_type": pattern["type"]
                },
                "output": {
                    "interpretation": f"{pattern['name']}：{pattern['meaning']}",
                    "keywords": [pattern["name"], star, pattern["type"]]
                },
                "source": "王亭之注《太微赋》"
            })
            case_id += 1

    # 巨门星系格局
    jumen_patterns = [
        {"name": "石中隐玉格", "condition": "巨门在子午石中隐玉", "meaning": "子午巨门石中隐玉，主聪明多能。", "type": "吉格"},
        {"name": "巨日同宫格", "condition": "巨门太阳同宫于寅申", "meaning": "巨日寅宫立命申，先驰名誉后食禄。", "type": "吉格"},
        {"name": "巨门羊陀格", "condition": "巨门羊陀于身命", "meaning": "巨门羊陀于身命，疾病羸黄。", "type": "凶格"},
        {"name": "巨门会煞格", "condition": "巨门与煞星同宫", "meaning": "巨门遇煞，是非纠纷，口舌频发。", "type": "凶格"}
    ]

    for pattern in jumen_patterns:
        for star in MAIN_STARS[9:12]:
            cases.append({
                "case_id": f"PAT_{case_id:03d}",
                "agent": "PatternAgent",
                "type": pattern["type"],
                "name": pattern["name"],
                "input": {
                    "main_star": star,
                    "condition": pattern["condition"],
                    "pattern_type": pattern["type"]
                },
                "output": {
                    "interpretation": f"{pattern['name']}：{pattern['meaning']}",
                    "keywords": [pattern["name"], star, pattern["type"]]
                },
                "source": "王亭之注《太微赋》"
            })
            case_id += 1

    # 天梁星系格局
    tianliang_patterns = [
        {"name": "梁居午地格", "condition": "天梁在午居庙旺", "meaning": "梁居午地官资清显，天梁单守午宫主清贵。", "type": "吉格"},
        {"name": "机梁会合格", "condition": "天机天梁同宫", "meaning": "机梁会合善谈兵，居戍亦为美论。", "type": "吉格"},
        {"name": "梁同巳亥格", "condition": "天梁在巳亥与天同会合", "meaning": "梁同巳亥，男多浪荡，女多淫。", "type": "凶格"},
        {"name": "天梁遇荫格", "condition": "天梁遇左辅右弼", "meaning": "天梁遇辅弼，有贵人与解厄之力。", "type": "吉格"}
    ]

    for pattern in tianliang_patterns:
        for star in MAIN_STARS[11:]:
            cases.append({
                "case_id": f"PAT_{case_id:03d}",
                "agent": "PatternAgent",
                "type": pattern["type"],
                "name": pattern["name"],
                "input": {
                    "main_star": star,
                    "condition": pattern["condition"],
                    "pattern_type": pattern["type"]
                },
                "output": {
                    "interpretation": f"{pattern['name']}：{pattern['meaning']}",
                    "keywords": [pattern["name"], star, pattern["type"]]
                },
                "source": "《命理学正解》"
            })
            case_id += 1

    # 七杀星系格局
    qisha_patterns = [
        {"name": "杀居旺宫格", "condition": "七杀在寅申子午宫坐命", "meaning": "七杀寅申子午宫，一生爵禄荣昌，多辛劳独创。", "type": "吉格"},
        {"name": "七杀朝斗格", "condition": "七杀在午申朝斗", "meaning": "七杀朝斗格多辛劳独创，独当一面，成就光辉。", "type": "吉格"},
        {"name": "马头带箭格", "condition": "七杀坐命午宫遇擎羊", "meaning": "马头带箭主人生多挫折，少际遇，不过却主权威。", "type": "凶格"},
        {"name": "紫杀无制格", "condition": "紫微七杀无辅曜制化", "meaning": "紫微七杀无辅曜制化为冷酷之徒格。", "type": "凶格"}
    ]

    for pattern in qisha_patterns:
        for star in MAIN_STARS[12:]:
            cases.append({
                "case_id": f"PAT_{case_id:03d}",
                "agent": "PatternAgent",
                "type": pattern["type"],
                "name": pattern["name"],
                "input": {
                    "main_star": star,
                    "condition": pattern["condition"],
                    "pattern_type": pattern["type"]
                },
                "output": {
                    "interpretation": f"{pattern['name']}：{pattern['meaning']}",
                    "keywords": [pattern["name"], star, pattern["type"]]
                },
                "source": "王亭之注《太微赋》"
            })
            case_id += 1

    # 破军星系格局
    pojun_patterns = [
        {"name": "破军子午格", "condition": "破军在子午与吉星同会", "meaning": "子午破军加官进禄，主先破后成。", "type": "吉格"},
        {"name": "破军贪狼格", "condition": "破军贪狼逢禄马", "meaning": "破军贪狼逢禄马，男多浪荡女多淫。", "type": "凶格"},
        {"name": "破军文昌格", "condition": "破军文昌于震地遇吉", "meaning": "破军文昌于震地，遇吉可贵，主先破后成。", "type": "中格"},
        {"name": "破军四煞格", "condition": "破军与煞星同宫", "meaning": "破军遇煞，冲动激进，多波折。", "type": "凶格"}
    ]

    for pattern in pojun_patterns:
        for star in MAIN_STARS[13:]:
            cases.append({
                "case_id": f"PAT_{case_id:03d}",
                "agent": "PatternAgent",
                "type": pattern["type"],
                "name": pattern["name"],
                "input": {
                    "main_star": star,
                    "condition": pattern["condition"],
                    "pattern_type": pattern["type"]
                },
                "output": {
                    "interpretation": f"{pattern['name']}：{pattern['meaning']}",
                    "keywords": [pattern["name"], star, pattern["type"]]
                },
                "source": "《命理学正解》"
            })
            case_id += 1

    return cases


# 生成禄存独座案例
def generate_lu_cun_solo_cases():
    cases = []
    case_id = 216  # 从216开始

    lu_cun_patterns = [
        {"name": "禄存独座", "palace": "命宫", "meaning": "禄存为财星，独坐命宫主财气随身，禀性温和。唯需注意羊陀夹宫或会照，形成财库。", "keywords": ["财星", "温和", "财库", "积聚"]},
        {"name": "禄存田宅", "palace": "田宅宫", "meaning": "主有祖业或自置产业，财库丰厚。逢化禄或吉星更佳。", "keywords": ["祖业", "产业", "财库", "不动置"]},
        {"name": "禄存财帛", "palace": "财帛宫", "meaning": "财星入库，理财能力佳，善储蓄。唯需注意钱财外露易招小人。", "keywords": ["理财", "储蓄", "财库", "小人"]}
    ]

    for pattern in lu_cun_patterns:
        cases.append({
            "case_id": f"PAT_{case_id:03d}",
            "agent": "PatternAgent",
            "type": "吉格",
            "name": pattern["name"],
            "input": {"main_star": "禄存", "palace": pattern["palace"], "condition": f"禄存在{pattern['palace']}", "arrangement": "独座"},
            "output": {"interpretation": pattern["meaning"], "formation_conditions": [f"禄存坐{pattern['palace']}", "无化忌冲破", "无煞星同宫"], "keywords": pattern["keywords"]},
            "source": "紫微斗数经典格局"
        })
        case_id += 1
    return cases


# 生成羊陀夹禄案例
def generate_yangtuo_jia_lu_cases():
    cases = []
    case_id = 219

    yangtuo_patterns = [
        {"name": "羊陀夹禄", "palace": "命宫", "meaning": "羊陀夹禄为凶兆，夹制禄存主财运受阻，奔波劳碌。唯夹制之力需有化忌或煞星才会显凶。", "keywords": ["夹制", "受阻", "劳碌", "财运"]},
        {"name": "羊陀夹财", "palace": "财帛宫", "meaning": "财帛被夹，主财来财去，不易聚财。理财需保守，以免破财。", "keywords": ["破财", "不聚财", "消耗", "财务"]},
        {"name": "羊陀夹印", "palace": "官禄宫", "meaning": "官禄被夹，主事业受阻，职位难升。需保守行事，避免与人竞争。", "keywords": ["事业", "受阻", "竞争", "职位"]}
    ]

    for pattern in yangtuo_patterns:
        cases.append({
            "case_id": f"PAT_{case_id:03d}",
            "agent": "PatternAgent",
            "type": "凶格",
            "name": pattern["name"],
            "input": {"malefic_stars": ["擎羊", "陀罗"], "palace": pattern["palace"], "condition": f"羊陀夹{pattern['palace']}", "arrangement": "夹制"},
            "output": {"interpretation": pattern["meaning"], "formation_conditions": [f"羊陀夹{pattern['palace']}", "禄存或吉星被夹", "逢化忌或煞星显凶"], "keywords": pattern["keywords"]},
            "source": "紫微斗数经典格局"
        })
        case_id += 1
    return cases


# 生成火星铃星入宫案例
def generate_huoxing_lingxing_cases():
    cases = []
    case_id = 222

    fire_star_patterns = [
        {"name": "火星入命", "star": "火星", "palace": "命宫", "meaning": "火星为浮荡之星，入命宫主性格刚烈，急躁不安。逢吉星可化解其凶性。", "keywords": ["刚烈", "急躁", "浮荡", "变动"]},
        {"name": "铃星入命", "star": "铃星", "palace": "命宫", "meaning": "铃星主暗发性，入命宫主外柔内刚，有突发之财。唯须注意意外灾祸。", "keywords": ["暗发", "突发", "外柔内刚", "意外"]},
        {"name": "火铃夹命", "star": "火星/铃星", "palace": "命宫", "meaning": "火铃夹命为凶兆，主一生多变动，飘荡不定。唯紫微天府可化解其凶性。", "keywords": ["变动", "飘荡", "不稳定", "奔波"]},
        {"name": "火星照壁", "star": "火星", "palace": "田宅宫", "meaning": "火星照田宅，主家宅不宁，或有火灾、意外之灾。宜注意居家安全。", "keywords": ["家宅", "火灾", "意外", "不宁"]},
        {"name": "铃星守财", "star": "铃星", "palace": "财帛宫", "meaning": "铃星守财帛宫，主有意外之财，但财来财去，不易积聚。", "keywords": ["意外之财", "不聚财", "波动", "理财"]}
    ]

    for pattern in fire_star_patterns:
        cases.append({
            "case_id": f"PAT_{case_id:03d}",
            "agent": "PatternAgent",
            "type": "凶格",
            "name": pattern["name"],
            "input": {"malefic_stars": [pattern["star"]], "palace": pattern["palace"], "condition": f"{pattern['star']}在{pattern['palace']}", "arrangement": "独坐或会照"},
            "output": {"interpretation": pattern["meaning"], "formation_conditions": [f"{pattern['star']}在{pattern['palace']}", "无紫微天府化解", "逢化忌更凶"], "keywords": pattern["keywords"]},
            "source": "紫微斗数经典格局"
        })
        case_id += 1
    return cases


# 生成紫微斗数经典格局
def generate_classic_pattern_cases():
    cases = []
    case_id = 227

    classic_patterns = [
        {"name": "紫府同宫格", "type": "吉格", "stars": ["紫微", "天府"], "palace": "命宫", "meaning": "紫府同宫，主贵而且吉。紫微为帝星，天府为财库，二星同宫主有权有势，财福兼收。", "keywords": ["权贵", "财富", "福气", "双星"]},
        {"name": "机月同梁格", "type": "吉格", "stars": ["天机", "太阴", "天同", "天梁"], "palace": "命宫或迁移宫", "meaning": "机月同梁，四星聚会，主聪明机巧，擅长策划。为公务员或企业策划人才之上选。", "keywords": ["聪明", "策划", "公务员", "机巧"]},
        {"name": "杀破狼格", "type": "吉格", "stars": ["七杀", "破军", "贪狼"], "palace": "命宫或迁移宫", "meaning": "杀破狼为变动之星，三星同宫或相会，主一生多变动，但能开创大业。为大改革家或企业家的格局。", "keywords": ["变动", "开创", "改革", "企业家"]},
        {"name": "府相朝垣", "type": "吉格", "stars": ["天府", "天相"], "palace": "命宫", "meaning": "天府天相为左右宰相，二星在命宫或相会于三方，主有贵气，仕途顺利。", "keywords": ["贵气", "仕途", "宰相", "辅助"]},
        {"name": "文梁振纪", "type": "吉格", "stars": ["文昌", "天梁"], "palace": "命宫", "meaning": "文昌为文星，天梁为荫星，二星相会主聪明慈善，有科名功名。", "keywords": ["科名", "慈善", "聪明", "功名"]},
        {"name": "天罗地网", "type": "凶格", "stars": ["天网"], "palace": "辰宫或戌宫", "meaning": "天罗地网指辰戌二宫为天罗地网之星入宫，主命运受阻，多灾难或法律纠纷。", "keywords": ["受阻", "灾难", "纠纷", "限制"]},
        {"name": "双忌冲破", "type": "凶格", "stars": ["化忌"], "palace": "命宫或财帛宫", "meaning": "双忌冲破指两个化忌同时冲破某宫，主破财严重，或有重大灾祸。", "keywords": ["破财", "灾祸", "双重", "冲破"]},
        {"name": "空劫夹命", "type": "凶格", "stars": ["地空", "地劫"], "palace": "命宫", "meaning": "空劫夹命主一生钱财不聚，虚耗多耗散。或有僧道之缘。", "keywords": ["耗散", "不聚财", "空虚", "僧道"]},
        {"name": "刑囚夹印", "type": "凶格", "stars": ["天相", "天梁", "廉贞", "擎羊", "陀罗"], "palace": "命宫或疾厄宫", "meaning": "天相被天梁、廉贞、羊陀夹制，主有刑灾、诉讼、伤病之灾。", "keywords": ["刑灾", "诉讼", "伤病", "夹制"]},
        {"name": "贪狼陷疾", "type": "凶格", "stars": ["贪狼"], "palace": "疾厄宫", "meaning": "贪狼陷于疾厄宫，主有暗疾或慢性病，或有桃花纠纷导致的身体损耗。", "keywords": ["暗疾", "慢性病", "桃花", "损耗"]}
    ]

    for pattern in classic_patterns:
        cases.append({
            "case_id": f"PAT_{case_id:03d}",
            "agent": "PatternAgent",
            "type": pattern["type"],
            "name": pattern["name"],
            "input": {"main_stars": pattern["stars"], "palace": pattern["palace"], "condition": f"{'、'.join(pattern['stars'])}在{pattern['palace']}", "arrangement": "同宫或相会"},
            "output": {"interpretation": pattern["meaning"], "formation_conditions": [f"{'、'.join(pattern['stars'])}在{pattern['palace']}", "符合格局要求"], "keywords": pattern["keywords"]},
            "source": "紫微斗数经典格局"
        })
        case_id += 1
    return cases


# 生成桃花感情格局
def generate_romance_pattern_cases():
    cases = []
    case_id = 262

    romance_patterns = [
        {"name": "红鸾入命", "type": "吉格", "stars": ["红鸾"], "palace": "命宫", "meaning": "红鸾星入命主有桃花运和喜庆之事。", "keywords": ["桃花", "喜庆", "婚姻", "红鸾"]},
        {"name": "天喜入命", "type": "吉格", "stars": ["天喜"], "palace": "命宫", "meaning": "天喜星入命主有喜庆之事和添丁之喜。", "keywords": ["添丁", "喜庆", "婚姻", "天喜"]},
        {"name": "咸池桃花", "type": "凶格", "stars": ["咸池"], "palace": "命宫或夫妻宫", "meaning": "咸池为桃花煞星，主有桃花劫或感情纠纷。", "keywords": ["桃花劫", "纠纷", "破财", "咸池"]},
        {"name": "天姚风流", "type": "凶格", "stars": ["天姚"], "palace": "命宫", "meaning": "天姚星主有风流才艺，但易有感情纠纷或外遇。", "keywords": ["风流", "才艺", "外遇", "天姚"]},
        {"name": "桃花滚浪", "type": "凶格", "stars": ["贪狼", "太阴", "天姚", "红鸾"], "palace": "命宫或夫妻宫", "meaning": "多颗桃花星聚会主有复杂的感情生活。", "keywords": ["桃花", "复杂", "纠纷", "多情"]}
    ]

    for pattern in romance_patterns:
        cases.append({
            "case_id": f"PAT_{case_id:03d}",
            "agent": "PatternAgent",
            "type": pattern["type"],
            "name": pattern["name"],
            "input": {"main_stars": pattern["stars"], "palace": pattern["palace"], "condition": f"{'、'.join(pattern['stars'])}在{pattern['palace']}", "arrangement": "同宫或相会"},
            "output": {"interpretation": pattern["meaning"], "formation_conditions": [f"{'、'.join(pattern['stars'])}在{pattern['palace']}"], "keywords": pattern["keywords"]},
            "source": "紫微斗数桃花格局"
        })
        case_id += 1
    return cases


# 生成科名功名格局
def generate_exam_pattern_cases():
    cases = []
    case_id = 267

    exam_patterns = [
        {"name": "文昌文科", "type": "吉格", "stars": ["文昌", "化科"], "palace": "命宫或官禄宫", "meaning": "文昌化科主有科名功名，利考试和学术。", "keywords": ["科名", "考试", "学术", "文昌"]},
        {"name": "文曲科名", "type": "吉格", "stars": ["文曲", "化科"], "palace": "命宫或官禄宫", "meaning": "文曲化科主有艺术科名，利文艺创作和学术。", "keywords": ["艺术", "文艺", "学术", "文曲"]},
        {"name": "魁钺及第", "type": "吉格", "stars": ["天魁", "天钺"], "palace": "命宫或迁移宫", "meaning": "魁钺及第主有贵人助考，利科举考试和仕途。", "keywords": ["贵人", "科举", "仕途", "魁钺"]},
        {"name": "三元及第", "type": "吉格", "stars": ["化禄", "化权", "化科"], "palace": "命宫或官禄宫", "meaning": "三元及第指禄权科三元齐全，主功名显达，富贵双全。", "keywords": ["功名", "富贵", "三元", "及第"]},
        {"name": "科星被破", "type": "凶格", "stars": ["文昌", "文曲", "化忌"], "palace": "官禄宫", "meaning": "科星被化忌冲破主有功名但难持久，或考试失利。", "keywords": ["考试", "失利", "破败", "功名"]}
    ]

    for pattern in exam_patterns:
        cases.append({
            "case_id": f"PAT_{case_id:03d}",
            "agent": "PatternAgent",
            "type": pattern["type"],
            "name": pattern["name"],
            "input": {"main_stars": pattern["stars"], "palace": pattern["palace"], "condition": f"{'、'.join(pattern['stars'])}在{pattern['palace']}", "arrangement": "同宫或相会"},
            "output": {"interpretation": pattern["meaning"], "formation_conditions": [f"{'、'.join(pattern['stars'])}在{pattern['palace']}"], "keywords": pattern["keywords"]},
            "source": "紫微斗数科名格局"
        })
        case_id += 1
    return cases


def main():
    # 读取现有案例
    cases_file = Path(__file__).parent / "pattern_cases.json"
    with open(cases_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_count = len(data["cases"])
    print(f"现有案例数量: {existing_count}")

    # 生成新案例
    new_cases = []
    new_cases.extend(generate_pattern_cases())
    new_cases.extend(generate_lu_cun_solo_cases())
    new_cases.extend(generate_yangtuo_jia_lu_cases())
    new_cases.extend(generate_huoxing_lingxing_cases())
    new_cases.extend(generate_classic_pattern_cases())
    new_cases.extend(generate_romance_pattern_cases())
    new_cases.extend(generate_exam_pattern_cases())

    print(f"新增案例数量: {len(new_cases)}")

    # 合并案例
    data["cases"].extend(new_cases)

    # 保存
    with open(cases_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"更新后案例总数: {len(data['cases'])}")

if __name__ == "__main__":
    main()
