"""Main FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1 import api_v1_router

app = FastAPI(
    title="AI Design Studio API",
    version="0.1.0",
    description="Collaborative Software Design Studio with AI Assistance",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routes
app.include_router(api_v1_router)


@app.get("/healthz", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "ai-design-studio"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
