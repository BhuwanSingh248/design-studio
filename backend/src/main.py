"""Main FastAPI application entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import llm_settings
from src.llm.client import LLMClient


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


@app.get("/healthz", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "ai-design-studio"}


@app.get("/test-llm", tags=["LLM"])
async def test_llm():
    llm_client = LLMClient(settings=llm_settings, cost_tracker=None)
    response = await llm_client.chat(
        messages=[
            {
                "role": "user",
                "content": "Explain what an interface is in one sentence.",
            }
        ]
    )
    content = response.choices[0].message.content if hasattr(response, "choices") else str(response)
    print("LLM Response:", response)
    return {"response": response}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)