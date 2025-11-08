from .auth import router as auth_router
from .employer import router as employer_router
from .jobs import router as jobs_router
from .resume import router as resume_router
from .news import router as news_router
from .resume_score import router as resume_score_router
routers = [
    auth_router,
    employer_router,
    jobs_router,
    resume_router,
    news_router,
    resume_score_router,
]
