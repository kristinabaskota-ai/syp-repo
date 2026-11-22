import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.seed import seed_database
from app.routers import (
    auth, users, products, cart, orders, wanted, import_check, doctor, reports
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all tables are created and initial demo data is seeded
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="E-commerce Marketplace for Rare Plants with AI-assisted Plant Doctor and Import Document Checker",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS setup - allow localhost and 127.0.0.1 on any port, plus any configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(wanted.router)
app.include_router(import_check.router)
app.include_router(doctor.router)
app.include_router(reports.router)

# Mount frontend static files
# Find frontend directory relative to file or current working directory
current_file_dir = Path(__file__).resolve().parent  # backend/app
frontend_dir = (current_file_dir.parent.parent / "frontend").resolve()
if not frontend_dir.exists():
    frontend_dir = (current_file_dir.parent / "frontend").resolve()

if frontend_dir.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/app/")


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "default_country": settings.DEFAULT_COUNTRY,
        "currency": settings.CURRENCY,
    }
