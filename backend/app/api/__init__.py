"""
API路由模块
"""

from flask import Blueprint

graph_bp = Blueprint('graph', __name__)
simulation_bp = Blueprint('simulation', __name__)
report_bp = Blueprint('report', __name__)

# 导入divination蓝图
try:
    from app.services.divination.api import divination_bp
    _divination_available = True
except ImportError as e:
    divination_bp = None
    _divination_available = False
    print(f"Divination import failed: {e}")

from . import graph  # noqa: E402, F401
from . import simulation  # noqa: E402, F401
from . import report  # noqa: E402, F401

