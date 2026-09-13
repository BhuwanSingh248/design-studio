# AI Design Studio — Learning & Project Roadmap

## Project Vision

Build **AI Design Studio**, a collaborative software-design workspace where a human and AI can work together on diagrams such as:

- Class diagrams
- Sequence diagrams
- Component diagrams
- Architecture diagrams
- ER diagrams

The long-term goal is:

> **Excalidraw-style collaborative canvas + AI design assistant + conversation + knowledge retrieval + AI-driven canvas editing.**

### Example interaction

Human draws:

```text
┌───────────────┐
│     User      │
├───────────────┤
│ - id          │
│ - name        │
├───────────────┤
│ + login()     │
└───────┬───────┘
        │ creates
        ▼
┌───────────────┐
│     Order     │
├───────────────┤
│ - id          │
│ - amount      │
└───────────────┘
```

Human:

> Is this design following SOLID?

AI:

> Mostly, but `User.login()` couples authentication behavior to the entity. I'd consider moving authentication behavior into an `AuthenticationService`.

Later:

> I recommend changing the diagram.

Human:

> Do it.

AI modifies the shared canvas through validated application tools.

---

# Learning Philosophy

We will build **one project incrementally** instead of creating disconnected AI demos.

Every phase follows:

```text
Concept
   ↓
Minimal implementation
   ↓
Integrate into AI Design Studio
   ↓
Break it intentionally
   ↓
Debug / analyze failure
   ↓
Design discussion
   ↓
Tests
   ↓
Git commit
   ↓
Next phase
```

For every important component, ask:

- What problem does it solve?
- What happens without it?
- What does the LLM control?
- What does the application control?
- What can fail?
- What are the security implications?
- What are the scaling implications?
- What are the alternatives?
- How would this be discussed in an interview?

---

# Technology Direction

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Redis
- WebSockets

## AI

Start with the provider's direct LLM API.

Learn the primitives before introducing orchestration frameworks:

- LLM API
- Prompting
- Structured output
- Function/tool calling
- Embeddings
- Evaluation
- RAG
- Agents

Introduce LangGraph only after understanding the underlying workflow.

## RAG

Initial direction:

- PostgreSQL
- pgvector

Later evaluate dedicated vector databases if useful.

## Frontend

- React
- TypeScript
- Collaborative canvas library
- WebSocket client

The exact canvas implementation can be selected when the project reaches the collaboration phases.

---

# High-Level Architecture Evolution

The architecture will evolve rather than being built all at once.

## Starting Point

```text
User
 │
 ▼
Chat UI
 │
 ▼
Backend
 │
 ▼
LLM
 │
 ▼
Response
```

## Intermediate System

```text
                    AI Design Studio

User
 │
 ├──────────────► Chat
 │
 └──────────────► Canvas
                       │
                       ▼
                    State
                       │
                       ▼
                      AI
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
      Tools          Memory          RAG
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                  AI Workflow
                       │
                       ▼
                Canvas Changes
```

## Final Direction

```text
                         ┌──────────────────┐
                         │      Browser     │
                         │                  │
                         │  ┌────────────┐  │
                         │  │   Canvas   │  │
                         │  └────────────┘  │
                         │                  │
                         │  ┌────────────┐  │
                         │  │    Chat    │  │
                         │  └────────────┘  │
                         └────────┬─────────┘
                                  │
                         HTTP + WebSocket
                                  │
                                  ▼
                    ┌──────────────────────┐
                    │       Backend        │
                    │                      │
                    │ Workspace Service    │
                    │ Canvas Service       │
                    │ Collaboration        │
                    │ AI Service            │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼─────────────────┐
              │                │                 │
              ▼                ▼                 ▼
          PostgreSQL       Vector DB           Redis
              │                │                 │
              │                ▼                 │
              │               RAG                │
              │                │                 │
              └────────────────┼─────────────────┘
                               ▼
                         AI Orchestrator
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
                   LLM       Tools       Memory
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         Canvas Tools     Search Tools    Analysis Tools
```

---

# Phase 0 — AI Stack Foundations

## Goal

Understand the complete AI application stack before implementing advanced functionality.

## Topics

- LLM
- Prompt
- Context window
- Tokens
- Temperature
- Tools
- Function calling
- Workflow
- Agent
- RAG
- Embeddings
- Vector database
- Memory
- Evaluation
- Fine-tuning

## Project Work

Create a small architecture document for AI Design Studio showing where each concept will eventually fit.

## Deliverable

```text
docs/
└── ai-stack.md
```

The document should explain:

```text
LLM
Prompt
Tools
Function Calling
Workflow
Agent
RAG
Embeddings
Vector DB
Memory
Evaluation
Fine-tuning
```

## Exit Criteria

You should be able to explain:

1. What an LLM is.
2. What prompting does.
3. Difference between tool calling and an agent.
4. Difference between RAG and fine-tuning.
5. Why embeddings are needed for semantic retrieval.
6. What a vector database stores.
7. Why memory is different from RAG.
8. Why evaluation is required.

---

# Phase 1 — LLM API Fundamentals

## Goal

Build the first working AI backend.

## Architecture

```text
User
 │
 ▼
POST /chat
 │
 ▼
LLMClient
 │
 ▼
LLM Provider
 │
 ▼
Response
 │
 ▼
User
```

## Topics

- API authentication
- Request/response lifecycle
- System prompt
- User messages
- Conversation history
- Model selection
- Temperature
- Token usage
- Timeouts
- Retries
- Error handling
- Streaming
- Configuration management

## Project Deliverable

Create:

```text
backend/
├── app/
│   ├── api/
│   ├── services/
│   ├── llm/
│   │   └── client.py
│   └── main.py
├── tests/
└── pyproject.toml
```

Implement:

```python
class LLMClient:
    def chat(...):
        ...
```

Expose:

```http
POST /chat
```

## AI Design Studio Feature

User can ask:

> Review this software design.

Initially the design can simply be supplied as text.

## Exit Criteria

- Working LLM API integration
- `LLMClient` abstraction
- Configuration separated from code
- Error handling
- Basic tests
- Token/cost logging

---

# Phase 2 — Structured Output

## Goal

Stop relying on free-form LLM text when the application needs machine-readable data.

## Architecture

```text
LLM
 │
 ▼
Structured Output
 │
 ▼
Pydantic Validation
 │
 ▼
Application Model
```

## Topics

- JSON
- JSON Schema
- Pydantic
- Validation
- Required fields
- Optional fields
- Enum values
- Invalid model output
- Retry / repair strategies

## Project Deliverable

Define a diagram model.

Example:

```python
class ClassDefinition(BaseModel):
    name: str
    attributes: list[Attribute]
    methods: list[Method]
```

And:

```python
class Relationship(BaseModel):
    source: str
    target: str
    relationship_type: RelationshipType
```

## AI Design Studio Feature

User:

> Create a class diagram for an ecommerce system.

AI returns a validated design model.

```text
LLM
 ↓
Pydantic
 ↓
Validated Diagram
```

## Exit Criteria

- LLM returns structured data
- Invalid output is rejected
- Domain models are independent of LLM response objects
- Tests cover malformed output

---

# Phase 3 — Tool Calling

## Goal

Allow AI to request safe application operations.

## Tools

Initial tools:

```text
create_class
delete_class
rename_class
add_attribute
remove_attribute
add_method
remove_method
add_relationship
remove_relationship
```

## Architecture

```text
                AI
                 │
           Tool Decision
                 │
                 ▼
          Application Tool
                 │
                 ▼
          Validate Request
                 │
                 ▼
            Execute
                 │
                 ▼
           Canvas State
```

## Critical Rule

The LLM does **not** directly modify the database.

```text
LLM
 ↓
Tool Request
 ↓
Validation
 ↓
Authorization
 ↓
Application Logic
 ↓
State Change
```

## Topics

- Function calling
- Tool schemas
- Tool validation
- Tool authorization
- Tool errors
- Idempotency
- Safe tool design

## Exit Criteria

- AI can request canvas operations
- Application validates every operation
- Invalid operations fail safely
- Tool execution is testable without the LLM

---

# Phase 4 — Tool-Calling Harness

## Goal

Build the first agent-like workflow.

## Workflow

```text
User Request
     │
     ▼
    LLM
     │
     ▼
Tool Call?
 ┌───┴────┐
No       Yes
 │         │
 ▼         ▼
Response  Tool Runner
             │
             ▼
          Tool Result
             │
             ▼
             LLM
             │
             ▼
          Response
```

## Example

Human:

> Create an ecommerce class diagram.

AI:

```text
create_class(User)
create_class(Product)
create_class(Order)
create_class(OrderItem)

add_relationship(User, Order)
add_relationship(Order, OrderItem)
add_relationship(OrderItem, Product)
```

## Topics

- Tool loop
- Maximum iterations
- Tool errors
- Partial execution
- Retry policy
- Stop conditions
- Tool result handling

## Exit Criteria

AI can complete a multi-step canvas task through tools.

---

# Phase 5 — Memory / State

## Goal

Make the system persistent and understand the difference between application state and AI memory.

## State Types

### Canvas State

The canonical diagram.

```text
Workspace
 └── Canvas
      ├── Nodes
      ├── Relationships
      └── Positions
```

### Conversation State

```text
Conversation
 ├── User messages
 ├── AI responses
 └── Tool calls
```

### AI Memory

Important facts such as:

```text
"We decided to keep authentication outside User."
```

## Architecture

```text
Workspace
 ├── Canvas State
 ├── Conversation
 └── Design Decisions
```

## Topics

- Stateful conversations
- Persistence
- Context management
- Conversation summarization
- Short-term vs long-term memory
- Canonical application state

## Exit Criteria

- Refreshing the application preserves state
- Conversation can continue later
- Canvas state is persisted independently from conversation
- Memory is not confused with RAG

---

# Phase 6 — Evaluation

## Goal

Measure AI behavior rather than trusting whether its answer sounds convincing.

## Evaluation Areas

```text
LLM
 ├── Answer correctness
 ├── Structured output validity
 ├── Tool-call accuracy
 └── Failure handling

Future RAG
 ├── Retrieval quality
 ├── Grounding
 └── Citation correctness
```

## Example Test

Input:

```text
User has many Orders.
Each Order belongs to one User.
```

Expected:

```text
User 1 ───── N Order
```

## Metrics

- Structured output validity
- Tool-call accuracy
- Task completion
- Answer correctness
- Hallucination rate
- Latency
- Token usage
- Cost

## Exit Criteria

Create a repeatable evaluation suite and baseline.

---

# Phase 7 — RAG

## Goal

Give AI access to software-design knowledge.

## Knowledge Base

Potential sources:

```text
SOLID
Design Patterns
DDD
Clean Architecture
UML
Database Design
System Design
LLD
Distributed Systems
```

## Pipeline

```text
Documents
    │
    ▼
Ingestion
    │
    ▼
Parsing
    │
    ▼
Chunking
    │
    ▼
Embeddings
    │
    ▼
Vector DB
    │
    ▼
Retriever
    │
    ▼
LLM
```

## Topics

- Document ingestion
- Text extraction
- Chunking
- Metadata
- Embeddings
- Vector similarity
- Vector databases
- Retrieval

## Exit Criteria

AI can retrieve relevant design knowledge before answering.

---

# Phase 8 — Retrieval Quality

## Goal

Improve retrieval instead of assuming the vector database is magical.

## Topics

- Chunk size
- Chunk overlap
- Metadata filtering
- Top-K
- Similarity thresholds
- Query transformation
- Embedding model selection
- Retrieval failure analysis

## Experiment

Create retrieval test cases:

```text
Question
   ↓
Expected relevant documents
   ↓
Actual retrieved documents
   ↓
Compare
```

## Exit Criteria

Have measurable retrieval-quality improvements over the Phase 7 baseline.

---

# Phase 9 — Hybrid Search

## Goal

Combine lexical and semantic retrieval.

## Architecture

```text
                  Query
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
        BM25                Vector
          │                   │
          └─────────┬─────────┘
                    ▼
             Hybrid Results
```

## Why

Vector search is good at semantic similarity.

BM25 is good at exact terminology.

Software design contains many exact terms, identifiers, class names, APIs, and technical phrases.

## Exit Criteria

Implement and evaluate:

```text
Vector Search
vs
BM25
vs
Hybrid Search
```

---

# Phase 10 — Reranking

## Goal

Improve the ordering of retrieved candidates.

## Architecture

```text
Query
  │
  ▼
Hybrid Search
  │
  ▼
Candidate Documents
  │
  ▼
Reranker
  │
  ▼
Best Documents
  │
  ▼
LLM
```

## Topics

- Candidate generation
- Reranking
- Precision vs recall
- Latency trade-offs
- Retrieval pipeline design

## Exit Criteria

Demonstrate measurable improvement on retrieval evaluation data.

---

# Phase 11 — Grounding + Citations

## Goal

Make AI answers traceable to retrieved knowledge.

## Architecture

```text
User Question
      │
      ▼
Retrieval
      │
      ▼
Relevant Sources
      │
      ▼
LLM
      │
      ├── Answer
      └── Citations
```

## Example

AI:

> The class has two responsibilities: authentication and user state management.

Then:

```text
Sources:
- Design principle documentation
- Architecture guide
```

## Topics

- Grounded generation
- Citation generation
- Source attribution
- Unsupported claims
- Citation correctness

## Exit Criteria

AI answers can identify the source supporting important claims.

---

# Phase 12 — RAG Evaluation

## Goal

Evaluate the complete retrieval + generation pipeline.

## Evaluation

```text
Question
   │
   ▼
Retriever
   │
   ├── Retrieval quality
   │
   ▼
Context
   │
   ▼
LLM
   │
   ├── Answer quality
   ├── Grounding
   └── Citation correctness
```

## Metrics

- Recall@K
- Precision@K
- MRR
- Context relevance
- Answer correctness
- Groundedness
- Citation correctness

## Exit Criteria

Have a benchmark and measurable RAG quality.

---

# Phase 13 — Production Hardening

## Goal

Turn the learning project into a reliable application.

## Areas

### Security

- Authentication
- Authorization
- Workspace isolation
- Prompt injection defense
- Tool authorization
- Input validation

### Reliability

- Timeouts
- Retries
- Circuit breakers where appropriate
- Idempotency
- Failure recovery

### Cost

- Token tracking
- Rate limits
- Usage limits
- Model selection
- Context management

### Observability

- Structured logs
- Metrics
- Tracing
- AI request tracing
- Tool execution logs

## Exit Criteria

The application has explicit security, reliability, observability, and cost controls.

---

# Phase 14 — Agents

## Goal

Introduce agents after understanding the primitives underneath them.

## Initial Agent Architecture

```text
                    Design Agent
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    Analyzer           RAG            Canvas Tools
        │                │                │
        ▼                ▼                ▼
 Design Rules       Knowledge Base     Canvas State
```

## Possible Specialized Agents

```text
DesignAnalyzer
ArchitectureReviewer
PatternAdvisor
RAGResearcher
CanvasEditor
```

## Example

User:

> Review my class diagram and fix the SOLID violations.

Workflow:

```text
Analyze
   ↓
Identify issues
   ↓
Retrieve relevant principles
   ↓
Generate recommendations
   ↓
Ask for approval / determine allowed action
   ↓
Modify canvas
   ↓
Validate result
```

## Exit Criteria

Build a controlled multi-step agent workflow with explicit state and tool boundaries.

---

# Phase 15 — LangGraph

## Goal

Model complex AI workflows explicitly.

## Workflow

```text
START
  │
  ▼
Analyze Design
  │
  ▼
Need Knowledge?
 ┌┴─────────┐
Yes         No
 │           │
 ▼           │
Retrieve     │
 │           │
 ▼           │
Rerank       │
 │           │
 └─────┬─────┘
       ▼
Generate Recommendation
       │
       ▼
Need Canvas Change?
 ┌─────┴─────┐
Yes          No
 │            │
 ▼            ▼
Tool         Response
 │
 ▼
Validate
 │
 ▼
Update Canvas
 │
 ▼
Response
```

## Topics

- Graph-based workflows
- Explicit state
- Nodes
- Edges
- Conditional routing
- Checkpoints
- Human-in-the-loop
- Agent persistence
- Failure recovery

## Exit Criteria

Rebuild the agent workflow using LangGraph and understand what abstraction it provides compared with the manually implemented harness.

---

# Phase 16 — Deployment / Cloud

## Goal

Deploy the complete system.

## Target Architecture

```text
                         Internet
                            │
                            ▼
                     ┌────────────┐
                     │   Client   │
                     └─────┬──────┘
                           │
                    HTTP/WebSocket
                           │
                           ▼
                  ┌──────────────────┐
                  │   API / Backend  │
                  └────────┬─────────┘
                           │
          ┌────────────────┼─────────────────┐
          ▼                ▼                 ▼
     PostgreSQL          Redis           AI Service
          │                                  │
          │                                  ▼
          │                                  LLM
          │
          ▼
      pgvector
```

## Topics

- Containers
- CI/CD
- Cloud deployment
- Secrets management
- Database migrations
- Horizontal scaling
- WebSocket scaling
- Redis
- Background workers
- Monitoring
- Production configuration

## Exit Criteria

The application is publicly deployable and has basic production observability.

---

# Collaboration Track

The AI roadmap alone is not enough for the final product.

AI Design Studio also needs a **real-time collaboration track**.

This becomes important once the core AI concepts are understood.

## Collaboration Topics

```text
WebSockets
    ↓
Real-time events
    ↓
Canvas synchronization
    ↓
Presence
    ↓
Concurrent edits
    ↓
Conflict resolution
    ↓
Versioning
    ↓
AI as a collaborative participant
```

## Target Interaction

```text
             Workspace
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      User A   User B     AI
        │        │        │
        └────────┼────────┘
                 ▼
              Canvas
```

## Key Design Question

> Who owns the canonical state when a human and AI modify the document simultaneously?

Do not solve this during Phase 1.

It becomes a deliberate system-design problem later.

---

# Final Product Capabilities

By the end of the roadmap, AI Design Studio should support:

## Canvas

- Create diagrams
- Edit diagrams
- Move elements
- Create relationships
- Delete elements
- Persist diagrams
- Version diagrams

## AI

- Discuss diagrams
- Understand diagram state
- Review architecture
- Suggest improvements
- Search design knowledge
- Cite sources
- Execute safe canvas operations
- Perform multi-step workflows

## Collaboration

- Shared workspace
- Multiple users
- Real-time updates
- Presence
- Conflict handling
- AI as a participant

## Engineering

- Structured AI outputs
- Tool calling
- Memory/state
- Evaluation
- RAG
- Hybrid retrieval
- Reranking
- Grounding
- Agents
- LangGraph
- Observability
- Security
- Cloud deployment

---

# Phase Completion Checklist

For each phase:

```text
[ ] Understand the concept
[ ] Explain the problem it solves
[ ] Implement minimal version
[ ] Integrate with AI Design Studio
[ ] Write tests
[ ] Intentionally break it
[ ] Analyze failure
[ ] Document design decisions
[ ] Review trade-offs
[ ] Create Git commit
[ ] Complete exit criteria
```

---

# Suggested Repository Structure

The structure will evolve, but the initial direction is:

```text
ai-design-studio/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── domain/
│   │   ├── services/
│   │   ├── llm/
│   │   └── main.py
│   │
│   └── tests/
│
├── frontend/
│
├── docs/
│   ├── ai-stack.md
│   ├── architecture/
│   ├── decisions/
│   └── evaluations/
│
├── experiments/
│
├── README.md
└── pyproject.toml
```

---

# Learning Order

```text
PHASE 0
AI Stack
   ↓
PHASE 1
LLM API Fundamentals
   ↓
PHASE 2
Structured Output
   ↓
PHASE 3
Tool Calling
   ↓
PHASE 4
Tool-Calling Harness
   ↓
PHASE 5
Memory / State
   ↓
PHASE 6
Evaluation
   ↓
PHASE 7
RAG
   ↓
PHASE 8
Retrieval Quality
   ↓
PHASE 9
Hybrid Search
   ↓
PHASE 10
Reranking
   ↓
PHASE 11
Grounding + Citations
   ↓
PHASE 12
RAG Evaluation
   ↓
PHASE 13
Production Hardening
   ↓
PHASE 14
Agents
   ↓
PHASE 15
LangGraph
   ↓
PHASE 16
Deployment / Cloud
   ↓
COLLABORATIVE REAL-TIME SYSTEM
   ↓
AI + HUMAN SHARED DESIGN WORKSPACE
```

---

# Rule for This Project

We do **not** jump ahead because a framework makes something look easy.

The intended progression is:

```text
Understand primitive
       ↓
Build primitive
       ↓
Build abstraction
       ↓
Understand abstraction
       ↓
Use framework
```

For example:

```text
LLM API
  ↓
Manual tool loop
  ↓
Agent abstraction
  ↓
LangGraph
```

rather than:

```text
Install framework
  ↓
Copy tutorial
  ↓
Declare victory
```

The second approach is how humans end up knowing six AI frameworks and understanding none of them.

---

# First Milestone

Start with **Phase 1: LLM API Fundamentals**.

The first implementation should be intentionally small:

```text
POST /chat
    ↓
LLMClient
    ↓
LLM Provider
    ↓
Response
```

Do not build the canvas, RAG, agents, or collaboration system yet.

The objective of the first milestone is to understand exactly what happens between a user message and an LLM response before adding machinery around it.
