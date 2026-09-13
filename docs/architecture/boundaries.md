# Architectural Boundary Matrix

| Concern | Application Controls | LLM Controls | Safety Mechanism |
|---|---|---|---|
| **Canvas State** | Canonical state, validation rules, mutation execution | Proposes tool calls with target arguments | Tools validate identifiers, existence, and invariants before mutation |
| **Database Persistence** | Database transactions, foreign keys, snapshots | Zero direct database access | Pydantic validation & repository abstractions |
| **Tool Execution** | Dispatch authorization, bounds checking, iteration limit | Tool selection and parameter synthesis | `ToolExecutionHarness` loop ceiling (max 10 iterations) |
| **Knowledge Retrieval** | Chunking, hybrid BM25 + pgvector query execution, reranking | Query formulation and synthesis | Strict source citation mapping and entailment verification |
