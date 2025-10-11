from fastapi import FastAPI
from backend.database import Base, engine
from backend.routers import users, jobs, auth

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

# Include routers
app.include_router(users)  # not users.router
app.include_router(jobs)   # not jobs.router
app.include_router(auth)   # if you want authentication routes
