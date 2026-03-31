"""
Specialized Routes - 专业分析路由

提供剖腹产良辰吉日、择日、事件预测、姻缘配对、职业推荐、姓名推荐等专业化API接口。
"""

from flask import Blueprint, request, jsonify

from app.services.divination.agents.birth_timing_agent import analyze_birth_timing_sync
from app.services.divination.agents.date_selection_agent import select_date_sync
from app.services.divination.agents.event_predictor_agent import predict_event_sync
from app.services.divination.agents.marriage_compatibility_agent import analyze_marriage_compatibility_sync
from app.services.divination.agents.career_recommendation_agent import recommend_career_sync
from app.services.divination.agents.name_recommendation_agent import recommend_name_sync
from app.models.divination import DivinationManager

# Create blueprint for specialized routes
specialized_bp = Blueprint('specialized', __name__, url_prefix='')


@specialized_bp.route('/birth-timing/analyze', methods=['POST'])
def analyze_birth_timing():
    """
    剖腹产良辰吉日分析

    Request Body:
        {
            "mother_birth": {
                "year": 1990, "month": 5, "day": 15, "hour": 10,
                "minute": 0, "gender": "female", "birthplace": "北京",
                "is_lunar": false
            },
            "father_birth": {
                "year": 1988, "month": 3, "day": 20, "hour": 14,
                "minute": 30, "gender": "male", "birthplace": "北京",
                "is_lunar": false
            },
            "target_year": 2026,
            "target_month": 8,
            "num_options": 5
        }

    Returns:
        {
            "success": true,
            "data": { ... }  // analyze_birth_timing_sync 返回的完整结果
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        mother_birth = data.get('mother_birth')
        father_birth = data.get('father_birth')
        target_year = data.get('target_year')
        target_month = data.get('target_month')
        num_options = data.get('num_options', 5)

        if not mother_birth:
            return jsonify({
                "success": False,
                "error": "缺少必需字段: mother_birth"
            }), 400

        if not father_birth:
            return jsonify({
                "success": False,
                "error": "缺少必需字段: father_birth"
            }), 400

        if not target_year or not target_month:
            return jsonify({
                "success": False,
                "error": "缺少必需字段: target_year 和 target_month"
            }), 400

        result = analyze_birth_timing_sync(
            mother_birth=mother_birth,
            father_birth=father_birth,
            target_year=target_year,
            target_month=target_month,
            num_options=num_options
        )

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"剖腹产良辰吉日分析时出错: {str(e)}"
        }), 500


@specialized_bp.route('/date-selection/analyze', methods=['POST'])
def analyze_date_selection():
    """
    择日分析（结婚、搬家、开业等）

    Request Body:
        {
            "chart_id": "uuid",  // optional
            "chart": { ... },     // optional
            "event_type": "结婚嫁娶",
            "start_date": "2026-04-01",
            "end_date": "2026-04-30",
            "num_options": 5
        }

    Returns:
        {
            "success": true,
            "data": { ... }  // select_date_sync 返回的完整结果
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        event_type = data.get('event_type')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        num_options = data.get('num_options', 5)

        if not event_type:
            return jsonify({
                "success": False,
                "error": "缺少必需字段: event_type"
            }), 400

        if not start_date or not end_date:
            return jsonify({
                "success": False,
                "error": "缺少必需字段: start_date 和 end_date"
            }), 400

        chart_data = None
        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if chart:
                chart_data = chart.chart_data
        else:
            chart_data = data.get('chart')

        result = select_date_sync(
            chart=chart_data,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            num_options=num_options
        )

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"择日分析时出错: {str(e)}"
        }), 500


@specialized_bp.route('/event-predict/analyze', methods=['POST'])
def analyze_event_predict():
    """
    事件成功率分析

    Request Body:
        {
            "chart_id": "uuid",  // optional
            "chart": { ... },     // optional
            "event_type": "跳槽",
            "target_year": 2026,
            "description": "计划跳槽到新公司"
        }

    Returns:
        {
            "success": true,
            "data": { ... }  // predict_event_sync 返回的完整结果
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        event_type = data.get('event_type')
        target_year = data.get('target_year')
        description = data.get('description', '')

        if not event_type:
            return jsonify({
                "success": False,
                "error": "缺少必需字段: event_type"
            }), 400

        if not target_year:
            return jsonify({
                "success": False,
                "error": "缺少必需字段: target_year"
            }), 400

        chart_data = None
        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if chart:
                chart_data = chart.chart_data
        else:
            chart_data = data.get('chart')

        result = predict_event_sync(
            chart=chart_data,
            event_type=event_type,
            target_year=target_year,
            description=description
        )

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"事件成功率分析时出错: {str(e)}"
        }), 500


@specialized_bp.route('/marriage-compatibility/analyze', methods=['POST'])
def analyze_marriage_compatibility():
    """
    姻缘配对分析

    Request Body:
        {
            "male_birth": {
                "year": 1990, "month": 5, "day": 15, "hour": 10,
                "minute": 0, "gender": "male", "birthplace": "北京",
                "is_lunar": false
            },
            "female_birth": {
                "year": 1992, "month": 8, "day": 20, "hour": 15,
                "minute": 30, "gender": "female", "birthplace": "上海",
                "is_lunar": false
            }
        }

    Returns:
        {
            "success": true,
            "data": { ... }  // analyze_marriage_compatibility_sync 返回的完整结果
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        male_birth = data.get('male_birth')
        female_birth = data.get('female_birth')

        if not male_birth:
            return jsonify({
                "success": False,
                "error": "缺少必需字段: male_birth"
            }), 400

        if not female_birth:
            return jsonify({
                "success": False,
                "error": "缺少必需字段: female_birth"
            }), 400

        # 将出生数据转换为命盘数据
        from app.services.divination.agents.chart_agent import generate_chart_sync
        chart_a = generate_chart_sync(
            year=male_birth['year'],
            month=male_birth['month'],
            day=male_birth['day'],
            hour=male_birth['hour'],
            gender=male_birth['gender'],
            minute=male_birth.get('minute', 0),
            birthplace=male_birth.get('birthplace', ''),
            is_lunar=male_birth.get('is_lunar', False)
        )
        chart_b = generate_chart_sync(
            year=female_birth['year'],
            month=female_birth['month'],
            day=female_birth['day'],
            hour=female_birth['hour'],
            gender=female_birth['gender'],
            minute=female_birth.get('minute', 0),
            birthplace=female_birth.get('birthplace', ''),
            is_lunar=female_birth.get('is_lunar', False)
        )

        result = analyze_marriage_compatibility_sync(
            chart_a=chart_a,
            chart_b=chart_b,
            name_a="甲方",
            name_b="乙方"
        )

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"姻缘配对分析时出错: {str(e)}"
        }), 500


@specialized_bp.route('/career-recommendation/analyze', methods=['POST'])
def analyze_career_recommendation():
    """
    职业推荐分析

    Request Body:
        {
            "chart_id": "uuid",  // optional
            "chart": { ... },     // optional
            "education_level": "本科",
            "current_industry": "互联网",
            "work_experience_years": 3
        }

    Returns:
        {
            "success": true,
            "data": { ... }  // recommend_career_sync 返回的完整结果
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        education_level = data.get('education_level', '')
        current_industry = data.get('current_industry', '')

        chart_data = None
        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if chart:
                chart_data = chart.chart_data
        else:
            chart_data = data.get('chart')

        result = recommend_career_sync(
            chart=chart_data,
            education_level=education_level,
            current_career=current_industry
        )

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"职业推荐分析时出错: {str(e)}"
        }), 500


@specialized_bp.route('/name-recommendation/analyze', methods=['POST'])
def analyze_name_recommendation():
    """
    改名起名推荐

    Request Body:
        {
            "chart_id": "uuid",  // optional
            "chart": { ... },     // optional
            "gender": "female",
            "family_name": "李",
            "num_options": 10
        }

    Returns:
        {
            "success": true,
            "data": { ... }  // recommend_name_sync 返回的完整结果
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400

        gender = data.get('gender')
        family_name = data.get('family_name', '')
        num_options = data.get('num_options', 10)

        if not gender:
            return jsonify({
                "success": False,
                "error": "缺少必需字段: gender"
            }), 400

        chart_data = None
        chart_id = data.get('chart_id')
        if chart_id:
            chart = DivinationManager.get_chart(chart_id)
            if chart:
                chart_data = chart.chart_data
        else:
            chart_data = data.get('chart')

        result = recommend_name_sync(
            chart=chart_data,
            gender=gender,
            family_name=family_name,
            num_options=num_options
        )

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"改名起名推荐时出错: {str(e)}"
        }), 500
