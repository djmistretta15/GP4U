"""
Celery Worker Entry Point
Import this file to start the Celery worker
"""
from app.services.worker import celery_app

__all__ = ['celery_app']
