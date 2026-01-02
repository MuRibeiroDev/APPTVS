"""
Routes package
"""

from .api_routes import create_routes as create_api_routes
from .web_routes import create_web_routes

__all__ = ['create_api_routes', 'create_web_routes']
