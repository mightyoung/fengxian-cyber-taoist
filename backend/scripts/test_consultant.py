
import os
import sys

# 将 backend 目录添加到路径
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.consultant_agent import CyberTaoistConsultant

def test_consultant_chat():
    """测试咨询 Agent 的对话能力"""
    # 注意：这里我们不传入真实的 ID，仅测试其 Prompt 生成和基本响应
    consultant = CyberTaoistConsultant(simulation_id="mock_sim", chart_id="mock_chart")
    
    print("\n--- 测试咨询对话 ---")
    message = "贫道最近运势多舛，在模拟中也处处碰壁，请道长指点迷津。"
    result = consultant.chat(message)
    
    print(f"问题: {message}")
    print(f"回复: {result['response']}")
    print(f"是否有上下文: {result['has_context']}")

if __name__ == "__main__":
    test_consultant_chat()
