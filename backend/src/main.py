"""
FastAPI application entry point for the Todo API.

This module initializes the FastAPI application with CORS configuration,
API routers, and health check endpoints.
"""


import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .models.database import init_db, close_db
from .api.auth import auth_router
from .api.todos import todos_router
from .api.chat_api import router as chat_router


# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup (sync functions called without await since using psycopg2 sync driver)
    print("Starting Todo API...")
    init_db()
    print("Database initialized successfully!")
    yield
    # Shutdown
    print("Shutting down Todo API...")
    close_db()
    print("Database connections closed!")


# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="Full-stack web todo application API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
print(f"FRONTEND_URL from environment: {frontend_url}")

# Parse multiple origins from FRONTEND_URL (comma-separated) or use default
origins = [url.strip() for url in frontend_url.split(",") if url.strip()]
print(f"Parsed origins from FRONTEND_URL: {origins}")

# Add common development and production URLs
default_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",  # Additional ports for when 3000-3003 are in use
    "https://todo-app-phase-ii-veok.vercel.app",
]

# Combine and deduplicate origins
all_origins = list(set(origins + default_origins))
print(f"All allowed origins: {all_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(todos_router, prefix="/todos", tags=["Todos"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check."""
    return {"status": "healthy", "message": "Todo API is running"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
