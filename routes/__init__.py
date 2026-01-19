"""
Routes package initialization
"""
from .auth_routes import auth_bp
from .record_routes import record_bp
from .comment_routes import comment_bp
from .report_routes import report_bp

__all__ = ['auth_bp', 'record_bp', 'comment_bp', 'report_bp']
