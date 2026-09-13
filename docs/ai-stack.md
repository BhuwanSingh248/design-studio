# AI Stack Architecture Guide

This document maps the 12 core AI concepts directly to the components within the **AI Design Studio**.

## 1. LLM & Providers
Native integration via provider SDKs (Groq, OpenAI, Anthropic, Gemini) encapsulated in `backend/src/llm/client.py`.

## 2. Prompts & System Instructions
Contextually constructed system prompts injecting diagram context, design decisions, and grounded knowledge.

## 3. Context Window & Token Management
Dynamic message sliding-window pruning implemented in `backend/src/domain/models/session.py`.

## 4. Temperature & Sampling
Controlled determinism: temperature=0 for structured diagram schema generation; temperature=0.3 for architectural trade-off evaluations.

## 5. Tools & Function Calling
Clean JSON schema declaration and sandboxed dispatching in `backend/src/tools/`.

## 6. Workflow vs. Agent
Deterministic LangGraph state machine with human-in-the-loop checkpoints in `backend/src/agents/graph.py`.

## 7. RAG (Retrieval-Augmented Generation)
Grounding architectural advice against verified engineering literature (SOLID, GoF, Clean Architecture).

## 8. Embeddings
Dense vector generation via `backend/src/rag/embeddings.py`.

## 9. Vector Database (pgvector)
PostgreSQL extension for cosine distance search on software design knowledge chunks (`backend/src/rag/vector_store.py`).

## 10. Memory
Three distinct tiers:
- Ephemeral canvas state (in-memory)
- Session conversation turns (sliding window)
- Long-term architectural decision records (`backend/src/domain/memory.py`)

## 11. Evaluation
Automated schema validity, tool precision/recall, and LLM-as-a-judge scorers in `backend/tests/eval/`.

## 12. Fine-Tuning vs. Grounded In-Context Learning
Prioritizing verifiable in-context grounding with citations (`backend/src/rag/citations.py`) over ungrounded parametric fine-tuning.
