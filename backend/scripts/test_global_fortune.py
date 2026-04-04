
import os
import sys

# 将 backend 目录添加到路径
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.models.divination import DivinationManager

def test_global_stats():
    """测试全服运势聚合逻辑"""
    print("\n--- 测试全服运势聚合 ---")
    stats = DivinationManager.get_global_stats()
    
    print(f"总计报告数: {stats['total_count']}")
    print(f"吉凶分布: {stats['vibe_distribution']}")
    print(f"吉凶比例: {stats['vibe_percentages']}")
    print(f"平均预测年份: {stats['average_year']}")
    print(f"更新时间: {stats['updated_at']}")

if __name__ == "__main__":
    test_global_stats()
