#!/usr/bin/env python3
"""
FengxianCyberTaoist React Frontend Migration Task Tracker
Usage:
    python task_tracker.py list                    # List all tasks
    python task_tracker.py status <task_id>       # Show task status
    python task_tracker.py start <task_id>        # Mark task as in progress
    python task_tracker.py complete <task_id>      # Mark task as completed
    python task_tracker.py block <task_id>         # Mark task as blocked
    python task_tracker.py reset <task_id>        # Reset task to pending
    python task_tracker.py summary                # Show progress summary
    python task_tracker.py update-md              # Update markdown tracker
"""

import json
import sys
from datetime import datetime
from pathlib import Path

TRACKER_FILE = Path(__file__).parent.parent / "docs" / "tasks.json"
MD_FILE = Path(__file__).parent.parent / "docs" / "task-tracker.md"


def load_tasks():
    """Load tasks from JSON file."""
    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(data):
    """Save tasks to JSON file."""
    data["meta"]["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_counts(data):
    """Update task counts in meta."""
    total = 0
    completed = 0
    in_progress = 0

    for phase in data["phases"]:
        phase["completed"] = 0
        for task in phase["tasks"]:
            total += 1
            if task["status"] == "completed":
                completed += 1
                phase["completed"] += 1
            elif task["status"] == "in_progress":
                in_progress += 1

    data["meta"]["totalTasks"] = total
    data["meta"]["completed"] = completed
    data["meta"]["inProgress"] = in_progress


def list_tasks(data, phase_filter=None):
    """List all tasks."""
    for phase in data["phases"]:
        if phase_filter and phase["id"] != phase_filter:
            continue
        print(f"\n## {phase['id']}: {phase['name']} [{phase['completed']}/{phase['taskCount']}]")
        print("-" * 60)
        for task in phase["tasks"]:
            status_icon = {"pending": "⬜", "in_progress": "🔄", "completed": "✅", "blocked": "❌"}.get(
                task["status"], "⬜"
            )
            print(f"  {status_icon} [{task['id']}] {task['name']}")


def show_status(data, task_id):
    """Show status of a specific task."""
    for phase in data["phases"]:
        for task in phase["tasks"]:
            if task["id"] == task_id:
                status_icon = {"pending": "⬜", "in_progress": "🔄", "completed": "✅", "blocked": "❌"}.get(
                    task["status"], "⬜"
                )
                print(f"\n任务: {task['name']}")
                print(f"ID: {task['id']}")
                print(f"状态: {status_icon} {task['status']}")
                print(f"依赖: {', '.join(task['dependsOn']) if task['dependsOn'] else '无'}")
                print(f"验收标准: {task['acceptance']}")
                return
    print(f"❌ 未找到任务: {task_id}")


def update_task_status(data, task_id, new_status):
    """Update task status."""
    for phase in data["phases"]:
        for task in phase["tasks"]:
            if task["id"] == task_id:
                old_status = task["status"]
                task["status"] = new_status
                update_counts(data)
                save_tasks(data)
                status_icon = {"pending": "⬜", "in_progress": "🔄", "completed": "✅", "blocked": "❌"}.get(
                    new_status, "⬜"
                )
                print(f"✅ [{task_id}] {task['name']}")
                print(f"   状态: {old_status} → {status_icon} {new_status}")
                return
    print(f"❌ 未找到任务: {task_id}")


def show_summary(data):
    """Show progress summary."""
    meta = data["meta"]
    total = meta["totalTasks"]
    completed = meta["completed"]
    in_progress = meta["inProgress"]
    remaining = total - completed - in_progress

    print("\n" + "=" * 50)
    print("FengxianCyberTaoist React 前端迁移 - 进度概览")
    print("=" * 50)
    print(f"总任务数:   {total}")
    print(f"已完成:    {completed} ({completed/total*100:.1f}%)" if total > 0 else "已完成:    0 (0%)")
    print(f"进行中:    {in_progress}")
    print(f"待开始:    {remaining}")
    print("-" * 50)
    print("各阶段进度:")
    for phase in data["phases"]:
        pct = phase["completed"] / phase["taskCount"] * 100 if phase["taskCount"] > 0 else 0
        bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        print(f"  {phase['id']} {phase['name']:12s} [{bar}] {phase['completed']}/{phase['taskCount']} ({pct:.0f}%)")
    print("=" * 50)


def update_markdown(data):
    """Update the markdown task tracker file."""
    md_lines = [
        "# FengxianCyberTaoist React 前端任务追踪\n",
        "## 项目概览\n",
        "| 属性 | 值 |\n",
        "|------|-----|\n",
        f"| 项目名称 | FengxianCyberTaoist React 前端迁移 |\n",
        f"| 总任务数 | {data['meta']['totalTasks']} |\n",
        f"| 已完成 | {data['meta']['completed']} |\n",
        f"| 进行中 | {data['meta']['inProgress']} |\n",
        f"| 预计工时 | ~{data['meta']['estimatedHours']}h |\n",
        "\n---\n",
    ]

    for phase in data["phases"]:
        md_lines.append(f"\n## {phase['id']}: {phase['name']} [{phase['completed']}/{phase['taskCount']}]\n\n")
        md_lines.append("| 状态 | 任务 | 依赖 | 验收标准 |\n")
        md_lines.append("|------|------|------|----------|\n")
        for task in phase["tasks"]:
            status_icon = {"pending": "⬜", "in_progress": "🔄", "completed": "✅", "blocked": "❌"}.get(
                task["status"], "⬜"
            )
            deps = ", ".join(task["dependsOn"]) if task["dependsOn"] else "-"
            md_lines.append(f"| {status_icon} | {task['name']} | {deps} | {task['acceptance']} |\n")
        md_lines.append(f"\n**子任务**: {phase['completed']}/{phase['taskCount']} 完成\n")

    md_lines.append("\n---\n\n## 状态说明\n\n")
    md_lines.append("| 符号 | 含义 |\n")
    md_lines.append("|------|------|\n")
    md_lines.append("| ⬜ | 待开始 |\n")
    md_lines.append("| 🔄 | 进行中 |\n")
    md_lines.append("| ✅ | 已完成 |\n")
    md_lines.append("| ❌ | 已阻塞 |\n\n")
    md_lines.append("## 更新日志\n\n")
    md_lines.append("```\n")
    md_lines.append(f"{datetime.now().strftime('%Y-%m-%d')}  更新任务状态\n")
    md_lines.append("```\n")

    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.writelines(md_lines)

    print(f"✅ 已更新 Markdown 追踪器: {MD_FILE}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "list":
        data = load_tasks()
        phase_filter = sys.argv[2] if len(sys.argv) > 2 else None
        list_tasks(data, phase_filter)

    elif command == "status":
        if len(sys.argv) < 3:
            print("❌ 请提供任务 ID")
            sys.exit(1)
        data = load_tasks()
        show_status(data, sys.argv[2])

    elif command == "start":
        if len(sys.argv) < 3:
            print("❌ 请提供任务 ID")
            sys.exit(1)
        data = load_tasks()
        update_task_status(data, sys.argv[2], "in_progress")
        update_markdown(data)

    elif command == "complete":
        if len(sys.argv) < 3:
            print("❌ 请提供任务 ID")
            sys.exit(1)
        data = load_tasks()
        update_task_status(data, sys.argv[2], "completed")
        update_markdown(data)

    elif command == "block":
        if len(sys.argv) < 3:
            print("❌ 请提供任务 ID")
            sys.exit(1)
        data = load_tasks()
        update_task_status(data, sys.argv[2], "blocked")
        update_markdown(data)

    elif command == "reset":
        if len(sys.argv) < 3:
            print("❌ 请提供任务 ID")
            sys.exit(1)
        data = load_tasks()
        update_task_status(data, sys.argv[2], "pending")
        update_markdown(data)

    elif command == "summary":
        data = load_tasks()
        show_summary(data)

    elif command == "update-md":
        data = load_tasks()
        update_markdown(data)

    else:
        print(f"❌ 未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
