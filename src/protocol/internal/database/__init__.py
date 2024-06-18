"""
Database Protocols module.
All protocols related to CRUD operations with databases should be defined here.
"""

from src.protocol.internal.database import allocation, form_field, room, user

__all__ = [allocation, form_field, room, user]
