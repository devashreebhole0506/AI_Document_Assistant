from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import (
    health,
    chat,
    documents
)

from app.core.logging_config import (
    setup_logging
)


setup_logging()


app = FastAPI(
    title="AI Document Assistant",
    description=(
        "AI-powered document chatbot "
        "using FastAPI, LangChain and RAG."
    ),
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(
    health.router
)

app.include_router(
    chat.router
)

app.include_router(
    documents.router
)


frontend_directory = Path("frontend")


if frontend_directory.exists():

    app.mount(
        "/app",
        StaticFiles(
            directory=str(frontend_directory),
            html=True
        ),
        name="frontend"
    )


@app.get("/")
async def root():

    return {
        "message": "AI Document Assistant API",
        "docs": "/docs",
        "health": "/health",
        "frontend": "/app"
    }