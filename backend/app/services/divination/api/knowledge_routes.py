"""
Knowledge Routes - 知识库相关路由

提供星曜、宫位、格局、四化等知识库的查询API接口。
"""

import json
import os
from functools import lru_cache
from typing import Dict, Any, Optional

from flask import Blueprint, request, jsonify

from app.services.divination.api.common import DATA_BASE_PATH

# Create blueprint for knowledge routes
knowledge_routes_bp = Blueprint('knowledge_routes', __name__, url_prefix='')

# 缓存装饰器
def _cached_json_loader(file_path: str) -> Dict[str, Any]:
    """带缓存的JSON文件加载器"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@lru_cache(maxsize=32)
def _load_stars_data() -> Dict[str, Any]:
    """加载星曜数据（带缓存）"""
    file_path = os.path.join(DATA_BASE_PATH, 'metadata', 'stars-attributes.json')
    return _cached_json_loader(file_path)


@lru_cache(maxsize=32)
def _load_palaces_data() -> Dict[str, Any]:
    """加载宫位数据（带缓存）"""
    file_path = os.path.join(DATA_BASE_PATH, 'metadata', 'palaces-attributes.json')
    return _cached_json_loader(file_path)


@lru_cache(maxsize=32)
def _load_patterns_index() -> Dict[str, Any]:
    """加载格局索引（带缓存）"""
    file_path = os.path.join(DATA_BASE_PATH, 'knowledge', 'patterns', 'index.json')
    return _cached_json_loader(file_path)


def _load_all_patterns() -> list:
    """加载所有格局数据"""
    patterns = []
    index_data = _load_patterns_index()

    for category in index_data.get('categories', []):
        category_file = category.get('file')
        if category_file and category_file != 'pattern-concepts.json':
            file_path = os.path.join(DATA_BASE_PATH, 'knowledge', 'patterns', category_file)
            try:
                data = _cached_json_loader(file_path)
                patterns.extend(data.get('patterns', []))
            except FileNotFoundError:
                continue
    return patterns


@lru_cache(maxsize=128)
def _load_transform_data(palace: str) -> Optional[Dict[str, Any]]:
    """加载指定宫位的四化数据（带缓存）"""
    # 映射宫位名到文件名
    palace_mapping = {
        '命宫': '命宫四化.json',
        '兄弟宫': '兄弟宫四化.json',
        '夫妻宫': '夫妻宫四化.json',
        '子女宫': '子女宫四化.json',
        '财帛宫': '财帛宫四化.json',
        '疾厄宫': '疾厄宫四化.json',
        '迁移宫': '迁移宫四化.json',
        '交友宫': '交友宫四化.json',
        '官禄宫': '官禄宫四化.json',
        '田宅宫': '田宅宫四化.json',
        '福德宫': '福德宫四化.json',
        '父母宫': '父母宫四化.json',
    }

    file_name = palace_mapping.get(palace)
    if not file_name:
        return None

    file_path = os.path.join(DATA_BASE_PATH, 'rules', 'transformations', file_name)
    try:
        return _cached_json_loader(file_path)
    except FileNotFoundError:
        return None


@knowledge_routes_bp.route('/stars/<star_name>', methods=['GET'])
def get_star_info(star_name: str):
    """
    获取星曜详情

    URL Parameters:
        star_name: 星曜名称（如：紫微、天机、贪狼等）

    Returns:
        {
            "success": true,
            "data": {
                "name": "紫微星",
                "wuxing": "土",
                "yinyang": "阳",
                "huàqì": "化气为权",
                "meaning": "紫微星代表...",
                "miáoxiàn": {
                    "庙": ["子", "丑", "午"],
                    "旺": ["寅", "卯", "辰"],
                    "陷": ["申", "酉"]
                }
            }
        }
    """
    try:
        stars_data = _load_stars_data()
        stars = stars_data.get('stars', [])

        # 查找匹配的星曜
        for star in stars:
            if star.get('name') == star_name:
                attrs = star.get('attributes', {})

                # 提取庙旺利陷信息
                brightness = attrs.get('brightness_levels', {})
                result = {
                    'name': star.get('name'),
                    'system': star.get('system'),
                    'category': star.get('category'),
                    'wuxing': attrs.get('五行', ''),
                    'yinyang': attrs.get('阴阳', ''),
                    'huàqì': attrs.get('化气', ''),
                    'meaning': star.get('meaning', ''),
                    'miáoxiàn': {
                        '庙': brightness.get('庙', []),
                        '旺': brightness.get('旺', []),
                        '地': brightness.get('地', []),
                        '利': brightness.get('利', []),
                        '陷': brightness.get('陷', [])
                    }
                }
                return jsonify({
                    'success': True,
                    'data': result
                })

        return jsonify({
            'success': False,
            'error': f'未找到星曜: {star_name}'
        }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取星曜信息时出错: {str(e)}'
        }), 500


@knowledge_routes_bp.route('/palaces/<palace_name>', methods=['GET'])
def get_palace_info(palace_name: str):
    """
    获取宫位详情

    URL Parameters:
        palace_name: 宫位名称（如：命宫、夫妻宫、官禄宫等）

    Returns:
        {
            "success": true,
            "data": {
                "name": "命宫",
                "branch": "子",
                "meaning": "主掌自我、性格、先天运势",
                "relationships": {
                    "对立": "迁移宫",
                    "会照": ["财帛宫", "官禄宫"],
                    "三方": ["财帛宫", "官禄宫", "迁移宫"]
                }
            }
        }
    """
    try:
        palaces_data = _load_palaces_data()
        palaces = palaces_data.get('palaces', [])

        # 查找匹配的宫位
        for palace in palaces:
            if palace.get('name') == palace_name:
                attrs = palace.get('attributes', {})

                result = {
                    'name': palace.get('name'),
                    'pinyin': palace.get('pinyin'),
                    'branch': attrs.get('五行', ''),
                    'dìzhī': palace.get('relationships', {}),
                    'meaning': attrs.get('主掌', ''),
                    'attributes': {
                        'yinyang': attrs.get('阴阳', ''),
                        'wuxing': attrs.get('五行', ''),
                        'type': attrs.get('属性', '')
                    },
                    'relationships': palace.get('relationships', {})
                }
                return jsonify({
                    'success': True,
                    'data': result
                })

        return jsonify({
            'success': False,
            'error': f'未找到宫位: {palace_name}'
        }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取宫位信息时出错: {str(e)}'
        }), 500


@knowledge_routes_bp.route('/patterns/<pattern_name>', methods=['GET'])
def get_pattern_info(pattern_name: str):
    """
    获取格局详情

    URL Parameters:
        pattern_name: 格局名称（如：君臣庆会格、三奇嘉会格等）

    Returns:
        {
            "success": true,
            "data": {
                "name": "君臣庆会格",
                "category": "吉格",
                "quality": "A+",
                "description": "紫微坐命，府相三方来朝，六吉各会一半",
                "conditions": {...},
                "effects": [...]
            }
        }
    """
    try:
        patterns = _load_all_patterns()

        # 查找匹配的格局
        for pattern in patterns:
            # 支持名称和别名匹配
            if pattern.get('name') == pattern_name or pattern_name in pattern.get('aliases', []):
                result = {
                    'id': pattern.get('id'),
                    'name': pattern.get('name'),
                    'aliases': pattern.get('aliases', []),
                    'category': pattern.get('category'),
                    'quality': pattern.get('quality'),
                    'source': pattern.get('source'),
                    'description': pattern.get('description'),
                    'conditions': pattern.get('conditions', {}),
                    'effects': pattern.get('effects', []),
                    'combinations': pattern.get('combinations', []),
                    'notes': pattern.get('notes', '')
                }
                return jsonify({
                    'success': True,
                    'data': result
                })

        return jsonify({
            'success': False,
            'error': f'未找到格局: {pattern_name}'
        }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取格局信息时出错: {str(e)}'
        }), 500


@knowledge_routes_bp.route('/transforms/<path:palace>/<transform_type>', methods=['GET'])
def get_transform_interpretation(palace: str, transform_type: str):
    """
    获取四化解读

    URL Parameters:
        palace: 宫位名称（如：命宫、夫妻宫等）
        transform_type: 四化类型（禄、权、科、忌）

    Returns:
        {
            "success": true,
            "data": {
                "palace": "命宫",
                "type": "禄",
                "effects": [
                    "主福。一生少忧，衣食无虞。",
                    "通情达理，随缘不固执。好心情。"
                ]
            }
        }
    """
    try:
        # 处理URL编码的中文
        palace = palace.replace('%20', ' ')

        # 加载四化数据
        transform_data = _load_transform_data(palace)

        if not transform_data:
            return jsonify({
                'success': False,
                'error': f'未找到宫位: {palace}'
            }), 404

        # 数据结构是 transform_data['transformations'] 列表
        transformations = transform_data.get('transformations', [])

        # 查找对应类型的解读
        for item in transformations:
            if item.get('type') == transform_type:
                return jsonify({
                    'success': True,
                    'data': {
                        'palace': palace,
                        'type': transform_type,
                        'category': item.get('category', ''),
                        'effects': item.get('effects', [])
                        }
                    })

        return jsonify({
            'success': False,
            'error': f'未找到四化类型: {transform_type}'
        }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取四化解读时出错: {str(e)}'
        }), 500


@knowledge_routes_bp.route('/search', methods=['GET'])
def search_knowledge():
    """
    知识库全文搜索

    Query Parameters:
        q: 搜索关键词（星曜名称、格局名称等）
        type: 可选，限定搜索类型 (star/pattern/palace/transform/all)

    Returns:
        {
            "success": true,
            "data": {
                "query": "紫微",
                "type": "all",
                "results": {
                    "stars": [...],
                    "patterns": [...],
                    "palaces": [...]
                },
                "total": 5
            }
        }
    """
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all').lower()

        if not query:
            return jsonify({
                'success': False,
                'error': '搜索关键词不能为空'
            }), 400

        results = {
            'stars': [],
            'patterns': [],
            'palaces': [],
            'transforms': []
        }

        # 搜索星曜
        if search_type in ('all', 'star'):
            stars_data = _load_stars_data()
            stars = stars_data.get('stars', [])
            query_lower = query.lower()
            for star in stars:
                star_name = star.get('name', '')
                attrs = star.get('attributes', {})
                # 匹配名称或关键词
                if (query_lower in star_name.lower() or
                    query_lower in attrs.get('化气', '').lower() or
                    query_lower in star.get('meaning', '').lower()):
                    results['stars'].append({
                        'name': star_name,
                        'system': star.get('system'),
                        'category': star.get('category'),
                        'wuxing': attrs.get('五行', ''),
                        'yinyang': attrs.get('阴阳', ''),
                        'huàqì': attrs.get('化气', ''),
                        'meaning': star.get('meaning', '')
                    })

        # 搜索格局
        if search_type in ('all', 'pattern'):
            patterns = _load_all_patterns()
            query_lower = query.lower()
            for pattern in patterns:
                pattern_name = pattern.get('name', '')
                aliases = pattern.get('aliases', [])
                description = pattern.get('description', '')
                # 匹配名称、别名或描述
                if (query_lower in pattern_name.lower() or
                    any(query_lower in alias.lower() for alias in aliases) or
                    query_lower in description.lower()):
                    results['patterns'].append({
                        'name': pattern_name,
                        'aliases': aliases,
                        'category': pattern.get('category'),
                        'quality': pattern.get('quality'),
                        'description': description
                    })

        # 搜索宫位
        if search_type in ('all', 'palace'):
            palaces_data = _load_palaces_data()
            palaces = palaces_data.get('palaces', [])
            query_lower = query.lower()
            for palace in palaces:
                palace_name = palace.get('name', '')
                pinyin = palace.get('pinyin', '')
                attrs = palace.get('attributes', {})
                meaning = attrs.get('主掌', '')
                # 匹配名称、拼音或含义
                if (query_lower in palace_name.lower() or
                    query_lower in pinyin.lower() or
                    query_lower in meaning.lower()):
                    results['palaces'].append({
                        'name': palace_name,
                        'pinyin': pinyin,
                        'meaning': meaning,
                        'attributes': {
                            'yinYang': attrs.get('阴阳', ''),
                            'wuxing': attrs.get('五行', ''),
                            'type': attrs.get('属性', '')
                        }
                    })

        # 计算总数
        total = sum(len(results[k]) for k in results)

        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'type': search_type,
                'results': results,
                'total': total
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'搜索时出错: {str(e)}'
        }), 500


@knowledge_routes_bp.route('/siyin/<system_id>', methods=['GET'])
def get_siyin_info(system_id: str):
    """
    获取六十星系统一详情

    URL Parameters:
        system_id: 星系统一ID（如：ziwei_tianji_01）

    Returns:
        {
            "success": true,
            "data": {
                "id": "ziwei_tianji_01",
                "name": "紫微天机组合",
                "main_star": "紫微",
                "secondary_stars": ["天机"],
                "palace_requirements": "命宫",
                "characteristics": "...",
                "positive_aspects": [...],
                "negative_aspects": [...]
            }
        }
    """
    try:
        from app.services.divination.agents.siyin_loader import SiyinLoader
        loader = SiyinLoader()

        # 尝试按ID查找
        system = loader.get_system_by_id(system_id)

        # 如果没找到，尝试按名称查找
        if not system:
            system = loader.get_system_by_name(system_id)

        if not system:
            return jsonify({
                'success': False,
                'error': f'未找到星系统一: {system_id}'
            }), 404

        return jsonify({
            'success': True,
            'data': system
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取星系统一时出错: {str(e)}'
        }), 500


@knowledge_routes_bp.route('/siyin', methods=['GET'])
def list_siyin_systems():
    """
    获取所有六十星系统一列表

    Query Parameters:
        main_star: 可选，按主星筛选

    Returns:
        {
            "success": true,
            "data": {
                "systems": [...],
                "total": 60
            }
        }
    """
    try:
        from app.services.divination.agents.siyin_loader import SiyinLoader
        loader = SiyinLoader()

        main_star = request.args.get('main_star', '').strip()

        systems = loader.get_all_systems()

        # 按主星筛选
        if main_star:
            systems = [s for s in systems if s.get('main_star') == main_star]

        return jsonify({
            'success': True,
            'data': {
                'systems': systems,
                'total': len(systems)
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取星系统一列表时出错: {str(e)}'
        }), 500


@knowledge_routes_bp.route('/health', methods=['GET'])
def knowledge_health():
    """知识库API健康检查"""
    return jsonify({
        "status": "ok",
        "service": "knowledge-api"
    })
