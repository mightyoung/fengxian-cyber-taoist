#!/usr/bin/env python3
"""
测试隔离检查脚本

检查生产代码(app目录)是否错误导入了测试代码(tests目录)。
这可以防止Mock数据意外进入生产环境。

使用方法:
    python scripts/check_test_isolation.py
    python scripts/check_test_isolation.py --fix  # 自动修复（可选）

退出码:
    0: 检查通过，无问题
    1: 发现问题
"""

import os
import sys
import re
import argparse
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
APP_DIR = PROJECT_ROOT / "app"
TESTS_DIR = PROJECT_ROOT / "tests"

# 需要检查的导入模式
FORBIDDEN_PATTERNS = [
    (r"from\s+tests\b", "tests模块导入"),
    (r"import\s+tests\b", "tests模块导入"),
    (r"from\s+\.\.?tests\b", "相对tests导入"),
    (r"from\s+tests\.mocks", "tests.mocks导入"),
    (r"import\s+tests\.mocks", "tests.mocks导入"),
    (r"MockChartAgent", "Mock类导入"),
    (r"MockPatternAgent", "Mock类导入"),
    (r"MockCausalChainPredictor", "Mock类导入"),
    (r"MockLLMClient", "Mock类导入"),
    (r"SAMPLE_CHART_DATA", "测试数据导入"),
]

# 需要排除的目录
EXCLUDE_DIRS = {
    "tests",
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    "node_modules",
}


def check_file(file_path: Path) -> list:
    """检查单个文件"""
    issues = []

    # 跳过测试目录本身
    if "tests" in file_path.parts:
        return issues

    # 只检查Python文件
    if file_path.suffix != ".py":
        return issues

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return issues

    for pattern, description in FORBIDDEN_PATTERNS:
        if re.search(pattern, content):
            issues.append({
                "file": str(file_path.relative_to(PROJECT_ROOT)),
                "pattern": description,
                "match": pattern,
            })

    return issues


def scan_directory(directory: Path) -> list:
    """扫描目录"""
    issues = []

    for root, dirs, files in os.walk(directory):
        # 排除不需要检查的目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        root_path = Path(root)
        for file in files:
            if file.endswith(".py"):
                file_path = root_path / file
                issues.extend(check_file(file_path))

    return issues


def main():
    parser = argparse.ArgumentParser(description="检查测试隔离")
    parser.add_argument("--fix", action="store_true", help="自动修复（目前不支持）")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    print("=" * 60)
    print("测试隔离检查")
    print("=" * 60)
    print(f"检查目录: {APP_DIR}")
    print()

    # 扫描app目录
    issues = scan_directory(APP_DIR)

    if issues:
        print(f"❌ 发现 {len(issues)} 个问题:")
        print()
        for issue in issues:
            print(f"  📁 {issue['file']}")
            print(f"     问题: {issue['pattern']}")
            print(f"     匹配: {issue['match']}")
            print()
        print("=" * 60)
        print("检查失败！生产代码不应导入测试代码。")
        print("=" * 60)
        return 1
    else:
        print("✅ 检查通过！没有发现测试代码导入。")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
