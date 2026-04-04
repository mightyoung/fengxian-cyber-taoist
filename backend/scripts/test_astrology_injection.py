
import os
import sys
from typing import Dict, List

# 将 backend 目录添加到路径
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.oasis_profile_generator import OasisProfileGenerator, EntityNode

def test_astrology_personality_injection():
    """测试星曜人格注入逻辑"""
    generator = OasisProfileGenerator()
    
    # 创建一个模拟实体
    entity = EntityNode(
        uuid="test-uuid-123",
        name="张三",
        labels=["Student", "Person"],
        summary="一个普通的大学生，关心时事。",
        attributes={"age": 21, "major": "Computer Science"}
    )
    
    # 场景1：注入“破军”特质 (激进)
    print("\n--- 场景1: 破军特质 ---")
    profile_pojun = generator.generate_profile_from_entity(
        entity=entity,
        user_id=1,
        use_llm=True,
        astrology_traits=["破军"]
    )
    print(f"姓名: {profile_pojun.name}")
    print(f"简介: {profile_pojun.bio}")
    print(f"详细人设片段: {profile_pojun.persona[:200]}...")
    
    # 场景2：注入“天同”特质 (佛系)
    print("\n--- 场景2: 天同特质 ---")
    profile_tiantong = generator.generate_profile_from_entity(
        entity=entity,
        user_id=2,
        use_llm=True,
        astrology_traits=["天同"]
    )
    print(f"姓名: {profile_tiantong.name}")
    print(f"简介: {profile_tiantong.bio}")
    print(f"详细人设片段: {profile_tiantong.persona[:200]}...")

if __name__ == "__main__":
    test_astrology_personality_injection()
