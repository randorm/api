"""
Application layer module.
Application is a compilation of several services, which perform designed task.
Example of application are:
- a web server, which serves HTTP requests
- a migrator, which performs database migrations
- a worker, which performs background tasks
etc
"""

from src.app import http
