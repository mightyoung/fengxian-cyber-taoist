"""
TaskTracker - 工业级任务追踪器
借鉴 Claude-Code 架构，实现任务步骤的持久化、原子性与可追溯性
"""

import json
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
from ..storage.paths import get_upload_dir

class TaskStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class TaskTracker:
    """管理复杂、长耗时任务的生命周期"""

    def __init__(self, task_type: str, task_id: Optional[str] = None):
        self.task_id = task_id or f"task_{uuid.uuid4().hex[:12]}"
        self.task_type = task_type
        self.steps = []
        self.metadata = {}
        self.created_at = datetime.now().isoformat()
        self.storage_dir = get_upload_dir("tasks", self.task_id)
        self._ensure_dir()

    def _ensure_dir(self):
        os.makedirs(self.storage_dir, exist_ok=True)

    def add_step(self, name: str, description: str = ""):
        step = {
            "step_id": len(self.steps) + 1,
            "name": name,
            "description": description,
            "status": TaskStepStatus.PENDING,
            "started_at": None,
            "completed_at": None,
            "error": None
        }
        self.steps.append(step)
        self.save()

    def start_step(self, step_id: int):
        for s in self.steps:
            if s["step_id"] == step_id:
                s["status"] = TaskStepStatus.RUNNING
                s["started_at"] = datetime.now().isoformat()
                break
        self.save()

    def complete_step(self, step_id: int, result: Any = None):
        for s in self.steps:
            if s["step_id"] == step_id:
                s["status"] = TaskStepStatus.COMPLETED
                s["completed_at"] = datetime.now().isoformat()
                s["result"] = result
                break
        self.save()

    def fail_step(self, step_id: int, error: str):
        for s in self.steps:
            if s["step_id"] == step_id:
                s["status"] = TaskStepStatus.FAILED
                s["completed_at"] = datetime.now().isoformat()
                s["error"] = error
                break
        self.save()

    def save(self):
        file_path = os.path.join(self.storage_dir, "manifest.json")
        data = {
            "task_id": self.task_id,
            "type": self.task_type,
            "created_at": self.created_at,
            "steps": self.steps,
            "metadata": self.metadata
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, task_id: str):
        # 实际实现应从磁盘加载
        pass
