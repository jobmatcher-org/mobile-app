import subprocess
from fastapi import FastAPI
from backend.database import Base, engine
from backend.routers import users, jobs, auth, resumes, employer

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

@app.on_event("startup")
def run_migrations():
    try:
        print("⚙️ Running Alembic migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("✅ Database is up to date.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

# Include routers
app.include_router(users)  # not users.router
app.include_router(jobs)   # not jobs.router
app.include_router(auth)   # if you want authentication routes
app.include_router(resumes)
app.include_router(employer.router)