"""
API v1 Module - API版本1

提供版本化的API接口。
"""

from flask import Blueprint
from app.api.v1 import auth, payments

# Create v1 blueprint
v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')

# Register sub-blueprints
v1_bp.register_blueprint(auth.auth_bp)
v1_bp.register_blueprint(payments.payments_bp)

__all__ = ['v1_bp']
