from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from core.config import Settings
from routers import story, job

# Load environment settings
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

# Initialize FastAPI app
app = FastAPI(
    title="Choose Your Own Adventure",
    description="AI to generate cool interactive stories",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(story.router, prefix=settings.API_PREFIX)
app.include_router(job.router, prefix=settings.API_PREFIX)

# For local development: run with python main.py
if __name__ == "__main__":
   
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
