from aiogram import Router

from .base import router as base_router
from .resumes import router as resumes_router
from .interview_flow import router as interview_router
from .history import router as history_router

router = Router()
router.include_routers(
    resumes_router,
    history_router,
    interview_router,
    base_router
)
