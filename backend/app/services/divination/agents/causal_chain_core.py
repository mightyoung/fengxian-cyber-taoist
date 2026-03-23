"""
因果链核心函数模块 - 紫微斗数因果分析核心算法

包含：
- 忌数强度评估
- 置信度计算
- 飞化目标计算
- 宫干计算
- 飞化路线计算
- 基础因果链分析函数
"""

from typing import Dict, List, TYPE_CHECKING

from .causal_chain_constants import (
    PALACE_NAMES,
    PALACE_INDEX,
    TransformType,
    SeverityLevel,
    CausalChainType,
    YEAR_STEM_TRANSFORMS,
    PALACE_GAN_TRANSFORMS,
    FLYING_ROUTES,
    DYNAMIC_FLYING_ROUTES,
)
from .causal_chain_types import FlyingPath, CausalChain

if TYPE_CHECKING:
    from .causal_chain_types import CausalChain as CausalChainType


def get_sanfang(palace: str) -> List[str]:
    """
    动态计算三方（不包含对宫）

    三方：相隔4宫和8宫的宫位
    公式：(宫位索引+4)%12, (宫位索引+8)%12

    Args:
        palace: 宫位名称

    Returns:
        三方宫位列表
    """
    idx = PALACE_INDEX.get(palace, 0)
    sanfang_indices = [(idx + 4) % 12, (idx + 8) % 12]
    return [PALACE_NAMES[i] for i in sanfang_indices]


def get_sizheng(palace: str) -> List[str]:
    """
    动态计算四正（三方+对宫）

    四正：三方 + 对宫
    公式：(宫位索引+4)%12, (宫位索引+6)%12, (宫位索引+8)%12

    Args:
        palace: 宫位名称

    Returns:
        四正宫位列表（含对宫）
    """
    idx = PALACE_INDEX.get(palace, 0)
    sicheng_indices = [(idx + 4) % 12, (idx + 6) % 12, (idx + 8) % 12]
    return [PALACE_NAMES[i] for i in sicheng_indices]


def get_duigong(palace: str) -> str:
    """
    动态计算对宫

    对宫：相隔6宫的宫位
    公式：(宫位索引+6)%12

    Args:
        palace: 宫位名称

    Returns:
        对宫名称
    """
    idx = PALACE_INDEX.get(palace, 0)
    return PALACE_NAMES[(idx + 6) % 12]


def count_ji_intensity(ji_count: int) -> SeverityLevel:
    """
    忌数强度评估

    Args:
        ji_count: 忌的数量

    Returns:
        SeverityLevel: 凶险等级
    """
    if ji_count == 0:
        return SeverityLevel.GOOD
    elif ji_count >= 4:
        return SeverityLevel.CATASTROPHIC
    elif ji_count == 3:
        return SeverityLevel.BAD
    elif ji_count == 2:
        return SeverityLevel.CONDITION
    else:
        return SeverityLevel.POTENTIAL


def calculate_causal_confidence(
    causal_chains: List['CausalChain'],
    ji_count: int,
    severity: SeverityLevel
) -> float:
    """
    计算因果链置信度

    基于王亭之中州派紫微斗数理论：
    【核心原则】忌越多=因果越明确=置信度越高
    - 0忌：因果模糊，难以判断 → 低置信度
    - 3+忌：因果链清晰明确 → 高置信度

    综合考虑：
    1. 因果链数量因子 (0-0.25): 链越多，分析越充分
    2. 忌数因子 (0-0.35): 王亭之理论核心 - 忌多=明确
    3. 严重等级因子 (0-0.25): 反映因果链的类型质量
    4. 链类型权重因子 (0-0.15): 每条链按类型质量加分

    Args:
        causal_chains: 因果链列表
        ji_count: 忌数
        severity: 整体凶险等级

    Returns:
        float: 置信度 (0.0-1.0)
    """
    # 1. 因果链数量因子 (0-0.25)
    chain_count = len(causal_chains)
    if chain_count == 0:
        chain_factor = 0.0
    elif 1 <= chain_count <= 3:
        chain_factor = 0.08
    elif 4 <= chain_count <= 6:
        chain_factor = 0.15
    elif 7 <= chain_count <= 10:
        chain_factor = 0.20
    else:  # 11+
        chain_factor = 0.25

    # 2. 忌数因子 (0-0.35) - 王亭之理论核心
    # 忌越多=因果越明确=置信度越高
    if ji_count == 0:
        ji_factor = 0.10  # 无忌=因果模糊
    elif ji_count == 1:
        ji_factor = 0.20  # 单忌=潜在
    elif ji_count == 2:
        ji_factor = 0.28  # 双忌=条件
    elif ji_count == 3:
        ji_factor = 0.32  # 三忌=确定
    else:  # 4+
        ji_factor = 0.35  # 多忌=重大因果

    # 3. 严重等级因子 (0-0.25) - 反映因果链类型质量
    # GOOD=因果平衡, BAD=因果明确, CATASTROPHIC=因果极明确
    severity_factor_map = {
        SeverityLevel.GOOD: 0.15,      # 因果平衡，难断
        SeverityLevel.POTENTIAL: 0.18,  # 潜在问题
        SeverityLevel.CONDITION: 0.20,  # 条件性问题
        SeverityLevel.BAD: 0.23,       # 因果明确
        SeverityLevel.CATASTROPHIC: 0.25  # 因果极明确
    }
    severity_factor = severity_factor_map.get(severity, 0.20)

    # 4. 链类型权重因子 (0-0.15)
    # 每条链按类型贡献加分
    chain_weight = 0.0
    for chain in causal_chains:
        if chain.chain_type.value in ["禄忌对称", "忌冲", "三忌汇聚"]:
            chain_weight += 0.05  # 核心因果链类型
        elif chain.chain_type.value in ["禄转忌", "忌转忌"]:
            chain_weight += 0.04  # 重要因果链
        elif chain.chain_type.value in ["忌入逢星", "忌入逢自化"]:
            chain_weight += 0.03  # 一般因果链
        else:
            chain_weight += 0.02  # 其他链
    chain_weight_factor = min(chain_weight, 0.15)  # 上限0.15

    # 汇总置信度
    confidence = chain_factor + ji_factor + severity_factor + chain_weight_factor

    # 确保在0.0-1.0范围内
    return max(0.0, min(1.0, confidence))


def get_flying_destinations(palace: str, transform_type: TransformType) -> List[str]:
    """
    获取飞化目标宫位（动态计算，根据本宫位调整）

    根据《中州派》紫微斗数理论，飞化路线应根据本宫位动态计算，
    而不是使用固定的万能路线。

    Args:
        palace: 本宫位
        transform_type: 四化类型

    Returns:
        List[str]: 飞化目标宫位列表
    """
    # 使用动态飞化路线表
    if palace in DYNAMIC_FLYING_ROUTES:
        route_key = transform_type.value
        if route_key in DYNAMIC_FLYING_ROUTES[palace]:
            return DYNAMIC_FLYING_ROUTES[palace][route_key]

    # 回退逻辑：如果不在动态表中，使用传统计算
    palace_idx = PALACE_INDEX.get(palace, 0)

    if transform_type == TransformType.HUA_JI:
        # 化忌飞化特殊规则：根据《飞星紫微斗数》理论
        # 化忌飞化到：对宫、三合方
        destinations = []
        # 对宫
        opposite_idx = (palace_idx + 6) % 12
        destinations.append(PALACE_NAMES[opposite_idx])
        # 三合方
        sanhe_indices = [(palace_idx + 4) % 12, (palace_idx + 8) % 12]
        destinations.extend([PALACE_NAMES[i] for i in sanhe_indices])
        return destinations
    else:
        # 禄权科飞化路线
        routes = FLYING_ROUTES.get(transform_type.value, [])
        return routes


def calculate_palace_stems(year_stem: str) -> Dict[str, str]:
    """
    根据年干计算各宫位的宫干

    宫干排法（紫微斗数基础规则）：
    - 命宫宫干 = 年干
    - 其他宫位按顺序递增

    Args:
        year_stem: 年干（甲、乙、丙、丁、戊、己、庚、辛、壬、癸）

    Returns:
        Dict[str, str]: 宫位到宫干的映射
    """
    gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    gan_index = gan_list.index(year_stem) if year_stem in gan_list else 0

    palace_stems = {}
    for i, palace in enumerate(PALACE_NAMES):
        palace_stems[palace] = gan_list[(gan_index + i) % 10]

    return palace_stems


def calculate_flying_paths(
    palace_stars: Dict[str, List[str]],
    year_stem: str
) -> List[FlyingPath]:
    """
    计算所有飞化路线（包括年干四化和宫干四化自化）

    Args:
        palace_stars: 宫位星曜映射 {宫位名: [星曜列表]}
        year_stem: 年干

    Returns:
        List[FlyingPath]: 飞化路径列表
    """
    paths = []
    transforms = YEAR_STEM_TRANSFORMS.get(year_stem, {})

    # 转换星曜名称列表（统一处理dict和string格式）
    def get_star_name(star) -> str:
        if isinstance(star, dict):
            return star.get("name", "")
        return str(star)

    # 获取四化星曜名称列表
    transform_star_names = list(transforms.values())

    # 找到每个化曜所在的宫位
    star_to_palace = {}
    for palace, stars in palace_stars.items():
        for star in stars:
            star_name = get_star_name(star)
            if star_name in transform_star_names:
                for t_type, t_star in transforms.items():
                    if star_name == t_star:
                        star_to_palace[star_name] = palace

    # 计算飞化路径（年干四化）
    for transform_type, star_name in transforms.items():
        if star_name not in star_to_palace:
            continue

        from_palace = star_to_palace[star_name]
        destinations = get_flying_destinations(from_palace, transform_type)

        for dest in destinations:
            # 包含自化路径（dest == from_palace）
            # 自化是重要因果链，用于检测本宫宫干化禄/忌入本宫的情况
            paths.append(FlyingPath(
                from_palace=from_palace,
                to_palace=dest,
                transform_type=transform_type,
                star_name=star_name
            ))

    # 计算宫干四化路径（自化逻辑）
    # 根据梁若瑜理论：本宫宫干化忌入本宫 = 自化
    palace_stems = calculate_palace_stems(year_stem)

    for palace, gan in palace_stems.items():
        gan_transforms = PALACE_GAN_TRANSFORMS.get(gan, {})

        for transform_type, star_name in gan_transforms.items():
            # 宫干四化：飞化的起点和终点都是本宫（自化）
            # 标记为"宫干自化"以便区分
            paths.append(FlyingPath(
                from_palace=palace,
                to_palace=palace,  # 自化：入本宫
                transform_type=transform_type,
                star_name=f"{gan}干{star_name}"  # 标记宫干四化
            ))

    return paths


def analyze_lu_zhuan_ji(
    flying_paths: List[FlyingPath],
    palace_stars: Dict[str, List[str]]
) -> List[CausalChain]:
    """
    分析禄转忌（得而复失）

    禄转忌定义（梁若瑜派）：禄在某宫化禄，然后忌从同一宫飞出，飞向另一宫。
    禄是因，忌是果，代表得而复失。

    注意：禄忌同入一宫（即禄和忌飞入同一宫）不是禄转忌，而是禄忌同宫。
    """
    chains = []
    lu_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_LU]
    ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

    for lu_path in lu_paths:
        for ji_path in ji_paths:
            # 禄转忌：禄和忌从同一宫飞出（from_palace相同），但飞向不同宫位
            # 这代表禄是因，忌是果 - 得而复失
            if lu_path.from_palace == ji_path.from_palace and lu_path.to_palace != ji_path.to_palace:
                chains.append(CausalChain(
                    chain_type=CausalChainType.LU_ZHUAN_JI,
                    palaces=[lu_path.from_palace, ji_path.to_palace],
                    transforms=[lu_path, ji_path],
                    severity=SeverityLevel.CONDITION,
                    description=f"{lu_path.star_name}化禄于{lu_path.from_palace}，后{ji_path.star_name}化忌自{ji_path.from_palace}飞入{ji_path.to_palace}，禄转忌得而复失"
                ))

    return chains


def analyze_ji_zhuan_ji(
    flying_paths: List[FlyingPath],
    palace_stars: Dict[str, List[str]]
) -> List[CausalChain]:
    """
    分析忌转忌（连续阻碍）

    本宫化忌，忌入某宫，该宫再化忌，形成连续的阻碍。
    根据梁若瑜《飞星紫微斗数》理论，必须同星曜才能契缘（祸不单行）。
    不同星曜的忌转忌，只是普通的因果延续，不是契缘。
    """
    chains = []
    ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

    for first_ji in ji_paths:
        for second_ji in ji_paths:
            # 检查是否形成连续的忌
            if first_ji.to_palace == second_ji.from_palace:
                # 梁若瑜派：必须同星曜才能契缘
                if first_ji.star_name == second_ji.star_name:
                    # 同星曜才算契缘，祸不单行
                    chains.append(CausalChain(
                        chain_type=CausalChainType.JI_ZHUAN_JI,
                        palaces=[first_ji.from_palace, first_ji.to_palace, second_ji.to_palace],
                        transforms=[first_ji, second_ji],
                        severity=SeverityLevel.CATASTROPHIC,
                        description=f"{first_ji.star_name}化忌于{first_ji.from_palace}冲{first_ji.to_palace}，"
                                    f"再{second_ji.star_name}化忌于{second_ji.from_palace}，同星曜契缘，祸不单行"
                    ))
                else:
                    # 不同星曜不算契缘，只是普通因果链
                    chains.append(CausalChain(
                        chain_type=CausalChainType.JI_ZHUAN_JI,
                        palaces=[first_ji.from_palace, first_ji.to_palace, second_ji.to_palace],
                        transforms=[first_ji, second_ji],
                        severity=SeverityLevel.BAD,
                        description=f"{first_ji.star_name}化忌于{first_ji.from_palace}冲{first_ji.to_palace}，"
                                    f"再{second_ji.star_name}化忌于{second_ji.from_palace}，不同星曜非契缘"
                    ))

    return chains


def analyze_lu_ji_tong_gong(
    flying_paths: List[FlyingPath],
    palace_stars: Dict[str, List[str]]
) -> List[CausalChain]:
    """
    分析禄忌同宫（得失参半）

    禄和忌同时飞入同一宫，代表得与失参半。
    """
    chains = []
    lu_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_LU]
    ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

    for lu_path in lu_paths:
        for ji_path in ji_paths:
            # 禄忌同宫：禄和忌飞入同一宫（to_palace相同）
            if lu_path.to_palace == ji_path.to_palace:
                chains.append(CausalChain(
                    chain_type=CausalChainType.LU_JI_TONG_GONG,
                    palaces=[lu_path.to_palace],
                    transforms=[lu_path, ji_path],
                    severity=SeverityLevel.CONDITION,
                    description=f"{lu_path.star_name}化禄与{ji_path.star_name}化忌同入{lu_path.to_palace}，得失参半"
                ))

    return chains


def analyze_san_ji_hui_ju(
    flying_paths: List[FlyingPath],
    palace_stars: Dict[str, List[str]]
) -> List[CausalChain]:
    """
    分析三忌汇聚（大凶之兆）

    三个或以上的忌飞入同一宫，代表大凶之兆。
    根据梁若瑜理论，这是宫位串联，不是简单的数量累计。
    """
    chains = []
    ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

    # 按目标宫位统计忌的数量
    ji_by_dest: Dict[str, List[FlyingPath]] = {}
    for p in ji_paths:
        if p.to_palace not in ji_by_dest:
            ji_by_dest[p.to_palace] = []
        ji_by_dest[p.to_palace].append(p)

    # 找出三忌及以上的宫位
    for palace, paths in ji_by_dest.items():
        if len(paths) >= 3:
            # 分离年干四化和宫干自化
            nian_gan_ji = [p for p in paths if not p.star_name.startswith("干")]
            gong_gan_zi = [p for p in paths if p.star_name.startswith("干")]

            desc_parts = []
            if nian_gan_ji:
                star_names = ", ".join([p.star_name for p in nian_gan_ji])
                desc_parts.append(f"年干四化忌：{star_names}")
            if gong_gan_zi:
                star_names = ", ".join([p.star_name for p in gong_gan_zi])
                desc_parts.append(f"宫干自化忌：{star_names}")

            chains.append(CausalChain(
                chain_type=CausalChainType.SAN_JI_HUI_JU,
                palaces=[palace],
                transforms=paths,
                severity=SeverityLevel.CATASTROPHIC,
                description=f"三忌汇聚{palace}，{'；'.join(desc_parts)}，大凶之兆"
            ))

    return chains


def analyze_ji_chong_palaces(
    flying_paths: List[FlyingPath],
    palace_stars: Dict[str, List[str]]
) -> List[CausalChain]:
    """
    分析忌冲宫位（命宫、迁移宫）

    化忌飞入命宫或迁移宫，代表该宫位受冲。
    """
    chains = []
    ji_paths = [p for p in flying_paths if p.transform_type == TransformType.HUA_JI]

    for p in ji_paths:
        if p.to_palace == "命宫":
            chains.append(CausalChain(
                chain_type=CausalChainType.JI_CHONG_MING,
                palaces=[p.from_palace, "命宫"],
                transforms=[p],
                severity=SeverityLevel.BAD,
                description=f"{p.star_name}化忌冲命宫"
            ))
        elif p.to_palace == "迁移宫":
            chains.append(CausalChain(
                chain_type=CausalChainType.JI_CHONG_YI,
                palaces=[p.from_palace, "迁移宫"],
                transforms=[p],
                severity=SeverityLevel.BAD,
                description=f"{p.star_name}化忌冲迁移宫"
            ))

    return chains
