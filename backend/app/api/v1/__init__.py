"""
API v1 Module - API版本1

提供版本化的API接口。
"""

from flask import Blueprint
from app.api.v1 import auth, payments, system, user, divination_case

# Create v1 blueprint
v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')

# Register sub-blueprints
v1_bp.register_blueprint(auth.auth_bp)
v1_bp.register_blueprint(payments.payments_bp)
v1_bp.register_blueprint(system.system_bp, url_prefix='/system')
v1_bp.register_blueprint(user.user_bp, url_prefix='/user')
v1_bp.register_blueprint(divination_case.case_bp, url_prefix='/divination/case')

__all__ = ['v1_bp']
