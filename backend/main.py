from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ Import routers and database
# If this file is inside backend/, keep imports relative like below:
from backend.routers import auth, users, jobs
from backend.database import Base, engine

# ✅ Create all tables in database
print("Creating tables in database...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")

# ✅ Initialize FastAPI app
app = FastAPI(
    title="JobMatcher Backend",
    description="Backend API for Android app and ReactJS web portal",
    version="1.0.0"
)

# ✅ CORS setup (for frontend apps to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 Change later to specific URLs for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Root endpoint for quick health check
@app.get("/")
def root():
    return {"message": "FastAPI backend is running 🚀"}

# ✅ Register routers (API endpoints)
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
