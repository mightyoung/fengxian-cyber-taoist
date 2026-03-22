"""
E2E Real LLM Function Tests

Tests all 5 LLM functions with REAL LLM calls (not mocked):
1. llm_analyze_synthesis_sync - in synthesis_agent.py
2. llm_analyze_birth_timing_sync - in birth_timing_agent.py
3. llm_analyze_marriage_compatibility_sync - in marriage_compatibility_agent.py
4. llm_analyze_event_predict_sync - in event_predictor_agent.py
5. llm_analyze_date_selection_sync - in date_selection_agent.py

Run with: .venv/bin/python tests/e2e/test_real_llm_functions.py
"""

import sys
import os

# Ensure backend dir is in path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import json
from datetime import datetime

# ============ Test Data ============

# Sample chart data for synthesis, event_predict, date_selection
SAMPLE_CHART_DATA = {
    "birth_info": {
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 10,
        "gender": "male",
        "wuxing_ju": "水二局"
    },
    "palaces": {
        "命宫": {
            "branch": "子",
            "tiangan": "甲",
            "stars": [
                {"name": "紫微", "type": "正曜", "level": "旺"},
                {"name": "天机", "type": "正曜", "level": "平"},
                {"name": "左辅", "type": "辅星", "level": "旺"}
            ]
        },
        "兄弟宫": {"branch": "丑", "tiangan": "乙", "stars": []},
        "夫妻宫": {
            "branch": "寅",
            "tiangan": "丙",
            "stars": [{"name": "贪狼", "type": "正曜", "level": "庙"}]
        },
        "子女宫": {"branch": "卯", "tiangan": "丁", "stars": []},
        "财帛宫": {
            "branch": "辰",
            "tiangan": "戊",
            "stars": [{"name": "太阳", "type": "正曜", "level": "旺"}]
        },
        "疾厄宫": {"branch": "巳", "tiangan": "己", "stars": []},
        "迁移宫": {"branch": "午", "tiangan": "庚", "stars": []},
        "仆役宫": {"branch": "未", "tiangan": "辛", "stars": []},
        "官禄宫": {
            "branch": "申",
            "tiangan": "壬",
            "stars": [{"name": "天府", "type": "正曜", "level": "旺"}]
        },
        "田宅宫": {"branch": "酉", "tiangan": "癸", "stars": []},
        "父母宫": {"branch": "戌", "tiangan": "甲", "stars": []},
        "福德宫": {"branch": "亥", "tiangan": "乙", "stars": []}
    },
    "stars": {
        "main_stars": [
            {"name": "紫微", "palace": "命宫", "level": "旺"},
            {"name": "天机", "palace": "命宫", "level": "平"},
            {"name": "太阳", "palace": "财帛宫", "level": "旺"},
            {"name": "天府", "palace": "官禄宫", "level": "旺"},
            {"name": "贪狼", "palace": "夫妻宫", "level": "庙"}
        ],
        "auxiliary_stars": [{"name": "左辅", "palace": "命宫", "level": "旺"}],
        "sha_stars": [],
        "transform_stars": []
    },
    "transforms": [
        {"type": "禄", "star": "廉贞", "palace": "财帛宫"},
        {"type": "权", "star": "紫微", "palace": "官禄宫"},
        {"type": "忌", "star": "廉贞", "palace": "福德宫"}
    ],
    "flowing_year": {"year": 2025, "score": 72},
    "flowing_month": {"month": 3, "score": 68}
}

SAMPLE_ANALYSIS_DATA = {
    "star_analysis": {
        "summary": "命宫紫微天机会照，具备领导才能和智慧。贪狼在夫妻宫旺位，感情方面有活力。"
    },
    "palace_analysis": {
        "summary": "命宫、财帛宫、官禄宫皆为强宫，事业财运有基础。"
    },
    "pattern_analysis": {
        "summary": "紫微天府坐命，代表领导才能和财运基础。"
    },
    "transform_analysis": {
        "summary": "廉贞化禄在财帛宫，财运转佳；紫微化权在官禄宫，事业发展有权力。"
    }
}

# Chart A for marriage
CHART_A = {
    "birth_info": {"year": 1990, "month": 5, "day": 15, "hour": 10, "gender": "male"},
    "palaces": {
        "命宫": {"stars": [{"name": "天同"}, {"name": "贪狼"}]},
        "夫妻宫": {"stars": [{"name": "天相"}]},
        "财帛宫": {"stars": [{"name": "武曲"}]},
        "官禄宫": {"stars": [{"name": "紫微"}]},
        "迁移宫": {"stars": [{"name": "太阳"}]},
        "福德宫": {"stars": []},
        "疾厄宫": {"stars": []},
    },
    "transforms": [
        {"type": "化禄", "star": "贪狼", "to_palace": "财帛宫"},
        {"type": "化权", "star": "武曲", "to_palace": "官禄宫"},
    ],
}

# Chart B for marriage
CHART_B = {
    "birth_info": {"year": 1992, "month": 8, "day": 20, "hour": 14, "gender": "female"},
    "palaces": {
        "命宫": {"stars": [{"name": "紫微"}, {"name": "天府"}]},
        "夫妻宫": {"stars": [{"name": "天机"}]},
        "财帛宫": {"stars": [{"name": "太阳"}]},
        "官禄宫": {"stars": [{"name": "天机"}]},
        "迁移宫": {"stars": [{"name": "天同"}]},
        "福德宫": {"stars": []},
        "疾厄宫": {"stars": []},
    },
    "transforms": [
        {"type": "化科", "star": "紫微", "to_palace": "官禄宫"},
        {"type": "化忌", "star": "天机", "to_palace": "夫妻宫"},
    ],
}

# Mother info for birth timing
MOTHER_INFO = {
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 10,
    "gender": "female",
    "birthplace": "北京",
}

# Daily options for date selection
DAILY_OPTIONS = [
    {
        "rank": 1,
        "solar_date": "2026-04-15",
        "lunar_date": "三月十九",
        "tiangan": "丙寅",
        "dizhi": "寅",
        "score": 78.0,
        "level": "良好",
        "is_auspicious": True,
        "suitable_for": ["结婚", "搬家", "祭祀"],
        "avoid": ["动土"],
        "key_factors": ["木火相生", "命宫能量加持"],
        "best_time_window": "巳时（09:00-11:00）",
        "warnings": [],
    },
    {
        "rank": 2,
        "solar_date": "2026-04-18",
        "lunar_date": "三月廿二",
        "tiangan": "己巳",
        "dizhi": "巳",
        "score": 75.0,
        "level": "良好",
        "is_auspicious": True,
        "suitable_for": ["结婚", "出行"],
        "avoid": [],
        "key_factors": ["巳火为命宫禄位"],
        "best_time_window": "午时（11:00-13:00）",
        "warnings": [],
    },
]


# ============ Test Functions ============

def test_synthesis():
    """Test 1: llm_analyze_synthesis_sync"""
    print("\n" + "=" * 60)
    print("TEST 1: llm_analyze_synthesis_sync")
    print("=" * 60)

    from app.services.divination.agents.synthesis_agent import llm_analyze_synthesis_sync

    try:
        result = llm_analyze_synthesis_sync(
            chart_data=SAMPLE_CHART_DATA,
            analysis_data=SAMPLE_ANALYSIS_DATA,
            question="请分析这个命盘的事业运势"
        )
        print(f"\nSUCCESS!")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        print(f"\nResult preview (first 500 chars):")
        result_str = json.dumps(result, ensure_ascii=False, indent=2)
        print(result_str[:500] if len(result_str) > 500 else result_str)
        return True, result
    except Exception as e:
        print(f"\nFAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def test_birth_timing():
    """Test 2: llm_analyze_birth_timing_sync"""
    print("\n" + "=" * 60)
    print("TEST 2: llm_analyze_birth_timing_sync")
    print("=" * 60)

    from app.services.divination.agents.birth_timing_agent import (
        analyze_birth_timing_sync,
        llm_analyze_birth_timing_sync,
    )

    try:
        # First run the rule-based analysis to get BirthTimingResult
        timing_result = analyze_birth_timing_sync(
            mother_birth_info=MOTHER_INFO,
            father_birth_info=None,
            date_range_start="2026-04-01",
            date_range_end="2026-04-02",
            top_n=3,
        )
        print(f"Rule-based analysis complete. Options count: {len(timing_result.options)}")

        # Then run LLM analysis
        result = llm_analyze_birth_timing_sync(
            birth_timing_result=timing_result,
            mother_chart=None,
            father_chart=None,
            question="请推荐最佳剖腹产时间并说明理由"
        )
        print(f"\nSUCCESS!")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        print(f"\nResult preview (first 500 chars):")
        result_str = json.dumps(result, ensure_ascii=False, indent=2)
        print(result_str[:500] if len(result_str) > 500 else result_str)
        return True, result
    except Exception as e:
        print(f"\nFAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def test_marriage_compatibility():
    """Test 3: llm_analyze_marriage_compatibility_sync"""
    print("\n" + "=" * 60)
    print("TEST 3: llm_analyze_marriage_compatibility_sync")
    print("=" * 60)

    from app.services.divination.agents.marriage_compatibility_agent import (
        llm_analyze_marriage_compatibility_sync,
    )

    try:
        result = llm_analyze_marriage_compatibility_sync(
            chart_a=CHART_A,
            chart_b=CHART_B,
            name_a="张三",
            name_b="李四",
            question="请分析我们的姻缘配对情况和最佳结婚时机"
        )
        print(f"\nSUCCESS!")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        print(f"\nResult preview (first 500 chars):")
        result_str = json.dumps(result, ensure_ascii=False, indent=2)
        print(result_str[:500] if len(result_str) > 500 else result_str)
        return True, result
    except Exception as e:
        print(f"\nFAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def test_event_predict():
    """Test 4: llm_analyze_event_predict_sync"""
    print("\n" + "=" * 60)
    print("TEST 4: llm_analyze_event_predict_sync")
    print("=" * 60)

    from app.services.divination.agents.event_predictor_agent import (
        llm_analyze_event_predict_sync,
    )

    try:
        result = llm_analyze_event_predict_sync(
            chart=SAMPLE_CHART_DATA,
            event_type="跳槽",
            target_year=2025,
            target_month=3
        )
        print(f"\nSUCCESS!")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        print(f"\nResult preview (first 500 chars):")
        result_str = json.dumps(result, ensure_ascii=False, indent=2)
        print(result_str[:500] if len(result_str) > 500 else result_str)
        return True, result
    except Exception as e:
        print(f"\nFAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def test_date_selection():
    """Test 5: llm_analyze_date_selection_sync"""
    print("\n" + "=" * 60)
    print("TEST 5: llm_analyze_date_selection_sync")
    print("=" * 60)

    from app.services.divination.agents.date_selection_agent import (
        llm_analyze_date_selection_sync,
        DailyOption,
    )

    try:
        # Convert dict options to DailyOption objects
        daily_options = [DailyOption(**opt) for opt in DAILY_OPTIONS]

        result = llm_analyze_date_selection_sync(
            chart=SAMPLE_CHART_DATA,
            date_type="结婚嫁娶",
            daily_options=daily_options,
            question="请推荐最适合结婚的日期并说明理由"
        )
        print(f"\nSUCCESS!")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        print(f"\nResult preview (first 500 chars):")
        result_str = json.dumps(result, ensure_ascii=False, indent=2)
        print(result_str[:500] if len(result_str) > 500 else result_str)
        return True, result
    except Exception as e:
        print(f"\nFAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)


# ============ Main ============

def main():
    print("=" * 60)
    print("REAL LLM FUNCTION TESTS")
    print("Testing all 5 LLM functions with real API calls")
    print("=" * 60)

    results = []

    # Test 1: Synthesis
    success, result = test_synthesis()
    results.append(("llm_analyze_synthesis_sync", success, result))

    # Test 2: Birth Timing
    success, result = test_birth_timing()
    results.append(("llm_analyze_birth_timing_sync", success, result))

    # Test 3: Marriage Compatibility
    success, result = test_marriage_compatibility()
    results.append(("llm_analyze_marriage_compatibility_sync", success, result))

    # Test 4: Event Predict
    success, result = test_event_predict()
    results.append(("llm_analyze_event_predict_sync", success, result))

    # Test 5: Date Selection
    success, result = test_date_selection()
    results.append(("llm_analyze_date_selection_sync", success, result))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for name, success, result in results:
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {name}")
        if not success:
            print(f"       Error: {str(result)[:100]}")

    print(f"\nTotal: {passed}/{total} passed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)