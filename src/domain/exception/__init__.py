"""
Domain level exceptions module.
All domain (a.k.a. business logic) exceptions should be defined here.
"""

from src.domain.exception import base, database

__all__ = [base, database]
