import subprocess
from fastapi import FastAPI
from backend.database import Base, engine
from backend.routers.jobs import router as jobs_router
from backend.routers.auth import router as auth_router
from backend.routers.resume import router as resumes_router
from backend.routers.employer import router as employer_router
from backend.routers.news import router as news_router
from backend.routers.test_news import router as test_news_router

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize app (only once!)
app = FastAPI(
    title="Job Matcher API",
    description="API backend for the Job Matcher platform",
    version="1.0.0"
)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Backend is running!"}

#@app.on_event("startup")
#def run_migrations():
#    try:
#        print("⚙️ Running Alembic migrations...")
#        subprocess.run(["alembic", "upgrade", "head"], check=True)
#        print("✅ Database is up to date.")
#    except Exception as e:
#        print(f"❌ Migration failed: {e}")

# Include routers
app.include_router(jobs_router)
app.include_router(auth_router)
app.include_router(resumes_router)
app.include_router(employer_router)
app.include_router(news_router)
app.include_router(test_news_router)