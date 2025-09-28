from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth, users, jobs
from backend.database import Base, engine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JobMatcher Backend",
    description="Backend API for Android app and ReactJS web portal",
    version="1.0.0"
)

# Allow Android and ReactJS frontends to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Replace "*" with your frontends' URLs for security, e.g., "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for quick health check
@app.get("/")
def root():
    return {"message": "FastAPI backend is running 🚀"}

# Register routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
