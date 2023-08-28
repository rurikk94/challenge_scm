from fastapi import APIRouter

from src.v1 import reports

v1 = APIRouter()

v1.include_router(reports.reports_routes, prefix='/reports')