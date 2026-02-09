from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.session import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up Amarktai Marketing API...")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="Amarktai Marketing API",
    description="Autonomous AI Social Media Marketing Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "name": "Amarktai Marketing API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
