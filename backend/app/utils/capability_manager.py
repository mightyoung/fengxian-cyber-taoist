"""
Capability Manager - 系统能力探测与管理
"""

import os
import logging
import importlib
from typing import Dict, Any

from ..config import Config

logger = logging.getLogger('fengxian_cyber_taoist.capability')

class CapabilityManager:
    """探测系统各项高级能力的可用状态"""
    
    @classmethod
    def get_capabilities(cls) -> Dict[str, Any]:
        """获取所有能力的可用性报告"""
        return {
            "llm": cls._check_llm(),
            "knowledge_graph": cls._check_zep(),
            "vector_db": cls._check_vector_db(),
            "redis": cls._check_redis(),
            "s3_storage": cls._check_s3(),
            "charts_and_pdf": cls._check_charts_pdf(),
            "divination": cls._check_divination(),
            "simulation": True, # 核心能力，始终开启
        }

    @classmethod
    def _check_llm(cls) -> Dict[str, Any]:
        """检查 LLM API 状态"""
        api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('LLM_API_KEY')
        return {
            "available": bool(api_key),
            "status": "ENABLED" if api_key else "DISABLED",
            "message": "LLM API Key configured" if api_key else "Missing LLM_API_KEY in .env"
        }

    @classmethod
    def _check_zep(cls) -> Dict[str, Any]:
        """检查 Zep Cloud (Knowledge Graph) 状态"""
        api_key = os.environ.get('ZEP_API_KEY')
        return {
            "available": bool(api_key),
            "status": "ENABLED" if api_key else "DISABLED",
            "message": "Zep API Key configured" if api_key else "Missing ZEP_API_KEY in .env"
        }

    @classmethod
    def _check_vector_db(cls) -> Dict[str, Any]:
        """检查 ChromaDB/VectorDB 状态"""
        # 这里尝试导入并检查，避免直接报错
        try:
            import chromadb
            available = True
            msg = "ChromaDB available"
        except ImportError:
            available = False
            msg = "chromadb package not installed"
        
        return {
            "available": available,
            "status": "ENABLED" if available else "DISABLED",
            "message": msg
        }

    @classmethod
    def _check_redis(cls) -> Dict[str, Any]:
        """检查 Redis 缓存状态"""
        try:
            import redis
            host = os.environ.get('REDIS_HOST', 'localhost')
            r = redis.Redis(host=host, port=int(os.environ.get('REDIS_PORT', 6379)), socket_timeout=1)
            r.ping()
            available = True
            msg = f"Redis connected at {host}"
        except Exception as e:
            available = False
            msg = f"Redis unavailable: {str(e)}"
            
        return {
            "available": available,
            "status": "ENABLED" if available else "DISABLED",
            "message": msg
        }

    @classmethod
    def _check_s3(cls) -> Dict[str, Any]:
        """检查 S3 存储状态"""
        endpoint = os.environ.get('S3_ENDPOINT_URL')
        bucket = os.environ.get('S3_BUCKET_NAME')
        available = bool(endpoint and bucket)
        return {
            "available": available,
            "status": "ENABLED" if available else "DISABLED",
            "message": "S3 configured" if available else "S3 not configured (using local storage)"
        }

    @classmethod
    def _check_charts_pdf(cls) -> Dict[str, Any]:
        """检查图表和 PDF 生成能力"""
        try:
            import matplotlib
            import fitz # PyMuPDF
            available = True
            msg = "Matplotlib and PyMuPDF available"
        except ImportError as e:
            available = False
            msg = f"Missing dependencies: {str(e)}"
            
        return {
            "available": available,
            "status": "ENABLED" if available else "DISABLED",
            "message": msg
        }

    @classmethod
    def _check_divination(cls) -> Dict[str, Any]:
        """检查命理分析模块可用性"""
        try:
            importlib.import_with_name = importlib.import_module("app.services.divination.agents.report_generator")
            available = True
            msg = "Divination modules loaded successfully"
        except Exception as e:
            available = False
            msg = f"Divination module error: {str(e)}"
            
        return {
            "available": available,
            "status": "ENABLED" if available else "DISABLED",
            "message": msg
        }
