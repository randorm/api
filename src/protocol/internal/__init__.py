"""
Interal protocols module.
Protocols are absract classes / interfaces, that define behavior of services.
All internal (infrastructure) protocols (ports) should be defined here.
Example of such protocols are databases, caches, workers etc.
"""

from src.protocol.internal import database

__all__ = [database]
