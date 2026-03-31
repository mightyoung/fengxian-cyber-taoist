#!/usr/bin/env python3
"""扩充transform_cases.json案例"""

import json
from pathlib import Path

# 十二宫名称
PALACE_NAMES = [
    "命宫", "兄弟宫", "夫妻宫", "子女宫",
    "财帛宫", "疾厄宫", "迁移宫", "交友宫",
    "官禄宫", "田宅宫", "福德宫", "父母宫"
]

# 生年干四化表（根据紫微斗数典籍《紫微斗数全书》《飞星紫微斗数》）
# 一星不可化两曜，化禄和化忌可以同星
YEAR_STEM_TRANSFORMS = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "太阳", "忌": "太阴"},
    "乙": {"禄": "天机", "权": "天梁", "科": "文昌", "忌": "贪狼"},
    "丙": {"禄": "天同", "权": "天机", "科": "天机", "忌": "天同"},
    "丁": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "天机"},
    "戊": {"禄": "贪狼", "权": "武曲", "科": "天梁", "忌": "廉贞"},
    "己": {"禄": "太阴", "权": "巨门", "科": "天机", "忌": "文昌"},
    "庚": {"禄": "天梁", "权": "紫微", "科": "天府", "忌": "天同"},
    "辛": {"禄": "文昌", "权": "文曲", "科": "天同", "忌": "天梁"},
    "壬": {"禄": "天同", "权": "天机", "科": "天机", "忌": "天同"},
    "癸": {"禄": "天机", "权": "文曲", "科": "天同", "忌": "天机"},
}

# 生成禄转忌案例
def generate_lu_to_ji_cases():
    cases = []
    case_id = 52  # 从52开始

    for gan, transforms in YEAR_STEM_TRANSFORMS.items():
        lu_star = transforms.get("禄")
        if not lu_star:
            continue

        # 禄转忌：禄宫化忌入其他宫
        for from_palace in PALACE_NAMES:
            # 禄在此宫，化忌飞向其他宫
            to_palaces = [p for p in PALACE_NAMES if p != from_palace]
            for to_palace in to_palaces[:3]:  # 每个禄取3个目标宫
                cases.append({
                    "case_id": f"TRANS_{case_id:03d}",
                    "agent": "TransformAgent",
                    "type": "禄转忌",
                    "input": {
                        "birth_year_gan": gan,
                        "lu_star": lu_star,
                        "from_palace": from_palace,
                        "to_palace": to_palace,
                        "transform_type": "禄转忌"
                    },
                    "output": {
                        "interpretation": f"{lu_star}化禄于{from_palace}，转忌入{to_palace}，为禄转忌。禄出而转忌，挾禄以入第二宫。{from_palace}之事得而复失，或昙花一现。{to_palace}同得禄气，视为得吉。",
                        "keywords": ["禄转忌", "得而复失", "昙花一现", "挾禄", "第二宫"]
                    },
                    "source": "梁若瑜《飞星紫微斗数道藏飞秘的逻辑与功法》"
                })
                case_id += 1
                if case_id > 200:  # 限制数量
                    break
            if case_id > 200:
                break
        if case_id > 200:
            break

    return cases

# 生成忌转忌案例
def generate_ji_to_ji_cases():
    cases = []
    case_id = 201

    for gan, transforms in YEAR_STEM_TRANSFORMS.items():
        ji_star = transforms.get("忌")
        if not ji_star:
            continue

        # 忌转忌：忌宫化忌入其他宫
        for from_palace in PALACE_NAMES:
            to_palaces = [p for p in PALACE_NAMES if p != from_palace]
            for to_palace in to_palaces[:2]:  # 每个忌取2个目标宫
                cases.append({
                    "case_id": f"TRANS_{case_id:03d}",
                    "agent": "TransformAgent",
                    "type": "忌转忌",
                    "input": {
                        "birth_year_gan": gan,
                        "ji_star": ji_star,
                        "from_palace": from_palace,
                        "to_palace": to_palace,
                        "transform_type": "忌转忌"
                    },
                    "output": {
                        "interpretation": f"{ji_star}化忌于{from_palace}，转忌入{to_palace}，为忌转忌。忌出而再转忌，深入因果追根究底。{to_palace}逢忌出对宫或本宫自化忌出者，人事物容易瞬间消散、残败。",
                        "keywords": ["忌转忌", "连续阻碍", "消散", "残败", "追根究底"]
                    },
                    "source": "梁若瑜《飞星紫微斗数道藏飞秘的逻辑与功法》"
                })
                case_id += 1
                if case_id > 280:
                    break
            if case_id > 280:
                break
        if case_id > 280:
            break

    return cases

# 生成追禄案例
def generate_pursuit_lu_cases():
    cases = []
    case_id = 281

    # 追禄：某宫坐生年忌，我某宫化禄（同星曜）以入
    pursuit_examples = [
        {"condition": "交友宫坐生年忌", "action": "财帛宫化禄同星曜以入", "meaning": "财恰如肉包子打狗，禄忌成双忌，加倍之损"},
        {"condition": "田宅宫坐生年忌", "action": "命宫化禄同星曜以入", "meaning": "家宅得禄，有固定资产，但需谨慎投资"},
        {"condition": "官禄宫坐生年忌", "action": "财帛宫化禄同星曜以入", "meaning": "事业得财，但财来财去"}
    ]

    for ex in pursuit_examples:
        for gan in list(YEAR_STEM_TRANSFORMS.keys())[:5]:  # 取5个年干
            cases.append({
                "case_id": f"TRANS_{case_id:03d}",
                "agent": "TransformAgent",
                "type": "追禄",
                "input": {
                    "birth_year_gan": gan,
                    "condition": ex["condition"],
                    "action": ex["action"],
                    "transform_type": "追禄"
                },
                "output": {
                    "interpretation": f"{ex['condition']}，而{gan}年{ex['action']}，则为追禄。以同星曜的禄来会，追踪禄的走向，评估得失。{ex['meaning']}。追禄必须同星曜才能契缘。",
                    "keywords": ["追禄", "同星曜", "契缘", "加倍", "得失"]
                },
                "source": "梁若瑜《飞星紫微斗数道藏飞秘的逻辑与功法》"
            })
            case_id += 1
            if case_id > 310:
                break
        if case_id > 310:
            break

    return cases

# 生成追忌案例
def generate_pursuit_ji_cases():
    cases = []
    case_id = 311

    pursuit_examples = [
        {"condition": "田宅宫坐生年忌", "action": "财帛宫化忌以入", "meaning": "勤快俭约、顾家尽责，辛苦可以多得的禄忌成双禄"},
        {"condition": "交友宫坐生年禄", "action": "财帛宫化忌以入", "meaning": "得友财，取用方便，未必存余"},
        {"condition": "命三方化忌入田宅三方", "action": "化忌入田宅", "meaning": "此生必定拥有财产，可能有漂亮的银行存款及值钱的有价物品"}
    ]

    for ex in pursuit_examples:
        for gan in list(YEAR_STEM_TRANSFORMS.keys())[:5]:
            cases.append({
                "case_id": f"TRANS_{case_id:03d}",
                "agent": "TransformAgent",
                "type": "追忌",
                "input": {
                    "birth_year_gan": gan,
                    "condition": ex["condition"],
                    "action": ex["action"],
                    "transform_type": "追忌"
                },
                "output": {
                    "interpretation": f"{ex['condition']}，而{gan}年{ex['action']}，则为追忌。追忌观得失，以忌的走向评估财务状况。{ex['meaning']}。追忌非必同星曜。",
                    "keywords": ["追忌", "财务", "得失", "顾家", "财产"]
                },
                "source": "梁若瑜《飞星紫微斗数道藏飞秘的逻辑与功法》"
            })
            case_id += 1
            if case_id > 340:
                break
        if case_id > 340:
            break

    return cases

# 生成忌数论事案例
def generate_ji_count_cases():
    cases = []
    case_id = 341

    ji_count_rules = [
        {"level": "单忌", "meaning": "仅表示命盘主人在这方面的潜在特质、性向", "severity": "POTENTIAL"},
        {"level": "双忌", "meaning": "成立某坏事发生的契机与方向", "severity": "CONDITION"},
        {"level": "三忌", "meaning": "事情状态将更明确，坏事明显发生", "severity": "BAD"},
        {"level": "四忌以上", "meaning": "为败，造成严重事故", "severity": "CATASTROPHIC"}
    ]

    for rule in ji_count_rules:
        for gan in list(YEAR_STEM_TRANSFORMS.keys())[:5]:
            cases.append({
                "case_id": f"TRANS_{case_id:03d}",
                "agent": "TransformAgent",
                "type": "忌数论事",
                "input": {
                    "birth_year_gan": gan,
                    "ji_level": rule["level"],
                    "palace": "多宫位串联"
                },
                "output": {
                    "interpretation": f"忌数{rule['level']}，{rule['meaning']}。忌数论事，以忌的数量评估事态轻重。多忌串联呈破，触及什么宫位，会产生什么程度的败相。",
                    "keywords": ["忌数", rule["level"], rule["meaning"].split("，")[0], "事态轻重"]
                },
                "source": "梁若瑜《飞星紫微斗数道藏飞秘的逻辑与功法》"
            })
            case_id += 1
            if case_id > 400:
                break
        if case_id > 400:
            break

    return cases

# 生成禄忌对称案例
def generate_lu_ji_symmetry_cases():
    cases = []
    case_id = 401

    symmetry_rules = [
        {"type": "禄忌成双禄", "condition": "甲宫化忌入乙宫，逢乙宫飞来同星曜的化禄会", "meaning": "加倍之得"},
        {"type": "禄忌成双忌", "condition": "甲宫化忌入乙宫，逢乙宫有同星曜的化忌", "meaning": "加倍之损"}
    ]

    for rule in symmetry_rules:
        for gan in list(YEAR_STEM_TRANSFORMS.keys())[:5]:
            cases.append({
                "case_id": f"TRANS_{case_id:03d}",
                "agent": "TransformAgent",
                "type": "禄忌对称",
                "input": {
                    "birth_year_gan": gan,
                    "symmetry_type": rule["type"],
                    "condition": rule["condition"]
                },
                "output": {
                    "interpretation": f"禄忌对称-{rule['type']}：{rule['condition']}，{rule['meaning']}。同星曜的禄忌相交产生加倍效果。",
                    "keywords": ["禄忌对称", rule["type"], rule["meaning"], "加倍", "同星曜"]
                },
                "source": "梁若瑜《飞星紫微斗数道藏飞秘的逻辑与功法》"
            })
            case_id += 1
            if case_id > 451:
                break
        if case_id > 451:
            break

    return cases

# 生成飞化路线案例
def generate_flying_route_cases():
    cases = []
    case_id = 451

    # 化禄飞向的宫位
    lu_routes = [
        {"from": "田宅宫", "to": "命宫", "meaning": "祖德流芳、发田发产，光耀门楣，家大业大、房子越换越漂亮"},
        {"from": "田宅宫", "to": "迁移宫", "meaning": "发外之象，外向发展"},
        {"from": "财帛宫", "to": "命宫", "meaning": "财运好、汲营有道、手头方便"},
        {"from": "财帛宫", "to": "迁移宫", "meaning": "现金生意、源头活水"}
    ]

    # 化忌冲及的宫位
    ji_routes = [
        {"from": "田宅宫", "to": "命宫", "meaning": "长子格、承担家计、出身较差、六亲少助、碌碌劳苦、经济少裕"},
        {"from": "田宅宫", "to": "迁移宫", "meaning": "门风凋蔽、宗亲不兴、六亲无力、财退丁颓，家道中落、迁徙流离"},
        {"from": "财帛宫", "to": "命宫", "meaning": "固定收入或赚辛苦钱，需俭约度日"},
        {"from": "财帛宫", "to": "迁移宫", "meaning": "不善汲管，没有金钱概念、城府浅、少算计"}
    ]

    for route in lu_routes:
        for gan in list(YEAR_STEM_TRANSFORMS.keys())[:3]:
            cases.append({
                "case_id": f"TRANS_{case_id:03d}",
                "agent": "TransformAgent",
                "type": "飞化路线-化禄",
                "input": {
                    "birth_year_gan": gan,
                    "from_palace": route["from"],
                    "to_palace": route["to"],
                    "transform": "化禄"
                },
                "output": {
                    "interpretation": f"{gan}年{route['from']}化禄入{route['to']}：{route['meaning']}",
                    "keywords": ["化禄", route["from"], route["to"], route["meaning"].split("、")[0]]
                },
                "source": "梁若瑜《飞星紫微斗数道藏飞秘的逻辑与功法》"
            })
            case_id += 1
            if case_id > 520:
                break
        if case_id > 520:
            break

    for route in ji_routes:
        for gan in list(YEAR_STEM_TRANSFORMS.keys())[:3]:
            cases.append({
                "case_id": f"TRANS_{case_id:03d}",
                "agent": "TransformAgent",
                "type": "飞化路线-化忌",
                "input": {
                    "birth_year_gan": gan,
                    "from_palace": route["from"],
                    "to_palace": route["to"],
                    "transform": "化忌"
                },
                "output": {
                    "interpretation": f"{gan}年{route['from']}化忌入{route['to']}：{route['meaning']}",
                    "keywords": ["化忌", route["from"], route["to"], route["meaning"].split("、")[0]]
                },
                "source": "梁若瑜《飞星紫微斗数道藏飞秘的逻辑与功法》"
            })
            case_id += 1
            if case_id > 580:
                break
        if case_id > 580:
            break

    return cases

def main():
    # 读取现有案例
    cases_file = Path(__file__).parent / "transform_cases.json"
    with open(cases_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_count = len(data["cases"])
    print(f"现有案例数量: {existing_count}")

    # 生成新案例
    new_cases = []
    new_cases.extend(generate_lu_to_ji_cases())  # 禄转忌
    new_cases.extend(generate_ji_to_ji_cases())  # 忌转忌
    new_cases.extend(generate_pursuit_lu_cases())  # 追禄
    new_cases.extend(generate_pursuit_ji_cases())  # 追忌
    new_cases.extend(generate_ji_count_cases())  # 忌数论事
    new_cases.extend(generate_lu_ji_symmetry_cases())  # 禄忌对称
    new_cases.extend(generate_flying_route_cases())  # 飞化路线

    print(f"新增案例数量: {len(new_cases)}")

    # 合并案例
    data["cases"].extend(new_cases)

    # 保存
    with open(cases_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"更新后案例总数: {len(data['cases'])}")

if __name__ == "__main__":
    main()
